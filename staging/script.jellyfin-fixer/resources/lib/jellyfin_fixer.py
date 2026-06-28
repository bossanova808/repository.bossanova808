import xbmcgui
import xbmc

from bossanova808.logger import Logger

# noinspection PyPackages
from .monitor import KodiEventMonitor
# noinspection PyPackages
from .store import Store
# noinspection PyPackages
from .ratings_purger import purge_tv_ratings, handle_jellyfin_sync_purge

# Give up waiting after 15 minutes (enough even for a very long sync)
JELLYFIN_STARTUP_TIMEOUT = 900  # seconds


# This is 'main'...
# noinspection PyUnusedLocal
def run():
    Logger.start()

    try:
        Store.load_config_from_settings()

        # Pass library update notification callback directly into the monitor
        kodi_monitor = KodiEventMonitor(jellyfin_update_callback=handle_jellyfin_sync_purge)

        # Wire settings updates to also trigger a real-time database clean evaluation
        def updated_settings_callback():
            Store.load_config_from_settings()
            if Store.clear_ratings:
                purge_tv_ratings()

        kodi_monitor.onSettingsChanged = updated_settings_callback

        player = None
        Logger.info(f'Waiting for Jellyfin startup/intial sync (timeout: {JELLYFIN_STARTUP_TIMEOUT}s)...')
        home = xbmcgui.Window(10000)
        elapsed = 0
        startup_successful = False

        while elapsed < JELLYFIN_STARTUP_TIMEOUT:
            if kodi_monitor.waitForAbort(1):
                break
            if home.getProperty('jellyfin_startup') == 'true':
                Logger.warning('Jellyfin startup/initial sync complete - JELLYFIN FIXER now ACTIVE.')
                startup_successful = True
                break
            elapsed += 1
        else:
            Logger.error(f'Jellyfin startup not detected after {JELLYFIN_STARTUP_TIMEOUT}s - JELLYFIN FIXER *NOT* ACTIVE.')

        # Only proceed to initialisation if the startup signal arrived
        if startup_successful:
            # Fire initial sanitation run when the startup delay completes or is bypassed
            purge_tv_ratings()

            if Store.enable_resume_fix:
                # noinspection PyPackages
                from .player import KodiPlayer
                player = KodiPlayer()

            while not kodi_monitor.abortRequested():
                if kodi_monitor.waitForAbort(1):
                    break
    finally:
        # We're done...
        Logger.stop()
        player = None
        kodi_monitor = None
