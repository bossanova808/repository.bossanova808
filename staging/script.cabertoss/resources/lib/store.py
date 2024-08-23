from bossanova808.common import *
import os


class Store:
    """
    Helper class to read in and store the addon settings, and to provide a centralised store

    from resources.lib.store import Store
    log(f'{Store.whatever}')
    """

    # Static class variables, referred to elsewhere by Store.whatever
    # https://docs.python.org/3/faq/programming.html#how-do-i-create-static-class-data-and-static-class-methods
    replaces = (('//.+?:.+?@', '//USER:PASSWORD@'), ('<user>.+?</user>', '<user>USER</user>'), ('<pass>.+?</pass>', '<pass>PASSWORD</pass>'),)
    destination_path = None

    def __init__(self):
        """
        Load in the addon settings and do basic initialisation stuff
        """
        Store.load_config_from_settings()

    @staticmethod
    def load_config_from_settings():
        """
        Load in the addon settings, at start or reload them if they have been changed
        Log each setting as it is loaded
        """
        log("Loading configuration from settings")

        Store.destination_path = ADDON.getSetting('log_path')
        log(f'Logs will be tossed to: {Store.destination_path}')





