import json
import os

from bossanova808.constants import PROFILE
from bossanova808.logger import Logger
from bossanova808.utilities import get_setting, get_setting_as_bool
# noinspection PyPackages
from .rotation import probe_needs_software_decode

# Number of path slots offered in the add-on's settings
NUMBER_OF_PATH_SETTINGS = 5


class Store:
    """
    Helper class to read in and store the addon settings, and to provide a centralised store
    """

    # Static class variables, referred to by Store.whatever
    # https://docs.python.org/3/faq/programming.html#how-do-i-create-static-class-data-and-static-class-methods
    kodi_event_monitor = None
    kodi_player = None

    # Paths (and subfolders) under which files are candidates for forced software decoding
    paths = []

    # If true, every video everywhere is a candidate, regardless of paths above
    apply_everywhere = False

    # Cache of file path -> whether it needs software decoding forced (True/False), so each file
    # only ever needs probing (reading its rotation matrix or AVI codec) once. Persisted so it
    # survives a service restart.
    probe_cache = {}
    probe_cache_file = None

    def __init__(self):
        """
        Load in the addon settings and do some basic initialisation stuff
        """
        Store.load_config_from_settings()

        if not os.path.exists(PROFILE):
            os.makedirs(PROFILE)
        Store.probe_cache_file = os.path.join(PROFILE, "probe_cache.json")
        Store._load_probe_cache()

    @staticmethod
    def load_config_from_settings():
        """
        Load in the addon settings, at start or reload them if they have been changed
        :return:
        """
        Logger.info("Loading configuration")

        Store.apply_everywhere = bool(get_setting_as_bool("ApplyEverywhere"))

        paths = []
        for i in range(1, NUMBER_OF_PATH_SETTINGS + 1):
            path = get_setting(f"Path{i}")
            if path:
                paths.append(path)
        Store.paths = paths

        Store.log_configuration()

    @staticmethod
    def log_configuration():
        """
        Log out our key configuration values
        :return:
        """
        if Store.apply_everywhere:
            Logger.info('Forcing software decoding for problem files everywhere (not limited by path).')
        elif Store.paths:
            Logger.info(f'Forcing software decoding for problem files under: {Store.paths}')
        else:
            Logger.info('No paths configured - add one or more in the add-on settings for this to do anything.')

    @staticmethod
    def is_managed_path(file_path):
        """
        Whether the given file is a candidate for the software decode override - either because
        "apply everywhere" is enabled, or because it lives under one of the paths configured in
        the add-on's settings.

        :param file_path: the full path of the file to check
        :return: True if this file is in scope
        """
        if not file_path:
            return False
        if Store.apply_everywhere:
            return True
        return any(path in file_path for path in Store.paths)

    @staticmethod
    def needs_software_decode(file_path):
        """
        Whether playback of the given file should be forced to software decoding - i.e. whether it
        is in scope (under a configured path, or "apply everywhere" is on) AND actually has a
        specific, known problem amcodec has with it: a 90/270 degree rotation matrix (MP4/MOV) it
        mishandles, or a video codec (e.g. MJPEG in old camera .avi files) it can't decode at all -
        see rotation.py. This deliberately excludes in-scope files that don't need it (e.g. modern
        4K clips from a mirrorless camera, which are rarely rotated but are too CPU-heavy to
        software decode, and forcing it was also observed to leave CoreELEC's HDR/HDMI mode-switch
        in a bad state on playback end).

        Successfully-determined results are cached per file path so each file is only ever probed
        once; a failed/undetermined lookup is deliberately not cached, so it's retried next time
        rather than being stuck reporting "doesn't need it" forever (e.g. after a bug fix here).

        :param file_path: the full path of the file about to play/be focused
        :return: True if this file needs software decoding forced
        """
        # Kodi VFS paths for directories always end in a separator (e.g. focusing a folder in the
        # file browser reports it via the same ListItem.FileNameAndPath used for files) - a folder
        # can't be probed, and this can otherwise be re-checked every poll tick while someone is
        # just sitting on a folder, since a failed lookup deliberately isn't cached.
        if not file_path or file_path.endswith('/') or file_path.endswith('\\') or not Store.is_managed_path(file_path):
            return False

        if file_path in Store.probe_cache:
            return Store.probe_cache[file_path]

        result = probe_needs_software_decode(file_path)
        if result is not None:
            Store.probe_cache[file_path] = result
            Store._save_probe_cache()

        return bool(result)

    @staticmethod
    def _load_probe_cache():
        if not Store.probe_cache_file or not os.path.exists(Store.probe_cache_file):
            Store.probe_cache = {}
            return
        try:
            with open(Store.probe_cache_file, 'r', encoding='utf-8') as f:
                # Drop any previously-persisted undetermined (null) entries so they get retried,
                # rather than being permanently stuck - see needs_software_decode() above.
                Store.probe_cache = {path: result for path, result in json.load(f).items() if result is not None}
            Logger.info(f'Loaded {len(Store.probe_cache)} cached file probe result(s)')
        except (OSError, ValueError) as e:
            Logger.warning(f'Could not load probe cache, starting fresh: {e}')
            Store.probe_cache = {}

    @staticmethod
    def _save_probe_cache():
        try:
            with open(Store.probe_cache_file, 'w', encoding='utf-8') as f:
                json.dump(Store.probe_cache, f)
        except OSError as e:
            Logger.warning(f'Could not save probe cache: {e}')
