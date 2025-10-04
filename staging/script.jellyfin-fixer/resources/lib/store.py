from bossanova808.logger import Logger
from bossanova808.utilities import get_setting, get_setting_as_bool


class Store:
    """
    Helper class to read in and store the addon settings, and to provide a centralised store
    """

    # Static class variables, referred to elsewhere by Store.whatever
    # https://docs.python.org/3/faq/programming.html#how-do-i-create-static-class-data-and-static-class-methods
    jumpback = 7
    jumpback_at_start = True
    jumpback_at_start_after_seconds = 1

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
        try:
            Store.jumpback = int(get_setting("jumpback_seconds"))
        except (ValueError, TypeError):
            Logger.warning("Invalid jumpback_seconds setting, using default")
            Store.jumpback = 7
        Logger.info(f"Jump back at resume seconds set to {Store.jumpback}")

        Store.jumpback_at_start = get_setting_as_bool("jumpback_at_start")
        Logger.info(f"Jump back on start: {Store.jumpback_at_start}")

        try:
            Store.jumpback_at_start_after_seconds = int(get_setting("jumpback_at_start_after_seconds"))
        except (ValueError, TypeError):
            Logger.warning("Invalid jumpback_at_start_after_seconds setting, using default")
            Store.jumpback_at_start_after_seconds = 1
        if Store.jumpback_at_start:
            Logger.info(f"Jump back on start after seconds: {Store.jumpback_at_start_after_seconds}")
