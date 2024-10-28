from urllib.parse import unquote

from bossanova808.logger import Logger
from bossanova808.utilities import *
# noinspection PyPackages
from .store import Store
# noinspection PyPackages
from .playback import Playback
import xbmc
import json


class KodiPlayer(xbmc.Player):
    """
    This class represents/monitors the Kodi video player
    """

    def __init__(self, *args):
        xbmc.Player.__init__(self)
        Logger.debug('KodiPlayer __init__')

    def onPlayBackStarted(self):
        Logger.info("onPlayBackStarted")

    # Use on AV started we want to record a playback only if the user actually saw a video...
    def onAVStarted(self):
        Logger.info('onAVStarted')
        # If Kodi is playing a file, gather info on it
        if xbmc.getCondVisibility('Player.HasMedia'):
            # Clear any legacy recroded playback details by creating a new Playback object
            Store.current_playback = Playback()
            Store.current_playback.file = self.getPlayingFile()
            # Get more info on what is playing, query depends on if video or audio...
            json_dict = {
                    "jsonrpc": "2.0",
                    "id": "getPlaybackDetails",
                    "method": "Player.GetItem",
            }
            if xbmc.getCondVisibility('Player.HasVideo'):
                params = {"playerid":1, "properties": ["title", "thumbnail", "fanart", "year", "showtitle", "season", "episode"]}
            else:
                params = {"playerid":0, "properties": ["title", "thumbnail", "fanart", "album", "artist", "duration", "streamdetails"]}
            json_dict['params'] = params
            query = json.dumps(json_dict)
            properties_json = send_kodi_json(f'Get properties for {Store.current_playback.file}', query)
            properties = properties_json['result']['item']
            Store.current_playback.title = properties['title']
            Store.current_playback.fanart = unquote(properties['fanart']).replace("image://","").rstrip("/")
            Store.current_playback.thumbnail = unquote(properties['thumbnail']).replace("image://","").rstrip("/")
            # @TODO - can this be improved?  Why does Kodi return e.g. '.mkv' files for thumbnail - extracted thumbs??
            if 'jpg' not in Store.current_playback.thumbnail:
                Store.current_playback.thumbnail = unquote(properties['fanart']).replace("image://","").rstrip("/")
            if "id" in properties:
                Store.current_playback.id = properties['id']
            if "type" in properties:
                Store.current_playback.type = properties['type']
            if "year" in properties:
                Store.current_playback.year = properties['year']
            if "showtitle" in properties:
                Store.current_playback.showtitle = properties['showtitle']
            if "season" in properties:
                Store.current_playback.season = properties['season']
            if "episode" in properties:
                Store.current_playback.episode = properties['episode']
            if "album" in properties:
                Store.current_playback.album = properties['album']
            if "artist" in properties:
                Store.current_playback.artist = properties['artist']
            if "duration" in properties:
                Store.current_playback.duration = properties['duration']
            if "streamdetails" in properties:
                Store.current_playback.streamdetails = properties['streamdetails']

            # Logger.info(current_playback)

    def onPlayBackEnded(self):  # video ended by by running out (user didn't stop it)
        Logger.info("onPlayBackEnded")
        self.onPlaybackFinished()

    def onPlayBackStopped(self):
        Logger.info("onPlayBackStopped")
        self.onPlaybackFinished()

    # noinspection PyMethodMayBeStatic
    def onPlaybackFinished(self):
        """
        Playback has finished, so update our Switchback List
        """
        Logger.debug("onPlaybackFinished")

        # Logger.debug("Current playback")
        # Logger.debug(Store.current_playback)
        # Logger.debug("Starting with Switchback list:")
        # Logger.debug(Store.switchback_list)

        # We only want to have the most current playback recorded in our list, so remove any previous playbacks
        Store.switchback_list = [x for x in Store.switchback_list if x.file != Store.current_playback.file]

        # Logger.debug("After removing dupes")
        # Logger.debug(Store.switchback_list)

        # Then, prepend this new playback to our list
        Store.switchback_list = [Store.current_playback] + Store.switchback_list[0:Store.maximum_list_length-1]

        # Logger.debug("After prepending and shortening")
        # Logger.debug(Store.switchback_list)

        # Finally, Save the playback list to file
        Store.save_switchback_list()

