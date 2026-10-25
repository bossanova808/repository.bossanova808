import xbmcaddon

from bossanova808.constants import HOME_WINDOW, TRANSLATE
from bossanova808.logger import Logger
from bossanova808.notify import Notify
from bossanova808.utilities import clear_property
from bossanova808.show_list import ShowList
# noinspection PyPackages
from .decoder_override import DecoderOverride
# noinspection PyPackages
from .messages import AMLOGIC_PROPERTY, CONTEXT_MENU_PROPERTY, NOTIFY_SERIES_CHANGED, SERIES_FILE, SERIES_LISTED_PROPERTY, notify_service
# noinspection PyPackages
from .monitor import KodiEventMonitor
# noinspection PyPackages
from .player import KodiPlayer
# noinspection PyPackages
from .store import NUMBER_OF_PATH_SETTINGS, Store


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
    Notify.info(TRANSLATE(32065))
    Logger.stop('(Clear paths)')


def run(args=None):
    """
    Either the settings action to manage the series list, or - by default - the service: load
    settings, wire up the Kodi monitor/player, then run until Kodi asks us to stop, rechecking the
    decoder override once a second in the meantime.

    :param args: the script's arguments (sys.argv)
    :return:
    """
    if args and len(args) > 1 and args[1] == 'ManageSeries':
        manage_series()
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
        DecoderOverride.recheck('Periodic check')
        DecoderOverride.periodic_check()
        if Store.kodi_event_monitor.waitForAbort(1):
            Logger.debug('Abort Requested')
            break

    # Best-effort restore in case we're still mid-override when Kodi shuts down
    DecoderOverride.shutdown()
    # The context menu item needs the service running, so don't offer it once we've stopped
    clear_property(HOME_WINDOW, CONTEXT_MENU_PROPERTY)
    clear_property(HOME_WINDOW, SERIES_LISTED_PROPERTY)
    clear_property(HOME_WINDOW, AMLOGIC_PROPERTY)

    Logger.stop()
