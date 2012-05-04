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

class Chooser(xbmcgui.WindowXML):

  ##############################################################################
  #constructor - create controls & add them to the window
  #create our SqueezePlayer object
  #create a threadlock to make squeeze CLI operations safe
  #initialise a few object vars

  def __init__( self, *args, **kwargs ):

    #blanks the screen - this is crude, and probably wrong, but works
    self.background = xbmcgui.ControlImage(0,0,1280,720, 'black.png')
    self.addControl(self.background)

  ##############################################################################
  #the method called when the window is inited
  #starts the GUI update thread...
  def onInit( self ):

    #get the window ID, and if present, the hidden button for artist slideshow...
    self.windowID = xbmcgui.getCurrentWindowId()
    Logger.log("On Init, Chooser window id is "+ str(self.windowID))

    #Set some basic properties
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_WINDOWID_CHOOSER", str(self.windowID))
    xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_TEST1", "TEST ELEMENT 1")

    self.listctrl = self.getControl(50)
    self.listctrl.addItem("hey")
    self.listctrl.addItem("hey2")

    Logger.log("Starting GUI update thread")
    self.running = True
    self.thread = threading.Thread(target=self.update)
    self.thread.setDaemon(True)
    self.thread.start()

  ##############################################################################
  # Essentially the reverse of init - need to remove any controls we added and blank out the properties
  # for a cleaner exit

  def deInit(self):

      Logger.log("Chooser deInit() called - cleaning covers, playlist and waiting on artist.slideshow to signal finish...")
      self.removeControl(self.background)
      del(self.background)
      xbmcgui.Window(self.windowID).clearProperty("XSQUEEZE_WINDOWID_CHOOSER")
      Logger.log("Chooser deInit() complete.")

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

    if actionNum != 0:
      Logger.log("Handling action id: " + str(actionNum) +  " Name: " + actionName + " SqueezeCode if any: " + actionSqueeze)

    #intercept special XBMC ones first
    if action == ACTION_CODES['ACTION_PREVIOUS_MENU'] or action == ACTION_CODES['ACTION_NAV_BACK']:
        #now close the window before we kill it
        self.close()


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
    pass
##    while self.running:
##      with self.lock:
##        self.updateLineDisplay()
##        #trigger a song changed update if required
##        if self.player.songChanged():
##          self.cleanupCovers()
##          self.cleanupPlaylist()
##        #is the player on play, pause or stop?
##        mode = self.player.getMode()
##        if not mode=="stop":
##          self.updateTrackProgress()
##        #set player state icon - play, pause or stop
##        xbmcgui.Window(self.windowID).setProperty("XSQUEEZE_NOWPLAYING", mode)
##        #this control SHOULD be there but jsut in case it's not...
##        try:
##          self.getControl( constants.PLAYSTATE  ).setImage( mode + '.png' )
##        except:
##          pass
##        self.updatePlaylistDetails()
##        self.updateCoverArtFromURLs()







