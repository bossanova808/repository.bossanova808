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
################################################################################
################################################################################
# Logging functions


def footprints():

    Logger.log( "### %s Starting ..." % constants.__addonname__ )
    Logger.log( "### Author: %s" % constants.__author__ )
    Logger.log( "### Version: %s" % constants.__version__ )


################################################################################
################################################################################
### MAIN

if ( __name__ == "__main__" ):

    #log some tracks...
    footprints()

    #xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Starting Up!,Wait a moment...)")


    #make our storage paths
    try:
      if not xbmcvfs.exists( constants.CHANGING_IMAGES_PATH ):
        Logger.log ( "Making output directory for cover art etc. in addon_data")
        os.makedirs( constants.CHANGING_IMAGES_PATH )
    except Exception as inst:
      Logger.log( "ERROR: Couldn't make folders in addon_data - bailing out!" , inst)
      sys.exit()


    #now let's make a window and see if we can send some commands...
    window = NowPlayingWindow("XSqueezeNowPlaying.xml",constants.__cwd__,"Default")

##    window.running = True
##    while window.running:
##      window.show()
##      window.update()
##      xbmc.sleep(10)

    window.doModal()

    # after the window is closed, Destroy it.
    del window

    Logger.log( "### Exiting XSqueeze..." )
    sys.modules.clear()