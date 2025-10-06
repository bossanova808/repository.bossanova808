import json

from bossanova808.logger import Logger
from bossanova808.utilities import send_kodi_json, get_resume_point
# noinspection PyPackages
from .store import Store

import xbmc


class KodiPlayer(xbmc.Player):
    """
    This class represents/monitors the Kodi video player
    """

    def __init__(self):
        xbmc.Player.__init__(self)
        Logger.debug('KodiPlayer __init__')

    def onAVStarted(self) -> None:
        """
        This method is called when the Kodi video player is started and AV is beginning to appear
        Chosen over onPlayBackStarted() as sometimes information is not yet available at that point.

        :return: None
        """
        Logger.info('onAVStarted')

        # Get active players
        command = json.dumps({
                "jsonrpc":"2.0",
                "id":1,
                "method":"Player.GetActivePlayers",
        })
        json_object = send_kodi_json("Get active players", command)

        active_players = json_object.get('result') or []
        video_players = [p for p in active_players if p.get('type') == 'video']
        if video_players:
            playerid = video_players[0].get('playerid')
            Logger.debug(f"Video player running with ID: {playerid}")
        else:
            Logger.debug("Player is not a video player")
            return

        command = json.dumps({
                "jsonrpc":"2.0",
                "id":1,
                "method":"Player.GetItem",
                "params":{"playerid":playerid},
        })
        json_object = send_kodi_json("Get playing item", command)

        item = json_object.get('result', {}).get('item', {})
        # Only do something if this is an episode of a TV show
        library_type = item.get('type')
        if library_type in ['episode', 'movie']:
            # @coderabbitai I have confirmed in both cases 'id' is returned so no need for a more specialised parameter
            dbid = item.get('id') or None
            if dbid:
                Logger.debug(f"Playing: {library_type} with dbid: {dbid}")

            resume_point = get_resume_point(library_type, dbid)
            Logger.info(f"Resume point retrieved: {resume_point}")

            # Resume just slightly back from where we were as per the user setting (default 7 seconds)
            if resume_point and resume_point > 20:
                self.seekTime(max(resume_point - Store.jumpback, 0))
            # Close to the beginning or no resume point - seek back to (0) to attempt to force trigger subtitles earlier
            # The 1-second delay introduces some jank but seems effective
            else:
                if Store.jumpback_at_start:
                    # Schedule seek to 0.0 after delay using a timer or background thread
                    import threading

                    def delayed_seek():
                        xbmc.sleep(Store.jumpback_at_start_after_seconds * 1000)
                        if self.isPlaying():
                            self.seekTime(1.0)

                    threading.Thread(target=delayed_seek, daemon=True).start()
