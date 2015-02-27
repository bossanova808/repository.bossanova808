import time
import xbmc
import os
from traceback import print_exc

#from infolabels import *

#Import the common code - basically the SqueezePlayer class
#which connects to the server and a player
from XSqueezeCommon import *
from b808common import *

 
#############################################################################
###############################################################################

# from xbmc.lcdproc - thanks!!

class LCD_MODE:
    LCD_MODE_GENERAL     = 0
    LCD_MODE_MUSIC       = 1
    LCD_MODE_VIDEO       = 2
    LCD_MODE_TVSHOW      = 3
    LCD_MODE_NAVIGATION  = 4
    LCD_MODE_SCREENSAVER = 5
    LCD_MODE_XBE_LAUNCH  = 6
    LCD_MODE_PVRTV       = 7
    LCD_MODE_PVRRADIO    = 8
    LCD_MODE_MAX         = 9

def getLcdMode():                 
    ret = LCD_MODE.LCD_MODE_GENERAL

    navActive = InfoLabel_IsNavigationActive()
    screenSaver = InfoLabel_IsScreenSaverActive()
    playingVideo = InfoLabel_PlayingVideo()
    playingTVShow = InfoLabel_PlayingTVShow()
    playingMusic = InfoLabel_PlayingAudio()
    playingPVRTV = InfoLabel_PlayingLiveTV()
    playingPVRRadio = InfoLabel_PlayingLiveRadio()

    if navActive:
        ret = LCD_MODE.LCD_MODE_NAVIGATION
    elif screenSaver:
        ret = LCD_MODE.LCD_MODE_SCREENSAVER
    elif playingPVRTV:
        ret = LCD_MODE.LCD_MODE_PVRTV
    elif playingPVRRadio:
        ret = LCD_MODE.LCD_MODE_PVRRADIO
    elif playingTVShow:
        ret = LCD_MODE.LCD_MODE_TVSHOW
    elif playingVideo:
        ret = LCD_MODE.LCD_MODE_VIDEO
    elif playingMusic:
        ret = LCD_MODE.LCD_MODE_MUSIC

    return ret


###############################################################################

def shutdown():
    pass

def renderVFD():
    #here's where we actually do stuff
    log("Tick %s" % time.time())
    
    #srcline = InfoLabel_GetInfoLabel(self.m_lcdMode[mode][inLine]['text'])

    if kodiplayer.isPlaying():
        squeezeplayer.show(xbmc.getInfoLabel("VideoPlayer.Title"),"-" + xbmc.getInfoLabel("VideoPlayer.TimeRemaining"),duration=1,brightness=4,font="huge",centered=True)
        #squeezeplayer.display(xbmc.getInfoLabel("VideoPlayer.Title"),"-" + xbmc.getInfoLabel("VideoPlayer.TimeRemaining"))

###############################################################################
###############################################################################

#Start up
footprints()

#connect to the appropriate player
#is there a mac in Xsqueeze Info Display settings?
mac=ADDON.getSetting('MAC')
log("MAC from Info Display settings is: " + mac)

try:
    #connect to the player defined in xsqueeze settings
    if mac == "":
        squeezeplayer = SqueezePlayer(basicOnly=True)
    else:
        squeezeplayer = SqueezePlayer(basicOnly=True,MAC=mac)
except:
    log( "### Failed to create SqueezePlayer object " )
    print_exc()
    sys.exit()


#InfoLabel_Initialize()

#the main  service loop that waits until xbmc quits 
if __name__ == '__main__':
    monitor = xbmc.Monitor()
    kodiplayer = xbmc.Player()
 
    while not xbmc.abortRequested:
        renderVFD()
        time.sleep(0.3)

    shutdown()


