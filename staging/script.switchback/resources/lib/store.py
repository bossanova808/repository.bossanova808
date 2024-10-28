import json
from json import JSONDecodeError

from bossanova808.constants import *
from bossanova808.logger import Logger
from bossanova808.notify import Notify
import os
from types import SimpleNamespace

from resources.lib.playback import Playback


class Store:
    """
    Helper class to read in and store the addon settings, and to provide a centralised store
    """

    # Static class variables, referred to elsewhere by Store.whatever
    # https://docs.python.org/3/faq/programming.html#how-do-i-create-static-class-data-and-static-class-methods
    kodi_event_monitor = None
    kodi_player = None
    # Holds our playlist of things played back, in first is the latest order
    switchback_list = []
    switchback_list_file = xbmcvfs.translatePath(os.path.join(PROFILE, "switchback_list.json"))
    current_playback = None
    # Basic settings
    maximum_list_length = ADDON.getSettingInt('maximum_list_length')

    def __init__(self):
        """
        Load in the addon settings and do basic initialisation stuff
        """
        Store.load_config_from_settings()

    @staticmethod
    def load_config_from_settings():
        """
        Load in the addon settings, at start or reload them if they have been changed
        :return:
        """
        Logger.info("Loading configuration")
        Logger.info(f"Maximum Switchback list length is: {Store.maximum_list_length}")

        Logger.info(f"Loading Switchback playlist from file: {Store.switchback_list_file}")
        try:
            with open(Store.switchback_list_file, 'r') as switchback_list_file:
                switchback_list_json = json.load(switchback_list_file)
                for playback in switchback_list_json:
                    Store.switchback_list.append(Playback(**playback))
        except FileNotFoundError:
            Logger.error("Unable to load existing switchback list (file not found), so creating empty switchback file")
            # Creates an empty Switchback list file if it doesn't yet exist
            os.makedirs(os.path.dirname(Store.switchback_list_file), exist_ok=True)
            with open(Store.switchback_list_file, 'w'):
                pass
            Store.switchback_list = []
        except JSONDecodeError:
            Logger.error("Unable to load existing switchback list, JSONDecodeError...corrupt or empty, starting a new empty list")
            Store.switchback_list = []
        except:
            raise

        Logger.info("Loaded Switchback List is:")
        Logger.info(Store.switchback_list)

    @staticmethod
    def save_switchback_list():
        with open(Store.switchback_list_file, 'w', encoding='utf-8') as f:
            temp_json = []
            for playback in Store.switchback_list:
                temp_json.append(playback.toJson())
            temp_json = ',\n'.join(temp_json)
            f.write(f"[\n{temp_json}\n]\n")



