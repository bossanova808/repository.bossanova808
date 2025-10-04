from bossanova808.logger import Logger

# noinspection PyPackages
from .monitor import KodiEventMonitor
# noinspection PyPackages
from .player import KodiPlayer
# noinspection PyPackages
from .store import Store


# This is 'main'...
# noinspection PyUnusedLocal
def run():

    Logger.start()

    try:
        Store.load_config_from_settings()
        kodi_monitor = KodiEventMonitor()
        player = KodiPlayer()
        while not kodi_monitor.abortRequested():
            if kodi_monitor.waitForAbort(1):
                break
    finally:
        # We're done...
        Logger.stop()
        player = None
        kodi_monitor = None
