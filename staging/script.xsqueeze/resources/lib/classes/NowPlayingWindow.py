import xbmc, xbmcgui
import sys
import threading
from traceback import print_exc

from XSqueezeCommon import *
import constants

################################################################################
################################################################################
# MAP OF ACTION NAMES TO ID NUMBERS
# MAP OF XBMC ACTION NAMES TO SQUEEZEBOX ACTION STRINGS

#FROM https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h

def swap_dictionary(original_dict):
   return dict([(v, k) for (k, v) in original_dict.iteritems()])

ACTION_CODES = {

                'ACTION_NONE'             :0,
                'ACTION_MOVE_LEFT'        :1,
                'ACTION_MOVE_RIGHT'       :2,
                'ACTION_MOVE_UP'          :3,
                'ACTION_MOVE_DOWN'        :4,
                'ACTION_PAGE_UP'          :5,
                'ACTION_PAGE_DOWN'        :6,
                'ACTION_SELECT_ITEM'      :7,
                'ACTION_HIGHLIGHT_ITEM'   :8,
                'ACTION_PARENT_DIR'       :9,
                'ACTION_PREVIOUS_MENU'    :10,
                'ACTION_SHOW_INFO'        :11,
                'ACTION_PAUSE'            :12,
                'ACTION_STOP'             :13,
                'ACTION_NEXT_ITEM'        :14,
                'ACTION_PREV_ITEM'        :15,
                'ACTION_FORWARD'          :16,
                'ACTION_REWIND'           :17,
                'REMOTE_0'                :58,
                'REMOTE_1'                :59,
                'REMOTE_2'                :60,
                'REMOTE_3'                :61,
                'REMOTE_4'                :62,
                'REMOTE_5'                :63,
                'REMOTE_6'                :64,
                'REMOTE_7'                :65,
                'REMOTE_8'                :66,
                'REMOTE_9'                :67,
                'ACTION_PLAYER_PLAY'      :79,
                'ACTION_VOLUME_UP'        :88,
                'ACTION_VOLUME_DOWN'      :89,
                'ACTION_MUTE'             :91,
                'ACTION_NAV_BACK'         :92,
                'ACTION_CONTEXT_MENU'     :117,
                'ACTION_JUMP_SMS2'        :142,
                'ACTION_JUMP_SMS3'        :143,
                'ACTION_JUMP_SMS4'        :144,
                'ACTION_JUMP_SMS5'        :145,
                'ACTION_JUMP_SMS6'        :146,
                'ACTION_JUMP_SMS7'        :147,
                'ACTION_JUMP_SMS8'        :148,
                'ACTION_JUMP_SMS9'        :149,

}

SQUEEZE_CODES = {
                'ACTION_NONE'             :'',
                'ACTION_MOVE_LEFT'        :'arrow_left',
                'ACTION_MOVE_RIGHT'       :'arrow_right',
                'ACTION_MOVE_UP'          :'arrow_up',
                'ACTION_MOVE_DOWN'        :'arrow_down',
                'ACTION_PAGE_UP'          :'',
                'ACTION_PAGE_DOWN'        :'',
                'ACTION_SELECT_ITEM'      :'play.single',
                'ACTION_PLAYER_PLAY'      :'play.single',
                'ACTION_HIGHLIGHT_ITEM'   :'',
                'ACTION_PARENT_DIR'       :'arrow_left',
                'ACTION_PREVIOUS_MENU'    :'arrow_left',
                'ACTION_SHOW_INFO'        :'',
                'ACTION_PAUSE'            :'pause.single',
                'ACTION_STOP'             :'stop',
                'ACTION_NEXT_ITEM'        :'fwd.single',
                'ACTION_PREV_ITEM'        :'rew.single',
                'ACTION_FORWARD'          :'fwd.hold',
                'ACTION_REWIND'           :'rew.hold',
                'REMOTE_0'                :'0',
                'REMOTE_1'                :'1',
                'REMOTE_2'                :'2',
                'REMOTE_3'                :'3',
                'REMOTE_4'                :'4',
                'REMOTE_5'                :'5',
                'REMOTE_6'                :'6',
                'REMOTE_7'                :'7',
                'REMOTE_8'                :'8',
                'REMOTE_9'                :'9',
                'ACTION_VOLUME_UP'        :'volup',
                'ACTION_VOLUME_DOWN'      :'voldown',
                'ACTION_MUTE'             :'muting',
                'ACTION_JUMP_SMS2'        :'2',
                'ACTION_JUMP_SMS3'        :'3',
                'ACTION_JUMP_SMS4'        :'4',
                'ACTION_JUMP_SMS5'        :'5',
                'ACTION_JUMP_SMS6'        :'6',
                'ACTION_JUMP_SMS7'        :'7',
                'ACTION_JUMP_SMS8'        :'8',
                'ACTION_JUMP_SMS9'        :'9',

}

ACTION_NAMES = swap_dictionary(ACTION_CODES)


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

    #we're not yet running (is set to true the first time we go through init)
    self.running=False

    #blanks the screen - this is crude, and probably wrong, but works
    self.background = xbmcgui.ControlImage(0,0,1280,720, 'black.png')
    self.addControl(self.background)

    #create a player instance (is really a player + server combo)
    try:
      self.player = SqueezePlayer()
    except:
      log( "### Failed to create SqueezePlayer object " )
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
##    try:
##      self.hiddenButton = self.getControl(999)
##    except:
##      pass
    log("onInit, window id is "+ str(self.windowID))

    #Set some basic properties
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_WINDOWID", str(self.windowID))
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_PLAYERMAC", constants.PLAYERMAC)
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_SERVER", constants.SERVERNAME)
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_NAME", "XSqueeze "+ VERSION)

    #kick off new threads if this is the first call to init
    # (as init is called when we drop back from the chooser plugin to XSqueeze)

    if not self.running:
      log("Starting GUI update thread")
      self.running = True
      self.thread = threading.Thread(target=self.update)
      self.thread.setDaemon(True)
      self.thread.start()

      log("Starting ArtistSlideshow thread")
      self.thread2 = threading.Thread(target=self.runArtistSlideshow)
      self.thread2.setDaemon(True)
      self.thread2.start()


  ##############################################################################
  # Essentially the reverse of init - need to remove any controls we added and blank out the properties
  # for a cleaner exit

  def deInit(self):

      log("deInit() called - cleaning covers, playlist and waiting on artist.slideshow to signal finish...")

      xbmcgui.Window(xbmcgui.getCurrentWindowId()).clearProperty("ArtistSlideshow.ExternalCall")
      log("Waiting for artistslideshow to stop")

      #wait here for Artist slideshow to finish, can occasionally take several seconds
      while (not xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty("ArtistSlideshow.CleanupComplete") == "True"):
        log("Still waiting for artistslideshow to stop")
        xbmc.sleep(1000)

      log("Cleaning covers and playlist properties.....")
      self.cleanupPlaylist(0)
      self.cleanupCovers()
      self.removeControl(self.background)
      del(self.background)
      xbmcgui.Window(self.windowID).clearProperty("XSQUEEZE_WINDOWID")

      log("deInit() complete. Artist Slideshow Cleanup Property = " + str(xbmcgui.Window(self.windowID).getProperty("Artistslideshow.CleanupComplete")))

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
      #log("Not handling eventid " + str(action.getId()))
      actionNum = 0
      actionName = ACTION_NAMES[actionNum]
      actionSqueeze = SQUEEZE_CODES[actionName]

    if actionNum != 0:
      log("Handling action id: " + str(actionNum) +  " Name: " + actionName + " SqueezeCode if any: " + actionSqueeze)

    #for testing xbmc's internal playlist - pause and display playlist...
    #10500 = music playlist
    #if action == ACTION_CODES['ACTION_PAUSE']:
    #    xbmc.executebuiltin("XBMC.ActivateWindow(10500)")

    #intercept special XBMC ones first
    if action == ACTION_CODES['ACTION_PREVIOUS_MENU'] or action == ACTION_CODES['ACTION_NAV_BACK']:
      #make sure we've only been through here once....
      if self.running:
        log("XBMC Action: Close")
        #prevent the GUI update thread from updating...
        self.running = False

        #we're controlling a local squeezeslave - best to stop the music before we kill it
        #otherwise it oddly resumes automatically on restart
        if constants.CONTROLSLAVE and not constants.CONTROLLERONLY:
          notify(LANGUAGE(19612),LANGUAGE(19609))
          with self.lock:
            self.player.button("stop")

        #tidy up before the window closes...
        self.deInit()

        #now close the window before we kill it
        self.close()

      #user has probably hammered the close button...tell them to cool their jets...
      else:
        notify(LANGUAGE(19622),LANGUAGE(19623))
        pass

    #Start the music chooser
    elif action == ACTION_CODES['ACTION_SHOW_INFO']:
      log("### Starting Chooser...")
      xbmc.executebuiltin("ActivateWindow(Programs,plugin://plugin.program.xsqueezechooser/?mode=0&callerid=" + str(self.windowID) + ")")

    #otherwise pass the button code to the squeezeplayer & trigger a matching player action if we have one
    else:
       if actionSqueeze:
        log("SqueezePlayer Action: " + actionSqueeze)
        with self.lock:
          self.player.button(actionSqueeze)

  ##############################################################################
  # Cleanup the cover art images

  def cleanupCovers (self):

    #log("Clearing cover images.....")
    self.getControl( constants.MAINCOVERART  ).setImage( "" )
    self.getControl( constants.UPCOMING1COVERART  ).setImage( "" )
    self.getControl( constants.UPCOMING2COVERART  ).setImage( "" )
    self.getControl( constants.UPCOMING3COVERART  ).setImage( "" )

  ##############################################################################
  # Cleanup the window labels, by default for all track 0 to 10
  # otherwise, from X to 10

  def cleanupPlaylist (self, start=0):

    #log("Clearing playlist properties....")

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
          log("Index error in updatePlaylistDetails")
        except KeyError as inst:
          log("Key error in updatePlaylistDetails", inst)
        except Exception as inst:
          log("General exception: ", inst)

      #remove old data from the rest of the playlist
      self.cleanupPlaylist(len(self.playlistDetails))

    #nothing in the playlist yet....
    else:
      log("Empty PlaylistDetails, setting current track to message about adding music...")
      stub = "XSQUEEZE_TRACK_0_"
      xbmcgui.Window(self.windowID).setProperty(stub + "INPLAYLIST", "false")
      xbmcgui.Window(self.windowID).setProperty(stub + "TITLE", LANGUAGE(19619))
      xbmcgui.Window(self.windowID).setProperty(stub + "ARTIST", LANGUAGE(19620))

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






