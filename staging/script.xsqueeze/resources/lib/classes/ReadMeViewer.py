# Modules general
import os

# Modules XBMC
import xbmc
import xbmcgui
from xbmcaddon import Addon
import constants
from traceback import print_exc

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
        self.window.getControl( self.CONTROL_LABEL ).setLabel( "%s from %s" % ( heading, constants.__addonname__, ) )
        # set text
        self.window.getControl( self.CONTROL_TEXTBOX ).setText( text )

    def getText( self ):
        try:
            txt = open( os.path.join( constants.__cwd__, "FIRSTRUN.txt" ) ).read()
            return "Your First Run Reminder...", txt
        except:
            print_exc()
        return "", ""

