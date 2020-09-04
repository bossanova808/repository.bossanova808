# Modules general
import os

# Modules XBMC
import xbmc
import xbmcgui
from xbmcaddon import Addon
import constants
from traceback import print_exc
from XSqueezeCommon import *

class ReadMeViewer():
    # constants
    WINDOW = 10147
    CONTROL_LABEL = 1
    CONTROL_TEXTBOX = 5

    def __init__( self, *args, **kwargs ):
        # activate the text viewer window
        xbmc.executebuiltin( "ActivateWindow(%d)" % ( self.WINDOW, ) )
        # get window
        self.window = xbmcgui.Window( self.WINDOW )
        # give window time to initialize
        xbmc.sleep( 100 )
        # set controls
        self.setControls()

    def setControls( self ):
        #get header, text
        heading, text = self.getText()
        # set heading
        self.window.getControl( self.CONTROL_LABEL ).setLabel( "%s - %s" % ( heading, ADDONNAME +"-"+ VERSION ) )
        # set text
        self.window.getControl( self.CONTROL_TEXTBOX ).setText( text )

    def getText( self ):
        try:
            txt = open( os.path.join( CWD, "FIRSTRUN.txt" ) ).read()
            return LANGUAGE(19621), txt
        except:
            print_exc()
        return "", ""

