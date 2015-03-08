### XSqueeze Common Code for XSqueeze & XSqueeze Chooser
### by bossanova808 2012
### Free in all senses....

import xbmc
import xbmcaddon
import xbmcplugin
import xbmcvfs
import xbmcgui
import pprint

import urllib
import sys
import os
import telnetlib
from traceback import print_exc
import subprocess

from b808common import *

################################################################################
################################################################################
### CONSTANTS & SETTINGS

#used to get settings from the main addon
REF_TO_XSQUEEZE = xbmcaddon.Addon(id='script.xsqueeze')

# Import PYLMS
from pylms.server import Server
from pylms.player import Player

# LMS SERVER SETTINGS
# The LMS Server and port - either discovered in the add on settings
#  or manually set
SERVERIP    = REF_TO_XSQUEEZE.getSetting('serverIP')
SERVERNAME  = SERVERIP
SERVERPORT  = REF_TO_XSQUEEZE.getSetting('serverPort')
SERVERUSER  = REF_TO_XSQUEEZE.getSetting('serverUser')
SERVERPASS  = REF_TO_XSQUEEZE.getSetting('serverPass')

#shorthand for the full server string, so e.g. 192.168.1.1:9090
SERVERIPPORT = SERVERIP + ":" + SERVERPORT
#Login details?
USERPASS=None
if SERVERUSER != "" or SERVERPASS !="":
  USERPASS = SERVERUSER + ":" + SERVERPASS + "@"

#url of the http interface for LMS

SERVERHTTPURL = SERVERIP + ":" + REF_TO_XSQUEEZE.getSetting('serverHTTPPort')
#prepend login details if needed
if USERPASS:
  SERVERHTTPURL = USERPASS + SERVERHTTPURL


#LOCAL PLAYBACK SETTINGS
#LMS is case sensitive and all MACs need to be lower case!!

#are we controlling the local slave or another external player?
if REF_TO_XSQUEEZE.getSetting('playback')=="true":
  PLAYBACK = True
else:
  PLAYBACK = False

# we either get the MAC from the local player setup, or from the controller setup
PLAYERTYPE = str.lower(REF_TO_XSQUEEZE.getSetting('player'))
PLAYERMAC  = str.lower(REF_TO_XSQUEEZE.getSetting('MAC'))
if ADDON.getSetting('sendPlayOnStart')=="true":
  SENDPLAYONSTART = True
else:
  SENDPLAYONSTART = False

################################################################################
################################################################################
################################################################################
### CLASS SQUEEZEPLAYER

class SqueezePlayer:

  ##############################################################################
  #constructor - connect to the server and player so we can do stuff
  #other handy start up stuff
  def __init__(self,basicOnly=False):

    #optionally pass in a player MAC here to connect to a different player for the info display
    #if MAC is not None:
    #  log("Using MAC " + MAC)
    #  PLAYERMAC = MAC

    #serverIP still null, something went wrong...
    if SERVERIP=="":
      notify("Can't find LMS server","Try manually configuring one in XSqueeze settings")
      sys.exit()

    log("Attempting to connect to LMS named [" + SERVERNAME + "] at IP:  " + SERVERIP + " on CLI port: " + SERVERPORT)
    try:
      self.sc = Server(hostname=SERVERIP, port=SERVERPORT, username=SERVERUSER, password=SERVERPASS)
      self.sc.connect()
      log( "LMS Logged in: %s" % self.sc.logged_in )
      log( "LMS Version: %s" % self.sc.get_version() )
    except:
      log(" Couldn't connect to server!")
      notify(LANGUAGE(19613),LANGUAGE(19614))
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
        log( "Player is None! %s" % PLAYERMAC )
        raise Exception
    except Exception as inst:
        log(" Couldn't connect to player: " + PLAYERMAC , inst)
        notify(LANGUAGE(19615),LANGUAGE(19616))
        raise

    #initialise if we're called from XSqueeze as opposed to the chooser
    try:
        if not basicOnly:
          self.currentTrack = None
          self.coverURLs = None
          self.playlistDetails = None
          self.updatePlaylistDetails()
          self.updateCoverArtURLs()
          #if the user wants music to start straight away...
          if SENDPLAYONSTART:
            self.sb.request("play")
    except Exception as inst:
      log(" Error in initialisation of XSqueeze after connection to: " + PLAYERMAC , inst)
      raise


  ##############################################################################
  #get the current squeezebox two line display text and return it

  def getDisplay(self):
    displayText = self.sb.requestRaw("display ? ?", True)
    lines = displayText.split(" ")

    try:
      if lines[2] == "":
        lines[2] = "."
    except:
      lines[2] = "."

    try:
     if lines[3] == "":
        lines[3] = "."
    except:
      lines[3]="."

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
            #log("Status info is " + str(statusInfo))
            if("artwork_url" in statusInfo):
              statusArtwork = statusInfo.split('artwork_url:')
              statusArtwork = statusArtwork.pop(1)
              statusArtwork = statusArtwork.split(' ')
              statusArtwork = statusArtwork.pop(0)
              #log("statusArtwork is " + str(statusArtwork))
              #check we have a full url....
              if("http" not in statusArtwork):
                coverURL = "http://" + SERVERHTTPURL + "/" + statusArtwork
              else:
                coverURL = statusArtwork
            else:
              statusId = statusInfo.split('id:')
              statusId = statusId.pop(1)
              statusId = statusId.split(' ')
              statusId = statusId.pop(0)
              #log("StatusID is " + str(statusId))
              coverURL = "http://" + SERVERHTTPURL + "/music/" + str(statusId) + "/cover.jpg"
            #now append the coverURL to our list of URLs
            #log ("Appending future cover: " + str(count) + " from " + coverURL)
            coverURLs.append(coverURL)

          #Something went wrong, go with null string just to be safe...
          except Exception as inst:
            log("No cover art so appending null string for playlist index " + str(count), inst)
            coverURLs.append("")

      self.coverURLs = coverURLs

##  ##############################################################################
##  # Gets more info about a particular song

  def getSongInfo(self, id):
    encoded = self.sb.requestRaw("songinfo 0 1000 track_id:" + str(id), True)

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

    #convert all the data to the right types - there is a much more pythomnesque way to right this I am sure...

    try:
      item['id'] = int(item['id'])
    except KeyError:
      pass
    try:
       item['duration'] = float(item['duration'])
    except KeyError:
      pass
    try:
        item['album_id'] = int(item['album_id'])
    except KeyError:
      pass
    try:
        item['filesize'] = int(item['filesize'])
    except KeyError:
        pass
    try:
      item['coverart'] = int(item['coverart'])
    except KeyError:
      pass
    try:
        item['genre_id'] = int(item['genre_id'])
    except KeyError:
      pass
    try:
        item['artist_id'] = int(item['artist_id'])
    except KeyError:
      pass
    try:
        item['tracknum'] = int(item['tracknum'])
    except KeyError:
      pass
    try:
        item['year'] = int(item['year'])
    except KeyError:
      pass
    try:
        item['compilation'] = int(item['compilation'])
    except KeyError:
      pass
    try:
        item['channels'] = int(item['channels'])
    except KeyError:
      pass
    try:
      item['samplesize'] = int(item['samplesize'])
    except KeyError:
      pass
    try:
        item['samplerate'] = int(item['samplerate'])
    except KeyError:
      pass
    try:
        item['album_replay_gain'] = float(item['album_replay_gain'])
    except KeyError:
      pass
    try:
        item['replay_gain'] = float(item['replay_gain'])
    except KeyError:
      pass

    return item

  ##############################################################################
  # Send a button command text, e.g. 'pause' - to the player

  def button(self, text):
    self.sb.ir_button(text)
    #something probably changed, trigger an update test
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
  # Show some text on the player's screen

  def show(self,line1="", line2=""''"", duration=3, brightness=4, font="standard", centered=False):
    self.sb.show(line1,line2,duration,brightness,font,centered)

  def display(self, line1="", line2="", duration=1):
    self.sb.request("display " + line1 + " " + line2 + " " + str(duration))

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
    #log("Full Album Info: " + str(fullAlbumInfo))
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
    artists = self.sc.request_with_results("artists 0 100000")
    #log(str(artists))
    return artists[1]

  ##############################################################################
  # returns all albums by a particular artist given an artist_id

  def getAlbumsByArtistID(self,artistID):
    fullAlbums = []
    albums = self.sc.request_with_results("albums 0 100000 artist_id:" + str(artistID))
    #log(str(albums))
    for album in albums[1]:
      fullAlbumInfo = self.getAlbumInfo(album['id'])
      fullAlbums.append(fullAlbumInfo)
    return fullAlbums

  ##############################################################################
  # returns all albums in a particular genre given a genre_id

  def getAlbumsByGenreID(self,genreID):
    fullAlbums = []
    albums = self.sc.request_with_results("albums 0 100000 genre_id:" + str(genreID))
    #log(str(albums))
    for album in albums[1]:
      fullAlbumInfo = self.getAlbumInfo(album['id'])
      fullAlbums.append(fullAlbumInfo)
    return fullAlbums

  ##############################################################################
  # returns all albums for a given year

  def getAlbumsByYear(self,year):
    fullAlbums = []
    albums = self.sc.request_with_results("albums 0 100000 year:" + str(year))
    #log(str(albums))
    for album in albums[1]:
      fullAlbumInfo = self.getAlbumInfo(album['id'])
      fullAlbums.append(fullAlbumInfo)
    return fullAlbums

  ##############################################################################
  # returns all genres

  def getGenres(self):
    genres = self.sc.request_with_results("genres 0 100000")
    log(str(genres))
    return genres[1][1:]

  ##############################################################################
  # returns all years

  def getYears(self):
    years = self.parseSpecial("years 0 100000", "year", True)
    #log(str(years))
    years.reverse()
    return years

  ##############################################################################
  # returns radios root menu

  def parseSpecial(self, cmdString, splitOn, playerRequest=False):
    quotedColon = urllib.quote(':')
    if playerRequest:
      log("Player Request: " + str(cmdString))
      results = self.sb.requestRaw(cmdString)
    else:
      log("Server Request: " + str(cmdString))
      results = self.sc.requestRaw(cmdString)
    log("Result string: "+ pprint.pformat(results))
    #strip off the request stuff at the start
    resultStr = results[results.find(splitOn):]
    log("Split string: "+ pprint.pformat(resultStr))
    #ok now split the string on 'splitOn' to get each radio station
    chunks = resultStr.split(splitOn + "%3A")[1:]
    log("Processed Chunks: " + pprint.pformat(chunks))
    output=[]
    for chunk in chunks:
      chunk = chunk.strip()
      subResults = chunk.split(" ")
      #log("SUB: " + str(subResults))

      #fix missing splitOn post split
      subResults[0] = splitOn + "%3A" + subResults[0]
      #log("SUB + splitOn: " + str(subResults))

      item={}
      for subResult in subResults:
          #save item
          key,value = subResult.split(quotedColon,1)
          item[unquoteUni(key)] = unquoteUni(value)
      output.append(item)

    return output

  def getRadios(self):
    return self.parseSpecial("radios 0 100000", "icon", playerRequest=True)

  def getRadioStations(self, cmd, itemid):
    if(itemid)!="" and itemid is not None:
      return self.parseSpecial(urllib.quote(cmd) + " items 0 100000 item_id:" + itemid,"id",playerRequest=True)
    else:
      return self.parseSpecial(urllib.quote(cmd) + " items 0 100000","id",playerRequest=True)

  def getAppItemsList(self, cmd, itemid):
    if(itemid)!="" and itemid is not None:
      return self.parseSpecial(urllib.quote(cmd) + " items 0 100000 item_id:" + itemid,"id",playerRequest=True)
    else:
      return self.parseSpecial(urllib.quote(cmd) + " items 0 100000","id",playerRequest=True)

  def getFavouritesSub(self, itemid):
    return self.parseSpecial("favorites items 0 100000 item_id:" + itemid,"id",playerRequest=True)

  def queueRadio(self, cmd, itemid):
      self.sb.request(urllib.quote(cmd) + " playlist play item_id:" + itemid)

  def getApps(self):
    return self.parseSpecial("apps 0 100000","cmd", playerRequest=True)

  def getFavourites(self):
    return self.parseSpecial("favorites items 0 100000","id", playerRequest=True)

  def getPlaylists(self):
    #return self.parseSpecial("playlists 0 100000","id", playerRequest=True)
    pls = self.sc.request_with_results("playlists 0 100000 tags:u")
    log(str(pls))
    return pls[1][1:]

  ##############################################################################
  # Clear playlist and queue up a favourite item given

  def queueFavourite(self, item_id):
     self.sb.request("favorites playlist play item_id:" + item_id)

  ##############################################################################
  # Clear playlist and queue up a playlist item given

  def queuePlaylist(self, item_id, url):
     self.sb.request("playlist play " + url)

  ##############################################################################
  # Clear playlist and queue up an album given an album title and artist

  def queueAlbum(self, title, artist):
    if artist=="Various Artists":
      self.sb.request("playlist loadalbum * * " + urllib.quote(title))
    else:
      self.sb.request("playlist loadalbum * " + urllib.quote(artist) + " " + urllib.quote(title))

  ##############################################################################
  # Clear playlist and queue up random albums

  def playRandomAlbums(self):
    self.sb.request("randomplay albums")

  ##############################################################################
  # Clear playlist and queue up random songs

  def playRandomTracks(self):
    self.sb.request("randomplay tracks")

  ##############################################################################
  # Clear playlist and queue up random songs

  def getShuffle(self):
    state = int(self.sb.request("playlist shuffle ?"))
    if state==0: return False
    else: return True

  def setShuffle(self):
    state = int(self.sb.request("playlist shuffle ?"))
    if state==0:
      state = 1
      notify("Shuffle Playlist: ON","")
    else:
      state = 0
      notify("Shuffle Playlist: OFF","")
    self.sb.request("playlist shuffle "+ str(state), debug=True)
    self.updatePlaylistDetails()

  def getRepeat(self):
    state = int(self.sb.request("playlist repeat ?"))
    if state==0: return False
    else: return True

  def setRepeat(self):
    state = int(self.sb.request("playlist repeat ?"))
    if state==0:
      state = 2
      notify("Repeat Playlist: ON")
    else:
      state = 0
      notify("Repeat Playlist: OFF")
    self.sb.request("playlist repeat "+ str(state), debug=True)

  def rewind(self):
    self.sb.rewind()

  def forward(self):
    self.sb.forward()

  def getVolume(self):
    return self.sb.get_volume()

  def getpowerstate(self):
    return self.sb.get_power_state()
