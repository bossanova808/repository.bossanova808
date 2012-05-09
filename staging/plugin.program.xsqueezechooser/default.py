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


def addNode(name, url, mode, iconimage, album="", artist="", artistID=""):

        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name) +"&album="+urllib.quote_plus(album) +"&artist="+urllib.quote_plus(artist) +"&artistID="+urllib.quote_plus(artistID)

        is_ok=True

        listItem=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        listItem.setInfo( type="Video", infoLabels={ "Title": name } )

        is_ok=xbmcplugin.addDirectoryItem(thisPlugin,url=u,listitem=listItem,isFolder=True)
        return is_ok




def buildRootListing():
  addNode("New Music (latest 50 albums)","",1,"")
  addNode("Albums","",2,"")
  addNode("Artists","",3,"")
  addNode("Genres","",4,"")
  addNode("Years","",5,"")
  addNode("Play Random Album","",6,"")
  addNode("Play Random Songs","",7,"")
  addNode("Radio","",8,"")
  addNode("Plugins e.g. Pandora etc.","",9,"")



def buildArtistList(listArtists):
  for artist in listArtists:
    addNode(artist['artist'] ,"",2001,"",artistID=artist['id'])

def buildAlbumList(listAlbums):
  for album in listAlbums:
    try:
      coverURL = "http://" + SERVERHTTPURL + "/music/" + album['artwork_track_id'] + "/cover.jpg"
    except KeyError:
      coverURL = ""
    addNode(album['album'] + ' (by ' + album['artist'] + ')',"",1001,coverURL,album=album['album'],artist=album['artist'])

def buildNewMusic():
  global squeezeplayer
  returnedList = squeezeplayer.getNewMusic()
  log(str(returnedList))
  buildAlbumList(returnedList)

def buildAlbums():
  global squeezeplayer
  returnedList = squeezeplayer.getAlbums()
  log(str(returnedList))
  buildAlbumList(returnedList)

def buildArtistsRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getArtists()
  log(str(returnedList))
  buildArtistList(returnedList)

def buildArtistSub(artistID):
  global squeezeplayer
  returnedList = squeezeplayer.getAlbumsByArtistID(artistID)
  log(str(returnedList))
  buildAlbumList(returnedList)


################################################################################
# BEGIN !
################################################################################

footprints()
print("Called as: " + str(sys.argv))

params=get_params()

url=None
album=None
artist=None
name=None
mode=None
rangeStart=None
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
try:
    album=urllib.unquote_plus(params["album"])
except:
    pass
try:
    artist=urllib.unquote_plus(params["artist"])
except:
    pass
try:
    artistID=int(params["artistID"])
except:
    pass



if mode==None or mode==0:
    log( "Xsqueeze Chooser Root Menu" )
    try:
        buildRootListing()
    except:
        print_exc()

#Not doing the root menu so need LMS & player connection...
#create a player instance (is really a player + server combo)
try:
  squeezeplayer = SqueezePlayer(basicOnly=True)
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
  try:
      buildAlbums()
  except:
      print_exc()

if mode==3:
  log( "Handling Artists Root" )
  try:
      buildArtistsRoot()
  except:
      print_exc()


#modes over 1000 are not part of the main menue
#1001+ are action modes
#2001+ are submenu modes

if mode==1001:
  log( "Queueing up an album...." )
  squeezeplayer.queueAlbum(album,artist)
  addNode("Album queued.  Now hit escape/exit to return to XSqueeze.","","","")


if mode==2001:
  log( "Handling Submenu of an artist...." )
  try:
      buildArtistSub(artistID)
  except:
      print_exc()

#and tell XBMC we're done...
xbmcplugin.endOfDirectory(thisPlugin)


