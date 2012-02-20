import xbmc
import xbmcaddon
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
#need to make sure this doesn't have \\ in it, in the case of windows
DUMMYAUDIO = xbmc.translatePath(os.path.join( AUDIO_PATH, "XSqueeze.mp3")).replace( "\\", "/" )
DUMMYVIDEO = xbmc.translatePath(os.path.join( VIDEO_PATH, "XSqueeze.mp4")).replace( "\\", "/" )
DUMMYPIC = xbmc.translatePath(os.path.join( IMAGES_PATH, "black.png")).replace( "\\", "/" )
#extend the python path
sys.path.append( LIB_PATH )
sys.path.append( CLASS_PATH )

################################################################################
#settings for the add on from xbmx settings page
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

SERVERIPPORT = SERVERIP + ":" + SERVERPORT
SERVERHTTPURL   = SERVERIP + ":9000"
#LMS is case sensitive and all MACs need to be lower case!!
PLAYERMAC   = str.lower(__addon__.getSetting('playerMAC'))
#things needed for the local squeezeslave if used
AUDIOOUTPUT = __addon__.getSetting('outputsAuto')

SLAVEARGS = __addon__.getSetting('slaveargs')
if __addon__.getSetting('controlslave')=="true":
  CONTROLSLAVE = True
else:
  CONTROLSLAVE = False
if __addon__.getSetting('linux')=="true":
  ISLINUX = True
else:
  ISLINUX = False
#other settings
if __addon__.getSetting('disablescreensaver')=="true":
  DISABLESCREENSAVER = True
else:
  DISABLESCREENSAVER = False
#work out what skin xml to load
enumVal=__addon__.getSetting('skin')
#print("********* enumVal" + enumVal)
if enumVal=='1' or enumVal=='01':
  SKIN="AeonNox"
else:
  #default to Confluence
  SKIN="Confluence"

################################################################################

LOCALSQUEEZESLAVEVERSION = 'squeezeslave-1.2-311'
BINWIN    = xbmc.translatePath(os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-win") + "//squeezeslave.exe")
BINOSX    = xbmc.translatePath(os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-osx") + "//squeezeslave")
BINLIN32  = xbmc.translatePath(os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-lnx26") + "//squeezeslave")
BINLIN64  = xbmc.translatePath(os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-lnx26") + "//squeezeslave-i64")

#32 or 64 bit?
is_64bits = sys.maxsize > 2**32

#need to work out what system we're on
SYSTEM=""

#this fails on Linux it seems...
try:
  #will return Windows or Darwin
  SYSTEM = platform.system()
except:
  #must be some linux flavour...
  SYSTEM = "Linux"

#choose the right executable
if SYSTEM=="Windows":
  EXE = [BINWIN]
elif SYSTEM=="Darwin":
  EXE = [BINOSX]
elif SYSTEM=="Linux":
  if is_64bits:
    EXE = [BINLIN64]
  else:
    EXE = [BINLIN32]
  try:
    #attempt to make the binary executable - this never works really...
    os.chmod(0775, EXE[0])
  except:
    Logger.log("Couldn't chmod +x binaries - hopefully user has done this manually!")
else:
  Logger.log("Something went wrong trying to determine the underlying OS")
  xbmc.executebuiltin("XBMC.Notification("+ __addonname__ +": Error determing OS type,Squeezeslave probably won't work...)")


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

