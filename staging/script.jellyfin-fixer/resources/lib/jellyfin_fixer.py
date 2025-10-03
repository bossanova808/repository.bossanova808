from bossanova808.logger import Logger

# noinspection PyPackages
from .monitor import KodiEventMonitor
# noinspection PyPackages
from .player import KodiPlayer


# This is 'main'...
def run():

    Logger.start()

    try:
        kodi_monitor = KodiEventMonitor()
        player = KodiPlayer()
        while not kodi_monitor.abortRequested():
            if kodi_monitor.waitForAbort(1):
                break
    finally:
        Logger.stop()
        player = None
        kodi_monitor = None

    # and, we're done...
    Logger.stop()
