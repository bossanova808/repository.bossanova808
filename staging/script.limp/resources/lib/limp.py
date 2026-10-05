from bossanova808.constants import HOME_WINDOW
from bossanova808.logger import Logger
from bossanova808.utilities import clear_property
# noinspection PyPackages
from .decoder_override import DecoderOverride
# noinspection PyPackages
from .messages import CONTEXT_MENU_PROPERTY
# noinspection PyPackages
from .monitor import KodiEventMonitor
# noinspection PyPackages
from .player import KodiPlayer
# noinspection PyPackages
from .store import Store


def run():
    """
    Start the service: load settings, wire up the Kodi monitor/player, then run until Kodi asks us
    to stop, rechecking the decoder override once a second in the meantime.

    :return:
    """
    Logger.start()
    # load settings and create the store for our globals
    Store()
    Store.kodi_event_monitor = KodiEventMonitor()
    Store.kodi_player = KodiPlayer()

    while not Store.kodi_event_monitor.abortRequested():
        DecoderOverride.recheck('Periodic check')
        if Store.kodi_event_monitor.waitForAbort(1):
            Logger.debug('Abort Requested')
            break

    # Best-effort restore in case we're still mid-override when Kodi shuts down
    DecoderOverride.restore_if_forced('Service shutting down')
    # The context menu item needs the service running, so don't offer it once we've stopped
    clear_property(HOME_WINDOW, CONTEXT_MENU_PROPERTY)

    Logger.stop()
