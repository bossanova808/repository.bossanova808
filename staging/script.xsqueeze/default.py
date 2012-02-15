import os
import re
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import time
import sys

#an orderly place to keep constants
import constants
#Classes
from NowPlayingWindow import *
import Logger

################################################################################
### MAIN

if ( __name__ == "__main__" ):

    #log some tracks...
    Logger.footprints()

    #xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Starting Up!,Wait a moment...)")

    #now let's make a window and see if we can send some commands...
    window = NowPlayingWindow("XSqueezeNowPlaying.xml",constants.__cwd__,"Default")

    window.doModal()

    # after the window is closed, Destroy it.
    del window

    Logger.log( "### Exiting XSqueeze..." )
    sys.modules.clear()