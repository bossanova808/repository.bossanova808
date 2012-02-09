import xbmcgui
import constants
import Logger
#a file that gives nice names to action numbers
from actionmap import *

################################################################################
################################################################################
### Class ActionHandler (i.e. a window)

class NowPlayingWindow(xbmcgui.Window): 
 
  #constructor - create controls & add them to the window
  def __init__(self, player):
  
    self.player = player
    
    Logger.log("@")
    #a Now Playing Window is attached to a particular player, so store a refernce to it
    #self.player = player
    Logger.log("@")
    
    #blank the screen - is this the right way?
    self.addControl(xbmcgui.ControlImage(0,0,1920,1080, ''))
    Logger.log("@")

    #cover art images - one diffuse in BG, large, smaller over the top
    self.coverArtBG = xbmcgui.ControlImage(0,0,1280, 720, constants.CHANGING_IMAGES_PATH + "currentCover.jpg", colorDiffuse='0x66666666')
    self.addControl(self.coverArtBG) 
    self.coverArt = xbmcgui.ControlImage(860,300,400, 400, constants.CHANGING_IMAGES_PATH + "currentCover.jpg")
    self.addControl(self.coverArt) 
        
    #create the controls for the two man SB display text lines
    self.strLine1 = xbmcgui.ControlLabel(10, 20, 500, 200, '', 'font14', constants.SQUEEZETEXT)
    self.addControl(self.strLine1)
    self.strLine2 = xbmcgui.ControlLabel(10, 50, 500, 200, '', 'font14', constants.SQUEEZETEXT)
    self.addControl(self.strLine2)
    
    #create the upcoming tracks list controls
    self.upcoming0 = xbmcgui.ControlLabel(10, 120, 1280, 200, '', 'font12', constants.UPCOMINGTEXT)
    self.upcoming1 = xbmcgui.ControlLabel(10, 150, 1280, 200, '', 'font12', constants.UPCOMINGTEXT)
    self.upcoming2 = xbmcgui.ControlLabel(10, 180, 1280, 200, '', 'font12', constants.UPCOMINGTEXT)
    self.upcoming3 = xbmcgui.ControlLabel(10, 210, 1280, 200, '', 'font12', constants.UPCOMINGTEXT)    
    self.addControl(self.upcoming0)
    self.upcoming0.setLabel("Coming up next:")
    self.addControl(self.upcoming1)
    self.addControl(self.upcoming2)
    self.addControl(self.upcoming3)

    Logger.log( "!")
    #and get the current data on screen...
    self.updateUpcomingTracks()
    Logger.log( "#")

    self.update()
    Logger.log( "@")
    
    
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
    Logger.log ("here1")
    songChanged = self.player.songChanged()
    Logger.log ("here2")
     
    #if song has changed, get new cover art etc.
    if songChanged:
      Logger.log ("herea")
    
      self.player.updateCoverArt()
      self.updateUpcomingTracks()
        
    #always update the line display even if song hasn't changed 
    Logger.log ("here3")
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
      running = False
      self.close()

    #elif etc
    
    #otherwise pass the button code to the squeezeplayer
    else:
      Logger.log("SqueezePlayer Action: " + actionSqueeze)
      self.player.button(actionSqueeze)
      self.update()
