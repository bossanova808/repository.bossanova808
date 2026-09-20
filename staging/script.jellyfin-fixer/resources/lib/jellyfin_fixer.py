import xbmcgui
import xbmc
import xbmcvfs

from bossanova808.logger import Logger
from bossanova808.constants import ADDON_ID

# noinspection PyPackages
from .monitor import KodiEventMonitor
# noinspection PyPackages
from .store import Store
# noinspection PyPackages
from .ratings_purger import purge_tv_ratings, handle_jellyfin_sync_purge

# Give up waiting after 15 minutes (enough even for a very long sync)
JELLYFIN_STARTUP_TIMEOUT = 900  # seconds
# Once startup handshake is seen, give up waiting for the write-back sync after 30 minutes
JELLYFIN_SYNC_TIMEOUT = 1800  # seconds
# How long to wait, after startup, to see whether a write-back sync even starts
JELLYFIN_SYNC_SETTLE = 30  # seconds

# Sent with a "Jellyfin" heading/icon, so it reads as a continuation of Jellyfin for Kodi's
# own startup notifications (e.g. its "Welcome <user>" toast), rather than as a separate addon
JELLYFIN_SYNC_NOTIFICATION_HEADING = 'Jellyfin'
JELLYFIN_SYNC_NOTIFICATION_MESSAGE = 'Initial sync complete, now ready...'
JELLYFIN_SYNC_NOTIFICATION_ICON = xbmcvfs.translatePath(f'special://home/addons/{ADDON_ID}/resources/notification_icon.png')


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
                Logger.info('Jellyfin startup handshake seen - waiting for library write-back sync to finish...')
                startup_successful = True
                break
            elapsed += 1
        else:
            Logger.error(f'Jellyfin startup not detected after {JELLYFIN_STARTUP_TIMEOUT}s - JELLYFIN FIXER *NOT* ACTIVE.')

        # jellyfin_startup only means Jellyfin for Kodi's fast-sync handshake with the server
        # returned - its writer threads then apply those changes to the Kodi database
        # asynchronously afterwards, and set jellyfin_sync true/cleared around that work.
        # Wait for that to actually finish before treating the sync as complete, otherwise
        # we can purge ratings while Jellyfin is still mid-write.
        if startup_successful:
            sync_elapsed = 0
            sync_seen_active = False
            while sync_elapsed < JELLYFIN_SYNC_TIMEOUT:
                if kodi_monitor.waitForAbort(1):
                    break
                syncing = home.getProperty('jellyfin_sync') == 'true'
                if syncing:
                    sync_seen_active = True
                elif sync_seen_active:
                    break
                elif sync_elapsed >= JELLYFIN_SYNC_SETTLE:
                    break
                sync_elapsed += 1
            Logger.warning('Jellyfin startup/initial sync complete - JELLYFIN FIXER now ACTIVE.')
            if Store.notify_sync_complete:
                xbmcgui.Dialog().notification(heading=JELLYFIN_SYNC_NOTIFICATION_HEADING,
                                               message=JELLYFIN_SYNC_NOTIFICATION_MESSAGE,
                                               icon=JELLYFIN_SYNC_NOTIFICATION_ICON)

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
