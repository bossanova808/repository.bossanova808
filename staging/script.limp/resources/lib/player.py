import xbmc

from bossanova808.logger import Logger
from bossanova808.utilities import send_kodi_json
# noinspection PyPackages
from .decoder_override import DecoderOverride


class KodiPlayer(xbmc.Player):
    """
    Rechecks the decoder override on playback start/stop, on top of the periodic focused/playing
    file check driven from the service's main loop (see decoder_override.py for why that's the
    primary mechanism, and this is just a backstop) - plus a playlist look-ahead, so a multi-clip
    "play from here"/"play all" queue gets the next clip's decode mode set correctly before Kodi
    opens it, rather than only reacting after it's already started.
    """

    def __init__(self):
        super().__init__()
        Logger.debug('KodiPlayer __init__')
        self._playlist_position = -1

    def onPlayBackStarted(self):
        # Capture where we are in the video playlist now, while it's unambiguous - Kodi's position
        # pointer may have already moved on by the time onPlayBackEnded/Stopped fire.
        try:
            self._playlist_position = xbmc.PlayList(xbmc.PLAYLIST_VIDEO).getposition()
        except Exception:
            self._playlist_position = -1
        DecoderOverride.recheck('Playback started')

    def onPlayBackEnded(self):
        self._recheck_for_end('Playback ended')

    def onPlayBackStopped(self):
        self._recheck_for_end('Playback stopped')

    def onPlayBackError(self):
        self._recheck_for_end('Playback error')

    def _recheck_for_end(self, reason):
        """
        If there's a next item already queued in the video playlist, evaluate the override against
        that specific file now, before Kodi opens it. Otherwise fall back to the generic
        focused/playing check, which correctly handles restoring when nothing else is queued.

        :param reason: a short human-readable reason, used in the log message on a state change
        """
        next_file = self._get_next_queued_file()
        if next_file:
            DecoderOverride.recheck_for_file(next_file, f'{reason} (next queued item)')
        else:
            DecoderOverride.recheck(reason)

    def _get_next_queued_file(self):
        """
        The file path of the next item in the video playlist after the one that was just playing,
        if there is one.

        :return: a file path, or None if we're not in a playlist, or this was the last item
        """
        if self._playlist_position < 0:
            return None

        next_position = self._playlist_position + 1
        try:
            if next_position >= xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size():
                return None
        except Exception:
            return None

        response = send_kodi_json("Get video playlist items", {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "Playlist.GetItems",
                "params": {"playlistid": xbmc.PLAYLIST_VIDEO, "properties": ["file"]},
        })
        items = (response or {}).get('result', {}).get('items') or []
        if next_position >= len(items):
            return None
        return items[next_position].get('file')
