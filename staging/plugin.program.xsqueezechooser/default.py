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


def addNode(name, url, mode, iconimage, album="", artist="", artistID="", genreID="", year=""):

        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&album="+urllib.quote_plus(album)+"&artist="+urllib.quote_plus(artist)+"&artistID="+urllib.quote_plus(artistID)+"&genreID="+urllib.quote_plus(genreID)+"&year="+urllib.quote_plus(year)

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
  addNode("Years (not working yet)","",5,"")
  addNode("Play Random Albums","",6,"")
  addNode("Play Random Songs","",7,"")
  addNode("Internet Radio (not working yet)","",8,"")
  addNode("Plugins e.g. Pandora etc. (not working yet)","",9,"")

def buildYearList(listYears):
  for year in listYears:
    addNode(year['year'] ,"",2005,"",year=year['year'])

def buildYearSub(year):
  global squeezeplayer
  returnedList = squeezeplayer.getAlbumsByYear(year)
  log(str(returnedList))
  buildAlbumList(returnedList)

def buildRadioList(listRadios):
  for radio in listRadios:
    addNode(radio['radio'],"",2002,"","")

def buildGenreList(listGenres):
  for genre in listGenres:
    addNode(genre['genre'] ,"",2002,"",genreID=genre['id'])

def buildGenreSub(genreID):
  global squeezeplayer
  returnedList = squeezeplayer.getAlbumsByGenreID(genreID)
  log(str(returnedList))
  buildAlbumList(returnedList)

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

def buildGenresRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getGenres()
  log(str(returnedList))
  buildGenreList(returnedList)

def buildYearsRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getYears()
  log(str(returnedList))
  buildYearList(returnedList)

def buildRadioRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getRadios()
  log(str(returnedList))
  buildRadioList(returnedList)

def playRandomAlbums():
  global squeezeplayer
  squeezeplayer.playRandomAlbums()
  addNode("Random albums mix queued.","","","")
  addNode("Now hit escape/exit to return to XSqueeze.","","","")

def playRandomTracks():
  global squeezeplayer
  squeezeplayer.playRandomTracks()
  addNode("Random tracks mix queued.","","","")
  addNode("Now hit escape/exit to return to XSqueeze.","","","")

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
artistID=None
genreID=None
year=None

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
try:
    genreID=int(params["genreID"])
except:
    pass
try:
    year=int(params["year"])
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

if mode==4:
  log( "Handling Genres Root" )
  try:
      buildGenresRoot()
  except:
      print_exc()

if mode==5:
  log( "Handling Years Root" )
  try:
      buildYearsRoot()
  except:
      print_exc()

if mode==6:
  log( "Handling Random Albums" )
  try:
      playRandomAlbums()
  except:
      print_exc()

if mode==7:
  log( "Handling Random Tracks" )
  try:
      playRandomTracks()
  except:
      print_exc()

if mode==8:
  log( "Handling Internet Radio" )
  try:
      buildRadioRoot()
  except:
      print_exc()

#modes over 1000 are not part of the main menu
#1001+ are action modes
#2001+ are submenu modes

if mode==1001:
  log( "Queueing up an album...." )
  squeezeplayer.queueAlbum(album,artist)
  addNode("Album queued.  Now hit escape/exit to return to XSqueeze.","","","")


if mode==2001:
  log( "Handling submenu of an artist...." )
  try:
      buildArtistSub(artistID)
  except:
      print_exc()

if mode==2002:
  log( "Handling submenu of a genre...." )
  try:
      buildGenreSub(genreID)
  except:
      print_exc()

if mode==2003:
  log( "Handling submenu of a year...." )
  try:
      buildYearSub(year)
  except:
      print_exc()


#and tell XBMC we're done...
xbmcplugin.endOfDirectory(thisPlugin)


