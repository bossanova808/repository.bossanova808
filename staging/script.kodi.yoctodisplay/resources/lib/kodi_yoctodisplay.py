# noinspection PyPackages
from .yocto_maxidisplay import YoctoMaxiDisplay
import time
import platform
import xbmc

from bossanova808.utilities import ADDON
from bossanova808.logger import Logger
from bossanova808.notify import Notify


def run(_args):

    Logger.start()

    YoctoMaxiDisplay()
    architecture = None
    if platform.system() != 'Windows':
        architecture = 'armhf'

    # Fail gracefully if the screen is not available
    try:
        YoctoMaxiDisplay.register_yocto_API(architecture)
        YoctoMaxiDisplay.register_display_and_module()
        YoctoMaxiDisplay.describe_display()
    except:
        Notify.warning("YoctoDisplay connection failed, see logs.")
        Logger.stop()
        return

    # Set up the display
    YoctoMaxiDisplay.set_brightness(ADDON.getSetting('brightness'))
    YoctoMaxiDisplay.set_led(ADDON.getSetting('led'))
    YoctoMaxiDisplay.initialise_layers()

    monitor = xbmc.Monitor()

    # Game loop - this loops until Kodi quits...
    # Run every 1/3rd of a second basically
    while not monitor.abortRequested():

        if monitor.waitForAbort(0.33):
            YoctoMaxiDisplay.clean_up_display()
            Logger.stop()
            break

        # This does all the work...
        process2ndScreen()


# The main processing loop for the 2nd screen
def process2ndScreen():

    # https://stackoverflow.com/questions/415511/how-to-get-current-time-in-python
    time_now = time.strftime("%I:%M")
    temperature = xbmc.getInfoLabel('Weather.Temperature')

    # If weather is not ready, show nothing
    if temperature.startswith("Busy") or temperature.startswith("°C"):
        temperature = ""
    else:
        temperature = temperature.replace("°C", "°")

    # strip leading zero in platform independent way, if there is one
    if time_now[0] == "0":
        time_now = time_now[1:]

    if temperature != "":
        time_and_temperature = time_now + "°" + temperature.replace("°", "")
    else:
        time_and_temperature = time_now

    if xbmc.getCondVisibility('Player.HasVideo') and not xbmc.getCondVisibility('VideoPlayer.Content(livetv)'):
        time_remaining = xbmc.getInfoLabel('Player.TimeRemaining')
        # if len(time_remaining) > 0 and time_remaining[0] == "0":
        #     time_remaining = time_remaining[1:]
        time_remaining = time_remaining.lstrip(" 0:")
        YoctoMaxiDisplay.display_text([time_and_temperature, "-" + time_remaining])
    else:
        YoctoMaxiDisplay.display_text([time_now, temperature])
