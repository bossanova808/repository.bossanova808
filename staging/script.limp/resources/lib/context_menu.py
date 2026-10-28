import os
import sys
import time

import xbmc

from bossanova808.constants import HOME_WINDOW, TRANSLATE
from bossanova808.logger import Logger
from bossanova808.notify import Notify
from bossanova808.utilities import get_property, clear_property
from bossanova808.show_list import ShowList, title_key
# noinspection PyPackages
from .messages import (ACK_PROPERTY, FILES_FILE, NOTIFY_FILES_CHANGED, NOTIFY_MESSAGE, NOTIFY_SERIES_CHANGED, SERIES_FILE,
                       notify_info, notify_service)

# How long to wait for the Limp service to pick up the request
ACK_TIMEOUT_SECONDS = 3


def _video_title(item, tag):
    """
    :return: a name for the selected video to show in lists and notifications - "Show S01E03 Title"
        for an episode, otherwise its title
    """
    title = tag.getTitle() or item.getLabel() or os.path.basename(item.getPath().rstrip('/\\'))
    show = tag.getTVShowTitle()
    if not show:
        return title
    season, episode = tag.getSeason(), tag.getEpisode()
    if season >= 0 and episode > 0:
        return f'{show} S{season:02d}E{episode:02d} {title}'
    return f'{show} - {title}'


def _video_key(item, tag):
    """
    The key a video is remembered under: its path exactly as the service sees it when the video is
    focused (ListItem.FileNameAndPath) - for a library item that's the real file or add-on path,
    where the item's own path can be a videodb:// one that would never match.

    :return: the video's path
    """
    return xbmc.getInfoLabel('ListItem.FileNameAndPath') or tag.getFile() or item.getPath()


def run():
    """
    The "Limp: toggle video as software decode" context menu action. This runs as its own short-lived
    script. If the selected video isn't remembered yet, it remembers it (so it uses software decoding
    every time it's played), then asks the (already running) Limp service to force software decode
    and play it, and waits for the service to confirm - and says so if it doesn't. If the video is
    already remembered, it's taken off the list instead, and nothing is played.

    The state is read from the list as the action runs, rather than shown in the menu's label, so it
    is always right however quickly the list was being scrolled.

    :return:
    """
    Logger.start('(Context menu)')

    item = sys.listitem
    tag = item.getVideoInfoTag()

    file_path = _video_key(item, tag)
    title = _video_title(item, tag)
    videos = ShowList(FILES_FILE)
    if not file_path or file_path.endswith(('/', '\\')):
        Logger.warning(f'Not a video Limp can remember: [{file_path}]')
        Logger.stop('(Context menu)')
        return

    if videos.contains(file_path):
        videos.remove(file_path)
        if videos.save():
            Logger.info(f'Removed from the video list: {title} [{file_path}]')
            notify_service(NOTIFY_FILES_CHANGED)
            notify_info(TRANSLATE(32036).format(title))
        else:
            Notify.error(TRANSLATE(32074))
        Logger.stop('(Context menu)')
        return

    videos.add(file_path, title)
    if videos.save():
        Logger.info(f'Added to the video list: {title} [{file_path}]')
        notify_service(NOTIFY_FILES_CHANGED)
        notify_info(TRANSLATE(32032).format(title))
    else:
        Notify.error(TRANSLATE(32074))

    request = {
            'id': str(time.time()),
            'file': item.getPath(),
            'dbtype': tag.getMediaType(),
            'dbid': tag.getDbId(),
    }

    clear_property(HOME_WINDOW, ACK_PROPERTY)
    notify_service(NOTIFY_MESSAGE, request)

    deadline = time.monotonic() + ACK_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if get_property(HOME_WINDOW, ACK_PROPERTY) == request['id']:
            break
        xbmc.sleep(50)
    else:
        Logger.warning('No confirmation from the Limp service.')
        Notify.warning(TRANSLATE(32021))

    Logger.stop('(Context menu)')


def run_series():
    """
    The "Limp: toggle series as software decode" context menu action: add the selected item's TV show
    to the list of series that always use software decoding, or take it off if it's already there.

    :return:
    """
    Logger.start('(Context menu - series)')

    title = sys.listitem.getVideoInfoTag().getTVShowTitle()
    if not title:
        Logger.warning('The selected item has no TV show title.')
        Notify.warning(TRANSLATE(32033))
    else:
        series = ShowList(SERIES_FILE)
        if series.contains(title_key(title)):
            series.remove(title_key(title))
            message, action = TRANSLATE(32036), 'Removed from'
        else:
            series.add(title_key(title), title)
            message, action = TRANSLATE(32032), 'Added to'
        if series.save():
            Logger.info(f'{action} the series list: {title}')
            notify_service(NOTIFY_SERIES_CHANGED)
            notify_info(message.format(title))
        else:
            Notify.error(TRANSLATE(32054))

    Logger.stop('(Context menu - series)')
