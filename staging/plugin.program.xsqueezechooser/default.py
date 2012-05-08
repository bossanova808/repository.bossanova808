import xbmc
import xbmcaddon
import xbmcplugin
import xbmcvfs
import xbmcgui

import urllib
from traceback import print_exc

from XSqueezeCommon import *

def connectLMS():
  pass


def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]
        return param


def addNode(name, url, mode, iconimage):

        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)

        is_ok=True

        listItem=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        listItem.setInfo( type="Video", infoLabels={ "Title": name } )

        is_ok=xbmcplugin.addDirectoryItem(thisPlugin,url=u,listitem=listItem,isFolder=True)
        return is_ok




def buildRootListing():

  addNode("New Music","",1,"")
  addNode("Albums","",2,"")



def buildNewMusic():

  pass




################################################################################
# BEGIN !
################################################################################

footprints()

params=get_params()
url=None
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass



if mode==None:
    log( "Xsqueeze Chooser Root Menu" )
    try:
        buildRootListing()
    except:
        print_exc()

#Not doing the root menu so need LMS & player connection...
#create a player instance (is really a player + server combo)
try:
  player = SqueezePlayer(basicOnly=True)
except:
  log( "### Failed to create SqueezePlayer object " )
  print_exc()
  sys.exit()


if mode==1:
    log( "Handling New Music" )
    try:
        buildNewMusic()
    except:
        print_exc()

if mode==2:
    log( "Handling Albums" )

#and tell XBMC we're done...
xbmcplugin.endOfDirectory(thisPlugin)


