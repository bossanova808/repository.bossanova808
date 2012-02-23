import xbmc
import xbmcaddon
import xbmcvfs
import os
import sys
import platform


################################################################################
# CONSTANTS FOR XSQUEEZE

################################################################################
#create an add on instation and store the reference
__addon__       = xbmcaddon.Addon()
#store some handy constants
__addonname__   = __addon__.getAddonInfo('name')
__addonid__     = __addon__.getAddonInfo('id')
__author__      = __addon__.getAddonInfo('author')
__version__     = __addon__.getAddonInfo('version')
__cwd__         = __addon__.getAddonInfo('path')
__language__    = __addon__.getLocalizedString
__useragent__   = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.6"

################################################################################
#useful paths
SOURCEPATH = __cwd__
RESOURCES_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources' ))
LIB_PATH = xbmc.translatePath(os.path.join( RESOURCES_PATH, "lib"))
CLASS_PATH = xbmc.translatePath(os.path.join (LIB_PATH, "classes"))
BIN_PATH = xbmc.translatePath(os.path.join( RESOURCES_PATH, "bin"))
AUDIO_PATH = xbmc.translatePath(os.path.join( RESOURCES_PATH, "audio"))
VIDEO_PATH = xbmc.translatePath(os.path.join( RESOURCES_PATH, "video"))
IMAGES_PATH = xbmc.translatePath( os.path.join( RESOURCES_PATH, 'images' ))
ADDON_DATA_PATH = xbmc.translatePath("special://userdata/addon_data/script.xsqueeze/")
RUNTOKEN_PATH = xbmc.translatePath("special://userdata/addon_data/script.xsqueeze/runtokens/")
#need to make sure this doesn't have \\ in it, in the case of windows
DUMMYAUDIO = xbmc.translatePath(os.path.join( AUDIO_PATH, "XSqueeze.mp3")).replace( "\\", "/" )
DUMMYVIDEO = xbmc.translatePath(os.path.join( VIDEO_PATH, "XSqueeze.mp4")).replace( "\\", "/" )
DUMMYPIC = xbmc.translatePath(os.path.join( IMAGES_PATH, "black.png")).replace( "\\", "/" )
#extend the python path
sys.path.append( LIB_PATH )
sys.path.append( CLASS_PATH )

################################################################################
# first run stuff
ISFIRSTRUN=True
#set a runtoken only if we are running the __main__ not the server discovery etc.
if len(sys.argv) == 1:
  runtoken = os.path.join(RUNTOKEN_PATH, "runtoken" + __version__)
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
#settings for the add on from xbmx settings page

# LMS SERVER SETTINGS
#The LMS Server and port - either discovered in the add on settings
# or manually set
if __addon__.getSetting('serverManual')=="true":
  MANUALSERVER = True
else:
  MANUALSERVER = False

if MANUALSERVER:
  SERVERIP    = __addon__.getSetting('serverIP')
  SERVERNAME = SERVERIP
  SERVERPORT  = __addon__.getSetting('serverPort')
else:
  SERVERIP = __addon__.getSetting('autoserverip')
  SERVERNAME = __addon__.getSetting('autoservername')
  SERVERPORT = '9090'

#shorthand for the full server string, so e.g. 192.168.1.1:9090
SERVERIPPORT = SERVERIP + ":" + SERVERPORT
#url of the http interface for LMS
SERVERHTTPURL   = SERVERIP + ":" + __addon__.getSetting('serverHTTPPort')

#LOCAL PLAYBACK SETTINGS
#LMS is case sensitive and all MACs need to be lower case!!

#are we controlling the local slave or another external player?
if __addon__.getSetting('controlSlave')=="true":
  CONTROLSLAVE = True
else:
  CONTROLSLAVE = False

if __addon__.getSetting('controllerOnly')=="true":
  CONTROLLERONLY = True
else:
  CONTROLLERONLY = False


# we either get the MAC from the local player setup, or from the controller setup

if CONTROLSLAVE:
  PLAYERMAC   = str.lower(__addon__.getSetting('slaveMAC'))
if CONTROLLERONLY:
  PLAYERMAC   = str.lower(__addon__.getSetting('controllerMAC'))

# have they manually specified an audio output
if __addon__.getSetting('manualAudioOutput')=="true":
  MANUALAUDIOOUTPUT = True
  AUDIOOUTPUT = __addon__.getSetting('outputsAuto')
else:
  MANUALAUDIOOUTPUT = False

#any extra squeezeslave arguments supplied for special needs?
SLAVEARGS = []
SLAVEARGS.append("-m" + PLAYERMAC)
tempargs = __addon__.getSetting('slaveargs').split(" ")
if tempargs[0] != '':
  SLAVEARGS.extend(tempargs)


#OTHER SETTINGS
if __addon__.getSetting('disablescreensaver')=="true":
  DISABLESCREENSAVER = True
else:
  DISABLESCREENSAVER = False

#work out what skin xml to load
SKIN=__addon__.getSetting('skin')


################################################################################

LOCALSQUEEZESLAVEVERSION = 'squeezeslave-1.2-311'
BINWIN    = xbmc.translatePath(os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-win") + "//squeezeslave.exe")
BINOSX    = xbmc.translatePath(os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-osx") + "//squeezeslave")
BINLIN32  = xbmc.translatePath(os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-lnx26") + "//squeezeslave")
BINLIN64  = xbmc.translatePath(os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-lnx26") + "//squeezeslave-i64")

#need to work out what system we're on
SYSTEM=""

try:
  #will return Windows or Darwin
  SYSTEM = platform.system()
except:
  #otherwise we assume some linux 2.6+ flavour...
  SYSTEM = "Linux"

#32 or 64 bit?
is_64bits = sys.maxsize > 2**32

#choose the right executable
if SYSTEM=="Windows":
  EXE = [BINWIN]
elif SYSTEM=="Darwin":
  EXE = [BINOSX]
else:
  if is_64bits:
    EXE = [BINLIN64]
  else:
    EXE = [BINLIN32]

#chmod +X the exe file...
if SYSTEM=="Darwin" or SYSTEM=="Linux":
  try:
    #attempt to make the binary executable - this never works really...
    #it's really about triggering the messages in the except clause below...
    os.system("chmod a+x " + EXE[0])
    xbmc.log(__addonname__ + __version__ +": chmod +x the Squeezeslave binaries - success")
  except:
    xbmc.log(__addonname__ + __version__ +": chmod +x the Squeezeslave binaries - failure -> You must do this manually!!")
    #Logger.notify("Failed to chmod +x the binaries" "Please do so manually - most likely a user permissions error", 10000)

################################################################################
#window control IDS - see XSqueezeNowPlaying.xml for matching controls
# only progress bar is referred to directly, the rest is put into $INFO

MAINCOVERART          = 100
UPCOMING1COVERART     = 101
UPCOMING2COVERART     = 102
UPCOMING3COVERART     = 103
CURRENTTITLE          = 200
CURRENTARTIST         = 201
CURRENTALBUM          = 202
CURRENTPROGRESS       = 203
CURRENTELAPSED        = 204
CURRENTREMAINING      = 205
CURRENTLENGTH         = 206
UPCOMING1             = 2001
UPCOMING2             = 2002
UPCOMING3             = 2003
DISPLAYLINE1          = 1000
DISPLAYLINE2          = 1001

