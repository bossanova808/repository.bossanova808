import xbmcaddon

from bossanova808.constants import HOME_WINDOW, TRANSLATE
from bossanova808.logger import Logger
from bossanova808.utilities import clear_property
from bossanova808.show_list import ShowList
# noinspection PyPackages
from .decoder_override import DecoderOverride
# noinspection PyPackages
from .messages import (AMLOGIC_PROPERTY, CONTEXT_MENU_PROPERTY, FILES_FILE, NOTIFY_FILES_CHANGED, NOTIFY_SERIES_CHANGED, SERIES_FILE,
                       notify_info, notify_service)
# noinspection PyPackages
from .monitor import KodiEventMonitor
# noinspection PyPackages
from .player import KodiPlayer
# noinspection PyPackages
from .store import NUMBER_OF_PATH_SETTINGS, Store


# How often the service loop checks what's focused/playing
TICK_SECONDS = 0.5


def manage_series():
    """
    The settings action: pick series to take off the list of those set to always use software
    decoding.

    :return:
    """
    Logger.start('(Manage series)')
    if ShowList(SERIES_FILE).manage(TRANSLATE(32030), TRANSLATE(32031)):
        notify_service(NOTIFY_SERIES_CHANGED)
    Logger.stop('(Manage series)')


def manage_files():
    """
    The settings action: pick individual videos to take off the list of those set to always use
    software decoding.

    :return:
    """
    Logger.start('(Manage videos)')
    if ShowList(FILES_FILE).manage(TRANSLATE(32072), TRANSLATE(32073)):
        notify_service(NOTIFY_FILES_CHANGED)
    Logger.stop('(Manage videos)')


def clear_paths():
    """
    The settings action: clear all the paths the automatic rules are limited to (the settings
    dialog's file browser can't clear one), so the rules apply everywhere again.

    :return:
    """
    Logger.start('(Clear paths)')
    addon = xbmcaddon.Addon()
    for i in range(1, NUMBER_OF_PATH_SETTINGS + 1):
        addon.setSetting(f"Path{i}", "")
    notify_info(TRANSLATE(32065))
    Logger.stop('(Clear paths)')


def run(args=None):
    """
    Either the settings action to manage the series list, or - by default - the service: load
    settings, wire up the Kodi monitor/player, then run until Kodi asks us to stop, rechecking the
    decoder override every half second in the meantime.

    :param args: the script's arguments (sys.argv)
    :return:
    """
    if args and len(args) > 1 and args[1] == 'ManageSeries':
        manage_series()
        return
    if args and len(args) > 1 and args[1] == 'ManageFiles':
        manage_files()
        return
    if args and len(args) > 1 and args[1] == 'ClearPaths':
        clear_paths()
        return

    Logger.start()
    # load settings and create the store for our globals
    Store()
    Store.kodi_event_monitor = KodiEventMonitor()
    Store.kodi_player = KodiPlayer()
    DecoderOverride.recover_stale_state()

    while not Store.kodi_event_monitor.abortRequested():
        DecoderOverride.tick()
        if Store.kodi_event_monitor.waitForAbort(TICK_SECONDS):
            Logger.debug('Abort Requested')
            break

    # Best-effort restore in case we're still mid-override when Kodi shuts down
    DecoderOverride.shutdown()
    # The context menu item needs the service running, so don't offer it once we've stopped
    clear_property(HOME_WINDOW, CONTEXT_MENU_PROPERTY)
    clear_property(HOME_WINDOW, AMLOGIC_PROPERTY)

    Logger.stop()
