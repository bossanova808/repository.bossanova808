import xbmc, xbmcgui
import constants
import Logger
import sys
import threading

#a file that gives nice names to action numbers
from actionmap import *
from traceback import print_exc
from SqueezePlayer import *
from utils import *

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
    self.background = xbmcgui.ControlImage(0,0,1280,720, 'black.png')
    self.addControl(self.background)

    #create a player instance (is really a player + server combo)
    try:
      self.player = SqueezePlayer()
    except:
      Logger.log( "### Failed to create SqueezePlayer object " )
      print_exc()
      sys.exit()

    #URLs for cover art are stored here so we can detect changes
    self.coverURLs = [""]
    #and playlist details too
    self.playlistDetails = [""]
    self.playlist = [""]
    #a thread lock to use so that each SB related action is finished before the
    #next one is sent - without this you get race conditions!
    self.lock = threading.Lock()

  ##############################################################################
  #the method called when the window is inited
  #starts the GUI update thread...
  def onInit( self ):

    #get the window ID, and if present, the hidden button for artist slideshow...
    self.windowID = xbmcgui.getCurrentWindowId()
    try:
      self.hiddenButton = self.getControl(999)
    except:
      pass
    Logger.log("On Init, window id is "+ str(self.windowID))

    #Set some basic properties
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_WINDOWID", str(self.windowID))
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_PLAYERMAC", constants.PLAYERMAC)
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_SERVER", constants.SERVERNAME)
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_NAME", "XSqueeze "+ constants.__version__)

    Logger.log("Starting GUI update thread")
    self.running = True
    self.thread = threading.Thread(target=self.update)
    self.thread.setDaemon(True)
    self.thread.start()

    Logger.log("Starting ArtistSlideshow thread")
    self.thread2 = threading.Thread(target=self.runArtistSlideshow)
    self.thread2.setDaemon(True)
    self.thread2.start()

  ##############################################################################
  # Essentially the reverse of init - need to remove any controls we added and blank out the properties
  # for a cleaner exit

  def deInit(self):

      Logger.log("deInit() called - cleaning covers, playlist and waiting on artist.slideshow to signal finish...")

      xbmcgui.Window(xbmcgui.getCurrentWindowId()).clearProperty("ArtistSlideshow.ExternalCall")
      Logger.log("Waiting for artistslideshow to stop")
      while (not xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty("ArtistSlideshow.CleanupComplete") == "True"):
        Logger.log("Still waiting for artistslideshow to stop")
        xbmc.sleep(1000)

      Logger.log("Cleaning covers and playlist properties.....")
      self.cleanupPlaylist(0)
      self.cleanupCovers()
      self.removeControl(self.background)
      del(self.background)
      xbmcgui.Window(self.windowID).clearProperty("XSQUEEZE_WINDOWID")
      #hold here for up to 5 seconds while we wait for artist slideshow to exit...
      count = 0

##      while xbmcgui.Window(self.windowID).getProperty("Artistslideshow.CleanupComplete")!= 'True':
##        Logger.log("Sleeping 0.5s waiting for artist.slideshow to finish (max 5 seconds)")
##        xbmc.sleep(500)
##        count+=1
##        if count > 100:
##          break

      Logger.log("deInit() complete. Artist Slideshow Cleanup Property = " + str(xbmcgui.Window(self.windowID).getProperty("Artistslideshow.CleanupComplete")))

  ##############################################################################
  # Handle window acitions
  # generally by mapping XBMC window actions to squeezeslave methods

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

    #if actionNum != 0:
    #  Logger.log("Handling action id: " + str(actionNum) +  " Name: " + actionName + " SqueezeCode if any: " + actionSqueeze)

    #for testing xbmc's internal playlist - pause and display playlist...
    #10500 = music playlist
    #if action == ACTION_CODES['ACTION_PAUSE']:
    #    xbmc.executebuiltin("XBMC.ActivateWindow(10500)")

    #intercept special XBMC ones first
    if action == ACTION_CODES['ACTION_PREVIOUS_MENU'] or action == ACTION_CODES['ACTION_NAV_BACK']:
      #make sure we've only been through here once....
      if self.running:
        Logger.log("XBMC Action: Close")
        #prevent the GUI update thread from updating...
        self.running = False

        #we're controlling a local squeezeslave - best to stop the music before we kill it
        #otherwise it oddly resumes automatically on restart
        if constants.CONTROLSLAVE and not constants.CONTROLLERONLY:
          Logger.notify(constants.__language__(19612),constants.__language__(19609))
          with self.lock:
            self.player.button("stop")

        #tidy up before the window closes...
        self.deInit()

##      #force artist.slideshow to get the message that the artist has been clear...
##      try:
##        self.setFocus(self.hiddenButton)
##      except:
##        pass

        #now close the window before we kill it
        self.close()

      #user has probably hammered the close button...do nothing
      else:
        Logger.notify(constants.__language__(19622),constants.__language__(19623))
        pass


    #elif etc

    #otherwise pass the button code to the squeezeplayer & trigger a matching player action if we have one
    else:
       if actionSqueeze:
        Logger.log("SqueezePlayer Action: " + actionSqueeze)
        with self.lock:
          self.player.button(actionSqueeze)

  ##############################################################################
  # Cleanup the cover art images

  def cleanupCovers (self):

    #Logger.log("Clearing cover images.....")
    self.getControl( constants.MAINCOVERART  ).setImage( "" )
    self.getControl( constants.UPCOMING1COVERART  ).setImage( "" )
    self.getControl( constants.UPCOMING2COVERART  ).setImage( "" )
    self.getControl( constants.UPCOMING3COVERART  ).setImage( "" )

  ##############################################################################
  # Cleanup the window labels, by default for all track 0 to 10
  # otherwise, from X to 10

  def cleanupPlaylist (self, start=0):

    #Logger.log("Clearing playlist properties....")

    for trackOffset in range(start,10):
      stub = "XSQUEEZE_TRACK_" + str(trackOffset) + "_"
      xbmcgui.Window(self.windowID).clearProperty(stub + "TITLE")
      xbmcgui.Window(self.windowID).clearProperty(stub + "ARTIST")
      xbmcgui.Window(self.windowID).clearProperty(stub + "UNIARTIST")
      xbmcgui.Window(self.windowID).clearProperty(stub + "ALBUM")
      xbmcgui.Window(self.windowID).clearProperty(stub + "TRACKNUM")
      xbmcgui.Window(self.windowID).clearProperty(stub + "TRACKLENGTH")
      xbmcgui.Window(self.windowID).clearProperty(stub + "ALBUMYEAR")
      xbmcgui.Window(self.windowID).clearProperty(stub + "INPLAYLIST")
      xbmcgui.Window(self.windowID).clearProperty(stub + "ELAPSED")
      xbmcgui.Window(self.windowID).clearProperty(stub + "REMAINING")
      xbmcgui.Window(self.windowID).clearProperty(stub + "DURATION")

  ##############################################################################
  # Kick off the artist.slideshow

  def runArtistSlideshow(self):
     #startup artistslideshow
     xbmcgui.Window(self.windowID).setProperty("ArtistSlideshow.ExternalCall", "True")
     artistslideshow = "RunScript(script.artistslideshow,windowid=%s&artistfield=%s)" % (self.windowID, "XSQUEEZE_TRACK_0_ARTIST")
     xbmc.executebuiltin(artistslideshow)

  ##############################################################################
  #this is our GUI update thread and is used to update the window's display
  #must lock other threads

  def update(self):
    while self.running:
      with self.lock:
        self.updateLineDisplay()
        #trigger a song changed update if required
        if self.player.songChanged():
          self.cleanupCovers()
          self.cleanupPlaylist()
        #is the player on play, pause or stop?
        mode = self.player.getMode()
        if not mode=="stop":
          self.updateTrackProgress()
        #set player state icon - play, pause or stop
        xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_NOWPLAYING", mode)
        #this control SHOULD be there but jsut in case it's not...
        try:
          self.getControl( constants.PLAYSTATE  ).setImage( mode + '.png' )
        except:
          pass
        self.updatePlaylistDetails()
        self.updateCoverArtFromURLs()



  ##############################################################################
  # get the cover URLS and pass them into window properties

  def updateCoverArtFromURLs(self):
    #grab the current URLs from the player
    newCoverURLs = self.player.coverURLs

    if not len(newCoverURLs)==0:

      #check if the URLs have changed...if so update the cover art
      if newCoverURLs[0] != self.coverURLs[0]:
        self.coverURLs = newCoverURLs

      try:
       #set the images if they are available in the skin file
        self.getControl( constants.MAINCOVERART  ).setImage( self.coverURLs[0]  )
        self.getControl( constants.UPCOMING1COVERART  ).setImage( self.coverURLs[1]  )
        self.getControl( constants.UPCOMING2COVERART  ).setImage( self.coverURLs[2]  )
        self.getControl( constants.UPCOMING3COVERART  ).setImage( self.coverURLs[3]  )
      except IndexError:
        pass
    else:
      self.getControl( constants.MAINCOVERART  ).setImage( "http://" + constants.SERVERHTTPURL + "/music/current/cover.jpg?player=" + constants.PLAYERMAC  )


  ##############################################################################
  # updates the 2 line squeeze display text to the window properties

  def updateLineDisplay(self):
    newLine1, newLine2 = self.player.getDisplay()
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_DISPLAYLINE1", newLine1)
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_DISPLAYLINE2", newLine2)

  ##############################################################################
  # update all the current playing track stuff into the window properties

  def updatePlaylistDetails(self):
    newPlaylistDetails = self.player.playlistDetails
    newPlaylist = self.player.playlist

    #make sure the playlist is not empty...
    if not len(newPlaylistDetails)==0:
      if newPlaylistDetails[0] != self.playlistDetails[0]:
        self.playlistDetails = newPlaylistDetails
        self.playlist = newPlaylist

      #print("NPW playlistDetails is " + str(self.playlistDetails))
      #print("NPW playlist is " + str(self.playlist))

      for trackOffset in range(0,len(self.playlistDetails)):
        #print("Settings window INFOs with " + str(self.playlistDetails[trackOffset]))
        stub = "XSQUEEZE_TRACK_" + str(trackOffset) + "_"

        #each element in this list looks like:
        #songinfo[{'album_id': 10, 'channels': 2, 'samplesize': 16, 'year': 2004, 'duration': 276.72000000000003, 'samplerate': 44100, 'id': 122, 'album': 'Gold - Greatest Hits', 'title': 'Lay All Your Love on Me', 'tracknum': 5, 'filesize': 34201960, 'artist_id': 17, 'type': 'flc', 'coverart': 1, 'compilation': 0, 'artwork_track_id': 'ed1047ba', 'lastUpdated': 'Thursday, December 8, 2011, 11:15 PM', 'modificationTime': 'Saturday, October 27, 2007, 5:14 PM', 'album_replay_gain': -7.7699999999999996, 'coverid': 'ed1047ba', 'genre': 'Pop', 'bitrate': '988kbps VBR', 'artist': 'Abba', 'addedTime': 'Thursday, December 8, 2011, 11:15 PM', 'replay_gain': -6.5199999999999996, 'genre_id': 4}]
        try:
          #local music
          if 'remote' not in self.playlistDetails[0]:
            xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_PLAYING_RADIO", "false")
            #some of this data may not be set if they have stupid untagged files...
            try:
              artist = self.playlistDetails[trackOffset]['artist']
            except KeyError:
              artist = ""
            try:
              title = self.playlistDetails[trackOffset]['title']
            except KeyError:
              title = ""
            try:
              tracknum = str(self.playlistDetails[trackOffset]['tracknum'])
            except KeyError:
              tracknum = ""

            xbmcgui.Window(self.windowID).setProperty(stub + "ALBUM", self.playlistDetails[trackOffset]['album'])
            duration = getInHMS(int(self.playlistDetails[trackOffset]['duration']))
            xbmcgui.Window(self.windowID).setProperty(stub + "TRACKLENGTH", duration)
            xbmcgui.Window(self.windowID).setProperty(stub + "ALBUMYEAR", str(self.playlistDetails[trackOffset]['year']))

          #radio stream - very variable in what details we get
          else:
            xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_PLAYING_RADIO", "true")
            artist = ""
            title = ""
            tracknum = "RADIO"
            try:
              title = self.playlist[0]['title']
              artist = self.playlist[0]['artist']
            except:
              pass

          uniartist = urllib.quote(artist)
          xbmcgui.Window(self.windowID).setProperty(stub + "INPLAYLIST", "true")
          xbmcgui.Window(self.windowID).setProperty(stub + "TRACKNUM", tracknum)
          xbmcgui.Window(self.windowID).setProperty(stub + "TITLE", title)
          xbmcgui.Window(self.windowID).setProperty(stub + "ARTIST", artist)
          xbmcgui.Window(self.windowID).setProperty(stub + "UNIARTIST", uniartist)

        except IndexError:
          Logger.log("Index error in updatePlaylistDetails")
        except KeyError as inst:
          Logger.log("Key error in updatePlaylistDetails", inst)
        except Exception as inst:
          Logger.log("General exception: ", inst)

      #remove old data from the rest of the playlist
      self.cleanupPlaylist(len(self.playlistDetails))

    #nothing in the playlist yet....
    else:
      Logger.log("Empty PlaylistDetails, setting current track to message about adding music...")
      stub = "XSQUEEZE_TRACK_0_"
      xbmcgui.Window(self.windowID).setProperty(stub + "INPLAYLIST", "false")
      xbmcgui.Window(self.windowID).setProperty(stub + "TITLE", constants.__language__(19619))
      xbmcgui.Window(self.windowID).setProperty(stub + "ARTIST", constants.__language__(19620))

  ##############################################################################
  # updates the track progress dialog

  def updateTrackProgress(self):
    trackLength = float(self.player.getTrackLength())
    trackElapsed = float(self.player.getTrackElapsed())
    trackRemaining = trackLength - trackElapsed

    if trackLength != 0.0:
      xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TRACK_0_ELAPSED", getInHMS(int(trackElapsed)))
      xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TRACK_0_REMAINING", "-" + getInHMS(int(trackRemaining)))
      xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TRACK_0_DURATION", getInHMS(int(trackLength)))
      percent = int((trackElapsed / trackLength) * 100.0)
      try:
        self.getControl( constants.CURRENTPROGRESS ).setPercent ( percent )
      except:
        pass
    else:
      xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TRACK_0_ELAPSED", "")
      xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TRACK_0_REMAINING", "")
      xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TRACK_0_DURATION", "")






