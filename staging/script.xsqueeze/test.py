#-------------------------------------------------------------------------------
# Name:        test of xsqueeze chooser
# Purpose:
#
# Author:      bossanova808
#
# Created:     04/05/2012
# Copyright:   (c) bossanova808 2012
# Licence:     GPL2
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import sys
from traceback import print_exc

LIB_PATH = "C:\\Users\\jeremy.IMAGESCIENCE\\AppData\\Roaming\\XBMC\\\\addons\\script.xsqueeze\\resources\\lib"
CLASS_PATH = "C:\\Users\\jeremy.IMAGESCIENCE\\AppData\\Roaming\\XBMC\\\\addons\\script.xsqueeze\\resources\\lib\\classes"
PYLMS_PATH = "C:\\Users\\jeremy.IMAGESCIENCE\\AppData\\Roaming\\XBMC\\\\addons\\script.xsqueeze\\resources\\lib\\pylms"

sys.path.append( LIB_PATH )
sys.path.append( CLASS_PATH )
sys.path.append( PYLMS_PATH )

from utils import *

from pylms.server import Server
from pylms.player import Player


def main():

  s = Server("192.168.16.2")
  s.connect()

  print s.get_players()

  player = s.get_player("Jem's SB3")
  #player.set_volume(50)

##  result = s.requestDecoded("albums 0 9 sort:new")
##  print "*** RESULT ["
##  print result

  result = s.request_with_results("albums 0 9 sort:new")
  print "*** RESULT ["
  print result



if __name__ == '__main__':
    main()
