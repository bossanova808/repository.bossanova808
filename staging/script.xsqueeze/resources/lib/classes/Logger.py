import xbmc
import constants

################################################################################
# Log a message to the XBMC Log, and an exception is supplied

def log(message, inst=None):
    if inst is None:
      xbmc.log(constants.__addonname__ + "-" + constants.__version__ +  ": " + str(message))
    else:
      xbmc.log(constants.__addonname__ + "-" + constants.__version__ +  ": Exception: " + str(message) + "[" + str(inst) +"]")


################################################################################
# Log a startup message to the XBMC log

def footprints():

    log( "### %s Starting ..." % constants.__addonname__ )
    log( "### Author: %s" % constants.__author__ )
    log( "### Version: %s" % constants.__version__ )




