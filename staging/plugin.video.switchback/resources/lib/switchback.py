from bossanova808.utilities import *
# noinspection PyPackages
from .store import Store

# noinspection PyPackages
from .monitor import KodiEventMonitor
# noinspection PyPackages
from .player import KodiPlayer

import os
import sys
import glob
import ntpath
import xbmc
import xbmcvfs


# This is 'main'...
def run():

    footprints()
    Store()
    Store.kodi_event_monitor = KodiEventMonitor(xbmc.Monitor)
    Store.kodi_player = KodiPlayer(xbmc.Player)

    while not Store.kodi_event_monitor.abortRequested():
        if Store.kodi_event_monitor.waitForAbort(1):
            # Abort was requested while waiting. We should exit
            break

    # and, we're done...
    footprints(startup=False)
