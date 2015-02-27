import xbmc, xbmcgui
import sys
from traceback import print_exc


def swap_dictionary(original_dict):
   return dict([(v, k) for (k, v) in original_dict.iteritems()])

ACTION_CODES = {

                'ACTION_NONE'             :0,
                'ACTION_MOVE_LEFT'        :1,
                'ACTION_MOVE_RIGHT'       :2,
                'ACTION_MOVE_UP'          :3,
                'ACTION_MOVE_DOWN'        :4,
                'ACTION_PAGE_UP'          :5,
                'ACTION_PAGE_DOWN'        :6,
                'ACTION_SELECT_ITEM'      :7,
                'ACTION_HIGHLIGHT_ITEM'   :8,
                'ACTION_PARENT_DIR'       :9,
                'ACTION_PREVIOUS_MENU'    :10,
                'ACTION_SHOW_INFO'        :11,
                'ACTION_PAUSE'            :12,
                'ACTION_STOP'             :13,
                'ACTION_NEXT_ITEM'        :14,
                'ACTION_PREV_ITEM'        :15,
                'ACTION_FORWARD'          :16,
                'ACTION_REWIND'           :17,
                'REMOTE_0'                :58,
                'REMOTE_1'                :59,
                'REMOTE_2'                :60,
                'REMOTE_3'                :61,
                'REMOTE_4'                :62,
                'REMOTE_5'                :63,
                'REMOTE_6'                :64,
                'REMOTE_7'                :65,
                'REMOTE_8'                :66,
                'REMOTE_9'                :67,
                'ACTION_PLAYER_FORWARD'   :77,
                'ACTION_PLAYER_REWIND'    :78,
                'ACTION_PLAYER_PLAY'      :79,
                'ACTION_VOLUME_UP'        :88,
                'ACTION_VOLUME_DOWN'      :89,
                'ACTION_MUTE'             :91,
                'ACTION_NAV_BACK'         :92,
                'ACTION_CONTEXT_MENU'     :117,
                'ACTION_JUMP_SMS2'        :142,
                'ACTION_JUMP_SMS3'        :143,
                'ACTION_JUMP_SMS4'        :144,
                'ACTION_JUMP_SMS5'        :145,
                'ACTION_JUMP_SMS6'        :146,
                'ACTION_JUMP_SMS7'        :147,
                'ACTION_JUMP_SMS8'        :148,
                'ACTION_JUMP_SMS9'        :149,
                'ACTION_FIRST_PAGE'       :159,
                'ACTION_LAST_PAGE'        :160,
}

ACTION_NAMES = swap_dictionary(ACTION_CODES)


################################################################################
################################################################################
### Class ActionHandler (i.e. a window)

class TestWindow(xbmcgui.WindowXML):

  ##############################################################################
  #constructor - create controls & add them to the window

  def __init__( self, *args, **kwargs ):


    #blanks the screen - this is crude, and probably wrong, but works
    self.background = xbmcgui.ControlImage(0,0,1280,720, 'black.png')
    self.addControl(self.background)


  ##############################################################################
  #the method called when the window is inited
  def onInit( self ):
      pass

  ##############################################################################
  # Handle button events

  def onClick( self, control ):
     pass


  ##############################################################################
  # Handle window acitions

  def onAction( self, action ):
    #intercept special XBMC ones first
    if action == ACTION_CODES['ACTION_PREVIOUS_MENU'] or action == ACTION_CODES['ACTION_NAV_BACK']:
      self.close()
    #Start the music chooser
    elif action == ACTION_CODES['ACTION_SHOW_INFO']:
      print("**************** EXECUTING PLUGIN")
      #pluggie="RunPlugin(plugin://plugin.program.b808minimal/?mode=0)"
      pluggie = "ActivateWindow(Programs,plugin://plugin.program.b808minimal"
      xbmc.executebuiltin(pluggie)

      #xbmc.executebuiltin("ActivateWindow(Programs,plugin://plugin.program.b808minimal")






