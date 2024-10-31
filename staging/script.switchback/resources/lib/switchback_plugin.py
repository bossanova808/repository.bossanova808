from urllib.parse import parse_qs

import xbmc
import xbmcplugin

from bossanova808.constants import *
from bossanova808.logger import Logger
from bossanova808.utilities import footprints
# noinspection PyPackages
from .store import Store
from infotagger.listitem import ListItemInfoTag


def create_kodi_list_item_from_playback(playback, index=None, offscreen=False):
    Logger.info("Creating list item from playback")
    Logger.info(playback)

    label = playback.title
    if playback.showtitle:
        if playback.season >= 0 and playback.episode >= 0:
            label = f"{playback.showtitle} ({playback.season}x{playback.episode:02d}) - {playback.title}"
        elif playback.season >= 0:
            label = f"{playback.showtitle} ({playback.season}x?) - {playback.title}"
        else:
            label = f"{playback.showtitle} - {playback.title}"
    if playback.album:
        label = f"{playback.artist[0]} - {playback.album} - {playback.title}"

    list_item = xbmcgui.ListItem(label=label, path=playback.file, offscreen=offscreen)
    tag = ListItemInfoTag(list_item, 'video')

    # tag = list_item.getVideoInfoTag()
    # tag.setTitle(playback.title)
    # tag.setPath(playback.file)
    # if playback.dbid:
    #     tag.setDbId(playback.dbid)
    # if playback.year != 0:
    #     tag.setYear(playback.year)
    # if playback.showtitle:
    #     tag.setTvShowTitle(playback.showtitle)
    # if playback.season:
    #     tag.setSeason(playback.season)
    # if playback.episode:
    #     tag.setEpisode(playback.episode)
    # # Seems to be for Music Videos only?  List?
    # if playback.artist:
    #     tag.setArtists(playback.artist)
    # if playback.album:
    #     tag.setAlbum(playback.album)
    # if playback.duration:
    #     tag.setDuration(playback.duration)
    # if playback.resumetime:
    #     tag.setResumePoint(playback.resumetime)

    infolabels = {
            'mediatype': playback.type,
            'dbid': playback.dbid,
            'title': playback.title,
            'year': playback.year,
            'tvshowtitle': playback.showtitle,
            'episode': playback.episode,
            'season': playback.season,
            'duration': playback.totaltime,
    }
    # list_item.setInfo("video", infolabels)
    tag.set_info(infolabels)
    list_item.setPath(path=playback.file)
    list_item.setArt({"thumbnail": playback.thumbnail})
    list_item.setArt({"poster": playback.poster})
    list_item.setArt({"fanart": playback.fanart})
    # Auto resumes just won't work without these, even though they are deprecated...
    list_item.setProperty('TotalTime', str(playback.totaltime))
    list_item.setProperty('ResumeTime', str(playback.resumetime))
    list_item.setProperty('StartOffset', str(playback.resumetime))
    list_item.setProperty('IsPlayable', 'true')

    # index can be zero, so explicitly check against None!
    if index is not None:
        list_item.addContextMenuItems([(LANGUAGE(32004), "RunPlugin(plugin://script.switchback?mode=delete&index=" + str(index) + ")")])

    return list_item


def run(args):
    plugin_instance = int(sys.argv[1])

    footprints()
    Logger.info("(Plugin)")
    Store()

    xbmcplugin.setContent(plugin_instance, 'mixed')

    parsed_arguments = parse_qs(sys.argv[2][1:])
    Logger.info(parsed_arguments)
    mode = parsed_arguments.get('mode', None)
    Logger.info(f"Mode: {mode}")

    if mode and mode[0] == "play_previous":
        Logger.info(f"Playing previous file (Store.switchback_list[1]) {Store.switchback_list[1].file}")
        if Store.switchback_list[1]:
            list_item = create_kodi_list_item_from_playback(Store.switchback_list[1], offscreen=True)
            xbmcplugin.setResolvedUrl(plugin_instance, True, list_item)
        else:
            Logger.error("No previous item found to play")
    if mode and mode[0] == "delete":
        index_to_remove = parsed_arguments.get('index', None)
        if index_to_remove:
            Logger.info(f"Deleting playback {index_to_remove[0]} from Switchback List")
            Store.switchback_list.remove(Store.switchback_list[int(index_to_remove[0])])
            Store.save_switchback_list()
            # Force refresh the list
            Logger.debug("Force refresh the list")
            xbmc.executebuiltin("Container.Refresh")
            # xbmc.executebuiltin("ActivateWindow(Videos,plugin://script.switchback)")
    # Default mode - show the whole Switchback List
    else:
        for index, playback in enumerate(Store.switchback_list[0:Store.maximum_list_length]):
            list_item = create_kodi_list_item_from_playback(playback, index=index)
            xbmcplugin.addDirectoryItem(plugin_instance, playback.file, list_item)

        xbmcplugin.endOfDirectory(plugin_instance)

    footprints(startup=False)
