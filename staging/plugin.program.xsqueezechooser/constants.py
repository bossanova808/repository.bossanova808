import xbmc
import xbmcaddon
import xbmcplugin
import xbmcvfs
import xbmcgui

from traceback import print_exc
import sys, os

################################################################################
# CONSTANTS & SETTINGS STUFF FOR XSQUEEZE

################################################################################
#create an add on instation and store the reference
__addon__       = xbmcaddon.Addon()
thisPlugin = int(sys.argv[1])

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
LIB_PATH = xbmc.translatePath(os.path.join( RESOURCES_PATH, "lib" ))
CLASS_PATH = xbmc.translatePath(os.path.join ( LIB_PATH, "classes" ))

sys.path.append( LIB_PATH )
sys.path.append( CLASS_PATH )


