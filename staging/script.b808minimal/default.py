import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
from TestWindow import *


#create an add on instation and store the reference
ADDON       = xbmcaddon.Addon()

#if we've been imported from the plugin we need the magic ID
if 'plugin' in sys.argv[0]:
  THIS_PLUGIN = int(sys.argv[1])

#used to get settings from the main addon
THIS_REF = xbmcaddon.Addon(id='script.b808minimal')

#store some handy constants
ADDONNAME   = ADDON.getAddonInfo('name')
ADDONID     = ADDON.getAddonInfo('id')
AUTHOR      = ADDON.getAddonInfo('author')
VERSION     = ADDON.getAddonInfo('version')
CWD         = ADDON.getAddonInfo('path')
LANGUAGE    = ADDON.getLocalizedString
USERAGENT   = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.6"

if ( __name__ == "__main__" ):

        window = TestWindow("TestWindow.xml",CWD,"Default")
        
        #and kick this bad boy off....
        window.doModal()

        # after the window is closed, Destroy it.
        del window

 