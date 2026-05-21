from bossanova808.logger import Logger
from bossanova808.utilities import get_setting, get_setting_as_bool


class Store:
    """
    Helper class to read in and store the addon settings, and to provide a centralised store
    """

    # Static class variables
    enable_resume_fix = True
    jumpback_delta = 7
    jumpback = 7
    clear_tv_ratings = False

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

        Store.enable_resume_fix = get_setting_as_bool("enable_resume_fix")
        Logger.info(f"Enable resume adjustment behavior: {Store.enable_resume_fix}")

        try:
            Store.jumpback_delta = int(get_setting("jumpback_delta"))
        except (ValueError, TypeError):
            Logger.warning("Invalid jumpback_delta setting, using default")
            Store.jumpback_delta = 7

        try:
            Store.jumpback = int(get_setting("jumpback_seconds"))
        except (ValueError, TypeError):
            Logger.warning("Invalid jumpback_seconds setting, using default")
            Store.jumpback = 7

        if Store.enable_resume_fix:
            Logger.info(f"Jump back delta set to {Store.jumpback_delta}")
            Logger.info(f"Jump back at resume seconds set to {Store.jumpback}")

        Store.clear_tv_ratings = get_setting_as_bool("clear_tv_ratings")
        Logger.info(f"Purge TV/Episode ratings: {Store.clear_tv_ratings}")
