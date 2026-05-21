from bossanova808.logger import Logger
from resources.lib.store import Store
import xbmc


class KodiEventMonitor(xbmc.Monitor):

    def __init__(self, jellyfin_update_callback=None):
        xbmc.Monitor.__init__(self)
        Logger.debug('KodiEventMonitor __init__')
        self.jellyfin_update_callback = jellyfin_update_callback

    def onSettingsChanged(self):
        Logger.info('onSettingsChanged - reload them.')
        Store.load_config_from_settings()

    # noinspection PyMethodMayBeStatic
    def onAbortRequested(self):
        Logger.debug('onAbortRequested')

    def onNotification(self, sender, method, data):
        # Keep your existing debug output signature intact
        Logger.debug(f"Notification: {sender} | {method} | {data}")

        # Intercept Jellyfin's explicit background sync completion notification
        if sender == "plugin.video.jellyfin" and method == "Other.LibraryChanged":
            Logger.info("KodiEventMonitor: Detected Jellyfin background library modification event.")
            if self.jellyfin_update_callback:
                try:
                    self.jellyfin_update_callback()
                except Exception as e:
                    Logger.error(f"KodiEventMonitor: Error executing Jellyfin update callback: {e}")