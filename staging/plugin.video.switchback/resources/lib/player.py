from plistlib import dumps
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
        # Player has to have a file...
        if xbmc.getCondVisibility('Player.HasMedia'):
            current_playback = Playback()
            current_playback.file = self.getPlayingFile()
            # Get more info on what is playing, query depends on if video or audio...
            json_dict = {
                    "jsonrpc": "2.0",
                    "id": "getPlaybackDetails",
                    "method": "Player.GetItem",
            }
            if xbmc.getCondVisibility('Player.HasVideo'):
                params = {"playerid":1, "properties": ["title", "thumbnail", "fanart", "year", "showtitle", "season", "episode"]}
            else:
                return
                # params = {"playerid":0, "properties": ["title", "thumbnail", "fanart", "album", "artist", "duration", "streamdetails"]}
            json_dict['params'] = params
            query = json.dumps(json_dict)
            properties_json = send_kodi_json(f'Get properties for {current_playback.file}', query)
            properties = properties_json['result']['item']
            current_playback.title = properties['title']
            current_playback.thumbnail = unquote(properties['thumbnail']).replace("image://","").rstrip("/")
            current_playback.fanart = unquote(properties['fanart']).replace("image://","").rstrip("/")
            if "year" in properties:
                current_playback.year = properties['year']
            if "showtitle" in properties:
                current_playback.showtitle = properties['showtitle']
            if "season" in properties:
                current_playback.season = properties['season']
            if "episode" in properties:
                current_playback.episode = properties['episode']
            # if "album" in properties:
            #     current_playback.album = properties['album']
            # if "artist" in properties:
            #     current_playback.artist = properties['artist']
            # if "duration" in properties:
            #     current_playback.duration = properties['duration']
            # if "streamdetails" in properties:
            #     current_playback.streamdetails = properties['streamdetails']

            # Logger.info(current_playback)

            # Prepend this playback to our list and write the playback out to file
            # Probably there's a faster way to do this but the list is never that long anyway..
            Store.switchback_list = [current_playback] + Store.switchback_list[0:Store.maximum_list_length-1]
            Store.save_switchback_list()

    def onPlayBackEnded(self):  # video ended normally (user didn't stop it)
        Logger.info("onPlayBackEnded")
        self.onPlaybackFinished()

    def onPlayBackStopped(self):
        Logger.info("onPlayBackStopped")
        self.onPlaybackFinished()

    def onPlaybackFinished(self):
        """
        Playback has finished, so update our S
        """
