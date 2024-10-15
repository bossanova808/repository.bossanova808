from bossanova808.utilities import *
# noinspection PyPackages
# from .store import Store
# noinspection PyPackages
# from .monitor import KodiEventMonitor
# noinspection PyPackages
# from .player import KodiPlayer

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

    # and, we're done...
    footprints(startup=False)
