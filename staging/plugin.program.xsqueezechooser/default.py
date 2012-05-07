import xbmc
import xbmcaddon
import xbmcplugin
import xbmcvfs
import xbmcgui
from traceback import print_exc


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


def buildRootListing():

  listing = []
  listing.append(["New Music","albums 0 9 sort:new"])
  listing.append(["Albums",""])
  listing.append(["Artists",""])
  listing.append(["Radio",""])
  
  return listing
  
def showRootListing(listing):
  
  for item in listing:
    listItem = xbmcgui.ListItem(item)
    xbmcplugin.addDirectoryItem(thisPlugin,listItem[1],listItem[0], True)
    
  xbmcplugin.endOfDirectory(thisPlugin)




################################################################################   
# BEGIN !
################################################################################

if ( __name__ == "__main__" ):
    try:
      showRootListing(buildRootListing())
    except:
        print_exc()
