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
    Logger.log("Attempting to connect to LMS at:  " + constants.SERVERIP + " on port: " + constants.SERVERPORT)
    try:
      self.sc = Server(hostname=constants.SERVERIP, port=constants.SERVERPORT)
      self.sc.connect()
      Logger.log( "Logged in: %s" % self.sc.logged_in )
      Logger.log( "Version: %s" % self.sc.get_version() )
    except:
      Logger.log(" Couldn't connect to server!")
      xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Couldn't connect to server!,Check your server settings)")
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
        Logger.log( "Player NoneType: %s" % constants.PLAYERMAC )
        raise Exception
    except Exception as inst:
      Logger.log(" Couldn't connect to player: " + constants.PLAYERMAC , inst)
      xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Couldn't connect to player!,Check you player settings)")
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
    return self.unquote(lines[2]), self.unquote(lines[3])

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

      for count in range(upcomer,end):
        try:
          currentID = self.playlist[count]['id']
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

