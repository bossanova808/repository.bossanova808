from bossanova808.logger import Logger
from bossanova808.utilities import get_setting_as_bool


class Store:
    """
    Helper class to read in and store the addon settings, and to provide a centralised store
    """

    # Static class variables
    clear_ratings = False
    notify_sync_complete = True

    def __init__(self):
        """
        Load in the addon settings and do basic initialisation stuff
        """
        Store.load_config_from_settings()

    @staticmethod
    def load_config_from_settings() -> None:
        """
        Load in the addon settings, at start or reload them if they have been changed
        :return: None
        """
        Logger.info("Loading configuration")

        Store.clear_ratings = get_setting_as_bool("clear_tv_ratings")
        Logger.info(f"Purge TV/Episode ratings: {Store.clear_ratings}")

        Store.notify_sync_complete = get_setting_as_bool("notify_sync_complete")
        Logger.info(f"Notify when initial Jellyfin sync is complete: {Store.notify_sync_complete}")
