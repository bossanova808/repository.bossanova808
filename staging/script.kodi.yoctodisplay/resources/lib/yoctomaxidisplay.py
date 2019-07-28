# -*- coding: utf-8 -*-
import os, sys

YOCTO_PATH = os.path.join( os.getcwd(), "yoctopuce" )
sys.path.append( YOCTO_PATH )

B808_PATH = os.path.join( os.getcwd(), "b808common" )
sys.path.append( B808_PATH )

from yocto_api import *
from yocto_display import *
from traceback import format_exc
from platform import python_version

# By deafult, all these are empty references
display = None
module = None
drawingLayer = None
displayLayer = None

try:
    from b808common import log as log
except ImportError:
    print("\nXBMC is not available -> probably unit testing")
    def log(str):
        print(str)

#########################################################
# SETUP FUNCTIONS
#########################################################

def registerYoctoAPI():
    
    log("registerYoctoAPI")
    errmsg = YRefParam()
    # Setup the API to use local USB devices
    if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
        log("Could not init Yocto API: " + str(errmsg))
        #sys.exit("Could not init Yocto API")


def registerDisplayandModule():

    log("registerDisplayandModule")
    
    global display, module

    display = YDisplay.FirstDisplay()
    if not display:
        sys.exit("Couldn't find the display")

    module = display.get_module()
    if not module:
        sys.exit("Couldn't find the module")
   
    log("Registered display " + str(display) + " and module " + str(module))


def describeDisplay():

    log("describeDisplay")

    global display

    if display.isOnline():
        try:
            log("Display found: " + str(display.describe()) + " - " + str(display.get_displayType()) + " - Friendly name: " + str(display.get_friendlyName( )))
        except Exception as inst:
            log("Exception in describe display..." + format_exc(inst))        
    else:
        log("Can't describeDisplay - display not online?")



#########################################################
# BEHAVIOUR FUNCTIONS (ASSUME DISPLAY IS SETUP)
#########################################################

def setBrightness(brightness):

    log("setBrightness " + str(brightness))

    global display

    display.set_brightness(brightness)


def setLED(on):

    log("setLED " + str(on))

    global module
   
    if on != "false":
        module.set_luminosity(50)
    else:
        module.set_luminosity(0)


def toggleLED():

    log("toggleLED")

    global module

    led = module.get_luminosity()
    log("LED was " + str(led))

    if led==50:
        module.set_luminosity(0)
    else:
        module.set_luminosity(50)

    led = module.get_luminosity()
    log("LED is now " + str(led))


# Set up our simple double buffering
def initialiseLayers():

    log("initialiseLayers")

    global display, drawingLayer, displayLayer

    # Start clean
    display.resetAll()

    # Which way is up?
    display.set_orientation(YDisplay.ORIENTATION_RIGHT)
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

    log("displayText " + str(lines))

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
    if python_version().startswith('2'):
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
    else:
        if numberOfLines == 1:
            drawingLayer.drawText(64, 32,YDisplayLayer.ALIGN.CENTER, lines[0])
        if numberOfLines == 2:
            drawingLayer.drawText(64, 1, YDisplayLayer.ALIGN.TOP_CENTER, lines[0])
            drawingLayer.drawText(64, 32, YDisplayLayer.ALIGN.TOP_CENTER, lines[1])
        if numberOfLines == 3:
            drawingLayer.drawText(64, 1, YDisplayLayer.ALIGN.TOP_CENTER, lines[0])
            drawingLayer.drawText(64, 22, YDisplayLayer.ALIGN.TOP_CENTER, lines[1])
            drawingLayer.drawText(64, 44, YDisplayLayer.ALIGN.TOP_CENTER, lines[2])
        if numberOfLines == 4:
            drawingLayer.drawText(64, 1, YDisplayLayer.ALIGN.TOP_CENTER, lines[0])
            drawingLayer.drawText(64, 16, YDisplayLayer.ALIGN.TOP_CENTER, lines[1])
            drawingLayer.drawText(64, 32, YDisplayLayer.ALIGN.TOP_CENTER, lines[2])
            drawingLayer.drawText(64, 48, YDisplayLayer.ALIGN.TOP_CENTER, lines[3])        


    # DISPLAYING
    #log("Swap layer content & show:")
    display.swapLayerContent(1,0)
    displayLayer.unhide()


def cleanupDisplay():
    
    log("cleanupDisplay")

    global display, displayLayer, drawingLayer

    if display:
        # toggleLED()        
        displayLayer.clear()
        drawingLayer.clear()
        log("Cleaned up.")
    else:
        log("Could not clean up - no display found.")


############################################################
# Simple unit test of the display

if __name__ == '__main__':

    log("__main__")
    log('Python', python_version())

    import atexit
    atexit.register(cleanupDisplay)

    log("Testing Yocto MaxiDisplay")

    registerYoctoAPI()
    registerDisplayandModule()

    if not display.isOnline():
        sys.exit("Error - display not online?")
    else:
        describeDisplay()

    initialiseLayers() 

    # toggleLED()    

    while True:
        log("Line 1")
        displayText(["Line 1"])
        time.sleep(2)
        log("Line 1, Line 2")
        displayText(["Line 1","Line 2"])
        time.sleep(2)
        log("Line 1, Line 2, Line 3")
        displayText(["Line 1","Line 2","Line 3"])
        time.sleep(2)
        log("Line 1, Line 2, Line 3, Line 4")
        displayText(["Line 1","Line 2","Line 3","Line 4"])
        time.sleep(2)



