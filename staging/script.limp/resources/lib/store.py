import json
import os
import re

import xbmcvfs

from bossanova808.constants import HOME_WINDOW, PROFILE
from bossanova808.logger import Logger
from bossanova808.utilities import get_setting, get_setting_as_bool, set_property, clear_property
from bossanova808.show_list import ShowList, title_key
# noinspection PyPackages
from .messages import AMLOGIC_PROPERTY, CONTEXT_MENU_PROPERTY, SERIES_FILE, SERIES_LISTED_PROPERTY
# noinspection PyPackages
from .platforms import Platform
# noinspection PyPackages
from .probe import probe_file, BROKEN_ROTATIONS, BROKEN_AVI_CODECS

# Number of path slots offered in the add-on's settings
NUMBER_OF_PATH_SETTINGS = 5

# What Kodi calls the resolutions that count as "1080p and below" (ListItem.VideoResolution)
LOW_RESOLUTIONS = ("480", "576", "540", "720", "1080")
# Otherwise, the size a video may be (1088 allows for macroblock padding) to count as "1080p and below"
LOW_RESOLUTION_MAX_WIDTH = 1920
LOW_RESOLUTION_MAX_HEIGHT = 1088

# Live TV only reveals its resolution once playing, by which time Kodi has already chosen the decoder
IGNORED_PREFIXES = ('pvr://',)
# Paths whose files we can't read the headers of - all we can go on is the resolution Kodi tells us
UNPROBEABLE_PREFIXES = ('plugin://', 'videodb://', 'http://', 'https://')

OLD_PROBE_CACHE = "probe_cache.json"
FACTS_CACHE = "facts_cache.json"


def _loggable(file_path):
    """
    :return: the path with any API key in it masked, for the log
    """
    return re.sub(r'(?i)(api_?key=)[^&]*', r'...', file_path)


def _setting_bool(setting, default):
    value = get_setting_as_bool(setting)
    return default if value is None else bool(value)


class Store:
    """
    Helper class to read in and store the addon settings, and to provide a centralised store
    """

    # Static class variables, referred to by Store.whatever
    # https://docs.python.org/3/faq/programming.html#how-do-i-create-static-class-data-and-static-class-methods
    kodi_event_monitor = None
    kodi_player = None

    # The automatic rules: engage software decoding for...
    rule_amlogic = False  # videos with a known Amlogic decoding failure (Amlogic only)
    rule_1080p = False  # all videos 1080p and below
    # All interlaced videos - not offered as a setting, as it's too unreliable (it can only see inside
    # files Kodi can read, so not Jellyfin and the like, and the flags aren't always right), but the
    # file reading in probe.py and the rule below are kept in case it's wanted again.
    rule_interlaced = False

    # Paths (and subfolders) the automatic rules are limited to - empty means everywhere
    paths = []

    # Whether the "Limp: software decode" context menu item is offered
    show_context_menu = True

    # Whether to quietly switch hardware decoding back on at start-up if it's found off
    hardware_at_startup = True

    # TV shows set (via the context menu) to always use software decoding
    series_list = None

    # Whether the focused item's show is on that list, as last published (None until the first time)
    _series_listed_published = None

    # Cache of file path -> facts read from the file's headers (see probe.py), so each file only
    # ever needs probing once. Persisted so it survives a service restart.
    facts_cache = {}
    facts_cache_file = None

    # Resolutions Kodi has told us about for files (library items), by path. Not persisted - Kodi
    # tells us again whenever the item is focused.
    resolutions = {}

    # The last decision made for each file, so it's only logged when it's new or changes
    decisions = {}

    # Files we failed to read this session - not retried until the service restarts
    unreadable = set()

    def __init__(self):
        """
        Load in the addon settings and do some basic initialisation stuff
        """
        Platform.detect()
        Store.load_config_from_settings()

        if not xbmcvfs.exists(PROFILE):
            xbmcvfs.mkdirs(PROFILE)
        old_cache = os.path.join(PROFILE, OLD_PROBE_CACHE)
        if xbmcvfs.exists(old_cache):
            xbmcvfs.delete(old_cache)
        Store.facts_cache_file = os.path.join(PROFILE, FACTS_CACHE)
        Store._load_facts_cache()
        Store.series_list = ShowList(SERIES_FILE)
        Logger.info(f'Series set to software decoding: {[title for _, title in Store.series_list.items()]}')

    @staticmethod
    def load_config_from_settings():
        """
        Load in the addon settings, at start or reload them if they have been changed
        :return:
        """
        Logger.info("Loading configuration")

        # The Amlogic rule is hidden (and ignored) anywhere else. On by default there, as it's
        # what Limp was originally for.
        Store.rule_amlogic = Platform.is_amlogic() and _setting_bool("RuleAmlogic", True)
        Store.rule_1080p = _setting_bool("Rule1080p", False)

        paths = []
        for i in range(1, NUMBER_OF_PATH_SETTINGS + 1):
            path = get_setting(f"Path{i}")
            if path:
                paths.append(path)
        Store.paths = paths

        Store.show_context_menu = _setting_bool("ShowContextMenu", True)
        Store.hardware_at_startup = _setting_bool("HardwareAtStartup", True)
        Store.publish_context_menu_visibility()
        if Platform.is_amlogic():
            set_property(HOME_WINDOW, AMLOGIC_PROPERTY, "true")
        else:
            clear_property(HOME_WINDOW, AMLOGIC_PROPERTY)

        Store.log_configuration()

    @staticmethod
    def load_series_list():
        """
        Reload the list of series from disk - it's changed by the context menu and settings scripts,
        which run as separate processes.
        """
        Store.series_list.load()
        Logger.info(f'Series set to software decoding: {[title for _, title in Store.series_list.items()]}')

    @staticmethod
    def is_series_listed(show_title):
        """
        Whether a TV show has been set to always use software decoding.

        :param show_title: the show's title, as Kodi reports it
        :return: True if the show is on the list
        """
        return bool(show_title) and Store.series_list is not None and Store.series_list.contains(title_key(show_title))

    @staticmethod
    def publish_series_listed(listed):
        """
        Mirror whether the focused item's TV show is on the series list into a Home window property,
        for the context menu's visibility conditions (see SERIES_LISTED_PROPERTY).

        :param listed: True if the focused item's show is on the list
        """
        if listed == Store._series_listed_published:
            return
        Store._series_listed_published = listed
        if listed:
            set_property(HOME_WINDOW, SERIES_LISTED_PROPERTY, "true")
        else:
            clear_property(HOME_WINDOW, SERIES_LISTED_PROPERTY)

    @staticmethod
    def publish_context_menu_visibility():
        """
        The context menu item's visibility condition (in addon.xml) can't read our settings, so
        mirror the "show context menu item" setting into a Home window property for it to check.
        Not offered at all on a platform we can't do anything on.
        """
        if Store.show_context_menu and Platform.hardware_setting:
            set_property(HOME_WINDOW, CONTEXT_MENU_PROPERTY, "true")
        else:
            clear_property(HOME_WINDOW, CONTEXT_MENU_PROPERTY)

    @staticmethod
    def log_configuration():
        """
        Log out our key configuration values
        :return:
        """
        Logger.info(f'Show context menu item: {Store.show_context_menu}, hardware decoding on at start-up: {Store.hardware_at_startup}')
        Logger.info(f'Automatic rules - known Amlogic failures: {Store.rule_amlogic}, '
                    f'1080p and below: {Store.rule_1080p}')
        if not Store.rules_enabled():
            Logger.info('No automatic rules are on - software decoding only for listed series and the context menu.')
        elif Store.paths:
            Logger.info(f'Automatic rules limited to: {Store.paths}')
        else:
            Logger.info('Automatic rules apply everywhere (no paths set).')

    @staticmethod
    def rules_enabled():
        """
        :return: True if any automatic rule is on
        """
        return Store.rule_amlogic or Store.rule_1080p or Store.rule_interlaced

    @staticmethod
    def is_within_limits(file_path):
        """
        Whether the automatic rules apply to the given file - anywhere, unless limited to the
        paths set in the add-on's settings.

        :param file_path: the full path of the file to check
        :return: True if the rules apply to this file
        """
        return not Store.paths or any(path in file_path for path in Store.paths)

    @staticmethod
    def needs_software_decode(file_path, resolution=None):
        """
        Whether playback of the given file should be forced to software decoding by the automatic
        rules: it's within the limits, and it meets the condition of at least one rule that's on.
        An explicit choice overrules any smarts - if a rule is on and the video meets it, software
        decoding it is. Anything we can't tell is left to hardware decoding.

        :param file_path: the full path of the file about to play/be focused
        :param resolution: Kodi's resolution label for it, if known ("720", "1080", "4K"...)
        :return: True if this file should use software decoding
        """
        # Kodi VFS paths for directories always end in a separator (e.g. focusing a folder in the
        # file browser reports it via the same ListItem.FileNameAndPath used for files) - a folder
        # can't be probed.
        if not Store.rules_enabled() or not file_path or file_path.endswith(('/', '\\')) \
                or file_path.startswith(IGNORED_PREFIXES) or not Store.is_within_limits(file_path):
            return False

        if resolution and Store.resolutions.get(file_path) != resolution:
            Store.resolutions[file_path] = resolution

        facts = Store._get_facts(file_path)

        result = bool(
                (Store.rule_amlogic and (facts.get('rotation') in BROKEN_ROTATIONS
                                         or str(facts.get('avi_codec') or '').upper() in BROKEN_AVI_CODECS))
                or (Store.rule_1080p and Store._is_1080p_or_below(file_path, facts))
                or (Store.rule_interlaced and facts.get('interlaced')))

        if Store.decisions.get(file_path) != result:
            Store.decisions[file_path] = result
            Logger.info(f'Automatic rules say software decoding {"YES" if result else "no"} for [{_loggable(file_path)}] '
                        f'(Kodi resolution: {Store.resolutions.get(file_path)}, file facts: {facts})')
        return result

    @staticmethod
    def is_stream(file_path):
        """
        Whether a path is a stream rather than a file we can look at - what a Jellyfin item turns into
        once playback starts, or live TV. Its details only show up a moment into playback, and what
        Kodi reports at first can be left over from the previous video, so only what was decided
        beforehand (when the item was focused) can be trusted.

        :return: True if the path is a stream
        """
        return bool(file_path) and file_path.startswith(UNPROBEABLE_PREFIXES + IGNORED_PREFIXES)

    @staticmethod
    def _is_1080p_or_below(file_path, facts):
        resolution = Store.resolutions.get(file_path)
        if resolution:
            return resolution in LOW_RESOLUTIONS
        width, height = facts.get('width'), facts.get('height')
        return bool(width and height and width <= LOW_RESOLUTION_MAX_WIDTH and height <= LOW_RESOLUTION_MAX_HEIGHT)

    @staticmethod
    def _get_facts(file_path):
        """
        The facts about a file from its headers, probing it the first time. Successfully-read
        results are cached per file path; a failed read is only remembered for this session, so
        it's neither retried every second nor stuck for good (e.g. after a bug fix here). Not
        probed at all if Kodi already told us the resolution and that's all the rules need.

        :return: a dict of facts - empty if there aren't any
        """
        if file_path in Store.facts_cache:
            return Store.facts_cache[file_path]
        if file_path in Store.unreadable or file_path.startswith(UNPROBEABLE_PREFIXES):
            return {}
        if Store.rule_1080p and not (Store.rule_amlogic or Store.rule_interlaced) and Store.resolutions.get(file_path):
            return {}

        facts = probe_file(file_path)
        if facts is None:
            Store.unreadable.add(file_path)
            return {}
        Store.facts_cache[file_path] = facts
        Store._save_facts_cache()
        return facts

    @staticmethod
    def _load_facts_cache():
        if not Store.facts_cache_file or not xbmcvfs.exists(Store.facts_cache_file):
            Store.facts_cache = {}
            return
        try:
            with xbmcvfs.File(Store.facts_cache_file) as f:
                Store.facts_cache = json.loads(f.read())
            Logger.info(f'Loaded {len(Store.facts_cache)} cached file probe result(s)')
        except (OSError, ValueError) as e:
            Logger.warning(f'Could not load probe cache, starting fresh: {e}')
            Store.facts_cache = {}

    @staticmethod
    def _save_facts_cache():
        with xbmcvfs.File(Store.facts_cache_file, 'w') as f:
            if not f.write(json.dumps(Store.facts_cache)):
                Logger.warning('Could not save probe cache')
