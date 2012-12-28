import xbmc
import xbmcaddon
import xbmcplugin
import xbmcvfs
import xbmcgui
import urllib
from traceback import print_exc

# magic; id of this plugin - cast to integer
if 'plugin' in sys.argv[0]:
  THIS_PLUGIN = int(sys.argv[1])

print(str(sys.argv))

# Step 2 - create the support functions (or classes)
def createListing():
    """
    Creates a listing that XBMC can display as a directory listing
    @return list
    """
    listing = []
    listing.append('The first item')
    listing.append('The second item')
    listing.append('The third item')
    listing.append('The fourth item')
    return listing

def sendToXbmc(listing):
    """
    Sends a listing to XBMC for display as a directory listing
    Plugins always result in a listing
    @param list listing
    @return void
    """
    #access global plugin id
    global THIS_PLUGIN
    # send each item to xbmc
    for item in listing:
        listItem = xbmcgui.ListItem(item)
        xbmcplugin.addDirectoryItem(THIS_PLUGIN,'',listItem)
    # tell xbmc we have finished creating the directory listing
    xbmcplugin.endOfDirectory(THIS_PLUGIN)

# Step 3 - run the program
sendToXbmc(createListing())