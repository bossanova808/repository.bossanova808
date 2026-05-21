import json

from bossanova808.constants import ADDON_ID
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
            "jsonrpc": "2.0",
            "id": f"{ADDON_ID}:Player.GetActivePlayers",
            "method": "Player.GetActivePlayers",
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
            "jsonrpc": "2.0",
            "id": f"{ADDON_ID}:Player.GetItem",
            "method": "Player.GetItem",
            "params": {
                "playerid": playerid,
                "properties": ["type", "uniqueid"]
            }
        })
        json_object = send_kodi_json("Get active item description", command)

        result = json_object.get('result') or {}
        item = result.get('item') or {}
        library_type = item.get('type') or 'unknown'

        if library_type not in ['episode', 'movie']:
            Logger.debug(f"Media type {library_type} is not an episode or movie, doing nothing.")
            return

        dbid = item.get('id') or None
        if not dbid:
            Logger.debug(f"No DB ID found for {library_type}, doing nothing.")
            return

        Logger.debug(f"Playing: {library_type} with dbid: {dbid}")

        resume_point = get_resume_point(library_type, dbid)
        Logger.info(f"Resume point retrieved: {resume_point}")

        if resume_point and resume_point > 20:
            playing_time = round(self.getTime(), 1)
            time_difference = round(abs(playing_time - resume_point), 1)
            Logger.debug(f"Currently playing time: {playing_time}, Kodi resume: {resume_point}, difference: {time_difference}")
            if time_difference < Store.jumpback_delta:
                Logger.warning(f"Decision: Do nothing. Difference {time_difference} < Delta {Store.jumpback_delta}.")
                return

            seek_to = max(resume_point - Store.jumpback, 0)
            Logger.error(f"Decision: Fix. Difference {time_difference} > Delta {Store.jumpback_delta}, fix by seek to (resume point {resume_point} - offset {Store.jumpback}): {seek_to}")
            self.seekTime(seek_to)
