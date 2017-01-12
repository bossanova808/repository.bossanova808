# -*- coding: utf-8 -*-

'''
    Kodu YoctoDisplay Addon
    Copyright (C) 2016 bossanova80    
'''

import os
import sys
from time import strftime

import xbmc
import xbmcaddon

# Minimal code to import bossanova808 common code
ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path')
RESOURCES_PATH = xbmc.translatePath(os.path.join(CWD, 'resources'))
LIB_PATH = xbmc.translatePath(os.path.join(RESOURCES_PATH, "lib"))
YOCTO_PATH = xbmc.translatePath(os.path.join(LIB_PATH, "yoctopuce"))

# Extra imports
sys.path.append(LIB_PATH)
sys.path.append(YOCTO_PATH)

from b808common import *
from infolabels import *
from yoctomaxidisplay import *

# The main processing loop for the 2nd screen
def process2ndScreen():

    monitor = xbmc.Monitor()

    # Run every 1/3rd of a second basically
    while not monitor.waitForAbort(0.33):

        # https://stackoverflow.com/questions/415511/how-to-get-current-time-in-python
        timeNow = strftime("%I:%M")
        temperature = InfoLabel_GetWeatherTemperature()

        # If weather is not ready, show nothing
        if temperature.startswith("Busy") or temperature.startswith("°C"):
            temperature = ""
        else:
            temperature = temperature.replace("°C","°")

        #strip leading zero in platform independent way, if there is one
        if timeNow[0] == "0":
            timeNow = timeNow[1:]

        if temperature != "":
            timeAndTemperature = timeNow + "°" + temperature.replace("°","")
        else:
            timeAndTemperature = timeNow

        if InfoLabel_IsPlayerPlaying():            
            timeRemaining = InfoLabel_GetPlayerTimeRemaining()
            if len(timeRemaining) > 0 and timeRemaining[0] == "0":
                timeRemaining = timeRemaining[1:]
            displayText([timeAndTemperature,"-" + timeRemaining])
        else:            
            displayText([timeNow, temperature])


    # Once Kodi is closing, fall through here and close down nicely...
    cleanupDisplay()
    footprints(False)


if __name__ == '__main__':

    footprints()
    InfoLabel_Initialize()

    # Changing Settings
    # if len(sys.argv) > 1:
    #     if sys.argv[1].startswith('SetBrightness'):
    #         log("Setting Brightness to " + ADDON.getSetting('brightness'))
    #         setBrightness(int(ADDON.getSetting('brightness')))
    #     if sys.argv[1].startswith('ToggleLED'):
    #         log("Toggling LED")
    #         toggleLED()

    # Run the service...
    #else:
  
    registerYoctoAPI()
    registerDisplayandModule()
    describeDisplay()
  
    # Set up the display
    setBrightness(ADDON.getSetting('brightness'))
    setLED(ADDON.getSetting('led'))
    initialiseLayers() 

    # Game loop - this loops until Kodi quits..
    process2ndScreen()
