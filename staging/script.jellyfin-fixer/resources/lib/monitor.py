from bossanova808.logger import Logger
from resources.lib.store import Store
import xbmc


class KodiEventMonitor(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        """
        Initialize the KodiEventMonitor by constructing the xbmc.Monitor base and recording a debug message.
        """
        xbmc.Monitor.__init__(self)
        Logger.debug('KodiEventMonitor __init__')

    def onSettingsChanged(self):
        """
        Handle addon settings changes by reloading the addon's configuration from Kodi settings.
        
        Called by Kodi when settings are changed; triggers reloading of configuration so the addon uses the updated settings.
        """
        Logger.info('onSettingsChanged - reload them.')
        Store.load_config_from_settings()

    # noinspection PyMethodMayBeStatic
    def onAbortRequested(self):
        """
        Handle an abort request from Kodi.
        
        Logs a debug message indicating that an abort was requested.
        """
        Logger.debug('onAbortRequested')
