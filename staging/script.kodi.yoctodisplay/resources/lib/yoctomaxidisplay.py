# -*- coding: utf-8 -*-
import os, sys

YOCTO_PATH = os.path.join( os.getcwd(), "yoctopuce" )
sys.path.append( YOCTO_PATH )

from yocto_api import *
from yocto_display import *

display = None
module = None
drawingLayer = None
displayLayer = None


def registerYoctoAPI():
    
    print("registerYoctoAPI")
    errmsg = YRefParam()

    # Setup the API to use local USB devices
    if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
        sys.exit("Could not init Yocto API")

def registerDisplayandModule():

    print("registerDisplayandModule")
    
    global display, module

    display = YDisplay.FirstDisplay()
    module = YModule.FirstModule()

    if not module:
        sys.exit("Couldn't find the module")
   
    if not display:
        sys.exit("Couldn't find the display")

def describeDisplay():

    global display

    print("Display found: " + str(display.describe()) + " - " + str(display.get_displayType()) + " - Friendly name: " + str(display.get_friendlyName( )))

def setBrightness(brightness):

    global display
    
    registerDisplayandModule()
    display.set_brightness(brightness)

def setLED(on):

    print("setLED " + str(on))

    global module

    registerDisplayandModule()
   
    if on != "false":
        module.set_luminosity(50)
    else:
        module.set_luminosity(0)


def toggleLED():

    global module

    registerDisplayandModule()

    led = module.get_luminosity()
    print("LED was " + str(led))

    if led==50:
        module.set_luminosity(0)
    else:
        module.set_luminosity(50)

    led = module.get_luminosity()
    print("LED is " + str(led))


# Set things up - and because we're actually assigning to our global vars here, we need to use the global keyword...
def initialiseLayers():

    global display, drawingLayer, displayLayer

    # Start clean
    display.resetAll()

    # Which way is up?
    # display.set_orientation(YDisplay.ORIENTATION_RIGHT)
    # First get the layers
    displayLayer = display.get_displayLayer(0)
    drawingLayer = display.get_displayLayer(1)
    displayLayer.clear()
    drawingLayer.clear()

    # the drawingLayer is set to hidden, the display to shown....simple double buffering
    drawingLayer.hide()
    displayLayer.unhide()


# To draw:
# Clear drawing layer
# Draw text
# Swap drawing layer into display layer

def displayText(lines):

    global display, drawingLayer, displayLayer

    drawingLayer.clear()

    numberOfLines = len(lines)

    # SETUP 
    # Fonts built-in into the device firmware are:
    # Small.yfm (height: 8 pixels)
    # Medium.yfm (height: 16 pixels)
    # Large.yfm (height: 32 pixels)
    # 8x8.yfm (monospaced)    
    if numberOfLines == 1 or numberOfLines == 2:
        # 32 pixel high font, but there is a baseline so up to two lines should be ok.
        drawingLayer.selectFont("Large.yfm")        
    elif numberOfLines == 3 or numberOfLines == 4: 
        # 16 pixel high font, but there is a baseline so up to four lines should be ok.
        drawingLayer.selectFont("Medium.yfm")

    # DRAWING 
    if numberOfLines == 1:
        drawingLayer.drawText(64, 32,YDisplayLayer.ALIGN.CENTER, lines[0].decode('utf8').encode("ISO-8859-1"))
    if numberOfLines == 2:
        drawingLayer.drawText(64, 1, YDisplayLayer.ALIGN.TOP_CENTER, lines[0].decode('utf8').encode("ISO-8859-1"))
        drawingLayer.drawText(64, 32, YDisplayLayer.ALIGN.TOP_CENTER, lines[1].decode('utf8').encode("ISO-8859-1"))
    if numberOfLines == 3:
        drawingLayer.drawText(64, 1, YDisplayLayer.ALIGN.TOP_CENTER, lines[0].decode('utf8').encode("ISO-8859-1"))
        drawingLayer.drawText(64, 22, YDisplayLayer.ALIGN.TOP_CENTER, lines[1].decode('utf8').encode("ISO-8859-1"))
        drawingLayer.drawText(64, 44, YDisplayLayer.ALIGN.TOP_CENTER, lines[2].decode('utf8').encode("ISO-8859-1"))
    if numberOfLines == 4:
        drawingLayer.drawText(64, 1, YDisplayLayer.ALIGN.TOP_CENTER, lines[0].decode('utf8').encode("ISO-8859-1"))
        drawingLayer.drawText(64, 16, YDisplayLayer.ALIGN.TOP_CENTER, lines[1].decode('utf8').encode("ISO-8859-1"))
        drawingLayer.drawText(64, 32, YDisplayLayer.ALIGN.TOP_CENTER, lines[2].decode('utf8').encode("ISO-8859-1"))
        drawingLayer.drawText(64, 48, YDisplayLayer.ALIGN.TOP_CENTER, lines[3].decode('utf8').encode("ISO-8859-1"))


    # DISPLAYING
    display.swapLayerContent(1,0)
    displayLayer.unhide()

def cleanupDisplay():
    global display, displayLayer, drawingLayer

    # toggleLED()    
    print("cleanupDisplay")
    displayLayer.clear()
    drawingLayer.clear()


############################################################
# Simple unit test of the display

if __name__ == '__main__':

    import atexit
    atexit.register(cleanupDisplay)

    print("Testing Yocto MaxiDisplay")

    registerYoctoAPI()
    registerDisplayandModule()

    if not display.isOnline():
        sys.exit("Error - display not online?")
    else:
        describeDisplay()

    initialiseLayers() 

    # toggleLED()    

    while True:
        print("Line 1")
        displayText(["Line 1"])
        time.sleep(2)
        print("Line 1, Line 2")
        displayText(["Line 1","Line 2"])
        time.sleep(2)
        print("Line 1, Line 2, Line 3")
        displayText(["Line 1","Line 2","Line 3"])
        time.sleep(2)
        print("Line 1, Line 2, Line 3, Line 4")
        displayText(["Line 1","Line 2","Line 3","Line 4"])
        time.sleep(2)



