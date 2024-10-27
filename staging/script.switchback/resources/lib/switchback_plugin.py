import xbmcplugin

from bossanova808.constants import *
from bossanova808.logger import Logger
from bossanova808.utilities import footprints
# noinspection PyPackages
from .store import Store


def run(args):

    plugin_instance = int(sys.argv[1])

    footprints()
    Store()

    Logger.info(f"Running plugin with {args}")
    Logger.info(Store.switchback_list)

    xbmcplugin.setContent(plugin_instance, 'videos')

    for item in Store.switchback_list[0:Store.maximum_list_length]:

        label = item.title
        if item.showtitle:
            label = f"{item.showtitle} - {item.season}x{item.episode} - {item.title}"
        list_item = xbmcgui.ListItem(label=label)
        list_item.setInfo('video', {'title': item.title})
        list_item.setArt({"thumbnail": item.thumbnail})
        list_item.setArt({"poster": item.thumbnail})
        list_item.setArt({"fanart": item.fanart})
        list_item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(plugin_instance, item.file, list_item)

    xbmcplugin.endOfDirectory(plugin_instance)

    # RUN MODE - DEFAULT - supply the playlist
    # if len(args) == 1:
    #     Logger.info("RUN MODE - DEFAULT")
    # # RUN MODE - delete - remove item from playlist
    # elif args[1] == 'action':
    #     pass
    # # SHOULD NEVER HAPPEN
    # else:
    #     Logger.error(f"Couldn't interperet switchback plugin arguments: {args}")

    footprints(startup=False)
