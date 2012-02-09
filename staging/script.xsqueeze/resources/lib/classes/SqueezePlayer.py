import constants
import urllib
import Logger
import xbmc

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
    return self.unquote(lines[2]), self.unquote(lines[3])

  def songChanged(self):
    newSong = self.sb.get_track_current_title()
    if newSong != self.getCurrentTrack():
      Logger.log(" Song change to: " + newSong)
      self.setCurrentTrack(newSong)
      return True;
    else:  
      return False
  
  #downloads the cover art for the current song from the server
  def updateCoverArt(self):
    Logger.log( " Updating cover art" )
    try:
      coverURL = "http://" + self.serverHTTPURL + "/music/current/cover.jpg?player=" + self.playerMAC 
      Logger.log (" Getting: " + coverURL)
      coverArt = self.image.retrieve(  coverURL , constants.CHANGING_IMAGES_PATH + "currentCover.jpg" )
      Logger.log ("Retrieved new cover art")
    except Exception as inst:
      Logger.log( "Couldn't retrieve currernt cover art", inst)
    
  
  #functions to map buttons to actions and then update the display once actioned...
  #called in ActionHandler...
  def button(self, text):
    self.sb.ir_button(text)

  def getCurrentTrack(self):
    if not self.currentTrack:
       self.currentTrack = self.sb.get_track_current_title()
    return self.currentTrack

  def setCurrentTrack(self, newTrackName = ""):
    #if we're not supplied a new track name, let's go get one
    if not newTrackName:
      newTrackName = self.sb.get_track_current_title()
    self.currentTrack = newTrackName

  def getPlaylist(self):
    self.playlist = self.sb.playlist_get_info()
    currentIndex = int(self.sb.request("playlist index ?"))
    Logger.log ("Index: " + str(currentIndex) + " playlist is " + str(self.playlist))
    upcoming1 = ""
    upcoming2 = ""
    upcoming3 = ""
    upcoming1 = self.getConsolidatedTrackDetailsFromPlaylist(currentIndex+1)
    upcoming2 = self.getConsolidatedTrackDetailsFromPlaylist(currentIndex+2)
    upcoming3 = self.getConsolidatedTrackDetailsFromPlaylist(currentIndex+3)
    return upcoming1, upcoming2, upcoming3    
   
  def getConsolidatedTrackDetailsFromPlaylist(self, trackNum):
    songTitle = self.playlist[trackNum]['title']
    songArtist = self.playlist[trackNum]['artist']
    songAlbum = self.playlist[trackNum]['album']      
    return songTitle + " by " + songArtist + " from " + songAlbum

  #constructor - connect to the server and player so we can do stuff
  def __init__(self):
    
    #get the various settings... 
    self.serverIP    = constants.__addon__.getSetting('serverIP')
    self.serverPort  = constants.__addon__.getSetting('serverPort')
    self.serverHTTPURL   = self.serverIP + ":9000"
    self.playerMAC   = constants.__addon__.getSetting('playerMAC')

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
      Logger.log( "Connected to: %s" % self.playerMAC )
    except:
      Logger.log(" Couldn't connect to player! " + self.playerMAC )
      xbmc.executebuiltin("XBMC.Notification("+ constants.__addonname__ +": Couldn't connect to player!,Check you player settings)")
      raise

    #take note of the current track...actually, no, instead let it trigger
    #an update on the first time through the loop
    self.currentTrack = ""       
    self.updateCoverArt()
    self.getPlaylist()
