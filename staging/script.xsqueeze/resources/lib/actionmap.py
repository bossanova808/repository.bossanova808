#FROM https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h

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
                'ACTION_REWIND'           :17 


}

SQUEEZE_CODES = {

                'ACTION_NONE'             :'',
                'ACTION_MOVE_LEFT'        :'arrow_left',
                'ACTION_MOVE_RIGHT'       :'arrow_right',
                'ACTION_MOVE_UP'          :'arrow_up',
                'ACTION_MOVE_DOWN'        :'arrow_down',
                'ACTION_PAGE_UP'          :'',
                'ACTION_PAGE_DOWN'        :'',
                'ACTION_SELECT_ITEM'      :'play.single',
                'ACTION_HIGHLIGHT_ITEM'   :'',
                'ACTION_PARENT_DIR'       :'arrow_left',
                'ACTION_PREVIOUS_MENU'    :'',
                'ACTION_SHOW_INFO'        :'',
                'ACTION_PAUSE'            :'pause.single',
                'ACTION_STOP'             :'stop',
                'ACTION_NEXT_ITEM'        :'fwd.single',
                'ACTION_PREV_ITEM'        :'rew.single',
                'ACTION_FORWARD'          :'fwd.hold', 
                'ACTION_REWIND'           :'rew.hold'

}

ACTION_NAMES = swap_dictionary(ACTION_CODES)
