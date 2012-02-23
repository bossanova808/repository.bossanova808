import constants
import urllib
import Logger
import xbmc
import sys
import os

from pysqueezecenter.server import Server
from pysqueezecenter.player import Player

################################################################################
### CLASS SQUEEZEPLAYER

class SqueezePlayer:

  ##############################################################################
  #constructor - connect to the server and player so we can do stuff
  #other handy start up stuff
  def __init__(self):

    #connect to server
    Logger.log("Attempting to connect to LMS named [" + constants.SERVERNAME + "] at IP:  " + constants.SERVERIP + " on CLI port: " + constants.SERVERPORT)
    try:
      self.sc = Server(hostname=constants.SERVERIP, port=constants.SERVERPORT)
      self.sc.connect()
      Logger.log( "LMS Logged in: %s" % self.sc.logged_in )
      Logger.log( "LMS Version: %s" % self.sc.get_version() )
    except:
      Logger.log(" Couldn't connect to server!")
      Logger.notify(constants.__language__(19613),constants.__language__(19614))
      raise

    #connect to player
    Logger.log( "Attempting to connect to player: " + constants.PLAYERMAC)
    try:
      self.sb = self.sc.get_player(constants.PLAYERMAC)
      if self.sb:
        Logger.log( "Connected to: %s" % constants.PLAYERMAC )
        state = self.sb.get_power_state()
        Logger.log ( "Power state is: " + str (state) )
      else:
        Logger.log( "Player is NoneType: %s" % constants.PLAYERMAC )
        raise Exception
    except Exception as inst:
      Logger.log(" Couldn't connect to player: " + constants.PLAYERMAC , inst)
      Logger.notify(constants.__language__(19615),constants.__language__(19616))
      sys.exit()

    #initialise
    self.currentTrack = self.sb.get_track_title()
    self.getPlaylist()

  ##############################################################################
  #unquote text coming back from LMS
  def unquote(self, text):
      try:
          import urllib.parse
          return urllib.parse.unquote(text, encoding=self.charset)
      except ImportError:
          import urllib
          return urllib.unquote(text)

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
    cleanedLines.append(self.unquote(lines[2]))
    cleanedLines.append(self.unquote(lines[3]))

    #print(cleanedLines)

    newLines=[]
    for line in cleanedLines:
      line = line.replace(u'solidblock', '*')
      line = line.replace(u'leftprogress4', u'*')
      line = line.replace(u'leftprogress2', u'*')
      line = line.replace(u'leftprogress0', u'(Mute)')
      line = line.replace(u'rightprogress0', u' ')
      line = line.replace(u'rightprogress4', u'(Max)')
      line = line.replace(u'middleprogress0', u' ')
      line = line.replace(u'\x1f',"")
      newLines.append(line)

    #print(newLines)

    return newLines[0], newLines[1]

  ##############################################################################
  #check if song changed and update local reference if so
  # returns boolean - but of course only once on each change

  def songChanged(self):
    oldSong = self.currentTrack
    newSong = self.sb.get_track_title()
    #Logger.log("newSong [" + newSong +"] old song [" + oldSong + "]")
    if newSong != oldSong:
      Logger.log(" Song change to: " + newSong)
      self.currentTrack = newSong
      return True;
    else:
      return False

  ##############################################################################
  # returns the URLs for the current and next three track cover art images

  def getCoverArtURLs(self):

      coverURLs = []

      #start at this song , end at + 3
      index = int(self.sb.request("playlist index ?"))
      upcomer = index
      end = index + 4

      #currently uses the track_id in the url - works well
      #supposed to use the cover_id number but this doesn't work so well...
      for count in range(upcomer,end):
        try:
          #print self.playlist[count]
          currentID = self.playlist[count]['id']
          #print "id " + str(currentID)
          #songinfo = self.getSongInfo(currentID)
          #print "songinfo" + str(songinfo)
          #currentCID = str(songinfo[0]['coverid'])
          #print "cid: " + currentCID
          coverURL = "http://" + constants.SERVERHTTPURL + "/music/" + str(currentID) + "/cover.jpg"
          #Logger.log (" Appending future cover: " + str(count) + " from " + coverURL)
          coverURLs.append(coverURL)
        except Exception as inst:
          #Logger.log("No cover art so appending null string for playlist index " + str(count), inst)
          coverURLs.append("")

      return coverURLs

  ##############################################################################
  #functions to map buttons to squeezebox actions
  #called in ActionHandler...


  ##############################################################################
  # Gets more info about a particular song

  def getSongInfo(self, id):
    encoded = self.sb.requestRaw("songinfo 0 100 track_id:" + str(id), True)

    encoded = encoded[57:]
    #print(encoded)
    list = encoded.split(" ")
    #print list

    decodedList = []
    for item in list:
      cleanItem = self.unquote(item)
      decodedList.append(cleanItem)

    #print decodedList

    songinfo = []
    item = {}
    for info in decodedList:
        info = info.split(':')
        key = info.pop(0)
        if key:
            item[key] = ':'.join(info)

    # 9 id:39 title:I'm Not The Man artist:10000 Maniacs coverid:94339a48 duration:226.36 album_id:4 filesize:22796274 genre:Pop coverart:1 artwork_track_id:94339a48
    # album:MTV Unplugged modificationTime:Thursday, November 27, 2008, 5:24 PM type:flc genre_id:4 bitrate:805kbps VBR artist_id:11 tracknum:4 year:1993 compilation:0
    # addedTime:Thursday, December 8, 2011, 11:15 PM channels:2 samplesize:16 samplerate:44100 lastUpdated:Thursday, December 8, 2011, 11:15 PM album_replay_gain:-6.46 replay_gain:-3.46

    #convert all the data to the right types
    #item['position'] = int(item['position'])
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

    songinfo.append(item)
    #print "songinfo is now " + str(songinfo)
    return songinfo


  ##############################################################################
  #functions to map buttons to squeezebox actions
  #called in ActionHandler...

  def button(self, text):
    self.sb.ir_button(text)

  ##############################################################################
  # returns the consolidated details of the next three tracks after the current

  def getPlaylist(self):
    self.playlist = self.sb.playlist_get_info()
    currentIndex = int(self.sb.request("playlist index ?"))
    #Logger.log ("Current index: " + str(currentIndex) + " len(playlist): " + str(len(self.playlist)) + " Playlist is: " + str(self.playlist))
    #the text list of upcoming tracks
    upcoming1 = self.getConsolidatedTrackDetailsFromPlaylist(currentIndex+1)
    upcoming2 = self.getConsolidatedTrackDetailsFromPlaylist(currentIndex+2)
    upcoming3 = self.getConsolidatedTrackDetailsFromPlaylist(currentIndex+3)
    return upcoming1, upcoming2, upcoming3

  ##############################################################################
  # retruns the details of the current track (title, artist, album)
  # or "" if not avialble

  def getCurrentTrack(self):
    currentIndex = int(self.sb.request("playlist index ?"))
    try:
      if 'title' in self.playlist[currentIndex]:
        title = self.playlist[currentIndex]['title']
      else:
        title = ""
      if 'artist' in self.playlist[currentIndex]:
        artist = self.playlist[currentIndex]['artist']
      else:
          artist = ""
      if 'album' in self.playlist[currentIndex]:
        album = self.playlist[currentIndex]['album']
      else:
        album = ""
    except IndexError:
      title= ""
      artist = ""
      album = ""

    #print repr(artist)

    return title, artist, album

  ##############################################################################
  # returns current track length if available (check for 0 etc. at other end)

  def getTrackLength(self):
    return self.sb.get_track_duration()

  ##############################################################################
  # returns current mode ('play' 'pause' or 'stop'

  def getMode(self):
      return self.sb.get_mode()

  ##############################################################################
  # returns length of time in seconds the current track has played for

  def getTrackElapsed(self):
    return self.sb.get_time_elapsed()

  ##############################################################################
  # given a track number return a consolidated string of track details

  def getConsolidatedTrackDetailsFromPlaylist(self, trackNum):
    #if we are near the end of the playlist, don't return tracks...
    returnText = ""
    if trackNum < len(self.playlist):
      songTitle = self.playlist[trackNum]['title']
      songIndex = str(self.playlist[trackNum]['position'])
      songArtist = self.playlist[trackNum]['artist']
      songAlbum = self.playlist[trackNum]['album']
      returnText = songIndex + ". " + songTitle + " (by " + songArtist + ", from " + songAlbum +")"
    return returnText

