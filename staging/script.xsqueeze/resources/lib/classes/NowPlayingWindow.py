import xbmcgui
import constants
import Logger
import sys
import threading

#a file that gives nice names to action numbers
from actionmap import *
from traceback import print_exc

from SqueezePlayer import *

################################################################################
################################################################################
### Class ActionHandler (i.e. a window)

class NowPlayingWindow(xbmcgui.WindowXML):

  ##############################################################################
  #constructor - create controls & add them to the window
  #create our SqueezePlayer object
  #create a threadlock to make squeeze CLI operations safe
  #initialise a few object vars

  def __init__( self, *args, **kwargs ):

    #blanks the screen - this is crude, and probably wrong, but works
    self.addControl(xbmcgui.ControlImage(0,0,1920,1080, 'black.png'))

    #create a player instance (is really a player + server combo)
    try:
      self.player = SqueezePlayer()
    except:
      Logger.log( "### Failed to create SqueezePlayer object " )
      print_exc()
      sys.exit()

    #URLs for cover art are stored here so we can detect changes
    self.coverURLs = [""]
    #a thread lock to use so that each SB related action is finished before the
    #next one is sent - without this you get race conditions!
    self.lock = threading.Lock()

  ##############################################################################
  #the method called when the window is inited
  #starts the GUI update thread...
  def onInit( self ):

    Logger.log("On Init, window id is "+ str(xbmcgui.getCurrentWindowId()))

    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("WINDOWID", str(xbmcgui.getCurrentWindowId()))

    #Set some basic properties
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("PLAYERMAC", constants.PLAYERMAC)
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("SERVER", constants.SERVERNAME)

    #Logger.log("onInit")
    self.running = True
    self.thread = threading.Thread(target=self.update)
    self.thread.setDaemon(True)
    Logger.log("Starting GUI update thread")
    self.thread.start()

  ##############################################################################
  #Maps XBMC window actions to squeezeslave methods
  def onAction( self, action ):

  #if we handle this action, do it, otherwise null it out
    try:
      actionNum = action.getId()
      actionName = ACTION_NAMES[actionNum]
      actionSqueeze = SQUEEZE_CODES[actionName]
    except KeyError:
      #action is not in our handled list (see actionmap.py)
      #Logger.log("Not handling eventid " + str(action.getId()))
      actionNum = 0
      actionName = ACTION_NAMES[actionNum]
      actionSqueeze = SQUEEZE_CODES[actionName]

    if actionNum != 0:
      Logger.log("Handling action id: " + str(actionNum) +  " Name: " + actionName + " SqueezeCode if any: " + actionSqueeze)

    if action == ACTION_CODES['ACTION_PAUSE']:
        xbmc.executebuiltin("XBMC.ActivateWindow(10500)")

    #intercept special XBMC ones first
    if action == ACTION_CODES['ACTION_PREVIOUS_MENU']:
      Logger.log("XBMC Action: Close")
      #we're controlling a local squeezeslave - best to stop the music before we kill it
      #otherwise it oddly resumes automatically on restart
      if constants.CONTROLSLAVE and not constants.CONTROLLERONLY:
        Logger.notify(constants.__language__(19612),constants.__language__(19609))
        with self.lock:
          self.player.button("stop")
      self.running = False
      self.close()

    #elif etc

    #otherwise pass the button code to the squeezeplayer & trigger a matching player action if we have one
    else:
       if actionSqueeze:
        Logger.log("SqueezePlayer Action: " + actionSqueeze)
        with self.lock:
          self.player.button(actionSqueeze)

  ##############################################################################
  #this is our GUI update thread and is used to update the window's display
  #must lock other threads

  def update(self):
    while self.running:
      with self.lock:
        #Logger.log("Update cycle...start")
        #always update the line display even if song hasn't changed
        self.updateLineDisplay()
        #Logger.log("Update cycle...1")
        #self.updateCoverArt(force)
        if self.player.songChanged():
          self.updateCoverArtFromURLs()
          #Logger.log("Update cycle...2")
          self.updateCurrentTrack()
          #Logger.log("Update cycle...3")
          if not self.player.getMode()=="stop":
            self.updateTrackProgress()
          #Logger.log("Update cycle...4")
          self.updateUpcomingTracks()
          #Logger.log("Update cycle...5")
          self.updatePlaylistDetails()

  ##############################################################################
  # get the cover URLS and pass them into window properties

  def updateCoverArtFromURLs(self):
    newCoverURLs = self.player.getCoverArtURLs()
    #check if the URLs have changed...if so update the cover art
    if newCoverURLs[0] != self.coverURLs[0]:
      self.getControl( constants.MAINCOVERART  ).setImage( newCoverURLs[0]  )
      self.getControl( constants.UPCOMING1COVERART  ).setImage( newCoverURLs[1]  )
      self.getControl( constants.UPCOMING2COVERART  ).setImage( newCoverURLs[2]  )
      self.getControl( constants.UPCOMING3COVERART  ).setImage( newCoverURLs[3]  )
      self.coverURLs = newCoverURLs

  ##############################################################################
  # updates the 2 line squeeze display text to the window properties
  def updateLineDisplay(self):
    newLine1, newLine2 = self.player.getDisplay()
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("DISPLAYLINE1", newLine1)
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("DISPLAYLINE2", newLine2)


  ##############################################################################
  # update all the current playing track stuff into the window properties
  def updatePlaylistDetails(self):
    playlistDetails = self.player.getPlaylistDetails()
    for trackOffset in range(0,len(playlistDetails)):
      #print("Settings window INFOs with " + str(playlistDetails[trackOffset]))
      stub = "XS_TRACK_" + str(trackOffset) + "_"

      #each element in this list looks like:
      #songinfo[{'album_id': 10, 'channels': 2, 'samplesize': 16, 'year': 2004, 'duration': 276.72000000000003, 'samplerate': 44100, 'id': 122, 'album': 'Gold - Greatest Hits', 'title': 'Lay All Your Love on Me', 'tracknum': 5, 'filesize': 34201960, 'artist_id': 17, 'type': 'flc', 'coverart': 1, 'compilation': 0, 'artwork_track_id': 'ed1047ba', 'lastUpdated': 'Thursday, December 8, 2011, 11:15 PM', 'modificationTime': 'Saturday, October 27, 2007, 5:14 PM', 'album_replay_gain': -7.7699999999999996, 'coverid': 'ed1047ba', 'genre': 'Pop', 'bitrate': '988kbps VBR', 'artist': 'Abba', 'addedTime': 'Thursday, December 8, 2011, 11:15 PM', 'replay_gain': -6.5199999999999996, 'genre_id': 4}]
      try:
        xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty(stub + "TITLE", playlistDetails[trackOffset]['title'])
        xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty(stub + "ARTIST", playlistDetails[trackOffset]['artist'])
        xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty(stub + "ALBUM", playlistDetails[trackOffset]['album'])
        xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty(stub + "TRACKNUM", str(playlistDetails[trackOffset]['tracknum']))
        duration = self.GetInHMS(int(playlistDetails[trackOffset]['duration']))
        xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty(stub + "TRACKLENGTH", duration)
        xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty(stub + "YEAR", str(playlistDetails[trackOffset]['year']))
      except IndexError:
        Logger.log("Index error in ")
      except Exception as inst:
        Logger.log("General exception: ", inst)

  ##############################################################################
  # update all the current playing track stuff into the window properties
  def updateCurrentTrack(self):
    title, artist, album = self.player.getCurrentTrack()
    uniartist = artist
    urllib.quote(uniartist.encode('utf8'))
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("CURRENTTITLE", title)
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("CURRENTARTIST", artist)
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("UNIARTIST", uniartist)
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("CURRENTALBUM", album)

  ##############################################################################
  # update the coming track list to the window properties
  def updateUpcomingTracks(self):
    upcoming1, upcoming2, upcoming3 = self.player.getPlaylist()
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("UPCOMING1", upcoming1)
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("UPCOMING2", upcoming2)
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("UPCOMING3", upcoming3)

  ##############################################################################
  # updates the track progress dialog
  def updateTrackProgress(self):
    trackLength = float(self.player.getTrackLength())
    trackElapsed = float(self.player.getTrackElapsed())
    trackRemaining = trackLength - trackElapsed
    if trackLength != 0.0:
      xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("TRACKELAPSED", self.GetInHMS(int(trackElapsed)))
      xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("TRACKREMAINING", self.GetInHMS(int(trackRemaining)))
      xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("TRACKLENGTH", self.GetInHMS(int(trackLength)))
      percent = int((trackElapsed / trackLength) * 100.0)
      self.getControl( constants.CURRENTPROGRESS ).setPercent ( percent )
    else:
      self.getControl( constants.CURRENTELAPSED   ).setLabel( ""   )
      self.getControl( constants.CURRENTREMAINING ).setLabel( ""   )
      self.getControl( constants.CURRENTLENGTH    ).setLabel( ""   )

  ##############################################################################
  # helper function - convert player seconds to summat nice for screen 00:00 etc
  def GetInHMS(self, seconds):
      hours = seconds / 3600
      seconds -= 3600*hours
      minutes = seconds / 60
      seconds -= 60*minutes
      if hours == 0:
          return "%02d:%02d" % (minutes, seconds)
      return "%02d:%02d:%02d" % (hours, minutes, seconds)





