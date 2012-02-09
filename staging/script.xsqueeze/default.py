import urllib
import os
import re
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import time
from traceback import print_exc

from pysqueezecenter.server import Server
from pysqueezecenter.player import Player

#create an add on instation and store the reference 
__addon__       = xbmcaddon.Addon()
#store some handy constants
__addonname__   = __addon__.getAddonInfo('name')
__addonid__     = __addon__.getAddonInfo('id')
__author__      = __addon__.getAddonInfo('author')
__version__     = __addon__.getAddonInfo('version')
__cwd__         = __addon__.getAddonInfo('path')
__language__    = __addon__.getLocalizedString
__useragent__   = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.6"

#useful paths
SOURCEPATH = __cwd__
RESOURCES_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources' ) )
STATIC_IMAGES_PATH = xbmc.translatePath( os.path.join( RESOURCES_PATH, 'images' ) )
CHANGING_IMAGES_PATH = xbmc.translatePath("special://profile/addon_data/script.xsqueeze/current_images/");

sys.path.append( os.path.join( RESOURCES_PATH, "lib" ) )

#a file that gives nice names to action numbers
from actionmap import *



################################################################################
################################################################################
################################################################################
# Logging functions
       
def log(message, inst=None):
    if inst is None: 
      xbmc.log(__addonname__ + "-" + __version__ +  ": " + message)
    else:
      xbmc.log(__addonname__ + "-" + __version__ +  ": Exception! " + message + "[" + str(inst) +"]")

def footprints():
    log( "### %s Starting ..." % __addonname__ )
    log( "### Author: %s" % __author__ )
    log( "### Version: %s" % __version__ )


################################################################################
################################################################################
### Class ActionHandler (i.e. a window)

class ActionHandler(xbmcgui.Window): 

  #reference to our instance of a SqueezePlayer
  global player
  
  #constructor - create controls & add them to the window
  def __init__(self):
    #blank the screen - is this the right way?
    self.addControl(xbmcgui.ControlImage(0,0,1920,1080, ''))
        
    #create the controls for the two display text lines
    self.strLine1 = xbmcgui.ControlLabel(300, 200, 500, 200, '', 'font14', '0xFF00FF00')
    self.addControl(self.strLine1)
    self.strLine2 = xbmcgui.ControlLabel(300, 250, 500, 200, '', 'font14', '0xFF00FF00')
    self.addControl(self.strLine2)
    
    #self.coverArt = xbmcgui.ControlImage(300,300,)
    
    #and get the current data on screen...
    self.update()
    
 #updates the display text on screen
  def updateLineDisplay(self):
    newLine1, newLine2 = player.getDisplay()
    self.strLine1.setLabel(newLine1)
    self.strLine2.setLabel(newLine2)

  ##############################################################################
  #this is called every 100 millis and is used to update the window's display
  #e.g. if trac/cover art changes etc 
  def update(self):     
    songChanged = player.songChanged()
     
    #if song has changed, get new cover art etc.
    if songChanged:
      player.updateCoverArt()
      
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
    
    log("Handling action id: " + str(actionNum) +  " Name: " + actionName + " SqueezeCode if any: " + actionSqueeze)

    #intercept special XBMC ones first
    if action == ACTION_CODES['ACTION_PREVIOUS_MENU']: 
      log("XBMC Action: Close")
      running = False
      self.close()

    #elif etc
    
    #otherwise pass the button code to the squeezeplayer
    else:
      log("SqueezePlayer Action: " + actionSqueeze)
      player.button(actionSqueeze)
      self.update()
    

################################################################################
################################################################################
### CLASS SQUEEZEPLAYER 


class SqueezePlayer:

  #reference to our window
  global window

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
      log(" Song change to: " + newSong)
      self.setCurrentTrack(newSong)
      return True;
    else:  
      return False
  
  #downloads the cover art for the current song from the server
  def updateCoverArt(self):
    log( "Updating images" )
    try:
      coverURL = "http://" + self.serverURL + "/music/current/cover.jpg?player=" + self.playerMAC 
      log ("Getting: " + coverURL)
      coverArt = self.image.retrieve(  coverURL , CHANGING_IMAGES_PATH + "currentCover.jpg" )
      log ("Retrieved new cover art")
    except Exception as inst:
      log( "Couldn't retrieve currernt cover art", inst)
    
  
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
    
  #constructor - connect to the server and player so we can do stuff
  def __init__(self):

    #get the various settings... 
    self.serverIP    = __addon__.getSetting('serverIP')
    self.serverPort  = __addon__.getSetting('serverPort')
    self.serverURL   = self.serverIP + ":9000"
    self.playerMAC   = __addon__.getSetting('playerMAC')

    #a handle for opening images
    self.image = urllib.URLopener() 

    #connect to server
    log("Attempting to connect to LMS at:  " + self.serverIP + " on port: " + self.serverPort)      
    try:
      self.sc = Server(hostname=self.serverIP, port=self.serverPort)
      self.sc.connect()
      log( "Logged in: %s" % self.sc.logged_in )
      log( "Version: %s" % self.sc.get_version() )
    except:
      log(" Couldn't connect to server!")
      xbmc.executebuiltin("XBMC.Notification("+ __addonname__ +": Couldn't connect to server!,Check your server settings)")
      raise
    
    #connect to player
    log( "Attempting to connect to player: " + self.playerMAC)
    try:
      self.sb = self.sc.get_player(self.playerMAC) 
    except:
      log(" Couldn't connect to player! " + self.playerMAC )
      xbmc.executebuiltin("XBMC.Notification("+ __addonname__ +": Couldn't connect to player!,Check you player settings)")
      raise

    #take note of the current track...actually, no, instead let it trigger
    #an update on the first time through the loop
    self.currentTrack = ""       
    self.updateCoverArt()
    


################################################################################
################################################################################
### MAIN

if ( __name__ == "__main__" ): 
    
    #log some tracks...
    footprints()

    #make our storage paths
    try:
      if not xbmcvfs.exists( CHANGING_IMAGES_PATH ):
        log ( "Making output directory for cover art etc. in addon_data")
        os.makedirs( CHANGING_IMAGES_PATH )        
    except Exception as inst:
      log( "ERROR: Couldn't make folders in addon_data - bailing out!" )
      sys.exit()
      
    
    try:
      player = SqueezePlayer()
    except:
      print_exc()
      sys.exit()

    #now let's make a window and see if we can send some commands...
    window = ActionHandler()
    # run our window
    
    running = True
    while running:
      window.show()
      xbmc.sleep(100)
      window.update()
        
    # after the window is closed, Destroy it.
    del window
    
    log( "### Exiting XSqueeze..." )
