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

__addon__     = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__addonid__   = __addon__.getAddonInfo('id')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')
__cwd__       = __addon__.getAddonInfo('path')
__language__  = __addon__.getLocalizedString
__useragent__    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.6"

SOURCEPATH = __cwd__
RESOURCES_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources' ) )
IMAGES_PATH = xbmc.translatePath( os.path.join( RESOURCES_PATH, 'images' ) )
sys.path.append( os.path.join( RESOURCES_PATH, "lib" ) )


def log(msg):
    xbmc.log( str( msg ),level=xbmc.LOGDEBUG )

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
    self.strAction1 = xbmcgui.ControlLabel(300, 200, 200, 200, '', 'font14', '0xFF00FF00')
    self.addControl(self.strAction1)
    self.strAction1.setLabel(slave.line1)
    self.strAction2 = xbmcgui.ControlLabel(300, 250, 500, 200, '', 'font14', '0xFF00FF00')
    self.addControl(self.strAction2)
    self.strAction2.setLabel(slave.line2)
    

  def onAction( self, action ):
    #PREVMENU -> EXIT
    if action == 10: 
      self.close()

    #LEFT (1) -> TV LEFT
    elif action == 1: 
      print "Left!"
      slave.buttonLeft()
      self.strAction1.setLabel(slave.line1)
      self.strAction2.setLabel(slave.line2)

		#RIGHT (2) -> TV RIGHT
    elif action == 2: 
      print "Right!"
      slave.buttonRight()
      self.strAction1.setLabel(slave.line1)
      self.strAction2.setLabel(slave.line2)
      
  
		#UP (3) -> TV UP
    elif action == 3: 
      print "Up!"
      slave.buttonUp()
      self.strAction1.setLabel(slave.line1)
      self.strAction2.setLabel(slave.line2)

		#DOWN (4) -> TV DOWN
    elif action == 4: 
      print "Down!"
      slave.buttonDown()
      self.strAction1.setLabel(slave.line1)
      self.strAction2.setLabel(slave.line2)

		#SELECT (7) -> TV SELECT
    elif action == 7:
      print "Select!"
      slave.buttonSelect()
      self.strAction1.setLabel(slave.line1)
      self.strAction2.setLabel(slave.line2)
		
    
################################################################################
################################################################################
### SQUEEZESLAVE


class SqueezeSlave:
  def __init__(self):
    #do stuff
    sc = Server(hostname="192.168.1.51", port=9090)
    sc.connect()
    print "Logged in: %s" % sc.logged_in
    print "Version: %s" % sc.get_version()
    self.sq = sc.get_player("00:00:00:00:00:01")    
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

  def button(self, text):
    self.sq.ir_button(text)
    self.line1, self.line2 = self.getdisplay()    
  def buttonDown(self):
    self.button("arrow_down")  
  def buttonUp(self):
    self.button("arrow_up")  
  def buttonLeft(self):
    self.button("arrow_left")  
  def buttonRight(self):
    self.button("arrow_right")  
  def buttonSelect(self):
    self.button("play.single")  



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
