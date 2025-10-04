import json

from bossanova808.logger import Logger
from bossanova808.utilities import send_kodi_json
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
            # @coderabbitai I have confirmed in both cases 'id' is returned so no need for a more specialised paramter
            dbid = item.get('id') or None

            if dbid:
                Logger.debug(f"Playing: {library_type} with dbid: {dbid}")

            if library_type == 'episode':
                get_method = 'VideoLibrary.GetEpisodeDetails'
                id_name = 'episodeid'
                result_key = 'episodedetails'
            elif library_type == 'movie':
                get_method = 'VideoLibrary.GetMovieDetails'
                id_name = 'movieid'
                result_key = 'moviedetails'
            else:
                Logger.error(f"Unsupported library type: {library_type}")
                return

            json_dict = {
                    "jsonrpc":"2.0",
                    "id":"getResumePoint",
                    "method":get_method,
                    "params":{
                            id_name:dbid,
                            "properties":["resume"],
                    }
            }

            query = json.dumps(json_dict)
            json_response = send_kodi_json(f'Get resume point for type {library_type} with dbid: {dbid}', query)
            result = json_response.get('result')
            if result:
                try:
                    resume_point = result[result_key]['resume']['position']
                except (KeyError, TypeError) as e:
                    Logger.error(f"Could not get resume point: {e}")
                    resume_point = None
            else:
                Logger.error("No result returned from JSON-RPC query")
                resume_point = None

            Logger.info(f"Resume point retrieved: {resume_point}")

            # Resume just slightly back from where we were...
            if resume_point and resume_point > 20:
                self.seekTime(resume_point - 7.0)
            # Close to the beginning or no resume point - seek back to (0) to attempt to force trigger subtitles earlier
            else:
                self.seekTime(0.0)
