import time
from urllib.parse import unquote

from bossanova808.logger import Logger
from bossanova808.utilities import *
# noinspection PyPackages
from .store import Store
# noinspection PyPackages
from .playback import Playback
import xbmc
import json


# This causes big delays and is only needed for addons.
def getInfoLabel(label):
    value = None
    retry = 0
    while retry < 50:
        value = xbmc.getInfoLabel(label)
        retry += 1
        if value:
            Logger.info(f"Value of infolabel {label} is {value}")
            break
        time.sleep(0.1)
    return value


class KodiPlayer(xbmc.Player):
    """
    This class represents/monitors the Kodi video player
    """

    def __init__(self, *args):
        xbmc.Player.__init__(self)
        Logger.debug('KodiPlayer __init__')

    # Use on AVStarted (vs Playback started) we want to record a playback only if the user actually saw a video...
    def onAVStarted(self):
        Logger.info('onAVStarted')
        # Reload the Switchback list in case the plugin has e.g. deleted anything
        Store.load_config_from_settings()
        # If Kodi is playing a file, gather info on it
        if xbmc.getCondVisibility('Player.HasMedia'):

            # Only record music playbacks if the user has requested we do via the settings
            if not xbmc.getCondVisibility('Player.HasVideo') and not Store.include_music:
                return

            # Clear any legacy recorded playback details by creating a new Playback object
            Store.current_playback = Playback()
            Store.current_playback.file = self.getPlayingFile()
            # Get more info on what is playing, query depends on if video or audio...

            # Unfortunately, when playing from an offscreen playlist, the GetItem properties don't seem to be set,
            # but can get info from Video/Music-Player it seems...
            # See https://forum.kodi.tv/showthread.php?tid=379301
            json_dict = {
                    "jsonrpc": "2.0",
                    "id": "XBMC.GetInfoLabels",
                    "method": "XBMC.GetInfoLabels",
            }
            stub = None
            if xbmc.getCondVisibility('Player.HasVideo'):
                params = {"labels": ["Player.Art(thumb)", "Player.Art(poster)", "Player.Art(fanart)", "Player.Duration", "Player.Art(tvshow.poster)", "Player.Art(movie.poster)", "VideoPlayer.DBID", "VideoPlayer.Title", "VideoPlayer.Year", "VideoPlayer.TVShowTitle", "VideoPlayer.Season", "VideoPlayer.Episode"]}
                stub = "Video"
            else:
                params = {"labels": ["Player.Art(thumb)", "Player.Art(poster)", "Player.Art(fanart)", "Player.Duration", "MusicPlayer.DBID", "MusicPlayer.Title", "MusicPlayer.Year", "MusicPlayer.Album", "MusicPlayer.Artist"]}
                stub = "Video"
            json_dict['params'] = params
            query = json.dumps(json_dict)
            properties_json = send_kodi_json(f'Get playback details from InfoLabels', query)
            properties = properties_json['result']

            Store.current_playback.title = properties[f'{stub}Player.Title']
            # if not Store.current_playback.title:
            #     Store.current_playback.title = properties['label']

            if 'Player.Art(poster)' in properties and properties['Player.Art(poster)']:
                Store.current_playback.poster = unquote(properties['Player.Art(poster)']).replace("image://", "").rstrip("/")
                Store.current_playback.type = "movie"
            if 'Player.Art(tvshow.poster)' in properties and properties['Player.Art(tvshow.poster)']:
                Store.current_playback.poster = unquote(properties['Player.Art(tvshow.poster)']).replace("image://", "").rstrip("/")
                Store.current_playback.type = "episode"

            if not Store.current_playback.type:
                if stub == 'Video':
                    Store.current_playback.type = "video"
                else:
                    Store.current_playback.type = "song"

            Store.current_playback.fanart = unquote(properties['Player.Art(fanart)']).replace("image://", "").rstrip("/")
            # @TODO - can this be improved?  Why does Kodi return e.g. '.mkv' files for thumbnail - extracted thumbs??
            Store.current_playback.thumbnail = unquote(properties['Player.Art(thumb)']).replace("image://", "").rstrip("/")
            if 'jpg' not in Store.current_playback.thumbnail:
                Store.current_playback.thumbnail = unquote(properties['Player.Art(fanart)']).replace("image://", "").rstrip("/")

            if f'{stub}Player.DBID' in properties:
                Store.current_playback.dbid = properties[f'{stub}Player.DBID']
                Store.current_playback.source = "Kodi Library"
            if f'{stub}Player.Year' in properties:
                Store.current_playback.year = properties[f'{stub}Player.Year']
            if 'Player.Duration' in properties:
                Store.current_playback.duration = properties['Player.Duration']

            if 'VideoPlayer.TVShowTitle' in properties:
                Store.current_playback.showtitle = properties[f'VideoPlayer.TVShowTitle']
            if 'VideoPlayer.Season' in properties:
                Store.current_playback.season = properties['VideoPlayer.Season']
            if 'VideoPlayer.Episode' in properties:
                Store.current_playback.episode = properties['VideoPlayer.Episode']

            if 'MusicPlayer.Album' in properties:
                Store.current_playback.album = properties['MusicPlayer.Album']
            if 'MusicPlayer.Artist' in properties:
                Store.current_playback.artist = properties['MusicPlayer.Artist']

            # These will get updated as playback progress by the service, but initialise them here...
            Store.current_playback.resumetime = Store.kodi_player.getTime()
            Store.current_playback.totaltime = Store.kodi_player.getTotalTime()

            # Try alternate ways to get things if they are missing
            # if not Store.current_playback.source:
            #     Logger.debug(" %%%%%%%%%%%%%%%%% HERE %%%%%%%%%%%%%%%%%%%%%")
            #     source = getInfoLabel('ListItem.Path')
            #     if source:
            #         Store.current_playback.source = source.split('/')[2]

            # json_dict = {
            #         "jsonrpc": "2.0",
            #         "id": "Player.GetItem",
            #         "method": "Player.GetItem",
            # }
            # if xbmc.getCondVisibility('Player.HasVideo'):
            #     params = {"playerid": 1, "properties": ["thumbnail", "fanart"]}
            # else:
            #     params = {"playerid": 0, "properties": ["thumbnail", "fanart"]}
            # json_dict['params'] = params
            # query = json.dumps(json_dict)
            # properties_json = send_kodi_json(f'Get properties for {Store.current_playback.file}', query)
            # properties_from_item = properties_json['result']['item']

            # Logger.info(current_playback)

    def onPlayBackEnded(self):  # video ended by simply running out (i.e. user didn't stop it)
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

        if not Store.current_playback.file:
            Logger.error("No current playback details available...not recording this playback")
            return

        Logger.debug(Store.switchback_list)

        # Logger.debug("Current playback")
        # Logger.debug(Store.current_playback)
        # Logger.debug("Starting with Switchback list:")
        # Logger.debug(Store.switchback_list)

        # OLD SIMPLE APPROACH - Can't use this as when we playback from the playlist happens, the details get blanked
        # We only want to have the most current playback recorded in our list, so remove any previous playbacks
        # Store.switchback_list = [x for x in Store.switchback_list if x.file != Store.current_playback.file]
        # Logger.debug("After removing dupes")
        # Logger.debug(Store.switchback_list)
        # Then, prepend this new playback to our list
        # Store.switchback_list = [Store.current_playback] + Store.switchback_list[0:Store.maximum_list_length-1]
        # Logger.debug("After prepending and shortening")
        # Logger.debug(Store.switchback_list)

        # NEW APPROACH - This keeps all the details from the original playback
        # (as playing back from plugin vs. the library loses the details it seems, even with a full InfoTagVideo?)
        # Allow only one playback of a particular thing in the list - if it has been played again, move it to the top of the list
        playback_to_remove = None
        for previous_playback in Store.switchback_list:
            if previous_playback.file == Store.current_playback.file:
                playback_to_remove = previous_playback
                break

        if playback_to_remove:
            # Logger.debug("Moving re-played item to top of the Switchback List - first remove:")
            # Logger.debug(playback_to_remove)
            Store.switchback_list.remove(playback_to_remove)
            # Logger.debug(Store.switchback_list)
            # Logger.debug("Then update times and add back")
            # Update with the current playback times
            playback_to_remove.resumetime = Store.current_playback.resumetime
            playback_to_remove.totaltime = Store.current_playback.totaltime
            Store.switchback_list.insert(0, playback_to_remove)
        else:
            # Logger.debug("Inserting new playback at top of Switchback List")
            Store.switchback_list.insert(0, Store.current_playback)

        Logger.debug(Store.switchback_list)

        # Trim the list to the max length
        Store.switchback_list = Store.switchback_list[0:Store.maximum_list_length - 1]

        # Finally, Save the playback list to file
        Store.save_switchback_list()
