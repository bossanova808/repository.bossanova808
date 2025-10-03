from bossanova808.logger import Logger

# noinspection PyPackages
from .monitor import KodiEventMonitor
# noinspection PyPackages
from .player import KodiPlayer


# This is 'main'...
def run():

    """
    Start logging, initialize KodiEventMonitor and KodiPlayer, and run until an abort is requested.
    
    Initializes the logger and creates monitor and player instances, then polls the monitor until an abort is signaled. Ensures the logger is stopped and created objects are released on exit.
    """
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
