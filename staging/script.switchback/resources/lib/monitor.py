from bossanova808.common import *
from resources.lib.store import Store
import xbmc


class KodiEventMonitor(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        log('KodiEventMonitor __init__')

    def onSettingsChanged(self):
        log('onSettingsChanged - reload them.')
        Store.load_config_from_settings()

    # noinspection PyMethodMayBeStatic
    def onAbortRequested(self):
        log('onAbortRequested')
