# -*- coding: utf-8 -*-

from bossanova808.common import *
# from .store import Store
# from .monitor import KodiEventMonitor
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

    # and, we're done...
    footprints(startup=False)
