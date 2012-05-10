### XSqueeze Common Code for XSqueeze & XSqueeze Chooser
### by bossanova808 2012
### Free in all senses....

import xbmc
import xbmcaddon
import xbmcplugin
import xbmcvfs
import xbmcgui

import urllib
import sys
import os
import telnetlib
from traceback import print_exc

################################################################################
################################################################################
### CONSTANTS & SETTINGS

#create an add on instation and store the reference
__addon__       = xbmcaddon.Addon()

#if we've been imported from the plugin we need the magic ID
if 'plugin' in sys.argv[0]:
  thisPlugin = int(sys.argv[1])

#used to get settings from the main addon
refToXSqueeze = xbmcaddon.Addon(id='script.xsqueeze')

#store some handy constants
__addonname__   = __addon__.getAddonInfo('name')
__addonid__     = __addon__.getAddonInfo('id')
__author__      = __addon__.getAddonInfo('author')
VERSION     = __addon__.getAddonInfo('version')
__cwd__         = __addon__.getAddonInfo('path')
__language__    = __addon__.getLocalizedString
__useragent__   = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.6"

# Set up the paths
RESOURCES_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources' ))
LIB_PATH = xbmc.translatePath(os.path.join( RESOURCES_PATH, "lib" ))
sys.path.append( LIB_PATH )

# Import PYLMS
from pylms.server import Server
from pylms.player import Player

# LMS SERVER SETTINGS
# The LMS Server and port - either discovered in the add on settings
#  or manually set
if refToXSqueeze.getSetting('serverManual')=="true":
  MANUALSERVER = True
else:
  MANUALSERVER = False

if MANUALSERVER:
  SERVERIP    = refToXSqueeze.getSetting('serverIP')
  SERVERNAME = SERVERIP
  SERVERPORT  = refToXSqueeze.getSetting('serverPort')
  SERVERUSER  = refToXSqueeze.getSetting('serverUser')
  SERVERPASS  = refToXSqueeze.getSetting('serverPass')
else:
  SERVERIP = refToXSqueeze.getSetting('autoserverip')
  SERVERNAME = refToXSqueeze.getSetting('autoservername')
  SERVERPORT = '9090'
  SERVERUSER  = ''
  SERVERPASS  = ''

#shorthand for the full server string, so e.g. 192.168.1.1:9090
SERVERIPPORT = SERVERIP + ":" + SERVERPORT
#url of the http interface for LMS
SERVERHTTPURL   = SERVERIP + ":" + refToXSqueeze.getSetting('serverHTTPPort')

#LOCAL PLAYBACK SETTINGS
#LMS is case sensitive and all MACs need to be lower case!!

#are we controlling the local slave or another external player?
if refToXSqueeze.getSetting('controlSlave')=="true":
  CONTROLSLAVE = True
else:
  CONTROLSLAVE = False

if refToXSqueeze.getSetting('controllerOnly')=="true":
  CONTROLLERONLY = True
else:
  CONTROLLERONLY = False


# we either get the MAC from the local player setup, or from the controller setup

if CONTROLSLAVE:
  PLAYERMAC   = str.lower(refToXSqueeze.getSetting('slaveMAC'))
if CONTROLLERONLY:
  PLAYERMAC   = str.lower(refToXSqueeze.getSetting('controllerMAC'))


################################################################################
################################################################################
### LOGGING

################################################################################
# Log a message to the XBMC Log, and an exception if supplied - if debug logging is on

def log(message, inst=None, level=xbmc.LOGNOTICE):
    if inst is None:
      xbmc.log(__addonname__ + "-" + __version__ +  ": " + str(message), level )
    else:
      xbmc.log(__addonname__ + "-" + __version__ +  ": Exception!", level )
      print_exc(inst)


################################################################################
# Log a message to the XBMC Log, and an exception if supplied

def notify(messageLine1, messageLine2 = "", time = 6000):
  imagepath = os.path.join(constants.__cwd__ ,"icon.png")
  notifyString = "XBMC.Notification("+ constants.__addonname__ + ": " + messageLine1 +"," + messageLine2+","+str(time)+","+imagepath+")"
  log("XBMC Notificaton Requested: [" + notifyString +"]")
  xbmc.executebuiltin( notifyString )

################################################################################
# Log a startup message to the XBMC log

def footprints():

    log( "### %s Starting ..." % __addonname__ )
    log( "### Author: %s" % __author__ )
    log( "### Version: %s" % __version__ )

################################################################################
################################################################################
###UTILS

################################################################################
# send a JSON command to XBMC and log the human description, json string, and
# the result returned

def sendXBMCJSON (humanDescription, jsonstr):
     log(humanDescription + " [" + jsonstr +"]")
     result = xbmc.executeJSONRPC(jsonstr)
     log("JSON result: "  + str(result))

##############################################################################
# helper function - convert player seconds to summat nice for screen 00:00 etc

def getInHMS(seconds):
    hours = seconds / 3600
    seconds -= 3600*hours
    minutes = seconds / 60
    seconds -= 60*minutes
    if hours == 0:
        return "%02d:%02d" % (minutes, seconds)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)

##############################################################################
# properly unquote text coming back from LMS

def unquoteUni(text):

    try:
        import urllib.parse
        return urllib.parse.unquote(text, encoding=self.charset)
    except ImportError:
        #import urllib
        #return urllib.unquote(text)
        _hexdig = '0123456789ABCDEFabcdef'
        _hextochr = dict((a+b, chr(int(a+b,16))) for a in _hexdig for b in _hexdig)
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        res = text.split('%')
        for i in xrange(1, len(res)):
            item = res[i]
            try:
                res[i] = _hextochr[item[:2]] + item[2:]
            except KeyError:
                res[i] = '%' + item
            except UnicodeDecodeError:
                res[i] = unichr(int(item[:2], 16)) + item[2:]
        return "".join(res)


################################################################################
################################################################################
################################################################################
### CLASS SQUEEZEPLAYER

class SqueezePlayer:

  ##############################################################################
  #constructor - connect to the server and player so we can do stuff
  #other handy start up stuff
  def __init__(self,basicOnly=False):

    #connect to server
    log("Attempting to connect to LMS named [" + SERVERNAME + "] at IP:  " + SERVERIP + " on CLI port: " + SERVERPORT)
    try:
      self.sc = Server(hostname=SERVERIP, port=SERVERPORT, username=SERVERUSER, password=SERVERPASS)
      self.sc.connect()
      log( "LMS Logged in: %s" % self.sc.logged_in )
      log( "LMS Version: %s" % self.sc.get_version() )
    except:
      log(" Couldn't connect to server!")
      notify(constants.__language__(19613),constants.__language__(19614))
      raise

    #connect to player
    log( "Attempting to connect to player: " + PLAYERMAC)
    try:
      self.sb = self.sc.get_player(PLAYERMAC)
      if self.sb:
        log( "Connected to: %s" % PLAYERMAC )
        state = self.sb.get_power_state()
        log ( "Power state is: " + str (state) )
      else:
        log( "Player is NoneType: %s" % PLAYERMAC )
        raise Exception
    except Exception as inst:
      log(" Couldn't connect to player: " + PLAYERMAC , inst)
      notify(constants.__language__(19615),constants.__language__(19616))
      sys.exit()

    #initialise if we're called from XSqueeze as opposed to the chooser
    if not basicOnly:
      self.currentTrack = None
      self.coverURLs = None
      self.playlistDetails = None
      self.updatePlaylistDetails()
      self.updateCoverArtURLs()


  ##############################################################################
  #get the current squeezebox two line display text and return it

  def getDisplay(self):
    displayText = self.sb.requestRaw("display ? ?", True)
    lines = displayText.split(" ")
    if lines[2] == "":
      lines[2] = "."
    if lines[3] == "":
      lines[3] = "."
    cleanedLines=[]
    cleanedLines.append((lines[2]))
    cleanedLines.append((lines[3]))

    #print(cleanedLines)

    #clean out the wierd characters used to represent volume...
    newLines=[]
    for line in cleanedLines:
      line = line.replace(u'cursorpos', u"\u2334")
      line = line.replace(u'rightarrow', u"\u2192")
      line = line.replace(u'solidblock', u'*')
      line = line.replace(u'leftprogress4', u'*')
      line = line.replace(u'leftprogress2', u'*')
      line = line.replace(u'leftprogress0', u'(Mute)')
      line = line.replace(u'rightprogress0', u' ')
      line = line.replace(u'rightprogress4', u'(Max)')
      line = line.replace(u'middleprogress0', u' ')
      line = line.replace(u'%1E',u"")
      line = line.replace(u'%1F',u"")
      newLines.append(line)

    #print(newLines)

    return unquoteUni(newLines[0]), unquoteUni(newLines[1])

  ##############################################################################
  # check if song changed and update local reference if so
  # returns boolean - but of course only once on each change
  # called every window update to see if the song has changed and only if it has
  # do we update the playlist and cover arts...reduces traffic a lot!

  def songChanged(self):
    oldSong = self.currentTrack
    newSong = self.sb.get_track_title()
    #log("New Song [" + newSong +"], Old song [" + oldSong + "]")
    if newSong != oldSong:
      log("### Detected song change to: " + repr(newSong) + " - triggering playlist and cover art updates...")
      self.currentTrack = newSong
      self.updatePlaylistDetails()
      self.updateCoverArtURLs()
      return True;
    else:
      return False

  ##############################################################################
  # returns the URLs for the current and next three track cover art images

  def updateCoverArtURLs(self):

      coverURLs = []

      #print "Playlist is" + str(self.playlist)

      #start at this song , end at + 3
      index = int(self.sb.request("playlist index ?"))
      upcomer = index
      end = index + 4

      #currently uses the track_id in the url - works well
      #supposed to use the cover_id number but this doesn't work so well...
      for count in range(upcomer,end):
        if(count<len(self.playlist)):
          try:
            statusInfo = self.sb.request("status " + str(count) + " 1 tags:Kal")
            if("artwork_url" in statusInfo):
              statusArtwork = statusInfo.split('artwork_url:')
              statusArtwork = statusArtwork.pop(1)
              statusArtwork = statusArtwork.split(' ')
              statusArtwork = statusArtwork.pop(0)
              #log("statusArtwork is " + str(statusArtwork))
              #check we have a full url....
              if("http" not in statusArtwork):
                coverURL = "http://" + constants.SERVERHTTPURL + "/" + statusArtwork
              else:
                coverURL = statusArtwork
            else:
              statusId = statusInfo.split('id:')
              statusId = statusId.pop(1)
              statusId = statusId.split(' ')
              statusId = statusId.pop(0)
              #log("StatusID is " + str(statusId))
              coverURL = "http://" + constants.SERVERHTTPURL + "/music/" + str(statusId) + "/cover.jpg"

            #now append the coverURL to our list of URLs
            #log ("Appending future cover: " + str(count) + " from " + coverURL)
            coverURLs.append(coverURL)

          #Something went wrong, go with null string just to be safe...
          except Exception as inst:
            log("No cover art so appending null string for playlist index " + str(count), inst)
            coverURLs.append("")

      self.coverURLs = coverURLs

  ##############################################################################
  # Gets more info about a particular song

  def getSongInfo(self, id):
    encoded = self.sb.requestRaw("songinfo 0 1000 track_id:" + str(id), True)

    #print encoded

    #find the index of id: - track_id%3A
    start = encoded.find('track_id%3A')
    encoded = encoded[start:]

    #print(str(id) + " Encoded: " +str(encoded))
    list = encoded.split(" ")
    #print("list: " + str(list))

    decodedList = []
    for item in list:
      cleanItem = unquoteUni(item)
      decodedList.append(cleanItem)

    #print("DecodedList: " +str(decodedList))

    item = {}
    for info in decodedList:
        info = info.split(':')
        key = info.pop(0)
        if key:
            item[key] = ':'.join(info)

    # example...
    # 9 id:39 title:I'm Not The Man artist:10000 Maniacs coverid:94339a48 duration:226.36 album_id:4 filesize:22796274 genre:Pop coverart:1 artwork_track_id:94339a48
    # album:MTV Unplugged modificationTime:Thursday, November 27, 2008, 5:24 PM type:flc genre_id:4 bitrate:805kbps VBR artist_id:11 tracknum:4 year:1993 compilation:0
    # addedTime:Thursday, December 8, 2011, 11:15 PM channels:2 samplesize:16 samplerate:44100 lastUpdated:Thursday, December 8, 2011, 11:15 PM album_replay_gain:-6.46 replay_gain:-3.46

    #print "Item" + str(item)

    #convert all the data to the right types
    try:
      item['id'] = int(item['id'])
      item['duration'] = float(item['duration'])
      item['album_id'] = int(item['album_id'])
      item['filesize'] = int(item['filesize'])
      item['coverart'] = int(item['coverart'])
      item['genre_id'] = int(item['genre_id'])
      item['artist_id'] = int(item['artist_id'])
      item['tracknum'] = int(item['tracknum'])
      item['year'] = int(item['year'])
      item['compilation'] = int(item['compilation'])
      item['channels'] = int(item['channels'])
      item['samplesize'] = int(item['samplesize'])
      item['samplerate'] = int(item['samplerate'])
      item['album_replay_gain'] = float(item['album_replay_gain'])
      item['replay_gain'] = float(item['replay_gain'])
    except KeyError as inst:
      #not all data is always returned, so we can just skip that but
      pass
      #log("Issue with missing data in songinfo", inst)
    except Exception as inst:
      log("****** Other songinfo issue: ", inst)

    #print "item is now " + str(item)
    return item

  ##############################################################################
  # Send a button command text, e.g. 'pause' - to the player

  def button(self, text):
    self.sb.ir_button(text)
    #song may have changed, trigger an update test
    self.songChanged()

  ##############################################################################
  # returns all the details of up to 10 tracks...

  def updatePlaylistDetails(self):
    self.playlist = self.sb.playlist_get_info()
    currentIndex = int(self.sb.request("playlist index ?"))
    #log ("Current index: " + str(currentIndex) + " len(playlist): " + str(len(self.playlist)) + " Playlist is: " + str(self.playlist))
    playlistDetails = []
    #retrieve a maxiumum of 10 tracks details
    for trackOffset in range(currentIndex,currentIndex+10):
      #don't go off the end of the playlist
      if trackOffset < len(self.playlist):
        trackID = self.playlist[trackOffset]['id']
        #log("Getting full details for id: " + str(trackID))
        playlistDetails.append(self.getSongInfo(trackID))

    #the caller should check the length of the playlist and process all entries...
    self.playlistDetails = playlistDetails

  ##############################################################################
  # returns current track length if available (check for 0 etc. at other end)

  def getTrackLength(self):
    return self.sb.get_track_duration()

  ##############################################################################
  # returns current mode ('play' 'pause' or 'stop')

  def getMode(self):
      return self.sb.get_mode()

  ##############################################################################
  # returns length of time in seconds the current track has played for

  def getTrackElapsed(self):
    return self.sb.get_time_elapsed()

  ##############################################################################
  # returns the full album info given an ID

  def getAlbumInfo(self, albumID):
    fullAlbumInfo = self.sc.request_with_results('albums 0 1 album_id:' + albumID + ' tags:yajl')
    log("Full Album Info: " + str(fullAlbumInfo))
    return fullAlbumInfo[1][0]

  ##############################################################################
  # returns the latest 50 albums

  def getNewMusic(self):
    fullAlbums = []
    albums = self.sc.request_with_results("albums 0 50 sort:new")
    for album in albums[1]:
      fullAlbumInfo = self.getAlbumInfo(album['id'])
      fullAlbums.append(fullAlbumInfo)
    return fullAlbums

  ##############################################################################
  # returns all albums

  def getAlbums(self):
    fullAlbums = []
    albums = self.sc.request_with_results("albums 0 100000")
    for album in albums[1]:
      fullAlbumInfo = self.getAlbumInfo(album['id'])
      fullAlbums.append(fullAlbumInfo)
    return fullAlbums

  ##############################################################################
  # returns all artists

  def getArtists(self):
    artists = self.sc.request_with_results("artists 0 100000", debug=True)
    log(str(artists))
    return artists[1]

  ##############################################################################
  # returns all albums by a particular artist given an artist_id

  def getAlbumsByArtistID(self,artistID):
    fullAlbums = []
    albums = self.sc.request_with_results("albums 0 100000 artist_id:" + str(artistID), debug=True)
    log(str(albums))
    for album in albums[1]:
      fullAlbumInfo = self.getAlbumInfo(album['id'])
      fullAlbums.append(fullAlbumInfo)
    return fullAlbums

  ##############################################################################
  # returns all albums in a particular genre given a genre_id

  def getAlbumsByGenreID(self,genreID):
    fullAlbums = []
    albums = self.sc.request_with_results("albums 0 100000 genre_id:" + str(genreID), debug=True)
    log(str(albums))
    for album in albums[1]:
      fullAlbumInfo = self.getAlbumInfo(album['id'])
      fullAlbums.append(fullAlbumInfo)
    return fullAlbums

  ##############################################################################
  # returns all albums for a given year

  def getAlbumsByYear(self,year):
    fullAlbums = []
    albums = self.sc.request_with_results("albums 0 100000 year:" + str(year), debug=True)
    log(str(albums))
    for album in albums[1]:
      fullAlbumInfo = self.getAlbumInfo(album['id'])
      fullAlbums.append(fullAlbumInfo)
    return fullAlbums

  ##############################################################################
  # returns all genres

  def getGenres(self):
    genres = self.sc.request_with_results("genres 0 100000", debug=True)
    log(str(genres))
    return genres[1][1:]

  ##############################################################################
  # returns all years

  def getYears(self):
    years = self.sc.request_with_results("years 0 100000", debug=True)
    log(str(years))
    return years

  ##############################################################################
  # returns all radios

  def getRadios(self):
    radios = self.sc.request_with_results("radios 0 100000", debug=True)
    log(str(radios))
    return radios

  ##############################################################################
  # Clear playlist and queue up an album given an album title and artist

  def queueAlbum(self, title, artist):
    if artist=="Various Artists":
      self.sb.request("playlist loadalbum * * " + urllib.quote(title),debug=True)
    else:
      self.sb.request("playlist loadalbum * " + urllib.quote(artist) + " " + urllib.quote(title),debug=True)

  ##############################################################################
  # Clear playlist and queue up random albums

  def playRandomAlbums(self):
    self.sb.request("randomplay albums")

  ##############################################################################
  # Clear playlist and queue up random songs

  def playRandomTracks(self):
    self.sb.request("randomplay tracks")

