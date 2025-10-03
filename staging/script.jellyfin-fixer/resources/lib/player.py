import json

from bossanova808.logger import Logger
from bossanova808.utilities import send_kodi_json
import xbmc


class KodiPlayer(xbmc.Player):
    """
    This class represents/monitors the Kodi video player
    """

    def __init__(self, *_args):
        """
        Initialize a KodiPlayer instance.
        
        Calls the xbmc.Player initializer and logs a debug message indicating construction.
        """
        xbmc.Player.__init__(self)
        Logger.debug('KodiPlayer __init__')

    # def onPlayBackStarted(self) -> None:
    #     Logger.info('onPlayBackStarted')

    def onAVStarted(self) -> None:
        """
        Adjusts playback position when audio/video starts based on Kodi resume data.
        
        Queries Kodi for an active video player and the currently playing item; if the item is a movie or episode, retrieves its resume position and seeks the player. If a resume position greater than 20 seconds is available, seeks to four seconds before that position; otherwise seeks to the start (0.0). This function performs JSON-RPC requests to Kodi and changes the player's playback position as a side effect.
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
            dbid = item.get('id') or item.get('episodeid')

            if dbid:
                Logger.debug(f"Playing: {library_type} with dbid: {dbid}")

            get_method = None
            id_name = None
            result_key = None

            if library_type == 'episode':
                get_method = 'VideoLibrary.GetEpisodeDetails'
                id_name = 'episodeid'
                result_key = 'episodedetails'
            elif library_type == 'movie':
                get_method = 'VideoLibrary.GetMovieDetails'
                id_name = 'movieid'
                result_key = 'moviedetails'

            json_dict = {
                "jsonrpc": "2.0",
                "id": "getResumePoint",
                "method": get_method,
            }
            params = {
                id_name: dbid,
                "properties": ["resume"],
            }

            json_dict['params'] = params
            query = json.dumps(json_dict)
            result = send_kodi_json(f'Get resume point for type {library_type} with dbid: {dbid}', query)['result']
            if result:
                try:
                    resume_point = result[result_key]['resume']['position']
                except:
                    Logger.error("Could not get resume point")
                    resume_point = None
                Logger.info(f"Resume point retrieved: {resume_point}")
                # Resume just slightly back from where we were...
                if resume_point and resume_point > 20:
                    self.seekTime(resume_point - 4.0)
                # Close to the beginnging or no resume point - seek back to (0) to attempt to force trigger subtitles earlier
                else:
                    self.seekTime(0.0)
