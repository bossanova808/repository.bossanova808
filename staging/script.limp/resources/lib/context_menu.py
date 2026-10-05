import sys
import time

import xbmc

from bossanova808.constants import HOME_WINDOW, TRANSLATE
from bossanova808.logger import Logger
from bossanova808.notify import Notify
from bossanova808.utilities import send_kodi_json, get_property, clear_property
# noinspection PyPackages
from .messages import NOTIFY_SENDER, NOTIFY_MESSAGE, ACK_PROPERTY

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
    send_kodi_json('Ask Limp service to play with software decode', {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "JSONRPC.NotifyAll",
            "params": {"sender": NOTIFY_SENDER, "message": NOTIFY_MESSAGE, "data": request},
    })

    deadline = time.monotonic() + ACK_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if get_property(HOME_WINDOW, ACK_PROPERTY) == request['id']:
            break
        xbmc.sleep(50)
    else:
        Logger.warning('No confirmation from the Limp service.')
        Notify.warning(TRANSLATE(32021))

    Logger.stop('(Context menu)')
