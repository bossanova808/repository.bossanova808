from bossanova808.common import *
import os


class Store:
    """
    Helper class to read in and store the addon settings, and to provide a centralised store
    """

    # Static class variables, referred to elsewhere by Store.whatever
    # https://docs.python.org/3/faq/programming.html#how-do-i-create-static-class-data-and-static-class-methods
    replaces = (('//.+?:.+?@', '//USER:PASSWORD@'), ('<user>.+?</user>', '<user>USER</user>'), ('<pass>.+?</pass>', '<pass>PASSWORD</pass>'),)
    kodi_log_path = xbmcvfs.translatePath('special://logpath')
    kodi_log_file = os.path.join(kodi_log_path, 'kodi.log')
    kodi_old_log_file = os.path.join(kodi_log_path, 'kodi.old.log')
    destination_path = None
    settings = None

    def __init__(self):
        """
        Load in the addon settings and do basic initialisation stuff
        """
        Store.load_config_from_settings()

    @staticmethod
    def load_config_from_settings():
        """
        Load in the addon settings, at start or reload them if they have been changed
        """
        log("Loading configuration from settings")
        Store.destination_path = ADDON.getSetting('log_path')

    @staticmethod
    def log_configuration():
        """
        Log out our key configuration values
        """
        log(f'Logs will be tossed to: {Store.destination_path}')


