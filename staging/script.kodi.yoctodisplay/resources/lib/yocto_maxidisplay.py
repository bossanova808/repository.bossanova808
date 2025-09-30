import sys
import os


unit_testing = False
try:
    # Running inside Kodi as usual
    from bossanova808.logger import Logger
    from bossanova808.constants import CWD
    sys.path.append(CWD + '/resources/lib/')
    sys.path.append(CWD + '/resources/lib/yoctopuce')
    from yocto_api import *
    from yocto_display import *
except ImportError:
    # Unit testing this module outside Kodi
    unit_testing = True
    CWD = os.getcwd()
    sys.path.append(CWD + '/resources/lib/')
    sys.path.append(CWD + '/resources/lib/yoctopuce')
    sys.path.append('..\\..\\..\\script.module.bossanova808\\resources\\lib')
    print(sys.path)
    from yoctopuce.yocto_api import *
    from yoctopuce.yocto_display import *
    from bossanova808.logger import Logger


class YoctoMaxiDisplay:
    # By default, all these are empty references
    display = None
    module = None
    drawingLayer = None
    displayLayer = None

    def __init__(self):
        pass

    @staticmethod
    def register_yocto_API(architecture=None):
        """
        Register the Yocto API to use a USB attached device
        :return: None
        """
        Logger.info("register_yocto_API")
        errmsg = YRefParam()

        # September 2021 - added to force correct library loading
        # (wrong ELF class: ELFCLASS64 errors in log)
        if architecture:
            YAPI.SelectArchitecture(architecture)

        # Set up the API to use local USB devices
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            Logger.error("Could not init Yocto API: " + str(errmsg))
            if unit_testing:
                sys.exit("Could not init Yocto API")

    @staticmethod
    def register_display_and_module():

        Logger.info("register_display_and_module")

        YoctoMaxiDisplay.display = YDisplay.FirstDisplay()
        if not YoctoMaxiDisplay.display and unit_testing:
            sys.exit("Couldn't find the display")

        if not YoctoMaxiDisplay.display:
            # Bubble this up as we'll send a UI warning notification...
            raise

        YoctoMaxiDisplay.module = YoctoMaxiDisplay.display.get_module()
        if not YoctoMaxiDisplay.module and unit_testing:
            sys.exit("Couldn't find the module")

        Logger.info(f'Registered display {YoctoMaxiDisplay.display} and module {YoctoMaxiDisplay.module}')

    @staticmethod
    def describe_display():

        Logger.info("describe_display")

        if YoctoMaxiDisplay.display.isOnline():
            try:
                Logger.info(f'Display found: {YoctoMaxiDisplay.display.describe()} - '
                            f'Display type: {YoctoMaxiDisplay.display.get_displayType()} - '
                            f'Friendly name: {YoctoMaxiDisplay.display.get_friendlyName()}')
            except Exception as e:
                Logger.error("Exception in describe display...")
                Logger.error(e)
        else:
            Logger.error("Can't describe_display - display not online?")

    @staticmethod
    def set_brightness(brightness):

        Logger.info("set_brightness " + str(brightness))

        YoctoMaxiDisplay.display.set_brightness(brightness)

    @staticmethod
    def set_led(on):

        Logger.info(f'set_led {on}')

        if on != 'false':
            YoctoMaxiDisplay.module.set_luminosity(50)
        else:
            YoctoMaxiDisplay.module.set_luminosity(0)

    @staticmethod
    def toggle_led():

        Logger.info("toggle_led")

        led = YoctoMaxiDisplay.module.get_luminosity()
        Logger.info(f'LED was at luminosity {led}')

        if led == 50:
            YoctoMaxiDisplay.module.set_luminosity(0)
        else:
            YoctoMaxiDisplay.module.set_luminosity(50)

        led = YoctoMaxiDisplay.module.get_luminosity()
        Logger.info(f'LED now at luminosity {led}')

    @staticmethod
    def initialise_layers():
        """
        Set up simple double buffering
        :return:
        """
        Logger.info("initialise_layers")

        # Start clean
        YoctoMaxiDisplay.display.resetAll()

        # Which way is up?
        YoctoMaxiDisplay.display.set_orientation(YDisplay.ORIENTATION_RIGHT)
        # First get the layers
        YoctoMaxiDisplay.displayLayer = YoctoMaxiDisplay.display.get_displayLayer(0)
        YoctoMaxiDisplay.drawingLayer = YoctoMaxiDisplay.display.get_displayLayer(1)
        YoctoMaxiDisplay.displayLayer.clear()
        YoctoMaxiDisplay.drawingLayer.clear()

        # the drawingLayer is initially set to hidden, the display to shown....simple double buffering
        YoctoMaxiDisplay.drawingLayer.hide()
        YoctoMaxiDisplay.displayLayer.unhide()

    @staticmethod
    def display_text(lines):
        """
        To draw:
        Clear drawing layer
        Draw text
        Swap drawing layer into display layer

        Fonts built-in into the device firmware are:
        Small.yfm (height: 8 pixels)
        Medium.yfm (height: 16 pixels)
        Large.yfm (height: 32 pixels)
        8x8.yfm (monospaced)

        :return: None
        """

        # Logger.info(f'display_text {lines}')

        YoctoMaxiDisplay.drawingLayer.clear()
        number_of_lines = len(lines)

        if number_of_lines == 1 or number_of_lines == 2:
            # 32 pixel high font, but there is a baseline so up to two lines should be OK.
            YoctoMaxiDisplay.drawingLayer.selectFont("Large.yfm")
        elif number_of_lines == 3 or number_of_lines == 4:
            # 16 pixel high font, but there is a baseline so up to four lines should be OK.
            YoctoMaxiDisplay.drawingLayer.selectFont("Medium.yfm")

        if number_of_lines == 1:
            YoctoMaxiDisplay.drawingLayer.drawText(64, 32, YDisplayLayer.ALIGN.CENTER, lines[0])
        elif number_of_lines == 2:
            YoctoMaxiDisplay.drawingLayer.drawText(64, 1, YDisplayLayer.ALIGN.TOP_CENTER, lines[0])
            YoctoMaxiDisplay.drawingLayer.drawText(64, 32, YDisplayLayer.ALIGN.TOP_CENTER, lines[1])
        elif number_of_lines == 3:
            YoctoMaxiDisplay.drawingLayer.drawText(64, 1, YDisplayLayer.ALIGN.TOP_CENTER, lines[0])
            YoctoMaxiDisplay.drawingLayer.drawText(64, 22, YDisplayLayer.ALIGN.TOP_CENTER, lines[1])
            YoctoMaxiDisplay.drawingLayer.drawText(64, 44, YDisplayLayer.ALIGN.TOP_CENTER, lines[2])
        elif number_of_lines == 4:
            YoctoMaxiDisplay.drawingLayer.drawText(64, 1, YDisplayLayer.ALIGN.TOP_CENTER, lines[0])
            YoctoMaxiDisplay.drawingLayer.drawText(64, 16, YDisplayLayer.ALIGN.TOP_CENTER, lines[1])
            YoctoMaxiDisplay.drawingLayer.drawText(64, 32, YDisplayLayer.ALIGN.TOP_CENTER, lines[2])
            YoctoMaxiDisplay.drawingLayer.drawText(64, 48, YDisplayLayer.ALIGN.TOP_CENTER, lines[3])
        else:
            Logger.info(f'Number of lines {number_of_lines} - not in 1 to 4 ')
            pass

        # Actually do the display...
        YoctoMaxiDisplay.display.swapLayerContent(1, 0)
        YoctoMaxiDisplay.displayLayer.unhide()

    @staticmethod
    def clean_up_display():

        Logger.info("clean_up_display")

        if YoctoMaxiDisplay.display:
            YoctoMaxiDisplay.displayLayer.clear()
            YoctoMaxiDisplay.drawingLayer.clear()
            Logger.info("Cleaned up.")
        else:
            Logger.error("Could not clean up - no display found.")


# Unit testing - simple function to cycle through 1 to 4 lines of text...
if __name__ == '__main__':

    Logger.info("__main__")

    yocto = YoctoMaxiDisplay()

    import atexit
    atexit.register(YoctoMaxiDisplay.clean_up_display)

    Logger.info("Testing Yocto MaxiDisplay")

    YoctoMaxiDisplay.register_yocto_API()
    YoctoMaxiDisplay.register_display_and_module()

    if not YoctoMaxiDisplay.display.isOnline():
        sys.exit("Error - display not online?")
    else:
        YoctoMaxiDisplay.describe_display()

    YoctoMaxiDisplay.initialise_layers()

    while True:
        Logger.info('Line 1')
        YoctoMaxiDisplay.display_text(['Line 1'])
        time.sleep(2)
        Logger.info('Line 1, Line 2')
        YoctoMaxiDisplay.display_text(['Line 1', 'Line 2'])
        time.sleep(2)
        Logger.info('Line 1, Line 2, Line 3')
        YoctoMaxiDisplay.display_text(['Line 1', 'Line 2', 'Line 3'])
        time.sleep(2)
        Logger.info('Line 1, Line 2, Line 3, Line 4')
        YoctoMaxiDisplay.display_text(['Line 1', 'Line 2', 'Line 3', 'Line 4'])
        time.sleep(2)
        # Can't really see this anyway, but it works..
        # log('Toggling LED')
        # YoctoMaxiDisplay.toggle_led()
        # time.sleep(2)
        # YoctoMaxiDisplay.toggle_led()
