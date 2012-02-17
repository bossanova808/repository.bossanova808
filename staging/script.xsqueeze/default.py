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
      xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Starting Squeezeslave player,Please wait a moment...)")

      #32 or 64 bit?
      is_64bits = sys.maxsize > 2**32

      #need to work out what system we're on
      system=""

      #hack to check if openelec via settings until we work out a better way
      if constants.ISOPENELEC:
        system = "Linux"
      else:
        system = platform.system()

      #choose the right executable
      if system=="Windows":
        exe = [constants.BINWIN]
      elif system=="Darwin":
        exe = [constants.BINOSX]
      elif system=="Linux":
        if is_64bits:
          exe = [constants.BINLIN64]
        else:
          exe = [constants.BINLIN32]
        try:
          #attempt to make the binary executable
          os.chmod(0775, exe[0])
        except:
          Logger.log("Couldn't chmod +x binaries - hopefully user has done this manually!")
      #no idea what platform we're on..best to stop now...
      else:
        xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Couldn't determine system type for squeezeslave,Bailing out...)")
        sys.exit()

      Logger.log("Starting local Squeezeslave, system is " + system)

      #builds the list ['/path/exefile','-arg1','-arg2',...]
      args = constants.SLAVEARGS.split(" ")
      args.append(constants.SERVERIP)
      exe.extend(args)

      Logger.log ("Attempting to start Squeezelave: " + str(exe))
      try:
        #need this to stop windows opening a console window
        if system=="Windows":
          slaveProcess = subprocess.Popen(exe, creationflags=0x08000000, shell=False)
        else:
          slaveProcess = subprocess.Popen(exe, shell=False)
      except Exception as inst:
        Logger.log("Failed creating squeezeslave process", inst)
        xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Couldn't start process squeezeslave,On OE/linux did you chmod +x the binaries?...)")
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