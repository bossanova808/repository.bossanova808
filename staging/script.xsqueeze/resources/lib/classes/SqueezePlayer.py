import constants
import urllib
import Logger
import xbmc
import sys
import os

from pysqueezecenter.server import Server
from pysqueezecenter.player import Player


################################################################################
################################################################################
### CLASS SQUEEZEPLAYER

class SqueezePlayer:

  #unquote text coming back from LMS
  def unquote(self, text):
      try:
          import urllib.parse
          return urllib.parse.unquote(text, encoding=self.charset)
      except ImportError:
          import urllib
          return urllib.unquote(text)

  #get the current two line display text and return it
  def getDisplay(self):
    displayText = self.sb.requestRaw("display ? ?", True)
    lines = displayText.split(" ")
    if lines[2] == "":
      lines[2] = "."
    if lines[3] == "":
      lines[3] = "."
    return self.unquote(lines[2]), self.unquote(lines[3])

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

  #downloads the cover art for the current song from the server
  def updateCoverArt(self, initialise=False):

    #is this the first time through?
    if not initialise:
      songChanged = self.songChanged()
    else:
      Logger.log (" Triggering update to cover art as we're initialising..." )
      songChanged = True

    #if song has changed, get new cover art etc.
    if songChanged:
      Logger.log( " Song Changed - Updating cover art" )

##      try:
##        os.remove(constants.CHANGING_IMAGES_PATH +'currentCover.jpg')
##        os.remove(constants.CHANGING_IMAGES_PATH +'currentCoverPlus1.jpg')
##        os.remove(constants.CHANGING_IMAGES_PATH +'currentCoverPlus2.jpg')
##        os.remove(constants.CHANGING_IMAGES_PATH +'currentCoverPlus3.jpg')
##      except Exception as inst:
##        Logger.log("Error removing old art, tried and failed -> perhaps there wasn't any?")

      try:
        coverURL = "http://" + self.serverHTTPURL + "/music/current/cover.jpg?player=" + self.playerMAC
        Logger.log (" Getting: " + coverURL)
        coverArt = self.image.retrieve(  coverURL , constants.CHANGING_IMAGES_PATH + "currentCover.jpg" )
        Logger.log ("Retrieved new cover art")
      except Exception as inst:
        Logger.log( "Couldn't retrieve currernt cover art", inst)

      #start at the song after current
      index = int(self.sb.request("playlist index ?"))
      upcomer = index + 1
      end = index + 4

      for count in range(upcomer,end):
        try:
          currentID = self.playlist[count]['id']
          coverURL = "http://" + self.serverHTTPURL + "/music/" + str(currentID) + "/cover.jpg"
          Logger.log (" Getting future cover: " + str(count) + " from " + coverURL)
          coverArt = self.image.retrieve(  coverURL , constants.CHANGING_IMAGES_PATH + "currentCoverPlus" + str(count-index) + ".jpg" )
          Logger.log ("Retrieved future cover")
        except Exception as inst:
          Logger.log("No cover art for playlist index " + str(count), inst)
          #couldn't get cover art - just use the current cover for now
          coverArt = self.image.retrieve(  coverURL , constants.CHANGING_IMAGES_PATH + "currentCoverPlus" + str(count-index) + ".jpg" )

##      #grab a list of up to 3 tracks after the current one (if the playlist is that long)
##      idList = []
##      while  (upcomer < len(self.playlist)) and (upcomer < end):
##        idList.append(self.playlist[upcomer]['id'])
##        upcomer += 1
##      #for each track id get the image
##      for count, id in enumerate(idList):
##        coverURL = "http://" + self.serverHTTPURL + "/music/" + str(id) + "/cover.jpg"
##        Logger.log (" Getting future cover: " + str(count) + " from " + coverURL)
##        coverArt = self.image.retrieve(  coverURL , constants.CHANGING_IMAGES_PATH + "currentCoverPlus" + str(count+1) + ".jpg" )
##        Logger.log ("Retrieved future cover")


  #functions to map buttons to actions and then update the display once actioned...
  #called in ActionHandler...
  def button(self, text):
    self.sb.ir_button(text)

  def getPlaylist(self):
    self.playlist = self.sb.playlist_get_info()
    currentIndex = int(self.sb.request("playlist index ?"))
    #Logger.log ("Current index: " + str(currentIndex) + " len(playlist): " + str(len(self.playlist)) + " Playlist is: " + str(self.playlist))
    #the text list of upcoming tracks
    upcoming1 = self.getConsolidatedTrackDetailsFromPlaylist(currentIndex+1)
    upcoming2 = self.getConsolidatedTrackDetailsFromPlaylist(currentIndex+2)
    upcoming3 = self.getConsolidatedTrackDetailsFromPlaylist(currentIndex+3)
    return upcoming1, upcoming2, upcoming3

  def getCurrentTrack(self):
    currentIndex = int(self.sb.request("playlist index ?"))
    title = self.playlist[currentIndex]['title']
    artist = self.playlist[currentIndex]['artist']
    album = self.playlist[currentIndex]['album']
    return title, artist, album

  def getTrackLength(self):
    return self.sb.get_track_duration()

  def getMode(self):
      return self.sb.get_mode()

  def getTrackElapsed(self):
    return self.sb.get_time_elapsed()

  def getConsolidatedTrackDetailsFromPlaylist(self, trackNum):
    #if we are near the end of the playlist, don't return tracks...
    returnText = "<nothing>"
    if trackNum < len(self.playlist):
      songTitle = self.playlist[trackNum]['title']
      songIndex = str(self.playlist[trackNum]['position'])
      songArtist = self.playlist[trackNum]['artist']
      songAlbum = self.playlist[trackNum]['album']
      returnText = songIndex + ". " + songTitle + " (by " + songArtist + ", from " + songAlbum +")"
    return returnText

  #constructor - connect to the server and player so we can do stuff
  def __init__(self):

    #get the various settings...
    self.serverIP    = constants.__addon__.getSetting('serverIP')
    self.serverPort  = constants.__addon__.getSetting('serverPort')
    self.serverHTTPURL   = self.serverIP + ":9000"
    #LMS is case sensitive and all MACs need to be lower case!!
    self.playerMAC   = str.lower(constants.__addon__.getSetting('playerMAC'))

    #a handle for opening images
    self.image = urllib.URLopener()

    #connect to server
    Logger.log("Attempting to connect to LMS at:  " + self.serverIP + " on port: " + self.serverPort)
    try:
      self.sc = Server(hostname=self.serverIP, port=self.serverPort)
      self.sc.connect()
      Logger.log( "Logged in: %s" % self.sc.logged_in )
      Logger.log( "Version: %s" % self.sc.get_version() )
    except:
      Logger.log(" Couldn't connect to server!")
      xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Couldn't connect to server!,Check your server settings)")
      raise

    #connect to player
    Logger.log( "Attempting to connect to player: " + self.playerMAC)
    try:
      self.sb = self.sc.get_player(self.playerMAC)
      if self.sb:
        Logger.log( "Connected to: %s" % self.playerMAC )
        state = self.sb.get_power_state()
        Logger.log ( "Power state is: " + str (state) )
      else:
        Logger.log( "Player NoneType: %s" % self.playerMAC )
        raise Exception
    except Exception as inst:
      Logger.log(" Couldn't connect to player: " + self.playerMAC , inst)
      xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Couldn't connect to player!,Check you player settings)")
      sys.exit()

    #initialise
    self.currentTrack = self.sb.get_track_title()
    self.getPlaylist()
    self.updateCoverArt(initialise=True)
