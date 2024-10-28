from urllib.parse import parse_qs

import xbmc
import xbmcplugin

from bossanova808.constants import *
from bossanova808.logger import Logger
from bossanova808.utilities import footprints
# noinspection PyPackages
from .store import Store


def create_kodi_list_item_from_playback(playback, offscreen=False):
    Logger.info("Creating list item from playback")
    Logger.info(playback)

    label = playback.title
    if playback.showtitle:
        label = f"{playback.showtitle} ({playback.season}x{playback.episode}) - {playback.title}"
    list_item = xbmcgui.ListItem(label=label, path=playback.file, offscreen=offscreen)

    # New VideoInfoTag properties
    tag = list_item.getVideoInfoTag()
    tag.setTitle(playback.title)
    tag.setPath(playback.file)
    if playback.id:
        tag.setDbId(playback.id)
    if playback.year != 0:
        tag.setYear(playback.year)
    if playback.showtitle:
        tag.setTvShowTitle(playback.showtitle)
    if playback.season:
        tag.setSeason(playback.season)
    if playback.episode:
        tag.setEpisode(playback.episode)
    # Seems to be for Music Videos only?  List?
    if playback.artist:
        tag.setArtists([playback.artist])
    if playback.album:
        tag.setAlbum(playback.album)
    if playback.duration:
        tag.setDuration(playback.duration)
    if playback.resumetime:
        tag.setResumePoint(playback.resumetime)
    # if playback.streamdetails:
    #     tag.setStreamDetails(playback.streamdetails)

    # Old style properties
    list_item.setProperty('IsPlayable', 'true')
    list_item.setPath(path=playback.file)
    list_item.setArt({"thumbnail": playback.thumbnail})
    list_item.setArt({"poster": playback.thumbnail})
    list_item.setArt({"fanart": playback.fanart})

    info_labels = {
            'mediatype': playback.type,
            'title': playback.title,
    }
    list_item.setInfo(playback.type, info_labels)

    # Auto resumes don't work without these, even though they are depracated...
    list_item.setProperty('TotalTime', str(playback.totaltime))
    list_item.setProperty('ResumeTime', str(playback.resumetime))
    list_item.setProperty('StartOffset', str(playback.resumetime))

    return list_item


def run(args):
    plugin_instance = int(sys.argv[1])

    footprints()
    Store()

    parsed_arguments = parse_qs(sys.argv[2][1:])
    Logger.info(parsed_arguments)
    mode = parsed_arguments.get('mode', None)
    Logger.info(f"Mode: {mode}")

    if mode and mode[0] == "play_previous":
        Logger.info("Playing previous file (Store.switchback_list[1])")
        if Store.switchback_list[1]:
            list_item = create_kodi_list_item_from_playback(Store.switchback_list[1], offscreen=True)
            xbmcplugin.setResolvedUrl(plugin_instance, True, list_item)
        else:
            Logger.error("No previous item found to play")
    else:
        xbmcplugin.setContent(plugin_instance, 'videos')

        for playback in Store.switchback_list[0:Store.maximum_list_length]:
            list_item = create_kodi_list_item_from_playback(playback)
            xbmcplugin.addDirectoryItem(plugin_instance, playback.file, list_item)

        xbmcplugin.endOfDirectory(plugin_instance)

    footprints(startup=False)
