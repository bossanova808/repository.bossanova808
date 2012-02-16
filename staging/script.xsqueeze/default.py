import os
import re
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import time
import sys
import platform
import subprocess

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


    #are we running the locally installed Squeezeslave?
    if constants.CONTROLSLAVE:
      xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Starting local Squeezeslave,Wait a moment...)")
      #system = platform.system()
      system = "Linux"
      Logger.log("Starting local Squeezeslave, system is " + system)

      if system=="Windows":
        exe = [constants.BINWIN]
      if system=="Windows":
        exe = [constants.BINWIN]
      elif system=="Darwin":
        exe = [constants.BINOSX]
      elif system=="Linux":
        is_64bits = sys.maxsize > 2**32
        if is_64bits:
          exe = [constants.BINLIN64]
        else:
          exe = [constants.BINLIN32]
      else:
        xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Couldn't determine system type for squeezeslave,Bailing out...)")
        sys.exit()

      args = constants.SLAVEARGS.split(" ")
      args.append(constants.SERVERIP)
      exe.extend(args)

      #args = constants.SERVERIP
      Logger.log ("Attempting to start " + str(exe))
      try:
        if system=="Windows":
          slaveProcess = subprocess.Popen(exe, creationflags=0x08000000, shell=False)
        else:
          slaveProcess = subprocess.Popen(exe, shell=False)
      except Exception as inst:
        Logger.log("Failed creating squeezeslave process", inst)
        xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Couldn't start process squeezeslave,Bailing out...)")
        sys.exit()

      pid = slaveProcess.pid
      Logger.log("Process ID for Squeezeslave is "+ str(pid))
      #little pause to give squeezeslave time to run & connect
      time.sleep(5)



    #now let's make a window and see if we can send some commands...
    window = NowPlayingWindow("XSqueezeNowPlaying.xml",constants.__cwd__,"Default")

    window.doModal()

    # after the window is closed, Destroy it.
    del window

    Logger.log( "### Exiting XSqueeze..." )

    #are we running the locally installed Squeezeslave? KILL IT!
    if constants.CONTROLSLAVE:
      Logger.log("Killing Squeezeslave process...")
      slaveProcess.kill()

    sys.modules.clear()