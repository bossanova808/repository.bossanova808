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

  #constructor - create controls & add them to the window
  def __init__( self, *args, **kwargs ):

    self.addControl(xbmcgui.ControlImage(0,0,1920,1080, 'black.png'))

    #create a player instance (is really a player + server combo)
    try:
      self.player = SqueezePlayer()
    except:
      Logger.log( "### Failed to create SqueezePlayer object " )
      print_exc()
      sys.exit()


  def onInit( self ):
    pass

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
      actionNum = 0
      actionName = ACTION_NAMES[actionNum]
      actionSqueeze = SQUEEZE_CODES[actionName]

    if actionNum != 0:
      Logger.log("Handling action id: " + str(actionNum) +  " Name: " + actionName + " SqueezeCode if any: " + actionSqueeze)

    #intercept special XBMC ones first
    if action == ACTION_CODES['ACTION_PREVIOUS_MENU']:
      Logger.log("XBMC Action: Close")
      self.running = False
      self.close()

    #elif etc

    #otherwise pass the button code to the squeezeplayer & trigger a matching player action if we have one
    else:
       if actionSqueeze:
        Logger.log("SqueezePlayer Action: " + actionSqueeze)
        self.player.button(actionSqueeze)
        #trigger an immeidate screen update
        self.update(force=True)


  ##############################################################################
  #this is called every 10 millis and is used to update the window's display
  #e.g. if trac/cover art changes etc
  #also called immediately when requires

  def update(self, force=False):
    #Logger.log("Update cycle...")
    #always update the line display even if song hasn't changed
    self.updateLineDisplay()
    self.updateCoverArt(force)
    self.updateCurrentTrack()
    if not self.player.getMode()=="stop":
      self.updateTrackProgress()
    self.updateUpcomingTracks()

  #updates the display text on screen
  def updateLineDisplay(self):
    newLine1, newLine2 = self.player.getDisplay()
    self.getControl( constants.DISPLAYLINE1 ).setLabel( newLine1 )
    self.getControl( constants.DISPLAYLINE2 ).setLabel( newLine2 )

  #update all the current playing track stuff
  def updateCurrentTrack(self):
    title, artist, album = self.player.getCurrentTrack()
    self.getControl( constants.CURRENTTITLE  ).setLabel( title  )
    self.getControl( constants.CURRENTARTIST ).setLabel( "by " + artist )
    self.getControl( constants.CURRENTALBUM  ).setLabel( "from " + album  )

  #update the coming track list
  def updateUpcomingTracks(self):
    upcoming1, upcoming2, upcoming3 = self.player.getPlaylist()
    self.getControl( constants.UPCOMING1 ).setLabel( upcoming1 )
    self.getControl( constants.UPCOMING2 ).setLabel( upcoming2 )
    self.getControl( constants.UPCOMING3 ).setLabel( upcoming3 )

  #updates the track progress dialog
  def updateTrackProgress(self):
    trackLength = float(self.player.getTrackLength())
    trackElapsed = float(self.player.getTrackElapsed())
    trackRemaining = trackLength - trackElapsed
    if trackLength != 0.0:
      self.getControl( constants.CURRENTELAPSED   ).setLabel( self.GetInHMS(int(trackElapsed))   )
      self.getControl( constants.CURRENTREMAINING ).setLabel( "-" + self.GetInHMS(int(trackRemaining)) )
      self.getControl( constants.CURRENTLENGTH    ).setLabel( self.GetInHMS(int(trackLength))    )
      percent = int((trackElapsed / trackLength) * 100.0)
      self.getControl( constants.CURRENTPROGRESS ).setPercent ( percent )
    else:
      self.getControl( constants.CURRENTELAPSED   ).setLabel( "?"   )
      self.getControl( constants.CURRENTREMAINING ).setLabel( "?"   )
      self.getControl( constants.CURRENTLENGTH    ).setLabel( "?"   )


  #def updates cover art if the track gas changed
  def updateCoverArt(self, force=False):
    self.player.updateCoverArt(force)

  #convert player seconds to summat nice
  def GetInHMS(self, seconds):
      hours = seconds / 3600
      seconds -= 3600*hours
      minutes = seconds / 60
      seconds -= 60*minutes
      if hours == 0:
          return "%02d:%02d" % (minutes, seconds)
      return "%02d:%02d:%02d" % (hours, minutes, seconds)





