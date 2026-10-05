import time

import xbmc

from bossanova808.logger import Logger
from bossanova808.utilities import get_kodi_setting, send_kodi_json
# noinspection PyPackages
from .store import Store

# The Kodi setting that selects hardware vs software video decoding.
# Confirmed working on Amlogic (CoreELEC/Ugoos AM6B+): toggles amcodec hardware decode off/on.
# TODO: other platforms have their own equivalent setting (e.g. videoplayer.usemediacodec on
# Android, videoplayer.usevaapi on Linux/VAAPI, videoplayer.usedxva2 on Windows) - add support for
# those here if/when needed.
HARDWARE_DECODE_SETTING = "videoplayer.useamcodec"

# How long a manual (context menu) override waits for its playback to start before lapsing
MANUAL_REQUEST_TIMEOUT_SECONDS = 30


def _set_kodi_setting(setting, value):
    """
    Set a Kodi setting via JSON-RPC.

    :param setting: the Kodi setting id to set
    :param value: the value to set it to
    """
    json_dict = {
            "jsonrpc": "2.0",
            "id": "setKodiSetting",
            "method": "Settings.SetSettingValue",
            "params": {"setting": setting, "value": value},
    }
    send_kodi_json(f'Set Kodi setting {setting} to {value}', json_dict)


def _current_file_of_interest():
    """
    The file that should currently be evaluated: the file actually playing if a video is playing,
    otherwise whatever the user has focused in a file/library list - so the override gets applied
    proactively, before Play is even pressed.

    :return: a file path, or None if there isn't one
    """
    player = xbmc.Player()
    if player.isPlayingVideo():
        try:
            return player.getPlayingFile()
        except Exception:
            return None
    return xbmc.getInfoLabel('ListItem.FileNameAndPath') or None


class DecoderOverride:
    """
    Tracks and applies whether software decoding is currently being forced for a managed file with
    a known amcodec problem (a rotation matrix, or an AVI codec it can't decode at all).

    Kodi selects the video decoder synchronously while opening a file - confirmed via Kodi log
    analysis (CDVDVideoCodecAmlogic opens the hardware decoder as part of VideoPlayer::OpenFile,
    tens of milliseconds before any Python addon's onPlayBackStarted callback even begins running).
    So reacting to playback starting is too late to reliably change it - it only won the race in
    testing when a given file's demux/probe happened to be slow.

    Instead, recheck() is driven proactively from the service's main loop, polling whatever the
    user currently has focused (in a file list, or actually playing) against Store's
    needs_software_decode() check - by the time the user actually presses play, the setting has
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

    @classmethod
    def recheck(cls, reason):
        """
        Work out whether software decode should currently be forced for whatever file is currently
        playing/focused, and apply/undo the override if that differs from the current state. Safe
        to call as often as needed - a no-op when nothing has changed.

        :param reason: a short human-readable reason, used in the log message on a state change
        """
        cls.recheck_for_file(_current_file_of_interest(), reason)

    @classmethod
    def recheck_for_file(cls, file_path, reason):
        """
        As recheck(), but against a specific file rather than auto-detecting the current one.

        :param file_path: the file to evaluate
        :param reason: a short human-readable reason, used in the log message on a state change
        """
        should_force = cls._manual_active() or Store.needs_software_decode(file_path)

        if should_force and not cls._forcing:
            cls._force(reason)
        elif not should_force and cls._forcing:
            cls._restore(reason)

    @classmethod
    def request_manual_force(cls):
        """
        Arm a one-off override: force software decode for the next playback, regardless of file or
        path. Applies immediately, so it's in place before the caller starts that playback.

        :return: True if software decode is now being forced
        """
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
        original_value = get_kodi_setting(HARDWARE_DECODE_SETTING)
        if original_value is None:
            Logger.warning(f"Could not read current value of {HARDWARE_DECODE_SETTING} - not forcing software decode.")
            return
        Logger.info(f'{reason} - forcing software decode.')
        cls._original_value = original_value
        cls._forcing = True
        _set_kodi_setting(HARDWARE_DECODE_SETTING, False)

    @classmethod
    def _restore(cls, reason):
        Logger.info(f'{reason} - restoring {HARDWARE_DECODE_SETTING} to {cls._original_value}.')
        _set_kodi_setting(HARDWARE_DECODE_SETTING, cls._original_value)
        cls._forcing = False
        cls._original_value = None

    @classmethod
    def restore_if_forced(cls, reason):
        """
        Best-effort restore, e.g. on service shutdown.

        :param reason: a short human-readable reason, used in the log message
        """
        if cls._forcing:
            cls._restore(reason)
