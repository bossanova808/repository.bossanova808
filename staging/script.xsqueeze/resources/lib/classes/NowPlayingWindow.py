import xbmcgui
import constants
import Logger
import sys

#a file that gives nice names to action numbers
from actionmap import *
from traceback import print_exc

from SqueezePlayer import *


################################################################################
################################################################################
### Class ActionHandler (i.e. a window)

class NowPlayingWindow(xbmcgui.Window): 
 
  #constructor - create controls & add them to the window
  def __init__(self):

    self.running = True
    
    #create a player instance (is really a player + server combo)    
    try:
      self.player = SqueezePlayer()
    except:
      print_exc()
      sys.exit()
    
    #blank the screen - is this the right way?
    self.addControl(xbmcgui.ControlImage(0,0,1920,1080, ''))

    #cover art images - one diffuse in BG, large, smaller over the top
    #self.coverArtBG = xbmcgui.ControlImage(560,0,720, 720, constants.CHANGING_IMAGES_PATH + "currentCover.jpg", colorDiffuse='0x66666666')
    #self.addControl(self.coverArtBG) 
    self.coverArt0 = xbmcgui.ControlImage(860,300,400, 400, constants.CHANGING_IMAGES_PATH + "currentCover.jpg")
    self.addControl(self.coverArt0) 
        
    self.coverArt1 = xbmcgui.ControlImage(500,600,100, 100, constants.CHANGING_IMAGES_PATH + "currentCoverPlus3.jpg")
    self.addControl(self.coverArt1) 
    self.coverArt2 = xbmcgui.ControlImage(620,600,100, 100, constants.CHANGING_IMAGES_PATH + "currentCoverPlus2.jpg")
    self.addControl(self.coverArt2) 
    self.coverArt3 = xbmcgui.ControlImage(740,600,100, 100, constants.CHANGING_IMAGES_PATH + "currentCoverPlus1.jpg")
    self.addControl(self.coverArt3) 

    #create the controls for the two man SB display text lines
    self.strLine1 = xbmcgui.ControlLabel(20, 20, 1280, 200, '', 'font14', constants.SQUEEZETEXT)
    self.addControl(self.strLine1)
    self.strLine2 = xbmcgui.ControlLabel(20, 50, 1280, 200, '', 'font14', constants.SQUEEZETEXT)
    self.addControl(self.strLine2)
    
    #create the upcoming tracks list controls
    self.upcoming0 = xbmcgui.ControlLabel(20, 460, 820, 200, '', 'font12', constants.UPCOMINGTEXT)
    self.upcoming1 = xbmcgui.ControlLabel(20, 490, 820, 200, '', 'font12', constants.UPCOMINGTEXT)
    self.upcoming2 = xbmcgui.ControlLabel(20, 520, 820, 200, '', 'font12', constants.UPCOMINGTEXT)
    self.upcoming3 = xbmcgui.ControlLabel(20, 550, 820, 200, '', 'font12', constants.UPCOMINGTEXT)    
    self.addControl(self.upcoming0)
    self.upcoming0.setLabel("Coming up next:")
    self.addControl(self.upcoming1)
    self.addControl(self.upcoming2)
    self.addControl(self.upcoming3)

    #and get the current data on screen...
    self.updateUpcomingTracks()
    self.update()
    
    
 #updates the display text on screen
  def updateLineDisplay(self):
    newLine1, newLine2 = self.player.getDisplay()
    self.strLine1.setLabel(newLine1)
    self.strLine2.setLabel(newLine2)

  def updateUpcomingTracks(self):
    upcoming1, upcoming2, upcoming3 = self.player.getPlaylist()
    self.upcoming1.setLabel("1. " + upcoming1)
    self.upcoming2.setLabel("2. " + upcoming2)
    self.upcoming3.setLabel("3. " + upcoming3)
    

  ##############################################################################
  #this is called every 100 millis and is used to update the window's display
  #e.g. if trac/cover art changes etc 
  def update(self):     
    songChanged = self.player.songChanged()
     
    #if song has changed, get new cover art etc.
    if songChanged:    
      self.updateUpcomingTracks()
      self.player.updateCoverArt()
       
    #always update the line display even if song hasn't changed 
    self.updateLineDisplay()
    
    
  ##############################################################################
  #Maps XBMC window actions to squeezeslave methods
  def onAction( self, action ):

    #use to control the main event loop
    global running
   
    actionNum = action.getId()
    actionName = ACTION_NAMES[actionNum]
    actionSqueeze = SQUEEZE_CODES[actionName]
    
    Logger.log("Handling action id: " + str(actionNum) +  " Name: " + actionName + " SqueezeCode if any: " + actionSqueeze)

    #intercept special XBMC ones first
    if action == ACTION_CODES['ACTION_PREVIOUS_MENU']: 
      Logger.log("XBMC Action: Close")
      self.running = False
      self.close()

    #elif etc
    
    #otherwise pass the button code to the squeezeplayer
    else:
      Logger.log("SqueezePlayer Action: " + actionSqueeze)
      self.player.button(actionSqueeze)
      self.update()
