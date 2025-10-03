from bossanova808.logger import Logger


class Store:
    """
    Helper class to read in and store the addon settings, and to provide a centralised store
    """

    # Static class variables, referred to elsewhere by Store.whatever
    # https://docs.python.org/3/faq/programming.html#how-do-i-create-static-class-data-and-static-class-methods
    whatever = None

    def __init__(self):
        """
        Initialize a Store instance and load addon settings into the class-level configuration.
        
        This performs minimal startup initialization so the class-level store is populated from the addon's settings.
        """
        Store.load_config_from_settings()

    @staticmethod
    def load_config_from_settings():
        """
        Load addon settings into the centralized Store at startup or when settings change.
        
        Reads the current addon configuration and updates the module-level store so other code can access up-to-date settings.
        """
        Logger.log("Loading configuration")
