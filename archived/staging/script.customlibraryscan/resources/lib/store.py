from .common import *
import os
import json
import xbmc


class Store:
    """
    Helper class to read in and store the addon settings, and to provide a centralised store
    """

    # Static class variables, referred to by Store.whatever
    # https://docs.python.org/3/faq/programming.html#how-do-i-create-static-class-data-and-static-class-methods
    recipe = None
    paths_to_update = []
    kodi_event_monitor = None

    def __init__(self):
        """
        Load in the addon settings and do some basic initialisation stuff
        """
        # Store.load_config_from_settings()
        pass

