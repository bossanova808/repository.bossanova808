import json
import os
import threading
import time

import xbmc
import xbmcgui
import xbmcvfs

from bossanova808.constants import PROFILE, TRANSLATE
from bossanova808.logger import Logger
from bossanova808.notify import Notify
from bossanova808.utilities import get_kodi_setting, send_kodi_json
# noinspection PyPackages
from .platforms import Platform
# noinspection PyPackages
from .store import Store

# How long a manual (context menu) override waits for its playback to start before lapsing
MANUAL_REQUEST_TIMEOUT_SECONDS = 30

# How long software decoding is held on after it was last wanted, while nothing is playing or
# focused - so the next item, auto-played straight after (the next episode, the next clip of a
# "play from here" queue), doesn't open on hardware
GRACE_SECONDS = 8

# Remembers the setting's original value on disk while we're forcing it - see recover_stale_state()
STATE_FILE = "forced_state.json"

# How long to wait before trying again if restoring the setting failed
RESTORE_RETRY_SECONDS = 10

# How often (while nothing is playing) to check the setting is as it should be
PERIODIC_CHECK_SECONDS = 60


def _set_kodi_setting(setting, value):
    """
    Set a Kodi setting via JSON-RPC.

    :param setting: the Kodi setting id to set
    :param value: the value to set it to
    :return: True if Kodi accepted the change
    """
    json_dict = {
            "jsonrpc": "2.0",
            "id": "setKodiSetting",
            "method": "Settings.SetSettingValue",
            "params": {"setting": setting, "value": value},
    }
    response = send_kodi_json(f'Set Kodi setting {setting} to {value}', json_dict)
    return bool(response) and response.get('result') is True


def _state_path():
    return os.path.join(PROFILE, STATE_FILE)


def _save_state(original_value):
    """
    Remember the setting's original value on disk, for as long as we're forcing it.
    """
    if not xbmcvfs.exists(PROFILE):
        xbmcvfs.mkdirs(PROFILE)
    with xbmcvfs.File(_state_path(), 'w') as f:
        if not f.write(json.dumps({Platform.hardware_setting: original_value})):
            Logger.warning('Could not save the forced state')


def _clear_state():
    if xbmcvfs.exists(_state_path()) and not xbmcvfs.delete(_state_path()):
        Logger.warning('Could not remove the forced state file')


def _load_state():
    """
    :return: the original value of the setting if we were left forcing it, otherwise None
    """
    if not xbmcvfs.exists(_state_path()):
        return None
    try:
        with xbmcvfs.File(_state_path()) as f:
            value = json.loads(f.read()).get(Platform.hardware_setting)
    except (OSError, ValueError, AttributeError):
        return None
    return value if isinstance(value, bool) else None


def _profile_name():
    """
    :return: the name of the Kodi profile we're running in (each profile has its own settings)
    """
    return xbmc.getInfoLabel('System.ProfileName') or 'unknown'


def _current_item():
    """
    The item that should currently be evaluated: the one actually playing if a video is playing,
    otherwise whatever the user has focused in a file/library list - so the override gets applied
    proactively, before Play is even pressed.

    :return: (file path, TV show title, resolution label, whether it's a stream that's already
        playing) - the first three may be None
    """
    player = xbmc.Player()
    if player.isPlayingVideo():
        try:
            file_path = player.getPlayingFile()
        except Exception:
            file_path = None
        return file_path, xbmc.getInfoLabel('VideoPlayer.TVShowTitle') or None, None, Store.is_stream(file_path)
    return (xbmc.getInfoLabel('ListItem.FileNameAndPath') or None, xbmc.getInfoLabel('ListItem.TVShowTitle') or None,
            xbmc.getInfoLabel('ListItem.VideoResolution') or None, False)


class DecoderOverride:
    """
    Tracks and applies whether software decoding is currently being forced: for a video one of the
    automatic rules picks out, a listed TV series, or a one-off request from the context menu.

    Kodi selects the video decoder synchronously while opening a file - confirmed via Kodi log
    analysis (CDVDVideoCodecAmlogic opens the hardware decoder as part of VideoPlayer::OpenFile,
    tens of milliseconds before any Python addon's onPlayBackStarted callback even begins running).
    So reacting to playback starting is too late to reliably change it - it only won the race in
    testing when a given file's demux/probe happened to be slow.

    Instead, recheck() is driven proactively from the service's main loop, polling whatever the
    user currently has focused (in a file list, or actually playing) against Store's
    needs_software_decode() rules - by the time the user actually presses play, the setting has
    normally already been changed well in advance.

    Player callbacks also call recheck() as a harmless backstop - it can occasionally still win the
    race (e.g. a slow first probe), and it makes restoration prompt on playback ending rather than
    waiting for the next poll tick. recheck_for_file() lets a caller (see player.py's playlist
    look-ahead) evaluate a specific file directly, rather than auto-detecting the current one - so
    a multi-clip "play from here"/"play all" queue can get the next clip's decode mode set
    correctly before Kodi opens it, not just after.

    The context menu's "software decode" action arms a one-off manual override instead (see
    request_manual_force()): it forces software decode for the very next playback, whatever the
    file and wherever it lives, and is dropped again once that playback finishes.
    """

    _forcing = False
    _original_value = None

    # One-off manual override, armed by the context menu action
    _manual = False
    _manual_started = False
    _manual_armed_at = 0.0

    # When forcing was last wanted - see GRACE_SECONDS
    _last_wanted_at = 0.0

    # Housekeeping for the restore retries and the periodic check
    _last_restore_attempt = 0.0
    _last_periodic_check = 0.0
    _last_seen_value = None

    # Asking the user to turn hardware decoding back on, if it's found off when we aren't the cause
    _restore_prompt_thread = None
    _restore_prompt_declined = False

    @classmethod
    def recheck(cls, reason):
        """
        Work out whether software decode should currently be forced for whatever file is currently
        playing/focused, and apply/undo the override if that differs from the current state. Safe
        to call as often as needed - a no-op when nothing has changed.

        :param reason: a short human-readable reason, used in the log message on a state change
        """
        file_path, show_title, resolution, streaming = _current_item()
        Store.publish_series_listed(Store.is_series_listed(xbmc.getInfoLabel('ListItem.TVShowTitle')))
        cls.recheck_for_file(file_path, reason, show_title, resolution, streaming)

    @classmethod
    def recheck_for_file(cls, file_path, reason, show_title=None, resolution=None, streaming=False):
        """
        As recheck(), but against a specific item rather than auto-detecting the current one.

        :param file_path: the file to evaluate
        :param reason: a short human-readable reason, used in the log message on a state change
        :param show_title: the item's TV show title, if it's an episode
        :param resolution: Kodi's resolution label for the item, if known
        :param streaming: whether the item is a stream that's already playing
        """
        if not Platform.hardware_setting:
            return
        should_force = cls._manual_active() or Store.is_series_listed(show_title)

        # Once a stream is playing, the decoder is already chosen, and what Kodi says about it is
        # unreliable at first - so leave what was decided beforehand (while the item was focused) alone
        if streaming:
            if should_force and not cls._forcing:
                cls._force(reason)
            if cls._forcing:
                cls._last_wanted_at = time.monotonic()
            return

        should_force = should_force or Store.needs_software_decode(file_path, resolution)
        if should_force:
            cls._last_wanted_at = time.monotonic()

        if should_force and not cls._forcing:
            cls._force(reason)
        elif not should_force and cls._forcing:
            # With nothing playing or focused (e.g. between auto-played episodes) hold on briefly
            if not file_path and not show_title and time.monotonic() - cls._last_wanted_at < GRACE_SECONDS:
                return
            # If a restore has just failed, give it a while before trying again
            if time.monotonic() - cls._last_restore_attempt < RESTORE_RETRY_SECONDS:
                return
            cls._restore(reason)

    @classmethod
    def request_manual_force(cls):
        """
        Arm a one-off override: force software decode for the next playback, regardless of file or
        path. Applies immediately, so it's in place before the caller starts that playback.

        :return: True if software decode is now being forced
        """
        if not Platform.hardware_setting:
            return False
        cls._manual = True
        cls._manual_started = False
        cls._manual_armed_at = time.monotonic()
        cls.recheck('Manual request')
        return cls._forcing

    @classmethod
    def note_playback_started(cls):
        """
        Playback has started - if a manual override is armed, this is the playback it was for.
        """
        if cls._manual:
            cls._manual_started = True

    @classmethod
    def note_playback_finished(cls):
        """
        Playback has ended, stopped or failed - drops a manual override once its playback is done.
        (A stop that arrives before the armed playback has started belongs to whatever was playing
        before it, so is ignored.)
        """
        if cls._manual and cls._manual_started:
            cls._manual = False
            cls._manual_started = False

    @classmethod
    def _manual_active(cls):
        """
        Whether a manual override is currently in force. One that never gets as far as a playback
        starting (e.g. the file failed to open) lapses after a while, rather than sticking forever.
        """
        if cls._manual and not cls._manual_started and time.monotonic() - cls._manual_armed_at > MANUAL_REQUEST_TIMEOUT_SECONDS:
            Logger.info('Manual software decode request lapsed - no playback started.')
            cls._manual = False
        return cls._manual

    @classmethod
    def _force(cls, reason):
        original_value = get_kodi_setting(Platform.hardware_setting)
        if original_value is None:
            Logger.warning(f"Could not read current value of {Platform.hardware_setting} - not forcing software decode.")
            return
        Logger.info(f'{reason} - forcing software decode.')
        # Remembered on disk before the change, so the original value isn't lost if Kodi is stopped
        # or killed while we're forcing (a crash, a profile switch...) - see recover_stale_state()
        _save_state(original_value)
        if not _set_kodi_setting(Platform.hardware_setting, False):
            Logger.warning('Could not force software decode.')
            _clear_state()
            return
        cls._original_value = original_value
        cls._forcing = True
        cls._last_restore_attempt = 0.0
        cls._last_seen_value = False

    @classmethod
    def _restore(cls, reason):
        """
        Put the setting back to its original value, and check that it took.

        :return: True if it's restored
        """
        cls._last_restore_attempt = time.monotonic()
        Logger.info(f'{reason} - restoring {Platform.hardware_setting} to {cls._original_value}.')
        if not _set_kodi_setting(Platform.hardware_setting, cls._original_value) \
                or get_kodi_setting(Platform.hardware_setting) != cls._original_value:
            Logger.error(f'Could not restore {Platform.hardware_setting} to {cls._original_value} - will try again.')
            return False
        cls._forcing = False
        cls._last_seen_value = cls._original_value
        cls._original_value = None
        _clear_state()
        return True

    @classmethod
    def restore_if_forced(cls, reason):
        """
        Best-effort restore, e.g. on service shutdown. If it doesn't work, the remembered state is
        left on disk, and recover_stale_state() puts it right the next time we start.

        :param reason: a short human-readable reason, used in the log message
        """
        if cls._forcing and not cls._restore(reason):
            Logger.error('Left software decoding forced - it will be restored the next time Limp starts.')

    @classmethod
    def shutdown(cls):
        """
        Called as the service stops (Kodi quitting, or the profile being switched): restore the
        setting if we're forcing it, and log what it ends up as - so if it's ever found different
        at the next start-up, the log shows whether it changed while Limp wasn't running.
        """
        if not Platform.hardware_setting:
            return
        was_forcing = cls._forcing
        cls.restore_if_forced('Service shutting down')
        Logger.info(f'Shutting down (profile: {_profile_name()}): {Platform.hardware_setting} is '
                    f'{get_kodi_setting(Platform.hardware_setting)}, Limp {"was" if was_forcing else "was not"} forcing it.')

    @classmethod
    def recover_stale_state(cls):
        """
        Called as the service starts. If we were stopped while forcing software decoding (Kodi
        crashed or was killed, or the profile was switched before the setting could be restored),
        the original value is still on disk - carry on as if we were still forcing, so the normal
        checks put the setting back as soon as it's not wanted.
        """
        if not Platform.hardware_setting:
            return
        current = get_kodi_setting(Platform.hardware_setting)
        cls._last_seen_value = current
        original = _load_state()
        if original is None:
            Logger.info(f'{Platform.hardware_setting} is {current} at start-up (profile: {_profile_name()}).')
            # Hardware decoding is the default, and Limp only switches it off while it's needed - so
            # finding it off at start-up isn't Limp's doing, and is quietly put right if allowed
            if current is False and Store.hardware_at_startup and cls._turn_hardware_on():
                Logger.warning(f'{Platform.hardware_setting} was off at start-up and Limp was not holding it off '
                               f'(profile: {_profile_name()}) - switched it back on.')
                return
            cls._check_hardware_decoding_on(current)
            return
        Logger.warning(f'Software decoding was still forced from a previous run (Kodi stopped, crashed or changed '
                       f'profile before it was restored): {Platform.hardware_setting} is {current}, and will be '
                       f'restored to {original}.')
        cls._forcing = True
        cls._original_value = original

    @classmethod
    def periodic_check(cls):
        """
        Every so often, while nothing is playing, check the setting is as it should be: still
        forced if we're forcing it, and otherwise log it if it has changed without us (which also
        leaves a trail in the log if hardware decoding is ever found switched off).
        """
        now = time.monotonic()
        if now - cls._last_periodic_check < PERIODIC_CHECK_SECONDS:
            return
        cls._last_periodic_check = now
        if not Platform.hardware_setting or xbmc.Player().isPlayingVideo():
            return

        value = get_kodi_setting(Platform.hardware_setting)
        if value is None:
            return
        if cls._forcing:
            if value is not False:
                Logger.warning(f'{Platform.hardware_setting} is {value} while forcing software decode - setting it to False again.')
                _set_kodi_setting(Platform.hardware_setting, False)
        else:
            if cls._last_seen_value is not None and value != cls._last_seen_value:
                Logger.warning(f'{Platform.hardware_setting} changed without Limp: {cls._last_seen_value} -> {value} '
                               f'(profile: {_profile_name()})')
            cls._check_hardware_decoding_on(value)
        cls._last_seen_value = value

    @classmethod
    def _check_hardware_decoding_on(cls, value):
        """
        Hardware decoding is meant to be on except while Limp is overriding it. If it's found off when
        we aren't forcing it, ask the user whether to turn it back on (once, until it's seen on again
        or Limp restarts), rather than carrying on and treating "off" as the value to restore.

        :param value: the setting's current value
        """
        if value is True:
            cls._restore_prompt_declined = False
            return
        if value is not False or cls._forcing or cls._restore_prompt_declined:
            return
        if cls._restore_prompt_thread is not None and cls._restore_prompt_thread.is_alive():
            return
        Logger.warning(f'{Platform.hardware_setting} is off and Limp is not forcing it (profile: {_profile_name()}) - asking the user.')
        # In its own thread, so a dialog nobody answers doesn't hold up the service loop
        cls._restore_prompt_thread = threading.Thread(target=cls._ask_to_turn_hardware_decoding_on, daemon=True)
        cls._restore_prompt_thread.start()

    @classmethod
    def _ask_to_turn_hardware_decoding_on(cls):
        if not xbmcgui.Dialog().yesno(TRANSLATE(32050), TRANSLATE(32051)):
            Logger.info('User chose to leave hardware decoding off.')
            cls._restore_prompt_declined = True
            return
        # Limp may have started forcing while the question was up, in which case it's off for a reason
        if cls._forcing:
            return
        if cls._turn_hardware_on():
            Logger.info(f'User chose to turn {Platform.hardware_setting} back on.')
            Notify.info(TRANSLATE(32052))
        else:
            Notify.error(TRANSLATE(32053))

    @classmethod
    def _turn_hardware_on(cls):
        """
        Set the hardware decoding setting to on, and check that it took.

        :return: True if it's on
        """
        if _set_kodi_setting(Platform.hardware_setting, True) and get_kodi_setting(Platform.hardware_setting) is True:
            cls._last_seen_value = True
            return True
        Logger.error(f'Could not turn {Platform.hardware_setting} back on.')
        return False
