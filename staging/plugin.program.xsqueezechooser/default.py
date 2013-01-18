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
from b808common import *

#Add a node to the plugin tree - a 'directory' node, so something we
#can click on to either get more choices or trigger an action
def addNode(name, url, mode, iconimage, album="", artist="", artistID="", genreID="", year="", cmd="", itemid="",itemCount=0):

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

        log("AddNode: url:[" + u +"] (isFolder=True), listitem:[" + str(listItem) + "] totalItems=" + str(itemCount))
        is_ok=xbmcplugin.addDirectoryItem(THIS_PLUGIN,url=u,listitem=listItem,isFolder=True, totalItems=itemCount)
        return is_ok


#Add a node at the end of the chain - not clickable
#Used for messages after an album is queued or whatever
def addEndNode(name, url, mode, iconimage, album="", artist="", artistID="", genreID="", year="", cmd="", itemid="",itemCount=0):

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

        log("AddENDNode: url:[" + u +"] (isFolder=False), listitem:[" + str(listItem) + "] totalItems=" + str(itemCount))
        is_ok=xbmcplugin.addDirectoryItem(THIS_PLUGIN,url=u,listitem=listItem,isFolder=False, totalItems=itemCount)
        return is_ok


################################################################################
### THESE FUNCTIONS BUILD THE MENUS


##def buildMenu(squeezeplayerFunc, *squeezeplayerFuncArgs):
##
##, listFunc, *listFuncArgs):
##  global squeezeplayer
##  returnedList = squeezeplayerFunc(*squeezeplayerFuncArgs)
##  log(str(returnedList))
##  buildAlbumList(returnedList)


def buildRootListing():
  addNode("New Music (latest 50 albums)","",NEW_MUSIC,"")
  addNode("Albums (Warning: can be slow with large collections!)","",ALBUMS,"")
  addNode("Artists","",ARTISTS,"")
  addNode("Genres","",GENRES,"")
  addNode("Years","",YEARS,"")
  addNode("Favourites","",FAVOURITES,"")
  addNode("Play Random Albums","",RANDOM_ALBUMS,"")
  addNode("Play Random Songs","",RANDOM_TRACKS,"")
  addNode("Internet Radio","",RADIOS,"")
  addNode("Apps (local playback only if Squeezeslave supports them)","",APPS,"")

### NEW MUSIC

def buildNewMusic():
  global squeezeplayer
  returnedList = squeezeplayer.getNewMusic()
  #log(str(returnedList))
  buildAlbumList(returnedList)

### ALBUMS

def buildAlbumList(listAlbums):
  itemCount = len(listAlbums)
  for album in listAlbums:
    try:
      coverURL = "http://" + SERVERHTTPURL + "/music/" + album['artwork_track_id'] + "/cover.jpg"
    except KeyError:
      coverURL = ""
    addNode(album['album'] + ' (by ' + album['artist'] + ')',"",PLAY_ALBUM,coverURL,album=album['album'],artist=album['artist'],itemCount=itemCount)

def buildAlbums():
  global squeezeplayer
  returnedList = squeezeplayer.getAlbums()
  #log(str(returnedList))
  buildAlbumList(returnedList)

### ARTISTS

def buildArtistsRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getArtists()
  #log(str(returnedList))
  buildArtistList(returnedList)

def buildArtistSub(artistID):
  global squeezeplayer
  returnedList = squeezeplayer.getAlbumsByArtistID(artistID)
  #log(str(returnedList))
  buildAlbumList(returnedList)

def buildArtistList(listArtists):
  for artist in listArtists:
    addNode(artist['artist'] ,"",SUBMENU_ARTISTS,"",artistID=artist['id'])

### GENRES

def buildGenresRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getGenres()
  #log(str(returnedList))
  buildGenreList(returnedList)

def buildGenreSub(genreID):
  global squeezeplayer
  returnedList = squeezeplayer.getAlbumsByGenreID(genreID)
  #log(str(returnedList))
  buildAlbumList(returnedList)

def buildGenreList(listGenres):
  for genre in listGenres:
    addNode(genre['genre'] ,"",SUBMENU_GENRES,"",genreID=genre['id'])

### YEARS

def buildYearsRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getYears()
  #log(str(returnedList))
  buildYearList(returnedList)

def buildYearSub(year):
  global squeezeplayer
  returnedList = squeezeplayer.getAlbumsByYear(year)
  #log(str(returnedList))
  buildAlbumList(returnedList)

def buildYearList(listYears):
  for year in listYears:
    addNode(year['year'] ,"",SUBMENU_YEARS,"",year=year['year'])

### Favourites

def buildFavouritesRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getFavourites()
  #log(str(returnedList))
  buildFavouritesList(returnedList)

def buildFavouritesList(listFavourites):
  for fave in listFavourites:
    try:
      coverURL = "http://" + SERVERHTTPURL + "/" + fave['icon']
    except:
      coverURL = ""

    #submenu - might lead to more menus...
    if 'hasitems' in fave:
      #item has a submenu...
      if fave['hasitems']!='0':
        addNode(fave['name'],"",SUBMENU_FAVOURITES,coverURL,cmd=cmd,itemid=fave['id'])
      #item is a playable station
      else:
        try:
          addNode(fave['name'],"",PLAY_FAVOURITE,coverURL,cmd=cmd,itemid=fave['id'])
        except Exception as inst:
          #log(str(fave))
          print_exc(inst)
    #subsubmenu
    else:
      if 'name' not in fave: continue
      else: addNode(fave['name'],"",PLAY_FAVOURITE,coverURL,cmd=cmd,itemid=fave['id'])


def buildFavouriteSub(cmd, itemid=""):
  global squeezeplayer
  returnedList = squeezeplayer.getFavouritesSub(itemid)
  #log(str(returnedList))
  buildFavouritesList(returnedList)

### RANDOM ALBUMS

def playRandomAlbums():
  global squeezeplayer
  squeezeplayer.playRandomAlbums()
  notify("Random Albums" , "", 10000)
  xbmc.executebuiltin("ActivateWindow(" + callerid + ")")

### RANDOM TRACKSS

def playRandomTracks():
  global squeezeplayer
  squeezeplayer.playRandomTracks()
  notify("Random Tracks", "", 10000)
  xbmc.executebuiltin("ActivateWindow(" + callerid + ")")

### RADIOS

def buildRadioRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getRadios()
  #log(str(returnedList))
  buildRadioList(returnedList)

def buildRadioList(listRadios):
  for radio in listRadios:
    if radio['cmd']=="search" : continue
    coverURL = "http://" + SERVERHTTPURL + "/" + radio['icon']
    addNode(radio['cmd'],"",SUBMENU_RADIOS,coverURL,cmd=radio['cmd'])

def buildRadioSub(cmd, itemid=""):
  global squeezeplayer
  returnedList = squeezeplayer.getRadioStations(cmd,itemid)
  #log(str(returnedList))
  buildRadioStationList(returnedList, cmd)

def buildRadioStationList(listRadios, cmd):
  #log(str(listRadios))
  #log(cmd)
  for radio in listRadios:
    try:
      coverURL = radio['image']
    except:
      coverURL = ""

    #submenu - might lead to more menus...
    if 'hasitems' in radio:
      #item has a submenu...
      if radio['hasitems']!='0':
        addNode(radio['name'],"",SUBMENU_RADIOS,coverURL,cmd=cmd,itemid=radio['id'])
      #item is a playable station
      else:
        try:
          addNode(radio['name'],"",PLAY_RADIO,coverURL,cmd=cmd,itemid=radio['id'])
        except Exception as inst:
          #log(str(radio))
          print_exc(inst)
    #subsubmenu
    else:
      if 'name' not in radio: continue
      else: addNode(radio['name'],"",PLAY_RADIO,coverURL,cmd=cmd,itemid=radio['id'])


### RADIOS

def buildAppsRoot():
  global squeezeplayer
  returnedList = squeezeplayer.getApps()
  #log(str(returnedList))
  buildAppsList(returnedList)

def buildAppsList(listApps):
  for app in listApps:
    if app['cmd']=="search" : continue
    coverURL = "http://" + SERVERHTTPURL + "/" + app['icon']
    addNode(app['cmd'],"",SUBMENU_RADIOS,coverURL,cmd=app['cmd'])


################################################################################
# BEGIN !  This is where the action starts
################################################################################

#Log that we've started, and how we were called....
footprints()
#parse the paramters
params=get_params()
if params==[]:
  notify("Please do not run XSqueeze Chooser directly!","In Xsqueeze use info on your remote (or key i) to open!", 15000)
  sys.exit()


#MENU MODES
ROOT = 0
NEW_MUSIC = 1
ALBUMS = 2
ARTISTS = 3
GENRES = 4
YEARS = 5
FAVOURITES = 6
RANDOM_ALBUMS = 7
RANDOM_TRACKS = 8
RADIOS = 9
APPS = 10

#PLAYING MODES
PLAY_ALBUM = 1001
PLAY_RADIO = 1002
PLAY_FAVOURITE = 1003

#SUBMENU MODES
SUBMENU_ARTISTS = 2001
SUBMENU_GENRES = 2002
SUBMENU_YEARS = 2003
SUBMENU_RADIOS = 2004
SUBMENU_APPS = 2005
SUBMENU_FAVOURITES = 2006


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


#these modes use the thumbnail view (for playable items)
thumbModes = [\
              None, \
              PLAY_ALBUM,\
              PLAY_RADIO,\
              NEW_MUSIC,\
              ALBUMS,\
              RADIOS,\
              SUBMENU_ARTISTS,\
              SUBMENU_GENRES,\
              SUBMENU_YEARS,\
              SUBMENU_RADIOS,\
              SUBMENU_APPS\
              ]


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

elif mode==FAVOURITES:
  log( "Handling Favourites Root" )
  try:
      buildFavouritesRoot()
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

elif mode==RADIOS:
  log( "Handling Internet Radio" )
  try:
      buildRadioRoot()
  except:
      print_exc()

elif mode==APPS:
  log( "Handling Apps" )
  try:
      buildAppsRoot()
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

elif mode==PLAY_RADIO:
  log( "Queueing up a radio station...." + cmd + "itemid " +itemid )
  squeezeplayer.queueRadio(cmd, itemid)
  notify("Radio" , name, 12000)
  xbmc.executebuiltin("ActivateWindow(" + callerid + ")")

elif mode==PLAY_FAVOURITE:
  log( "Queueing up a favourite...." + name + "itemid " +itemid )
  squeezeplayer.queueFavourite(itemid)
  notify("Favourite" , name, 12000)
  xbmc.executebuiltin("ActivateWindow(" + callerid + ")")


elif mode==SUBMENU_ARTISTS:
  log( "Handling submenu of an artist...." )
  try:
      buildArtistSub(artistID)
  except:
      print_exc()

elif mode==SUBMENU_GENRES:
  log( "Handling submenu of a genre...." )
  try:
      buildGenreSub(genreID)
  except:
      print_exc()

elif mode==SUBMENU_YEARS:
  log( "Handling submenu of a year...." )
  try:
      buildYearSub(year)
  except:
      print_exc()

elif mode==SUBMENU_FAVOURITES:
  log( "Handling submenu of a favourite...." )
  try:
      buildFavouriteSub(cmd,itemid)
  except:
      print_exc()

elif mode==SUBMENU_RADIOS:
  log( "Handling submenu of a radio/app...." )
  try:
      buildRadioSub(cmd,itemid)
  except:
      print_exc()


################################################################################
# FALL THROUGH to here after the list building above....

#if we've just built a list of albums, force thumbnail mode
if mode in thumbModes:
  log("Playable Items -> Trying to set thumnbnail mode...")
  xbmc.executebuiltin('Container.SetViewMode(500)')
else:
  log("List Items -> Trying to set list mode...")
  xbmc.executebuiltin('Container.SetViewMode(50)')


#and tell XBMC we're done...
xbmcplugin.endOfDirectory(THIS_PLUGIN)

footprints(startup=False)

