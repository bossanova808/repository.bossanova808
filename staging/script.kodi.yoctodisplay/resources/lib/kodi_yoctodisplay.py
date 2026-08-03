# noinspection PyPackages
from .yocto_maxidisplay import YoctoMaxiDisplay
import time
import platform
import xbmc

from bossanova808.utilities import ADDON
from bossanova808.logger import Logger
from bossanova808.notify import Notify


# How long to wait between (re)connection attempts - both at startup (in case the device
# hasn't finished USB-enumerating yet) and for as long as Kodi runs afterwards (in case it
# gets plugged in later, or is disconnected and reconnected mid-session).
RETRY_DELAY_SECONDS = 5

# How often (in main loop iterations, ~0.33s each) to re-check the brightness/LED
# settings in case the user changed them while the service is running.
SETTINGS_RECHECK_EVERY_N_LOOPS = 30

# How long to show the (fairly long) connection-related notifications for
NOTIFICATION_DURATION_MS = 8000


def try_connect(architecture):
    """
    Attempt to connect to and fully set up the display.
    :return: (True, None) on success, or (False, error message) on failure
    """
    try:
        YoctoMaxiDisplay.register_yocto_API(architecture)
        YoctoMaxiDisplay.register_display_and_module()
        YoctoMaxiDisplay.describe_display()
        YoctoMaxiDisplay.set_brightness(ADDON.getSetting('brightness'))
        YoctoMaxiDisplay.set_led(ADDON.getSettingBool('led'))
        YoctoMaxiDisplay.initialise_layers()
        return True, None
    except Exception as e:
        Logger.error("YoctoDisplay connection attempt failed")
        Logger.error(e)
        YoctoMaxiDisplay.free_api()
        return False, str(e)


def run(_args):

    Logger.start()

    YoctoMaxiDisplay()

    architecture = None
    machine = platform.machine().lower()
    # The bundled Yocto library auto-detects the right binary to load, except it can't
    # reliably tell hard-float (armhf) apart from soft-float (armel) on 32-bit Linux ARM,
    # so only override architecture selection in that specific case.
    if platform.system() == 'Linux' and machine.startswith('arm') and machine != 'aarch64':
        architecture = 'armhf'

    monitor = xbmc.Monitor()
    notified_disconnected = False

    # Outer loop: keeps (re)trying to connect for as long as Kodi is running, so the
    # display gets picked up whenever it's plugged in - at startup or any time later -
    # and is retried again if it ever gets disconnected mid-session.
    while not monitor.abortRequested():

        connected, error_message = try_connect(architecture)

        if not connected:
            if not notified_disconnected:
                Notify.warning(f"YoctoDisplay: {error_message} Will keep retrying - see logs.",
                                NOTIFICATION_DURATION_MS)
                notified_disconnected = True
            # Wait before retrying, but bail out immediately & cleanly if Kodi is shutting down
            if monitor.waitForAbort(RETRY_DELAY_SECONDS):
                break
            continue

        if notified_disconnected:
            Notify.info("YoctoDisplay connected.")
            notified_disconnected = False

        # Connected - game loop, displaying data until disconnected or Kodi quits
        # (or this profile is exited). Runs every 1/3rd of a second basically.
        loop_count = 0
        current_brightness_setting = ADDON.getSetting('brightness')
        current_led_setting = ADDON.getSettingBool('led')

        while not monitor.abortRequested():

            if monitor.waitForAbort(0.33):
                break

            # Periodically re-check brightness/LED settings, in case the user changed
            # them while the service is running, and re-apply if they've changed
            loop_count += 1
            if loop_count >= SETTINGS_RECHECK_EVERY_N_LOOPS:
                loop_count = 0
                try:
                    new_brightness_setting = ADDON.getSetting('brightness')
                    if new_brightness_setting != current_brightness_setting:
                        current_brightness_setting = new_brightness_setting
                        YoctoMaxiDisplay.set_brightness(current_brightness_setting)

                    new_led_setting = ADDON.getSettingBool('led')
                    if new_led_setting != current_led_setting:
                        current_led_setting = new_led_setting
                        YoctoMaxiDisplay.set_led(current_led_setting)
                except Exception as e:
                    Logger.warning("Failed to re-apply changed YoctoDisplay settings")
                    Logger.warning(e)

            # This does all the work...
            try:
                process2ndScreen()
            except Exception as e:
                Logger.error("Error updating YoctoDisplay - it may have been disconnected")
                Logger.error(e)
                Notify.warning("YoctoDisplay lost connection, will keep trying to reconnect - see logs.",
                                NOTIFICATION_DURATION_MS)
                notified_disconnected = True
                break

        # Clean up whatever was set up, whether Kodi is exiting or we're about to retry
        try:
            YoctoMaxiDisplay.clean_up_display()
        except Exception as e:
            Logger.warning("Error cleaning up YoctoDisplay")
            Logger.warning(e)

    Logger.stop()


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
