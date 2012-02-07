import urllib
import os
import re
from traceback import print_exc
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs

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
IMAGES_PATH = xbmc.translatePath( os.path.join( RESOURCES_PATH, 'images' ) )
sys.path.append( os.path.join( RESOURCES_PATH, "lib" ) )

#a file that gives nice names to action numbers
from actionmap import *



################################################################################
# log messages neatly to the XBMC master log
       
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
### ActionHandler

class ActionHandler(xbmcgui.Window): 

  global slave

  def __init__(self):
    self.addControl(xbmcgui.ControlImage(0,0,1920,1080, 'special://addon/resources/images/background.png'))
    self.strLine1 = xbmcgui.ControlLabel(300, 200, 500, 200, '', 'font14', '0xFF00FF00')
    self.addControl(self.strLine1)
    self.strLine1.setLabel(slave.line1)
    self.strLine2 = xbmcgui.ControlLabel(300, 250, 500, 200, '', 'font14', '0xFF00FF00')
    self.addControl(self.strLine2)
    self.strLine2.setLabel(slave.line2)
 
  #updates the display text on screen
  def updateDisplay(self):
    self.strLine1.setLabel(slave.line1)
    self.strLine2.setLabel(slave.line2)


#NOT HANDLED
#                 'ACTION_PAGE_UP'          :5,
#                 'ACTION_PAGE_DOWN'        :6,
#                 'ACTION_HIGHLIGHT_ITEM'   :8,
#                 'ACTION_SHOW_INFO'        :11,
#                 'ACTION_PAUSE'            :12,
#                 'ACTION_STOP'             :13,
#                 'ACTION_NEXT_ITEM'        :14,
#                 'ACTION_PREV_ITEM'        :15,
#                 'ACTION_FORWARD'          :16, 
#                 'ACTION_REWIND'           :17 

    
  #Maps XBMC window actions to squeezeslave methods
  def onAction( self, action ):

    actionNum = action.getId()
    actionName = ACTION_NAMES[actionNum]
    actionSqueeze = SQUEEZE_CODES[actionName]
    
    log("Handling action id: " + str(actionNum) +  " Name: " + actionName + " SqueezeCode: " + actionSqueeze)

    #intercept special XBMC ones first
    if action == ACTION_CODES['ACTION_PREVIOUS_MENU']: 
      log("XBMC Action: Close")
      self.close()

    #elif etc
    
    #otherwise pass the button code to the squeezeplayer
    else:
      slave.button(actionSqueeze)

      
    #ALL ACTIONS
    #ACTION DONE -> UPDATE DISPLAY TEXT
    self.updateDisplay()  
    
################################################################################
################################################################################
### SQUEEZESLAVE


class SqueezeSlave:
  def __init__(self):

    #get the various settings... 
    serverIP    = __addon__.getSetting('serverIP')
    serverPort  = __addon__.getSetting('serverPort')
    playerMAC   = __addon__.getSetting('playerMAC')

    log("Connecting to server: " + serverIP + " on port: " + serverPort)  

    sc = Server(hostname=serverIP, port=serverPort)
    sc.connect()
    log( "Logged in: %s" % sc.logged_in )
    log( "Version: %s" % sc.get_version() )
    
    log( "Getting connection to player: " + playerMAC)
    self.sq = sc.get_player(playerMAC)    
    self.line1, self.line2 = self.getdisplay()


  def unquote(self, text):
      try:
          import urllib.parse
          return urllib.parse.unquote(text, encoding=self.charset)
      except ImportError:
          import urllib
          return urllib.unquote(text)

  def getdisplay(self):
    displayText = self.sq.requestRaw("display ? ?", True)  
    lines = displayText.split(" ")
    return self.unquote(lines[2]), self.unquote(lines[3])

  #functions to map buttons to actions and then update the display once actioned...
  #called in ActionHandler...
  def button(self, text):
    self.sq.ir_button(text)
    self.line1, self.line2 = self.getdisplay()    
    



################################################################################
################################################################################
### MAIN

if ( __name__ == "__main__" ): 
    footprints()
    slave = SqueezeSlave()

    line1, line2 = slave.getdisplay()
    print line1
    print line2

    #now let's make a window and see if we can send some commands...
    sqwindow = ActionHandler()
    # run our window
    sqwindow.doModal()
    # after the window is closed, Destroy it.
    del sqwindow
    
    log( "### Exiting XSqueeze..." )
