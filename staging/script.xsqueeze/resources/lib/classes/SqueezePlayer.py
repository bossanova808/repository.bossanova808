import constants
import urllib
import Logger
import xbmc
import sys

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

    #start at the song after current
    index = int(self.sb.request("playlist index ?"))
    upcomer = index + 1
    end = index + 4
    #grab a list of up to 3 tracks after the current one (if the playlist is that long)
    idList = []
    while  (upcomer < len(self.playlist)) and (upcomer < end): 
      idList.append(self.playlist[upcomer]['id'])
      upcomer += 1
    #for each track id get the image
    for count, id in enumerate(idList):
      coverURL = "http://" + self.serverHTTPURL + "/music/" + str(id) + "/cover.jpg" 
      Logger.log (" Getting future cover: " + str(count) + " from " + coverURL)
      coverArt = self.image.retrieve(  coverURL , constants.CHANGING_IMAGES_PATH + "currentCoverPlus" + str(count+1) + ".jpg" )
      Logger.log ("Retrieved new cover art")
    
  
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
    Logger.log ("Current index: " + str(currentIndex) + " len(playlist): " + str(len(self.playlist)) + " Playlist is: " + str(self.playlist))
    #the text list of upcoming tracks
    upcoming1 = self.getConsolidatedTrackDetailsFromPlaylist(currentIndex+1)
    upcoming2 = self.getConsolidatedTrackDetailsFromPlaylist(currentIndex+2)
    upcoming3 = self.getConsolidatedTrackDetailsFromPlaylist(currentIndex+3)    
    return upcoming1, upcoming2, upcoming3    
      
  
  def getConsolidatedTrackDetailsFromPlaylist(self, trackNum):
    #if we are near the end of the playlist, don't return tracks...
    returnText = "<nothing>"
    if trackNum < len(self.playlist):
      songTitle = self.playlist[trackNum]['title']
      songArtist = self.playlist[trackNum]['artist']
      songAlbum = self.playlist[trackNum]['album']      
      returnText = songTitle + " by " + songArtist + " from " + songAlbum
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

    #take note of the current track...actually, no, instead let it trigger
    #an update on the first time through the loop
    self.currentTrack = ""       
    self.getPlaylist()
    self.updateCoverArt()
