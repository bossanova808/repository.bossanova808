from bossanova808.common import *
from resources.lib.store import Store
import xbmc


class KodiPlayer(xbmc.Player):
    """
    This class represents/monitors the Kodi video player
    """

    def __init__(self, *args):
        xbmc.Player.__init__(self)
        log('KodiPlayer __init__')

    def onAVStarted(self):
        """
        This does all the actual work...check if the previous episode exists, and if it has been watched.

        :return:
        """
        log('onAVStarted')
