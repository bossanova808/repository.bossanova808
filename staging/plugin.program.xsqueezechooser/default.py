### XSqueeze Chooser
### by bossanova808 2012
### Free in all senses....

import xbmc
import xbmcaddon
import xbmcplugin
import xbmcvfs
import xbmcgui
import urllib
from traceback import print_exc

#Import the common code - basically the SqueezePlayer class
#which connects to the server and a player
from XSqueezeCommon import *


#Borrow from somewhere....parses the parameter stings (arrives in sys.argv[2])
#into a dict
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


#Add a node to the plugin tree - a 'directory' node, so something we
#can click on to either get more choices or trigger an action
def addNode(name, url, mode, iconimage, album="", artist="", artistID="", genreID="", year="", cmd="", itemid=""):

        global callerid

        u=sys.argv[0]+\
        "?url="+urllib.quote_plus(url)+\
        "&mode="+str(mode)+\
        "&name="+urllib.quote_plus(name)+\
        "&album="+urllib.quote_plus(album)+\
        "&artist="+urllib.quote_plus(artist)+\
        "&artistID="+urllib.quote_plus(artistID)+\
        "&genreID="+urllib.quote_plus(genreID)+\
        "&year="+urllib.quote_plus(year)+\
        "&itemid="+urllib.quote_plus(itemid)+\
        "&callerid="+urllib.quote_plus(callerid)+\
        "&cmd="+urllib.quote_plus(cmd)

        is_ok=True

        listItem=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        listItem.setInfo( type="Video", infoLabels={ "Title": name } )

        is_ok=xbmcplugin.addDirectoryItem(THIS_PLUGIN,url=u,listitem=listItem,isFolder=True)
        return is_ok


#Add a node at the end of the chain - not clickable
#Used for messages after an album is queued or whatever
def addEndNode(name, url, mode, iconimage, album="", artist="", artistID="", genreID="", year="", cmd="", itemid=""):

        global callerid

        u=sys.argv[0]+\
        "?url="+urllib.quote_plus(url)+\
        "&mode="+str(mode)+\
        "&name="+urllib.quote_plus(name)+\
        "&album="+urllib.quote_plus(album)+\
        "&artist="+urllib.quote_plus(artist)+\
        "&artistID="+urllib.quote_plus(artistID)+\
        "&genreID="+urllib.quote_plus(genreID)+\
        "&year="+urllib.quote_plus(year)+\
        "&itemid="+urllib.quote_plus(itemid)+\
        "&callerid="+urllib.quote_plus(callerid)+\
        "&cmd="+urllib.quote_plus(cmd)

        is_ok=True

        listItem=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        listItem.setInfo( type="Video", infoLabels={ "Title": name } )

        is_ok=xbmcplugin.addDirectoryItem(THIS_PLUGIN,url=u,listitem=listItem,isFolder=False)
        return is_ok


################################################################################
### THESE FUNCTIONS BUILD THE MENUS

def buildRootListing():
  addNode("New Music (latest 50 albums)","",1,"")
  addNode("Albums","",2,"")
  addNode("Artists","",3,"")
  addNode("Genres","",4,"")
  #addNode("  NOT YET WORKING : Years","",5,"")
  addNode("Play Random Albums","",6,"")
  addNode("Play Random Songs","",7,"")
  addNode("  NOT YET WORKING : Internet Radio","",8,"")
  #addNode("  NOT YET WORKING : Plugins e.g. Pandora etc.","",9,"")

### NEW MUSIC

def buildNewMusic():
  global squeezeplayer
  returnedList = squeezeplayer.getNewMusic()
  log(str(returnedList))
  buildAlbumList(returnedList)

### ALBUMS

def buildAlbumList(listAlbums):
  for album in listAlbums:
    try:
      coverURL = "http://" + SERVERHTTPURL + "/music/" + album['artwork_track_id'] + "/cover.jpg"
    except KeyError:
      coverURL = ""
    addNode(album['album'] + ' (by ' + album['artist'] + ')',"",1001,coverURL,album=album['album'],artist=album['artist'])

def buildAlbums():
  global squeezeplayer
  returnedList = squeezeplayer.getAlbums()
  log(str(returnedList))
  buildAlbumList(returnedList)

### ARTISTS

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

def buildArtistList(listArtists):
  for artist in listArtists:
    addNode(artist['artist'] ,"",2001,"",artistID=artist['id'])

### GENRES

def buildGenresRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getGenres()
  log(str(returnedList))
  buildGenreList(returnedList)

def buildGenreSub(genreID):
  global squeezeplayer
  returnedList = squeezeplayer.getAlbumsByGenreID(genreID)
  log(str(returnedList))
  buildAlbumList(returnedList)

def buildGenreList(listGenres):
  for genre in listGenres:
    addNode(genre['genre'] ,"",2002,"",genreID=genre['id'])

### YEARS

def buildYearsRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getYears()
  log(str(returnedList))
  buildYearList(returnedList)

def buildYearSub(year):
  global squeezeplayer
  returnedList = squeezeplayer.getAlbumsByYear(year)
  log(str(returnedList))
  buildAlbumList(returnedList)

def buildYearList(listYears):
  for year in listYears:
    addNode(year['year'] ,"",2005,"",year=year['year'])

### RANDOM ALBUMS

def playRandomAlbums():
  global squeezeplayer
  squeezeplayer.playRandomAlbums()
  addNode("Random albums mix queued.","","","")
  addNode("Now hit escape/exit to return to XSqueeze.","","","")

### RANDOM TRACKSS

def playRandomTracks():
  global squeezeplayer
  squeezeplayer.playRandomTracks()
  addNode("Random tracks mix queued.","","","")
  addNode("Now hit escape/exit to return to XSqueeze.","","","")

### RADIOS

def buildRadioRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getRadios()
  log(str(returnedList))
  buildRadioList(returnedList)

def buildRadioSub(cmd):
  global squeezeplayer
  returnedList = squeezeplayer.getRadioStations(cmd)
  log(str(returnedList))
  buildRadioStationList(returnedList)

def buildRadioList(listRadios):
  for radio in listRadios:
    if radio['cmd']=="search" : continue
    coverURL = "http://" + SERVERHTTPURL + "/" + radio['icon']
    addNode(radio['cmd'],"",2004,coverURL,cmd=radio['cmd'])

def buildRadioStationList(listRadios):
  for radio in listRadios:
    addNode(radio['name'],"",1002,radio['image'],cmd=radio['name'],itemid=radio['id'])


##
##
##  for album in listAlbums:
##    try:
##      coverURL = "http://" + SERVERHTTPURL + "/music/" + album['artwork_track_id'] + "/cover.jpg"
##    except KeyError:
##      coverURL = ""
##    addNode(album['album'] + ' (by ' + album['artist'] + ')',"",1001,coverURL,album=album['album'],artist=album['artist'])


################################################################################
# BEGIN !  This is where the action starts
################################################################################

#Log that we've started, and how we were called....
footprints()
log("Called as: " + str(sys.argv))
#parse the paramters
params=get_params()
log("Parameters parsed: " + str(params))


#By default we use a list view unless we're displaying actual albums with art
#then we use thumbnails
albumview=False

#MODES
ROOT = 0
NEW_MUSIC = 1
ALBUMS = 2
ARTISTS = 3
GENRES = 4
YEARS = 5
RANDOM_ALBUMS = 6
RANDOM_TRACKS = 7
RADIO = 8

PLAY_ALBUM = 1001
PLAY_RADIO = 1002

SUBMENU_ARTISTS = 2001
SUBMENU_GENRES = 2002
SUBMENU_YEARS = 2003
SUBMENU_RADIOS = 2004



#zero out all the things we pass between runs before we check
#if they are in the parameters
url=None
album=None
artist=None
name=None
mode=None
artistID=None
genreID=None
year=None
cmd=None
itemid=None
#default is 13000
callerid=None

#if the params have data in them, store it in a variable
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

try:
    cmd=urllib.unquote_plus(params["cmd"])
except:
    pass

try:
    itemid=urllib.unquote_plus(params["itemid"])
except:
    pass

try:
    callerid=urllib.unquote_plus(params["callerid"])
except:
    pass


#MODES WITH SUBMENUS use list view
thumbModes = [None,PLAY_ALBUM, PLAY_RADIO, NEW_MUSIC, ALBUMS, SUBMENU_ARTISTS, SUBMENU_GENRES, SUBMENU_YEARS, SUBMENU_RADIOS]



#OK the mode variable controls what we're actually doing...
if mode==None or mode==ROOT:
  log( "Xsqueeze Chooser Root Menu" )
  try:
      buildRootListing()
  except:
      print_exc()
else:
  #Not doing the root menu so need LMS & player connection...
  #create a player instance (is really a player + server combo)
  try:
    squeezeplayer = SqueezePlayer(basicOnly=True)
  except:
    log( "### Failed to create SqueezePlayer object " )
    print_exc()
    sys.exit()

if mode==NEW_MUSIC:
  log( "Handling New Music" )
  try:
      albumview=True
      buildNewMusic()
  except:
      print_exc()

elif mode==ALBUMS:
  log( "Handling Albums" )
  try:
      albumview=True
      buildAlbums()
  except:
      print_exc()

elif mode==ARTISTS:
  log( "Handling Artists Root" )
  try:
      buildArtistsRoot()
  except:
      print_exc()

elif mode==GENRES:
  log( "Handling Genres Root" )
  try:
      buildGenresRoot()
  except:
      print_exc()

elif mode==YEARS:
  log( "Handling Years Root" )
  try:
      buildYearsRoot()
  except:
      print_exc()

elif mode==RANDOM_ALBUMS:
  log( "Handling Random Albums" )
  try:
      playRandomAlbums()
  except:
      print_exc()

elif mode==RANDOM_TRACKS:
  log( "Handling Random Tracks" )
  try:
      playRandomTracks()
  except:
      print_exc()

elif mode==RADIO:
  log( "Handling Internet Radio" )
  try:
      buildRadioRoot()
  except:
      print_exc()

#modes over 1000 are not part of the main menu
#1001+ are action modes
#2001+ are submenu modes

elif mode==PLAY_ALBUM:
  log( "Queueing up " + album + " by "+ artist + "...." )
  squeezeplayer.queueAlbum(album,artist)
  notify(artist , album, 12000)
  xbmc.executebuiltin("ActivateWindow(" + callerid + ")")
  #addEndNode("Album queued.","","","")
  #addEndNode("Now hit escape/exit to return to XSqueeze.","","","")

elif mode==PLAY_RADIO:
  log( "Queueing up a radio station...." )
  squeezeplayer.queueRadio(cmd, itemid)
  addEndNode("Radio queued.","","","")
  addEndNode("Now hit escape/exit to return to XSqueeze.","","","")


elif mode==SUBMENU_ARTISTS:
  log( "Handling submenu of an artist...." )
  try:
      albumview=True
      buildArtistSub(artistID)
  except:
      print_exc()

elif mode==SUBMENU_GENRES:
  log( "Handling submenu of a genre...." )
  try:
      albumview=True
      buildGenreSub(genreID)
  except:
      print_exc()

elif mode==SUBMENU_YEARS:
  log( "Handling submenu of a year...." )
  try:
      buildYearSub(year)
  except:
      print_exc()

elif mode==SUBMENU_RADIOS:
  log( "Handling submenu of a radio...." )
  try:
      albumview=True
      buildRadioSub(cmd)
  except:
      print_exc()



################################################################################
# FALL THROUGH to here after the list building above....

#if we've just built a list of albums, force thumbnail mode
if mode in thumbModes:
  log("Playable Items -> Trying to set thumnbnail mode...")
  xbmc.executebuiltin('Container.SetViewMode(500)')
  #set this variable back jsut in case
  albumview=False
else:
  log("List Items -> Trying to set list mode...")
  xbmc.executebuiltin('Container.SetViewMode(50)')


#and tell XBMC we're done...
xbmcplugin.endOfDirectory(THIS_PLUGIN)

