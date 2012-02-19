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
#the logging class
import Logger
#the window class
from NowPlayingWindow import *

################################################################################
### MAIN

if ( __name__ == "__main__" ):

    #log some tracks...
    Logger.footprints()

    #the script is being called with an argument - we're either
    # auto discovering servers and choosing them
    #or
    # choosing an audio output

    if len(sys.argv) > 1:
      if sys.argv[1].startswith('ServerDiscovery'):
        Logger.log("Doing server discovery...")
        exe = constants.EXE
        exe.append("-I")

        #need this to stop windows opening a console window & grab output
        Logger.log("Calling SqueezeSlave for server discovery..." + str(exe))

        if constants.SYSTEM=="Windows":
          output, result = subprocess.Popen(exe, creationflags=0x08000000, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=False).communicate()
        else:
          output, result = subprocess.Popen(exe, shell=False, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()

        Logger.log("Error, if any: " + str(result))
        Logger.log("Lines returned is " + str(output))
        lines = output.split("\n")
        #Each line is: My Music Library Name:9000 (192.168.1.1)

        nameIPList = {}

        for count, line in enumerate(lines):
          ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
          if len(ip) > 0:
            Logger.log("Parsing line " + line)
            #this will fail if they have a colon in their name - fuck 'em for using a stupid name
            name = line.split(":")[0]
            nameIPList[name] = ip[0]

        Logger.log("List of servers is " + str(nameIPList))



      elif sys.argv[1].startswith('AudioOutputs'):
        Logger.log("Doing audio output discovery...")

    #we're running the main script now...
    else:

      #disable the screensaver if the user has this on
      if constants.DISABLESCREENSAVER:
        Logger.log("Disabling screensaver")
        screensaver = xbmc.executehttpapi( "GetGUISetting(3;screensaver.mode)" ).replace( "<li>", "" )
        xbmc.executehttpapi( "SetGUISetting(3,screensaver.mode,None)" )

      #are we running the locally installed Squeezeslave?
      if constants.CONTROLSLAVE:
        xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Starting Squeezeslave player,Please wait a moment...)")
        Logger.log("Starting local Squeezeslave, system is " + constants.SYSTEM)

        #builds the list ['/path/exefile','-arg1','-arg2',...]
        exe = constants.EXE
        args = constants.SLAVEARGS.split(" ")
        args.append(constants.SERVERIP)
        exe.extend(args)

        Logger.log ("Attempting to start Squeezelave: " + str(exe))
        try:
          #need this to stop windows opening a console window
          if constants.SYSTEM=="Windows":
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

      ##########################################################################
      # SETUP DONE > ON WITH THE SHOW

      #now let's make a window and see if we can send some commands...
      #check what skin to use
      if constants.SKIN == "AeonNox":
        Logger.log("Skin set to Aeon Nox")
        window = NowPlayingWindow("XSqueezeNowPlaying.xml",constants.__cwd__,"AeonNox")
      #default to Confluence
      else:
        Logger.log("Skin set to Confluence")
        window = NowPlayingWindow("XSqueezeNowPlaying.xml",constants.__cwd__,"Default")

      #add a dummy track to the playlist
      #AddToPlaylist = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Playlist.Add", "id": 1, "params": {"item": {"songid": 7}}}')
      #result = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Playlist.Add", "id": 1, "params": {"Playlist.Item": "' + constants.DUMMYAUDIO + '"}}')
      #Logger.log(" Added dummy track 1" + str(result))
      #and kick this bad boy off....
      window.doModal()

      ############################################################################
      # FINISHED - CLEAN UP!

      # after the window is closed, Destroy it.
      del window

      #are we running the locally installed Squeezeslave? KILL IT!
      if constants.CONTROLSLAVE:
        Logger.log("Killing Squeezeslave process...")
        slaveProcess.kill()

      #re-enable the screensaver as it was
      if constants.DISABLESCREENSAVER:
        Logger.log("Re-enabling screensaver")
        xbmc.executehttpapi( "SetGUISetting(3,screensaver.mode,%s)" % screensaver )

      sys.modules.clear()
      Logger.log( "### Exiting XSqueeze..." )
