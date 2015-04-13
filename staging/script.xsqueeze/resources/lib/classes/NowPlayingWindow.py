import xbmc
import xbmcgui
import sys
import threading
from traceback import print_exc
from XSqueezeCommon import *
from b808common import *
import datetime
import constants

#hdmi support
if constants.CECSUPPORT == 'true':
  import cec
  cec.init()
  avr  = cec.Device(5)

################################################################################
################################################################################
################################################################################
# CONST DATA NEEDED JUST HERE
# MAP OF ACTION NAMES TO ID NUMBERS
# MAP OF XBMC ACTION NAMES TO SQUEEZEBOX ACTION STRINGS
# FROM https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h
################################################################################
################################################################################
################################################################################

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
                'ACTION_PLAYER_FORWARD'   :77,
                'ACTION_PLAYER_REWIND'    :78,
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
                'ACTION_FIRST_PAGE'       :159,
                'ACTION_LAST_PAGE'        :160,
}

SQUEEZE_CODES = {
                'ACTION_NONE'             :'',
                'ACTION_MOVE_LEFT'        :'arrow_left',
                'ACTION_MOVE_RIGHT'       :'arrow_right',
                'ACTION_MOVE_UP'          :'arrow_up',
                'ACTION_MOVE_DOWN'        :'arrow_down',
                'ACTION_PAGE_UP'          :'volup',
                'ACTION_PAGE_DOWN'        :'voldown',
                'ACTION_SELECT_ITEM'      :'',
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
                'ACTION_PLAYER_FORWARD'   :'fwd.hold',
                'ACTION_PLAYER_REWIND'    :'rew.hold',
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
                'ACTION_FIRST_PAGE'       :'fwd.single',
                'ACTION_LAST_PAGE'        :'rew.single',
                'BUTTON_SKIPBACK'         : 'rew.single',
                'BUTTON_REWIND'           : 'rew.hold',
                'BUTTON_PLAYPAUSE'        : 'play.single',
                'BUTTON_STOP'             : 'stop',
                'BUTTON_FASTFORWARD'      : 'fwd.hold',
                'BUTTON_SKIPFORWARD'      : 'fwd.single',
                'BUTTON_SHUFFLE'          : 'shuffle.single',
                'BUTTON_REPEAT'           : 'repeat',
                'BUTTON_VOLUP'            : 'volup',
                'BUTTON_VOLDN'            : 'voldown',
                'SLIDER_TRACKPROGRESS'    : 'seek'
}

#if using squeezeslave we can get away using ok as play/pause like I do with video..
if not constants.TOUCHENABLED and not constants.PLAYERTYPE=='squeezelite':
    SQUEEZE_CODES['ACTION_SELECT_ITEM'] = 'play.single'

ACTION_NAMES = swap_dictionary(ACTION_CODES)

BUTTON_CODES ={
                'BUTTON_EXIT'             : constants.BUTTONEXIT,
                'BUTTON_SKIPBACK'         : constants.BUTTONSKIPBACK,
                'BUTTON_REWIND'           : constants.BUTTONREWIND,
                'BUTTON_PLAYPAUSE'        : constants.BUTTONPLAYPAUSE,
                'BUTTON_STOP'             : constants.BUTTONSTOP,
                'BUTTON_FASTFORWARD'      : constants.BUTTONFASTFORWARD,
                'BUTTON_SKIPFORWARD'      : constants.BUTTONSKIPFORWARD,
                'BUTTON_SHUFFLE'          : constants.BUTTONSHUFFLE,
                'BUTTON_REPEAT'           : constants.BUTTONREPEAT,
                'BUTTON_CHOOSER'          : constants.BUTTONCHOOSER,
                'BUTTON_VOLUP'            : constants.BUTTONVOLUP,
                'BUTTON_VOLDN'            : constants.BUTTONVOLDN,
                'SLIDER_TRACKPROGRESS'    : constants.CURRENTPROGRESS
}

BUTTON_NAMES = swap_dictionary(BUTTON_CODES)

PLAYSTATEICONS = {
                'play'                    :"OSDPlayFO.png",
                'pause'                   :"OSDPauseFO.png",
                'stop'                    :"OSDStopFO.png"
}

SHUFFLESTATEICONS = {
                'shuffleon_fo'                    :"OSDRandomOnFO.png",
                'shuffleon_nf'                    :"OSDRandomOnNF.png",
                'shuffleoff_fo'                   :"OSDRandomOffFO.png",
                'shuffleoff_nf'                   :"OSDRandomOffNF.png"
}

REPEATSTATEICONS = {
                'repeaton_fo'                    :"OSDRepeatOnFO.png",
                'repeaton_nf'                    :"OSDRepeatOnNF.png",
                'repeatoff_fo'                   :"OSDRepeatOffFO.png",
                'repeatoff_nf'                   :"OSDRepeatOffNF.png"
}

################################################################################
################################################################################
### Class ActionHandler (i.e. a window)

class NowPlayingWindow(xbmcgui.WindowXML):

################################################################################
################################################################################
################################################################################
# INIT, THREADS, MAIN UPDATE LOOP
################################################################################
################################################################################
################################################################################

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
      raise

    #Initialise music details
    self.coverURLs = [""]
    self.playlistDetails = [""]
    self.playlist = [""]

    #a thread lock to use so that each SB related action is finished before the
    #next one is sent - without this you get race conditions over the telnet
    #interface!
    self.lock = threading.Lock()


  ##############################################################################
  #the method called when the window is inited
  #starts the GUI update thread...

  def onInit( self ):

    #get the window ID
    self.windowID = xbmcgui.getCurrentWindowId()
    log("onInit, window id is "+ str(self.windowID))

    #Set some basic properties into $INFO for skin display
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_WINDOWID", str(self.windowID))
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_PLAYERMAC", constants.PLAYERMAC)
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_SERVER", constants.SERVERNAME)
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_NAME", "XSqueeze "+ VERSION)
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_SHUFFLESTATE", SHUFFLESTATEICONS['shuffleoff_fo'])

    #variable to ensure that hdmipower commands are only send once and not all the time
    self.hdmipower = "false"

    #variable for hdmi support
    self.hdmivol ="false"

    #kick off new threads if this is the first call to init
    # (as init is called when we drop back from the chooser plugin to XSqueeze)

    try:
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
    except Exception as inst:
        log("Exception in NowPlayingWindow main loop: ", inst)
        raise

  ##############################################################################
  #this is our GUI update thread and is used to update the window's display
  #must lock other threads

  def update(self):
    while self.running:
      #we put a little pause in here so we're not thrashing the system polling
      #all this stuff and holding the lock
      #this one line makes Pi-s etc perform *much better*!
      xbmc.sleep(500)
      with self.lock:
        if constants.PLAYERTYPE=="squeezeslave":
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
        #update the play state icon...
        xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_PLAYSTATE", PLAYSTATEICONS[mode])
        #update the shuffle state icon
        shuffle = self.player.getShuffle()
        if shuffle:
          xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_SHUFFLESTATE", SHUFFLESTATEICONS['shuffleon_fo'])
        else:
          xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_SHUFFLESTATE", SHUFFLESTATEICONS['shuffleoff_fo'])
        repeat = self.player.getRepeat()
        if repeat:
          xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_REPEATSTATE", REPEATSTATEICONS['repeaton_fo'])
        else:
          xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_REPEATSTATE", REPEATSTATEICONS['repeatoff_fo'])
        self.updateVolume()
        self.updatePlaylistDetails()
        self.updateCoverArtFromURLs()

        #trigger a hdmi command, if a controller has changed the power status or the volume
        if constants.CECSUPPORT == 'true':
          powerstate = self.player.getPowerState()
          if powerstate == 0 and self.hdmipower == "true":
            if constants.TURNONAVR == "true":
               avr.standby()
            self.hdmipower = "false"
          elif powerstate != 0 and self.hdmipower == "false":
            if constants.TURNONAVR == "true":
               avr.power_on()
               avr.set_av_input(constants.AVRINPUT)
            self.hdmipower = "true"
          else:
            pass

        if constants.ADJUSTVOL == "true" and constants.CECSUPPORT == 'true':
         self.updatehdmivol()

     
##############################################################################
  # Kick off the artist.slideshow

  def runArtistSlideshow(self):
     #startup artistslideshow
     xbmcgui.Window(self.windowID).setProperty("ArtistSlideshow.ExternalCall", "True")
     artistslideshow = "RunScript(script.artistslideshow,windowid=%s&artistfield=%s&titlefield=%s)" % (self.windowID, "XSQUEEZE_TRACK_0_ARTIST", "XSQUEEZE_TRACK_0_TITLE")
     xbmc.executebuiltin(artistslideshow)
     #pass

################################################################################
################################################################################
################################################################################
# ACTION HANDLERS
################################################################################
################################################################################
################################################################################

  ##############################################################################
  # Handle button events

  def onClick( self, control ):

    if self.running:

      #get the thread lock so we're only communicating one thing at a time to the player
      with self.lock:

        actionSqueeze = ''
        buttonName = ''
        #directCommand is set to true if we're not sending it as a simple button event
        directCommand = False

        try:
          buttonName = BUTTON_NAMES[control]
          actionSqueeze = SQUEEZE_CODES[buttonName]
        except:
          pass

        log ("onClick() event, Control is: [" + str(control) +"], buttonName is [" + buttonName + "] actionSqueeze is: [" + str(actionSqueeze) + "]")

        ####Sliding the progress bar to seek in a track
        #### NOT CURRENTLY WORKING!!
        if control == constants.CURRENTPROGRESS:
            #protect this block in case the control is missing...
            try:
              trackElapsed, trackRemaining, trackLength, percent = self.calculateTrackPostionandPercent()
              newPercent = self.getControl( constants.CURRENTPROGRESS ).getPercent()
              newPosition = trackLength * (newPercent / 100.0)
              log("Slider event: CURRENTPROGRESS, track length [" +str(trackLength) +"] percent [" + str(newPercent) + "] new position [" + str(newPosition) + "]")
              self.player.seek(newPosition)
              self.getControl( constants.CURRENTPROGRESS ).setPercent(newPercent)
            except:
               pass


        ####DEFAULT - the playback controls - everything slips through to here
        else:

          #define handlers for each of the controls to determine the correct
          #squeezebox code to seend

          if (control == constants.BUTTONSKIPBACK):
            log("Button event: SKIPBACK")

          if (control == constants.BUTTONREWIND):
            log("Button event: REWIND")
            directCommand = True
            self.player.rewind()

          if (control == constants.BUTTONPLAYPAUSE):
            log("Button event: PLAYPAUSE")

          if (control == constants.BUTTONSTOP):
            log("Button event: STOP")

          if (control == constants.BUTTONFASTFORWARD):
            log("Button event: FASTFORWARD")
            directCommand = True
            self.player.forward()

          if (control == constants.BUTTONSKIPFORWARD):
            log("Button event: SKIPFORWARD")

          if (control == constants.BUTTONSHUFFLE):
            log("Button event: SHUFFLE")
            directCommand = True
            self.player.setShuffle()

          if (control == constants.BUTTONREPEAT):
            log("Button event: REPEAT")
            directCommand = True
            self.player.setRepeat()

          if (control == constants.BUTTONCHOOSER):
            log("Button event: CHOOSER")
            directCommand = True
            log("### Starting Chooser...")
            xbmc.executebuiltin("ActivateWindow(Programs,plugin://plugin.program.xsqueezechooser/?mode=0&callerid=" + str(self.windowID) + ")")

          if (control == constants.BUTTONEXIT):
            log("Button event: EXIT")
            self.exitXSqueeze()

         #hdmi support
          if (control == constants.BUTTONVOLUP) and constants.CECSUPPORT == 'true' and constants.ADJUSTVOL == "true":
           if self.vol1 < 100:
             i = 0
             for i in range(int(constants.VOLFACTOR)):
               cec.volume_up()
             self.hdmivol = "false"

          if (control == constants.BUTTONVOLDN) and constants.CECSUPPORT == 'true' and constants.ADJUSTVOL == "true" :
           if self.vol1 > 0:  
             i = 0
             for i in range(int(constants.VOLFACTOR)):
               cec.volume_down()
             self.hdmivol = "false"

          #ok now actually send the command through if it is a squeeze command
          if (actionSqueeze != '') and not directCommand:
            actionSqueeze = self.modifyActionSqueeze(actionSqueeze)
            log("Sending button to LMS: " + actionSqueeze)
            self.player.button(actionSqueeze)
            #make volume a bit quickcer...send the signal twice..
            if actionSqueeze=="volup" or actionSqueeze =="voldown":
              self.player.button(actionSqueeze)


    #...else user has probably hammered the close button...tell them to cool their jets...
    else:
      notify("Cool your jets.","I'm cleaning up before exiting...")
      pass

  ##############################################################################
  # used when we need to use logic to change what button to send the player

  def modifyActionSqueeze(self,actionSqueeze):
      #so far only used for play/pause
      mode = self.player.getMode()
      log("mode " + mode +" actionSqueeze " + actionSqueeze)
      if mode == "play" and actionSqueeze == "play.single": # and "Now Playing" in xbmcgui.Window(self.windowID).getProperty("XSQUEEZE_DISPLAYLINE1"):
        actionSqueeze="pause.single"
        log("SqueezePlayer Action Changed To: " + actionSqueeze)

      return actionSqueeze

  ##############################################################################
  # Handle window acitions
  # generally by mapping XBMC window actions to squeezeslave methods

  def onAction( self, action ):

    if self.running:

      #get the thread lock so we're only communicating one thing at a time to the player
      with self.lock:

      #if we handle this action, do it, otherwise null it out
        try:
          actionNum = action.getId()
          actionName = ACTION_NAMES[actionNum]
          actionSqueeze = SQUEEZE_CODES[actionName]
        except KeyError:
          #action is not in our handled list (see top of this file)
          #do not log mouse movements, way too much log spew...
          if action.getId() != 107:
            log("Not handling eventid " + str(action.getId()))
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
          self.exitXSqueeze()

        #Start the music chooser
        elif action == ACTION_CODES['ACTION_SHOW_INFO']:
          log("### Starting Chooser...")
          xbmc.executebuiltin("ActivateWindow(Programs,plugin://plugin.program.xsqueezechooser/?mode=0&callerid=" + str(self.windowID) + ")")


        #otherwise pass the button code to the squeezeplayer & trigger a matching player action if we have one
        else:
           if actionSqueeze:
            log("SqueezePlayer Action: " + actionSqueeze)
            #cope with play/pause on one button
            actionSqueeze = self.modifyActionSqueeze(actionSqueeze)
            #send the command through
            #with self.lock:
            self.player.button(actionSqueeze)

    #...else user has probably hammered the close button...tell them to cool their jets...
    else:
      #notify(LANGUAGE(19622),LANGUAGE(19623))
      pass


################################################################################
################################################################################
################################################################################
# UPDATERS
################################################################################
################################################################################
################################################################################

  ##############################################################################
  # get the cover URLS and pass them into window properties

  def updateCoverArtFromURLs(self):

    stub="XSQUEEZE_"
    #grab the current URLs from the player
    newCoverURLs = self.player.coverURLs

    if not len(newCoverURLs)==0:

      #check if the URLs have changed...if so update the cover art
      if newCoverURLs[0] != self.coverURLs[0]:
        self.coverURLs = newCoverURLs

      try:
        xbmcgui.Window(self.windowID).setProperty(stub+"MAINCOVER", self.coverURLs[0])
        xbmcgui.Window(self.windowID).setProperty(stub+"UPCOMING1COVERART", self.coverURLs[1])
        xbmcgui.Window(self.windowID).setProperty(stub+"UPCOMING2COVERART", self.coverURLs[2])
        xbmcgui.Window(self.windowID).setProperty(stub+"UPCOMING3COVERART", self.coverURLs[3])
      except:
        pass

    else:
      xbmcgui.Window(self.windowID).setProperty(stub+"MAINCOVER", "http://" + constants.SERVERHTTPURL + "/music/current/cover.jpg?player=" + constants.PLAYERMAC)

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

    #log("NPD " + str(len(newPlaylistDetails)) + "  " + str(newPlaylistDetails))
    #log("NP " + str(len(newPlaylist)) + "  " + str(newPlaylist))

    #playlist is empty....
    if len(newPlaylistDetails)==0:
      log("Empty PlaylistDetails, setting current track to message about adding music...")
      stub = "XSQUEEZE_TRACK_0_"
      xbmcgui.Window(self.windowID).setProperty(stub + "INPLAYLIST", "false")
      #xbmcgui.Window(self.windowID).setProperty(stub + "TITLE", "Empty Playlist")
      xbmcgui.Window(self.windowID).setProperty(stub + "ARTIST", "Empty Playlist - add some music to get things going!")

    #otherwise try and pgrab as much data as we can
    # N.B. - some streaming services don't use play-list details, so we may need to use the play-list
    else:
      #only do work if something has changed....
      if newPlaylistDetails != self.playlistDetails or newPlaylist != self.playlist:
        #log("Playlist update detected")
        self.playlistDetails = newPlaylistDetails
        self.playlist = newPlaylist

      #first remove old data from the rest of the playlist in $INFO
      self.cleanupPlaylist(len(self.playlistDetails))

      # store temp map of play-list data
      playlistMap = {}
      for entry in self.playlist:
        playlistMap[entry['id']] = entry
        #log('temp map is ' + str(playlistMap))

      for trackOffset in range(0,len(self.playlistDetails)):
        trackDetails = self.playlistDetails[trackOffset]
        trackId = int(trackDetails['track_id'])
        plItem = playlistMap.get(trackId,{})
        #log("Settings window INFOs with " + str(trackDetails))
        #log('Alternate info is ' + str(plItem))
        stub = "XSQUEEZE_TRACK_" + str(trackOffset) + "_"

        #each element in this list looks like:
        #songinfo[{'album_id': 10, 'channels': 2, 'samplesize': 16, 'year': 2004, 'duration': 276.72000000000003, 'samplerate': 44100, 'id': 122, 'album': 'Gold - Greatest Hits', 'title': 'Lay All Your Love on Me', 'tracknum': 5, 'filesize': 34201960, 'artist_id': 17, 'type': 'flc', 'coverart': 1, 'compilation': 0, 'artwork_track_id': 'ed1047ba', 'lastUpdated': 'Thursday, December 8, 2011, 11:15 PM', 'modificationTime': 'Saturday, October 27, 2007, 5:14 PM', 'album_replay_gain': -7.7699999999999996, 'coverid': 'ed1047ba', 'genre': 'Pop', 'bitrate': '988kbps VBR', 'artist': 'Abba', 'addedTime': 'Thursday, December 8, 2011, 11:15 PM', 'replay_gain': -6.5199999999999996, 'genre_id': 4}]

        # alternate from play-list looks like:
        # {'album': 'Beautiful Garbage', 'artist': 'Garbage', 'title': 'Cherry Lips (Go Baby Go!)', 'buttons': 'HASH(0xc987e4c)', 'duration': 192.0, 'position': 0, 'id': -209808524}

        #NOW GRAB AS MUCH DATA FROM THE STREAM DETAILS AS WE CAN
        #VERY HIT AND MISS
        artist = trackDetails.get('artist',plItem.get('artist',''))
        title = trackDetails.get('title',plItem.get('title',''))
        tracknum = str(trackDetails.get('tracknum',0))
        if tracknum == '0': tracknum = ''
        fileformat = trackDetails.get('type','')
        bitrate = str(trackDetails.get('bitrate',0))
        if bitrate == '0': bitrate = ''
        genre = trackDetails.get('genre','')
        album = trackDetails.get('album',plItem.get('album',''))
        stype = trackDetails.get('type','')
        duration = int(trackDetails.get('duration',plItem.get('duration',0)))
        duration = getInHMS(duration)

        year = trackDetails.get('year',0)
        #little hack if we're getting 0 back as the year - put in current year
        if year==0:
          now = datetime.datetime.now()
          year = str(now.year)
        else:
          year = str(year)

        #playing Radio/App
        if 'remote' in self.playlistDetails[0]:
          xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_PLAYING_RADIO", "true")
          tracknum = ""
        else:
          xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_PLAYING_RADIO", "false")


        #some of this data may not be set if they have stupid untagged files...
        xbmcgui.Window(self.windowID).setProperty(stub + "ALBUM", album)
        xbmcgui.Window(self.windowID).setProperty(stub + "TRACKLENGTH", duration)
        xbmcgui.Window(self.windowID).setProperty(stub + "ALBUMYEAR", year)
        xbmcgui.Window(self.windowID).setProperty(stub + "INPLAYLIST", "true")
        xbmcgui.Window(self.windowID).setProperty(stub + "TRACKNUM", tracknum)
        xbmcgui.Window(self.windowID).setProperty(stub + "TITLE", title)
        xbmcgui.Window(self.windowID).setProperty(stub + "ARTIST", artist)
        xbmcgui.Window(self.windowID).setProperty(stub + "UNIARTIST", urllib.quote(artist))
        xbmcgui.Window(self.windowID).setProperty(stub + "FILEFORMAT", fileformat)
        xbmcgui.Window(self.windowID).setProperty(stub + "BITRATE", bitrate)
        xbmcgui.Window(self.windowID).setProperty(stub + "GENRE", genre)
        xbmcgui.Window(self.windowID).setProperty(stub + "TYPE", stype)




  ##############################################################################
  # returns a tuple of [trackElapsed, trackRemaining, trackLength, percent]

  def calculateTrackPostionandPercent(self):

    trackLength = float(self.player.getTrackLength())
    trackElapsed = float(self.player.getTrackElapsed())
    trackRemaining = trackLength - trackElapsed
    if trackLength != 0.0:
      percent = int((trackElapsed / trackLength) * 100.0)
    else:
      percent = 0
    return [trackElapsed, trackRemaining, trackLength, percent]

  ##############################################################################
  # updates the track progress bar

  def updateTrackProgress(self):

    trackElapsed, trackRemaining, trackLength, percent = self.calculateTrackPostionandPercent()

    if trackLength != 0.0:
      xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TRACK_0_ELAPSED", getInHMS(int(trackElapsed)))
      xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TRACK_0_REMAINING", "-" + getInHMS(int(trackRemaining)))
      xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TRACK_0_DURATION", getInHMS(int(trackLength)))
      try:
        self.getControl( constants.CURRENTPROGRESS ).setPercent ( percent )
      #if the control doesn't exist, do nothing
      except Exception as inst:
        #log("Progress bar update exception: " + str(inst))
        pass
    else:
      xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TRACK_0_ELAPSED", "")
      xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TRACK_0_REMAINING", "")
      xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TRACK_0_DURATION", "")

  ##############################################################################
  # updates the volume bar & digits

  def updateVolume(self):
    if constants.TOUCHENABLED or constants.PLAYERTYPE=='squeezelite':
        volume = int(self.player.getVolume())
        xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_VOLUME", str(volume))
        try:
            self.getControl ( constants.VOLUMEBAR ).setPercent ( volume )
        except Exception as inst:
            #log("Volume bar update exception: " + str(inst))
            pass

  def updatehdmivol(self):
     self.vol2 = self.player.getVolume()
     if self.hdmivol == "false":
       self.vol1 = self.player.getVolume()
       self.hdmivol = "true"
     counter = 0
     if self.vol2 > self.vol1:
       while counter <= (abs(self.vol1 -self.vol2) * int(constants.VOLFACTOR)):
         cec.volume_up()
         self.hdmivol = "false"
         counter = counter + 1
     elif self.vol2 < self.vol1:
       while counter <= (abs(self.vol1 -self.vol2) * int(constants.VOLFACTOR)):
         cec.volume_down()
         self.hdmivol = "false"
         counter = counter + 1
     elif self.vol2 == self.vol1:
       pass

################################################################################
################################################################################
################################################################################
# EXIT AND CLEANUP
################################################################################
################################################################################
################################################################################

  ##############################################################################
  # Call this to exit XSqueeze...

  def exitXSqueeze(self):

      log("### XSqueeze XBMC Action: Close")

      #if this the first time through....
      if self.running:

        #Kill Artist Slideshow first cause it's slow to react...
        xbmcgui.Window(xbmcgui.getCurrentWindowId()).clearProperty("ArtistSlideshow.ExternalCall")

       #prevent the GUI update thread from updating anymore...
        self.running = False

        #we're controlling a local player - best to stop the music before we kill it
        if constants.PLAYBACK:
          notify(LANGUAGE(19612),LANGUAGE(19609))
          self.player.button("stop")

        #tidy up before the window closes...
        log("Cleanup - cleaning covers, playlist and waiting on artist.slideshow to signal finish...")
        self.cleanupPlaylist(0)
        self.cleanupCovers()
        try:
            self.removeControl(self.background)
            del(self.background)
        except:
            log("Error removing background control")

        #wait here for Artist slideshow to finish, can occasionally take several seconds
        log("Waiting for artistslideshow to stop")
        count = 0
        while (not xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty("ArtistSlideshow.CleanupComplete") == "True" and count < constants.SECONDS_TO_WAIT_FOR_ARTISTSLIDESHOWEXIT):
          log("Still waiting for artistslideshow to stop")
          count+=1
          xbmc.sleep(1000)

        log("exitXSqueeze() complete. Artist Slideshow Cleanup Property = " + str(xbmcgui.Window(self.windowID).getProperty("Artistslideshow.CleanupComplete")))

        #now close the window before we kill it
        xbmcgui.Window(self.windowID).clearProperty("XSQUEEZE_WINDOWID")
        self.close()


  ##############################################################################
  # Cleanup the cover art images

  def cleanupCovers (self):

      stub="XSQUEEZE_"
      xbmcgui.Window(self.windowID).setProperty(stub+"MAINCOVER", "")
      xbmcgui.Window(self.windowID).setProperty(stub+"UPCOMING1COVERART", "")
      xbmcgui.Window(self.windowID).setProperty(stub+"UPCOMING2COVERART", "")
      xbmcgui.Window(self.windowID).setProperty(stub+"UPCOMING3COVERART", "")


  ##############################################################################
  # Cleanup the window labels, by default for all track 0 to 10
  # otherwise, from X to 10

  def cleanupPlaylist (self, start=0):

    #log("Clearing playlist properties....")

    for trackOffset in range(start,10):
      stub = "XSQUEEZE_TRACK_" + str(trackOffset) + "_"
      try:
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
        xbmcgui.Window(self.windowID).clearProperty(stub + "BITRATE")
        xbmcgui.Window(self.windowID).clearProperty(stub + "GENRE")
        xbmcgui.Window(self.windowID).clearProperty(stub + "TYPE")
      #since we're just tidying, doesn't matter if the above fails
      except:
        pass
