import sys
import time

import xbmc

from bossanova808.constants import HOME_WINDOW, TRANSLATE
from bossanova808.logger import Logger
from bossanova808.notify import Notify
from bossanova808.utilities import get_property, clear_property
from bossanova808.show_list import ShowList, title_key
# noinspection PyPackages
from .messages import NOTIFY_MESSAGE, NOTIFY_SERIES_CHANGED, ACK_PROPERTY, SERIES_FILE, notify_service

# How long to wait for the Limp service to pick up the request
ACK_TIMEOUT_SECONDS = 3


def run():
    """
    The "Limp: software decode" context menu action. This runs as its own short-lived script, so
    it just asks the (already running) Limp service to force software decode and play the selected
    item, then waits for the service to confirm - and says so if it doesn't.

    :return:
    """
    Logger.start('(Context menu)')

    item = sys.listitem
    tag = item.getVideoInfoTag()
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
    The "Limp: software decode series" context menu action: add the selected item's TV show to the
    list of series that always use software decoding (taken off again in the settings).

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
            Notify.info(TRANSLATE(32034).format(title))
        else:
            series.add(title_key(title), title)
            if series.save():
                Logger.info(f'Added to the series list: {title}')
                notify_service(NOTIFY_SERIES_CHANGED)
                Notify.info(TRANSLATE(32032).format(title))
            else:
                Notify.error(TRANSLATE(32054))

    Logger.stop('(Context menu - series)')


def run_series_stop():
    """
    The "Limp: stop software decoding series" context menu action: take the selected item's TV
    show off the list of series that always use software decoding.

    :return:
    """
    Logger.start('(Context menu - stop series)')

    title = sys.listitem.getVideoInfoTag().getTVShowTitle()
    if not title:
        Logger.warning('The selected item has no TV show title.')
        Notify.warning(TRANSLATE(32033))
    else:
        series = ShowList(SERIES_FILE)
        if not series.contains(title_key(title)):
            Notify.info(TRANSLATE(32035).format(title))
        else:
            series.remove(title_key(title))
            if series.save():
                Logger.info(f'Removed from the series list: {title}')
                notify_service(NOTIFY_SERIES_CHANGED)
                Notify.info(TRANSLATE(32036).format(title))
            else:
                Notify.error(TRANSLATE(32054))

    Logger.stop('(Context menu - stop series)')
