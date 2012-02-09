import os
import re
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import time
from traceback import print_exc

#an orderly place to keep constants
import constants 
#Classes
from NowPlayingWindow import *
from SqueezePlayer import *
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

    #make our storage paths
    try:
      if not xbmcvfs.exists( constants.CHANGING_IMAGES_PATH ):
        Logger.log ( "Making output directory for cover art etc. in addon_data")
        os.makedirs( constants.CHANGING_IMAGES_PATH )        
    except Exception as inst:
      Logger.log( "ERROR: Couldn't make folders in addon_data - bailing out!" , inst)
      sys.exit()
      
    #create a player instance (is really a player + server combo)    
    try:
      player = SqueezePlayer()
    except:
      print_exc()
      sys.exit()

    #init the player
    #player.getPlaylist()

    #now let's make a window and see if we can send some commands...
    window = NowPlayingWindow(player)
    
    running = True
    while running:
      window.update()
      window.show()
      xbmc.sleep(100)
        
    # after the window is closed, Destroy it.
    del window
    
    Logger.log( "### Exiting XSqueeze..." )
