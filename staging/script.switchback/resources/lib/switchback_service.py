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
    Logger.info("(Service)")
    Store()
    Store.kodi_event_monitor = KodiEventMonitor(xbmc.Monitor)
    Store.kodi_player = KodiPlayer(xbmc.Player)

    while not Store.kodi_event_monitor.abortRequested():
        # Abort was requested while waiting. We should exit
        if Store.kodi_event_monitor.waitForAbort(1):
            break
        # Otherwise, if we're playing something, record where we are up to and the total time, for resumes
        # (Playback record is created onAVStarted in player.py, so check here that it is available)
        elif Store.current_playback and Store.kodi_player.isPlaying():
            Store.current_playback.resumetime = Store.kodi_player.getTime()
            Store.current_playback.totaltime = Store.kodi_player.getTotalTime()
            xbmc.sleep(500)

    # and, we're done...
    footprints(startup=False)
