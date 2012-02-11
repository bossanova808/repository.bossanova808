import xbmc
import constants

def log(message, inst=None):
    if inst is None:
      xbmc.log(constants.__addonname__ + "-" + constants.__version__ +  ": " + str(message))
    else:
      xbmc.log(constants.__addonname__ + "-" + constants.__version__ +  ": Exception: " + str(message) + "[" + str(inst) +"]")







