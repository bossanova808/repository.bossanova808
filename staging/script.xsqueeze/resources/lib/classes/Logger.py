import xbmc
import os
import constants

################################################################################
# Log a message to the XBMC Log, and an exception if supplied

def log(message, inst=None):
    if inst is None:
      xbmc.log(constants.__addonname__ + "-" + constants.__version__ +  ": " + str(message))
    else:
      xbmc.log(constants.__addonname__ + "-" + constants.__version__ +  ": Exception: " + str(message) + "[" + str(inst) +"]")


################################################################################
# Log a message to the XBMC Log, and an exception if supplied

def notify(messageLine1, messageLine2 = "", time = 6000):
  imagepath = os.path.join(constants.__cwd__ ,"icon.png")
  notifyString = "XBMC.Notification("+ constants.__addonname__ + ": " + messageLine1 +"," + messageLine2+","+str(time)+","+imagepath+")"
  log("XBMC Notificaton Requested: [" + notifyString +"]")
  xbmc.executebuiltin( notifyString )

################################################################################
# Log a startup message to the XBMC log

def footprints():

    log( "### %s Starting ..." % constants.__addonname__ )
    log( "### Author: %s" % constants.__author__ )
    log( "### Version: %s" % constants.__version__ )




