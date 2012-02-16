import xbmc
import xbmcaddon
import os
import sys

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
RESOURCES_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources' ) )
LIB_PATH = os.path.join( RESOURCES_PATH, "lib")
CLASS_PATH = os.path.join (LIB_PATH, "classes")
BIN_PATH = os.path.join( RESOURCES_PATH, "bin")
STATIC_IMAGES_PATH = xbmc.translatePath( os.path.join( RESOURCES_PATH, 'images' ) )
CHANGING_IMAGES_PATH = xbmc.translatePath("special://profile/addon_data/script.xsqueeze/current_images/");
#extend the python path
sys.path.append( LIB_PATH )
sys.path.append( CLASS_PATH )

################################################################################
#settings for the add on from xbmx settings page
SERVERIP    = __addon__.getSetting('serverIP')
SERVERPORT  = __addon__.getSetting('serverPort')
SERVERIPPORT = SERVERIP + ":" + SERVERPORT
SERVERHTTPURL   = SERVERIP + ":9000"
#LMS is case sensitive and all MACs need to be lower case!!
PLAYERMAC   = str.lower(__addon__.getSetting('playerMAC'))
CONTROLSLAVE = __addon__.getSetting('controlslave')
SLAVEARGS = __addon__.getSetting('slaveargs')

################################################################################

LOCALSQUEEZESLAVEVERSION = 'squeezeslave-1.2-311'
BINWIN    = os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-win") + "\\squeezeslave.exe"
BINOSX    = os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-osx") + "\\squeezeslave"
BINLIN32  = os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-lnx26") + "\\squeezeslave"
BINLIN64  = os.path.join( BIN_PATH, LOCALSQUEEZESLAVEVERSION + "-win") + "\\squeezeslave-i64"

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

