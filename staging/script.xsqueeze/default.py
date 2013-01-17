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
import shutil

#Import the common code - basically the SqueezePlayer class
#which connects to the server and a player
from b808common import *
from XSqueezeCommon import *

#an orderly place to keep XSqueeze specific constants
import constants

#the window for the README
from ReadMeViewer import *

#the window class
from NowPlayingWindow import *

################################################################################
# Do some cleanup (even if we are exiting early)

def cleanup(andexit=False):

    global xbmcAudioSuspended

    log("### Doing Cleanup")

    #Try and resume XBMC's AudioEngine if we suspended it
    if xbmcAudioSuspended:
      try:
        xbmc.audioResume();
        log("### Resumed XBMC AE")
      except:
        pass

    #remove our custom keymap and force a re-load
    try:
      os.remove(constants.KEYMAPDESTFILE)
      xbmc.executebuiltin('Action(reloadkeymaps)')
      log("### Removed custom keymap")
    except Exception as inst:
      pass

    #and exit if requested
    if andexit:
      footprints(startup=False)
      sys.exit()


#called if we are running a playing instance...
def playInit():

    global xbmcAudioSuspended

    xbmcAudioSuspended = False
    #Try and suspend XBMC's AudioEngine if it is present and has exclusive access to the audio device
    try:
      xbmc.audioSuspend();
      log("Suspended XBMC AE")
      xbmcAudioSuspended = True
    except Exception as inst:
      log("Unable to suspend XBMC AE: " + str(inst))
      pass

################################################################################
### MAIN

if ( __name__ == "__main__" ):

    #log some tracks...
    footprints()

    #set up for actual playback - suspend AE as it an hog the audio device
    xbmcAudioSuspended = False
    playInit()

    #is the add on configured yet?
    if constants.SERVERIP=="":

      #open the settings dialogue
      notify(LANGUAGE(19626), LANGUAGE(19631))
      constants.ADDON.openSettings()
      notify(LANGUAGE(19632),LANGUAGE(19633))
      cleanup(andexit=True)

    #possibly display the readme file if this is the users' first run of this version
    #not localized!
    #then exit so they have a chance to re-visit their settings.
    if constants.ISFIRSTRUN:
      viewer=ReadMeViewer()
      #pass
    else:

      #serverIP still null, something went wrong...
      if constants.SERVERIP=="":
        notify(LANGUAGE(19624),LANGUAGE(19625))
        cleanup(andexit=True)

      #load our custom keymap to make sure that volume/skip track keys don't raise annoying xbmc messages
      #needed because xbmc addons can't swallow events
      #Each run we copy our keymap over, force xbmc to relaoad the keymaps, then at the end
      #we do the reverse - delete our custom one and reload the original setup
      try:
        shutil.copy(constants.KEYMAPSOURCEFILE, constants.KEYMAPDESTFILE)
        xbmc.executebuiltin('Action(reloadkeymaps)')
        log("Installed custom keymap")
      except Exception as inst:
        log("Error - couldn't copy & load custom keymap: " + str(inst))

      #are we running the locally installed Squeezeslave?
      if constants.PLAYBACK:
        notify(LANGUAGE(19608),LANGUAGE(19609))
        log("Starting local player [" + constants.PLAYERTYPE +"], system is [" + constants.SYSTEM + "]")

        #builds the list ['/path/exefile','-arg1','-arg2',...]
        exe = constants.EXE
        args = constants.PLAYERARGS

        args.append(constants.SERVERIP)
        exe.extend(args)

        log ("Attempting to start player: " + str(exe))
        log ("Path is: " + str(sys.path))

        try:
          #need this to stop windows opening a console window
          if constants.SYSTEM.startswith("win"):
            #for debugging, grab the process output....
            #output, result = subprocess.Popen(exe, creationflags=0x08000000, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=False).communicate()
            #log("$$$$$$$$$$$$$$$ " + str(output))
            #log("$$$$$$$$$$$$$$$ " + str(result))
            slaveProcess = subprocess.Popen(exe, creationflags=0x08000000, shell=False)
          else:
            slaveProcess = subprocess.Popen(exe, shell=False)
        except Exception as inst:
          log("Failed creating player process", inst)
          notify(LANGUAGE(19610),LANGUAGE(19611))
          cleanup(andexit=True)

        pid = slaveProcess.pid
        log("Process ID for player is "+ str(pid))
        #little pause to give player time to run & connect
        time.sleep(2)

      ##########################################################################
      # SETUP DONE > ON WITH THE SHOW

      #now let's make a window and see if we can send some commands...
      #check what skin to use
      if constants.TOUCHENABLED:
        window = NowPlayingWindow("XSqueezeNowPlayingTouch.xml",CWD,"Default")
      else:
        window = NowPlayingWindow("XSqueezeNowPlaying.xml",CWD,"Default")

       #and kick this bad boy off....
      window.doModal()

      ############################################################################
      # FINISHED - CLEAN UP!

      #are we running the locally installed Squeezeslave? KILL IT!
      if constants.PLAYBACK:
        log("Killing player process...")
        try:
          slaveProcess.terminate()
        except Exception as inst:
          log("Error killing player: ", str(inst))


      # after the window is closed, Destroy it.
      del window

      cleanup(andexit=True)

