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

#Import the common code - basically the SqueezePlayer class
#which connects to the server and a player
from XSqueezeCommon import *

#an orderly place to keep XSqueeze specific constants
import constants

#the window for the README
from ReadMeViewer import *

#the window class
from NowPlayingWindow import *


################################################################################
# Server Discovery function - can be called from add on settings, or can just auto-default to
# first server found if callede from main() as the user had not configured a server

def serverDiscovery(defaultFirstServer=False):

    foundServer = False


    #return a boolen of success or failure
    return foundServer

################################################################################
### MAIN

if ( __name__ == "__main__" ):

    #log some tracks...
    footprints()

    #the script is being called with an argument - we're either
    # auto discovering servers and choosing them
    #or
    # choosing an audio output

    if len(sys.argv) > 1:

      ##########################################################################
      ### SERVER DISCOVERY

      if sys.argv[1].startswith('ServerDiscovery'):

        log("Doing server discovery...")
        exe = constants.EXE
        exe.append("-I")

        #need this to stop windows opening a console window & grab output
        log("Calling SqueezeSlave for server discovery..." + str(exe))

        if constants.SYSTEM.startswith("win"):
          output, result = subprocess.Popen(exe, creationflags=0x08000000, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=False).communicate()
        else:
          output, result = subprocess.Popen(exe, shell=False, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()

        log("Error, if any: " + str(result))
        log("Lines returned is " + str(output))
        lines = output.split("\n")
        #Each line is: My Music Library Name:9000 (192.168.1.1)

        names = []
        ips = []

        for line in lines:
          ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line )
          if len(ip) > 0:
            log("Parsing line " + line)
            #this will fail if they have a colon in their name - fuck 'em for using a stupid name
            names.append(line.split(":")[0])
            ips.append(ip[0])

        log("List of servers is " + str(names) + str(ips))

        #are we being run from settings as normal?
        if not defaultFirstServer:

            #now get them to choose an actual location
            #present the server names for user choice
            dialog = xbmcgui.Dialog()
            if names != []:
                selected = dialog.select(LANGUAGE(19601), names)
                if selected != -1:
                    ADDON.setSetting('autoserverip', ips[selected])
                    ADDON.setSetting('autoservername', names[selected])
            else:
                dialog.ok(ADDONNAME, LANGUAGE(19602))

        #being run from main (user has not configured add on) so default to the first server found...
        else:
          notify("Auto discovering your LMS server","Found: " + names[0] + " IP: " + ips[0])
          ADDON.setSetting('autoserverip', ips[0])
          ADDON.setSetting('autoservername', names[0])
          constants.SERVERIP = ips[0]
          constants.SERVERNAME = names[0]
          constants.SERVERPORT = '9090'
          constants.SERVERUSER  = ''
          constants.SERVERPASS  = ''


      ##########################################################################
      ### AUDIO OUTPUTS

      elif sys.argv[1].startswith('AudioOutputs'):

        log("Doing audio output discovery...")
        exe = constants.EXE
        exe.append("-L")

        #need this to stop windows opening a console window & grab output
        log("Calling SqueezeSlave for server discovery..." + str(exe))

        if constants.SYSTEM.startswith("win"):
          output, result = subprocess.Popen(exe, creationflags=0x08000000, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=False).communicate()
        else:
          output, result = subprocess.Popen(exe, shell=False, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()

        log("Error, if any: " + str(result))
        log("Lines returned is " + str(output))
        lines = output.split("\n")
        #Each line is: * 3: (Windows DirectSound) Primary Sound Driver (0/0)
        outputNumbers = ["Auto"]
        outputNames = ["Auto"]
        for line in lines:
          outputNumber = re.findall( r'[0-9]+', line )
          if len(outputNumber)>1:
            outputNumbers.append("-o" + outputNumber[0])
            outputNames.append(line)

        log("List of outputs is: " + str(outputNumbers) + str(outputNames))

        #present the audio output for user choice
        dialog = xbmcgui.Dialog()
        if outputNumbers != []:
            selected = dialog.select(LANGUAGE(19603), outputNames)
            if selected != -1:
               ADDON.setSetting('audioOutput', outputNumbers[selected])
        else:
            dialog.ok(ADDONNAME, LANGUAGE(19604))


    ############################################################################
    ### MAIN

    else:

      #is the add on configured yet?
      if constants.SERVERIP=="":

        #open the settings dialogue
        notify("No LMS server set in XSqueeze settings...", "Please configure XSqueeze before use")
        constants.ADDON.openSettings()
        sys.exit()

      #sanity checks
      if constants.CONTROLLERONLY and constants.CONTROLSLAVE:
        notify(LANGUAGE(19605), LANGUAGE(19606), 10000)
        sys.exit()
      if not constants.CONTROLLERONLY and not constants.CONTROLSLAVE:
        notify(LANGUAGE(19605), LANGUAGE(19607), 10000)
        sys.exit()

      #display the readme file if this is the users' first run of this version
      #not localized!
      #then exit so they have a chance to re-visit their settings.
      if constants.ISFIRSTRUN:
        viewer=ReadMeViewer()

      else:


##          log("SERVERIP is null, doing auto server discovery and defaulting to first server found")
##          #no serverIP, user has run XSqueeze without configuring add on
##          #so call server discovery and default to first server found,
##          #display message about this
##          notify(LANGUAGE(19626),LANGUAGE(19627))
##          foundServer=serverDiscovery(True)
##          if foundServer:
##            notify(LANGUAGE(19628),LANGUAGE(19629))
##          else:
##            notify(LANGUAGE(19630),LANGUAGE(19629))
##          #and exit, user must re-run XSqueeze
##          sys.exit()

        #serverIP still null, something went wrong...
        if constants.SERVERIP=="":
          notify(LANGUAGE(19624),LANGUAGE(19625))
          sys.exit()

        #disable the screensaver if the user has this on
        if constants.DISABLESCREENSAVER:
          log("Disabling screensaver")
          screensaver = xbmc.executehttpapi( "GetGUISetting(3;screensaver.mode)" ).replace( "<li>", "" )
          xbmc.executehttpapi( "SetGUISetting(3,screensaver.mode,None)" )

        #are we running the locally installed Squeezeslave?
        if constants.CONTROLSLAVE and not constants.CONTROLLERONLY:
          notify(LANGUAGE(19608),LANGUAGE(19609))
          log("Starting local Squeezeslave, system is " + constants.SYSTEM)

          #builds the list ['/path/exefile','-arg1','-arg2',...]
          exe = constants.EXE

          args = constants.SLAVEARGS

          #if they have used the audio output selector
          if constants.MANUALAUDIOOUTPUT:
            args.append(constants.AUDIOOUTPUT)



          args.append(constants.SERVERIP)
          exe.extend(args)

          log ("Attempting to start Squeezelave: " + str(exe))
          try:
            #need this to stop windows opening a console window
            if constants.SYSTEM.startswith("win"):
              slaveProcess = subprocess.Popen(exe, creationflags=0x08000000, shell=False)
            else:
              slaveProcess = subprocess.Popen(exe, shell=False)
          except Exception as inst:
            log("Failed creating squeezeslave process", inst)
            notify(LANGUAGE(19610),LANGUAGE(19611))
            sys.exit()

          pid = slaveProcess.pid
          log("Process ID for Squeezeslave is "+ str(pid))
          #little pause to give squeezeslave time to run & connect
          time.sleep(5)

        ##########################################################################
        # SETUP DONE > ON WITH THE SHOW

        #now let's make a window and see if we can send some commands...
        #check what skin to use
        window = NowPlayingWindow("XSqueezeNowPlaying.xml",CWD,"Default")

  ##      #add a dummy track to the playlist - thanks to Mizaki for the examples!!
  ##      #need to convert any stupid windows \\ paths to / paths
  ##      jsonstr = '{"jsonrpc": "2.0", "method": "Playlist.Clear", "params": { "playlistid": 2 }, "id": 1}'
  ##      sendXBMCJSON("Clear Audio Playlist", jsonstr)
  ##      jsonstr = '{ "jsonrpc": "2.0", "method": "Playlist.Add", "params": { "item": {"file": "' + constants.DUMMYPIC + '"}, "playlistid": 2 }, "id": 2}'
  ##      sendXBMCJSON("Add Dummy XSqueeze Track To Playlist", jsonstr)
  ##      jsonstr = '{ "jsonrpc": "2.0", "method": "Playlist.Add", "params": { "item": {"file": "' + constants.DUMMYPIC + '"}, "playlistid": 2 }, "id": 3}'
  ##      sendXBMCJSON("Add Dummy XSqueeze Track To Playlist", jsonstr)
  ##      jsonstr = '{ "jsonrpc": "2.0", "method": "Playlist.Add", "params": { "item": {"file": "' + constants.DUMMYPIC + '"}, "playlistid": 2 }, "id": 4}'
  ##      sendXBMCJSON("Add Dummy XSqueeze Track To Playlist", jsonstr)
  ##      jsonstr = '{ "jsonrpc": "2.0", "method": "Playlist.Add", "params": { "item": {"file": "' + constants.DUMMYPIC  + '"}, "playlistid": 2 }, "id": 5}'
  ##      sendXBMCJSON("Add Dummy XSqueeze Track To Playlist", jsonstr)
  ##      jsonstr = '{"jsonrpc": "2.0", "method": "Player.Repeat", "params": { "playerid": 0, "state": "one" }, "id": 6}'
  ##      sendXBMCJSON("Set Playlist To Plalist", jsonstr)
  ##      jsonstr = '{ "jsonrpc": "2.0", "method": "JSONRPC.Introspect", "params": { "filter": { "id": "Playlist.Add", "type": "method" } }, "id": 7 }'
  ##      sendXBMCJSON("Introspect", jsonstr)

         #and kick this bad boy off....
        window.doModal()

        ############################################################################
        # FINISHED - CLEAN UP!


        #re-enable the screensaver as it was
        #this tends to cause hangs...
        if constants.DISABLESCREENSAVER:
          log("Re-enabling screensaver")
          xbmc.executehttpapi( "SetGUISetting(3,screensaver.mode,%s)" % screensaver )

  ##      #clear the playlist
  ##      jsonstr = '{"jsonrpc": "2.0", "method": "Playlist.Clear", "params": { "playlistid": 2 }, "id": 100}'
  ##      sendXBMCJSON("Clear Audio Playlist", jsonstr)

        #are we running the locally installed Squeezeslave? KILL IT!
        if constants.CONTROLSLAVE and not constants.CONTROLLERONLY:
          log("Killing Squeezeslave process...")
          try:
            slaveProcess.terminate()
          except Exception as inst:
            log("Error killing Squeezeslave", inst)

        # after the window is closed, Destroy it.
        del window

        #sys.modules.clear()
        footprints(startup=False)
