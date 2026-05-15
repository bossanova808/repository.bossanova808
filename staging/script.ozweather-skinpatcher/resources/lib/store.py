import os
import sys
import xbmc
import xbmcvfs
from bossanova808.constants import CWD
from bossanova808.logger import Logger
from bossanova808.notify import Notify
from bossanova808.utilities import get_addon_version


# Just a place to store all our config stuff, so we don't go crazy with globals
class Store:
    supported_skins = ['amber', 'estuary', 'estouchy', 'confluence', 'plextuary', 'xonfluence', 'aczg', 'aeon', 'osmc']

    # These are all populated by update_from_kodi() - either on __init__ or at any time on demand
    current_skin_path = None
    current_skin = None
    skin_version_now = None
    ozweather_version_now = None

    skin = None
    destination_skin_xml_folder = None
    skin_specific_xml_source_folder = None
    skin_independent_xml_source_folder = None
    xml_destination_folder = None
    current_myweather_xml = None
    current_videofullscreen_xml = None
    backup_myweather_xml = None
    backup_videofullscreen_xml = None

    def __init__(self):
        Store.update_from_kodi()

    @staticmethod
    def update_from_kodi():
        """
        Read the current Kodi skin configuration and populate all Store fields.
        Safe to call at any time - e.g. after a delay to detect a skin change.
        Exits (via sys.exit) if the skin/xml folder cannot be determined,
        matching original behaviour.
        """
        Store.current_skin_path = xbmcvfs.translatePath('special://skin')
        Store.current_skin = os.path.basename(Store.current_skin_path.rstrip('/').rstrip('\\'))
        Store.skin_version_now = get_addon_version(Store.current_skin)
        Store.ozweather_version_now = get_addon_version("weather.ozweather")

        Logger.info(f'OzWeather is version: {Store.ozweather_version_now}')
        Logger.info(f'current_skin is [{Store.current_skin}], version {Store.skin_version_now}')
        Logger.info(f'special://skin is [{Store.current_skin_path}]')
        Logger.info(f'CWD is {CWD}')

        skin = None
        destination_skin_xml_folder = None
        skin_specific_xml_source_folder = None

        # TO SUPPORT A NEW SKIN:
        #
        # First, develop the skin files (including testing controls navigate OK!)
        # Then create a folder for the skin & copy the files
        # Add the skin name to the supported_skins list above
        # Each skin also needs an 'if' below
        #  (skin var in the addon id must match the name of the skin-files subfolder!)
        #  e.g. amber or aeon.nox.silvo etc.

        if 'amber' in Store.current_skin_path:
            Logger.info('Amber in skin folder name -> skin supported.')
            skin = 'amber'
            destination_skin_xml_folder = '1080i'
        if 'estuary' in Store.current_skin_path:
            Logger.info('Estuary in skin folder name -> skin supported.')
            skin = 'estuary'
            destination_skin_xml_folder = 'xml'
        # Plextuary is just Estuary, really...treat it as such
        if 'plextuary' in Store.current_skin_path:
            Logger.info('Plextuary in skin folder name -> skin supported (as Estuary).')
            skin = 'estuary'
            destination_skin_xml_folder = 'xml'
        if 'estouchy' in Store.current_skin_path:
            Logger.info('Estouchy in skin folder name -> skin supported.')
            skin = 'estouchy'
            destination_skin_xml_folder = 'xml'
        # Note Confluence changed from 720 -> 1080 with Omega, so handle that here
        # and below when working out the destination folder
        if 'confluence' in Store.current_skin_path:
            Logger.info('confluence in skin folder name -> skin supported.')
            skin = 'confluence'
            # Kodi >= Omega, when Confluence became 1080p...
            if int(xbmc.getInfoLabel('System.BuildVersionCode').split(".")[0]) >= 21:
                destination_skin_xml_folder = '1080p'
                skin_specific_xml_source_folder = os.path.join(CWD, 'resources', 'skin-files', skin, '1080p')
            else:
                destination_skin_xml_folder = '720p'
                skin_specific_xml_source_folder = os.path.join(CWD, 'resources', 'skin-files', skin, '720p')
        # Confluence Zeitgeist
        if 'aczg' in Store.current_skin_path:
            Logger.info('Confluence Zeitgeist (aczg) in skin folder name -> skin supported.')
            skin = 'aczg'
            destination_skin_xml_folder = 'xml'
        if 'xonfluence' in Store.current_skin_path:
            Logger.info('xonfluence in skin folder name -> skin supported.')
            skin = 'xonfluence'
            destination_skin_xml_folder = 'xml'
        if 'aeon.nox' in Store.current_skin_path:
            Logger.info('aeon.nox in skin folder name -> skin supported.')
            skin = 'aeon'
            destination_skin_xml_folder = '16x9'
        if 'aeon.tajo' in Store.current_skin_path:
            Logger.info('aeon.tajo in skin folder name -> skin supported.')
            skin = 'aeon'
            destination_skin_xml_folder = '1080i'
        if 'skin.osmc' in Store.current_skin_path:
            Logger.info('osmc in skin folder name -> skin supported.')
            skin = 'osmc'
            destination_skin_xml_folder = 'xml'

        if not skin or not destination_skin_xml_folder:
            Logger.error("Error - skin/skin_xml_folder variable is empty - this should never happen!")
            sys.exit(1)

        Store.skin = skin
        Store.destination_skin_xml_folder = destination_skin_xml_folder

        Store.skin_independent_xml_source_folder = os.path.join(CWD, 'resources', 'skin-files', 'skin-independent-components')
        # (Confluence already set above due to different 720p/1080p)
        Store.skin_specific_xml_source_folder = skin_specific_xml_source_folder or os.path.join(CWD, 'resources', 'skin-files', skin)

        Store.xml_destination_folder = os.path.join(Store.current_skin_path, destination_skin_xml_folder)
        Store.current_myweather_xml = os.path.join(Store.xml_destination_folder, 'MyWeather.xml')
        Store.current_videofullscreen_xml = os.path.join(Store.xml_destination_folder, 'VideoFullScreen.xml')
        Store.backup_myweather_xml = os.path.join(Store.xml_destination_folder, 'MyWeather.xml.original')
        Store.backup_videofullscreen_xml = os.path.join(Store.xml_destination_folder, 'VideoFullScreen.xml.original')

        Logger.info(f'Source - Skin independent XML folder is {Store.skin_independent_xml_source_folder}')
        Logger.info(f'Source - Skin specific XML folder is {Store.skin_specific_xml_source_folder}')
        Logger.info(f'Destination - Skin XML folder is {Store.xml_destination_folder}')
        Logger.info(f'Current - MyWeather.xml is {Store.current_myweather_xml}')
        Logger.info(f'Current - VideoFullScreen.xml is {Store.current_videofullscreen_xml}')
        Logger.info(f'Backup - MyWeather.xml will be {Store.backup_myweather_xml}')
        Logger.info(f'Backup - VideoFullScreen.xml will be {Store.backup_videofullscreen_xml}')