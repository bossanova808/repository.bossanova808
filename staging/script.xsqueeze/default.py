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
#the window for the README
from ReadMeViewer import *
#the window class
from NowPlayingWindow import *


################################################################################
# send a JSON command to XBMC and log the human description, json string, and
#the result returned

def sendXBMCJSON (humanDescription, jsonstr):
     Logger.log(humanDescription + " [" + jsonstr +"]")
     result = xbmc.executeJSONRPC(jsonstr)
     Logger.log("JSON result: "  + str(result))


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

        names = []
        ips = []

        for line in lines:
          ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
          if len(ip) > 0:
            Logger.log("Parsing line " + line)
            #this will fail if they have a colon in their name - fuck 'em for using a stupid name
            names.append(line.split(":")[0])
            ips.append(ip[0])

        Logger.log("List of servers is " + str(names) + str(ips))

        #now get them to choose an actual location

        #present the server names for user choice
        dialog = xbmcgui.Dialog()
        if names != []:
            selected = dialog.select("Select your server", names)
            if selected != -1:
                constants.__addon__.setSetting('autoserverip', ips[selected])
                constants.__addon__.setSetting('autoservername', names[selected])
                constants.__addon__.setSetting('serverAuto', names[selected])
        else:
            dialog.ok(constants.__addonname__, "No LMS Servers Found!  Check log or squeezeslave -I output manually")

      elif sys.argv[1].startswith('AudioOutputs'):
        Logger.log("Doing audio output discovery...")
        exe = constants.EXE
        exe.append("-L")

        #need this to stop windows opening a console window & grab output
        Logger.log("Calling SqueezeSlave for server discovery..." + str(exe))

        if constants.SYSTEM=="Windows":
          output, result = subprocess.Popen(exe, creationflags=0x08000000, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=False).communicate()
        else:
          output, result = subprocess.Popen(exe, shell=False, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()

        Logger.log("Error, if any: " + str(result))
        Logger.log("Lines returned is " + str(output))
        lines = output.split("\n")
        #Each line is: * 3: (Windows DirectSound) Primary Sound Driver (0/0)
        outputNumbers = []
        outputNames = []
        for line in lines:
          outputNumber = re.findall( r'[0-9]+', line )
          if len(outputNumber)>1:
            outputNumbers.append("-o" + outputNumber[0])
            outputNames.append(line)

        Logger.log("List of outputs is: " + str(outputNumbers) + str(outputNames))

        #present the audio output for user choice
        dialog = xbmcgui.Dialog()
        if outputNumbers != []:
            selected = dialog.select("Select your audio output", outputNames)
            if selected != -1:
               constants.__addon__.setSetting('outputsAuto', outputNumbers[selected])
        else:
            dialog.ok(constants.__addonname__, "No Audio Outputs Found! Check Log or squeezeslave -L output manually")


    ############################################################################
    #we're running the main script now...
    else:

      viewer=ReadMeViewer()

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
        #if they have used the audio output selector
        outputString = constants.__addon__.getSetting('outputsAuto')
        if outputString != "":
          args.append(outputString)
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

      #add a dummy track to the playlist - thanks to Mizaki for the examples!!
      #need to convert any stupid windows \\ paths to / paths
      jsonstr = '{"jsonrpc": "2.0", "method": "Playlist.Clear", "params": { "playlistid": 2 }, "id": 1}'
      sendXBMCJSON("Clear Audio Playlist", jsonstr)
      jsonstr = '{ "jsonrpc": "2.0", "method": "Playlist.Add", "params": { "item": {"file": "' + constants.DUMMYPIC + '"}, "playlistid": 2 }, "id": 2}'
      sendXBMCJSON("Add Dummy XSqueeze Track To Playlist", jsonstr)
      jsonstr = '{ "jsonrpc": "2.0", "method": "Playlist.Add", "params": { "item": {"file": "' + constants.DUMMYPIC + '"}, "playlistid": 2 }, "id": 3}'
      sendXBMCJSON("Add Dummy XSqueeze Track To Playlist", jsonstr)
      jsonstr = '{ "jsonrpc": "2.0", "method": "Playlist.Add", "params": { "item": {"file": "' + constants.DUMMYPIC + '"}, "playlistid": 2 }, "id": 4}'
      sendXBMCJSON("Add Dummy XSqueeze Track To Playlist", jsonstr)
      jsonstr = '{ "jsonrpc": "2.0", "method": "Playlist.Add", "params": { "item": {"file": "' + constants.DUMMYPIC  + '"}, "playlistid": 2 }, "id": 5}'
      sendXBMCJSON("Add Dummy XSqueeze Track To Playlist", jsonstr)
      jsonstr = '{"jsonrpc": "2.0", "method": "Player.Repeat", "params": { "playerid": 0, "state": "one" }, "id": 6}'
      sendXBMCJSON("Set Playlist To Plalist", jsonstr)

      jsonstr = '{ "jsonrpc": "2.0", "method": "JSONRPC.Introspect", "params": { "filter": { "id": "Playlist.Add", "type": "method" } }, "id": 7 }'
      sendXBMCJSON("Introspect", jsonstr)

       #and kick this bad boy off....
      window.doModal()

      ############################################################################
      # FINISHED - CLEAN UP!


##        #re-enable the screensaver as it was
##      if constants.DISABLESCREENSAVER:
##        Logger.log("Re-enabling screensaver")
##        xbmc.executehttpapi( "SetGUISetting(3,screensaver.mode,%s)" % screensaver )

##      #clear the playlist
##      jsonstr = '{"jsonrpc": "2.0", "method": "Playlist.Clear", "params": { "playlistid": 2 }, "id": 100}'
##      sendXBMCJSON("Clear Audio Playlist", jsonstr)

      #are we running the locally installed Squeezeslave? KILL IT!
      if constants.CONTROLSLAVE:
        Logger.log("Killing Squeezeslave process...")
        slaveProcess.terminate()

      # after the window is closed, Destroy it.
      del window

      #sys.modules.clear()
      Logger.log( "### Exiting XSqueeze..." )
