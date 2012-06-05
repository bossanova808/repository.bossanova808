import xbmc
import xbmcaddon
import xbmcvfs
import os
import sys
import platform
import stat

#Import the common code - basically the SqueezePlayer class
#which connects to the server and a player
from XSqueezeCommon import *

################################################################################
#window control IDS - see XSqueezeNowPlaying.xml for matching controls
# only progress bar is referred to directly, the rest is put into $INFO

MAINCOVERART          = 100
UPCOMING1COVERART     = 101
UPCOMING2COVERART     = 102
UPCOMING3COVERART     = 103
PLAYSTATE             = 104
SLIDESHOW             = 105
CURRENTTITLE          = 200
CURRENTARTIST         = 201
CURRENTALBUM          = 202
CURRENTPROGRESS       = 998
CURRENTELAPSED        = 204
CURRENTREMAINING      = 205
CURRENTLENGTH         = 206
DISPLAYLINE1          = 1000
DISPLAYLINE2          = 1001
UPCOMING1             = 2001
UPCOMING2             = 2002
UPCOMING3             = 2003

################################################################################
#useful paths
CLASS_PATH = xbmc.translatePath(os.path.join ( LIB_PATH, "classes" ))
BIN_PATH = xbmc.translatePath(os.path.join( RESOURCES_PATH, "bin" ))
AUDIO_PATH = xbmc.translatePath(os.path.join( RESOURCES_PATH, "audio" ))
VIDEO_PATH = xbmc.translatePath(os.path.join( RESOURCES_PATH, "video" ))
IMAGES_PATH = xbmc.translatePath( os.path.join( RESOURCES_PATH, 'images' ))
ADDON_DATA_PATH = xbmc.translatePath("special://userdata/addon_data/script.xsqueeze/")
RUNTOKEN_PATH = xbmc.translatePath("special://userdata/addon_data/script.xsqueeze/runtokens/")
#need to make sure this doesn't have \\ in it, in the case of windows
DUMMYAUDIO = xbmc.translatePath(os.path.join( AUDIO_PATH, "XSqueeze.mp3")).replace( "\\", "/" )
DUMMYVIDEO = xbmc.translatePath(os.path.join( VIDEO_PATH, "XSqueeze.mp4")).replace( "\\", "/" )
DUMMYPIC = xbmc.translatePath(os.path.join( IMAGES_PATH, "black.png")).replace( "\\", "/" )
#extend the python path
sys.path.append( CLASS_PATH )

################################################################################
# first run stuff - set once here, then a constant

ISFIRSTRUN=True
#set a runtoken only if we are running the __main__ not the server discovery etc.
if len(sys.argv) == 1:
  runtoken = os.path.join(RUNTOKEN_PATH, "runtoken" + VERSION)
  if not xbmcvfs.exists(runtoken):
    if not xbmcvfs.exists(ADDON_DATA_PATH):
      xbmcvfs.mkdir(ADDON_DATA_PATH)
    if not xbmcvfs.exists(RUNTOKEN_PATH):
      xbmcvfs.mkdir(RUNTOKEN_PATH)
    ISFIRSTRUN=True
    token = open(runtoken, 'w')
    token.close()
  else:
    ISFIRSTRUN=False

################################################################################
# LOCAL PLAYBACK SETTINGS
# LMS is case sensitive and all MACs need to be lower case!!

#are we controlling the local slave or another external player?
if ADDON.getSetting('controlSlave')=="true":
  CONTROLSLAVE = True
else:
  CONTROLSLAVE = False

if ADDON.getSetting('controllerOnly')=="true":
  CONTROLLERONLY = True
else:
  CONTROLLERONLY = False

# we either get the MAC from the local player setup, or from the controller setup
if CONTROLSLAVE:
  PLAYERMAC   = str.lower(ADDON.getSetting('slaveMAC'))
if CONTROLLERONLY:
  PLAYERMAC   = str.lower(ADDON.getSetting('controllerMAC'))

# have they manually specified an audio output
AUDIOOUTPUT = ADDON.getSetting('audioOutput')

if AUDIOOUTPUT != "Auto" and AUDIOOUTPUT !="":
  MANUALAUDIOOUTPUT = True
else:
  MANUALAUDIOOUTPUT = False

#any extra squeezeslave arguments supplied for special needs?
SLAVEARGS = []
SLAVEARGS.append("-m" + PLAYERMAC)
tempargs = ADDON.getSetting('slaveArgs').split(" ")
if tempargs[0] != '':
  SLAVEARGS.extend(tempargs)

################################################################################
#OTHER SETTINGS

if ADDON.getSetting('disablescreensaver')=="true":
  DISABLESCREENSAVER = True
else:
  DISABLESCREENSAVER = False

#work out what skin xml to load
SKIN=ADDON.getSetting('skin')

################################################################################
# Deal with the squeezeslave executeables...

LOCALSQUEEZESLAVEVERSION = 'squeezeslave-1.2-311'
BINWIN    = xbmc.translatePath(os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-win") + "/squeezeslave.exe")
BINOSX    = xbmc.translatePath(os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-osx") + "/squeezeslave")
BINLIN32  = xbmc.translatePath(os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-lnx26") + "/squeezeslave")
BINLIN64  = xbmc.translatePath(os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-lnx26") + "/squeezeslave-i64")

#32 or 64 bit?
is_64bits = sys.maxsize > 2**32

##System.Platform.Linux Returns true if XBMC is running on a linux/unix/osx based computer.
##System.Platform.Windows Returns true if XBMC is running on a windows based computer.
##System.Platform.OSX Returns true if XBMC is running on an OSX based computer.
##System.Platform.IOS Returns true if XBMC is running on an IOS device.
##System.Platform.ATV2 Returns true if XBMC is running on an atv2.

#need to work out what system we're on
SYSTEM="linux"

if xbmc.getCondVisibility( "System.Platform.OSX" ):
  SYSTEM = "darwin"
elif xbmc.getCondVisibility( "System.Platform.IOS" ):
  SYSTEM = "ios"
elif xbmc.getCondVisibility( "System.Platform.ATV2" ):
  SYSTEM = "atv2"
elif xbmc.getCondVisibility( "System.Platform.Windows" ):
  SYSTEM = "windows"

#log the system
xbmc.log(ADDONNAME + "-" + VERSION + ": ### sys.platform is " + SYSTEM)

#and define the capabilities of each system - systems not in this list are only usable as a controller, no local playback
LOCALPLAYBACKCAPABLE = ["linux","darwin","windows"]

#choose the right executable
if SYSTEM.startswith("win"):
  EXE = [BINWIN]
elif SYSTEM.startswith("darwin"):
  EXE = [BINOSX]
else:
  if is_64bits:
    EXE = [BINLIN64]
  else:
    EXE = [BINLIN32]

#chmod +X the exe file on linux/osx ...

if SYSTEM.startswith("lin"):
  try:
    os.system("chmod a+x " + EXE[0])
    xbmc.log(ADDONNAME + "-" + VERSION + ": ### (linux) chmod +x the Squeezeslave binaries - success")
  except:
    xbmc.log(ADDONNAME + "-" + VERSION + ": ### chmod +x the Squeezeslave binaries - failure -> You must do this manually!!")
elif SYSTEM.startswith("darwin"):
  try:
    os.chmod(EXE[0], stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    xbmc.log(ADDONNAME + "-" + VERSION + ": ### (OSX) chmod +x the Squeezeslave binaries - success")
  except:
    xbmc.log(ADDONNAME + "-" + VERSION + ": ### chmod +x the Squeezeslave binaries - failure -> You must do this manually!!")
else:
  xbmc.log(ADDONNAME + "-" + VERSION + ": ### Windows or ATV/IOS, so no need to chmod the binaries.")


