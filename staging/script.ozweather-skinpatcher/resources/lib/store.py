import os
import sys
import xbmc
import xbmcvfs
from bossanova808.constants import CWD
from bossanova808.logger import Logger


# Just a place to store all our config stuff, so we don't go crazy with globals
class Store:

    def __init__(self):
        pass
    
    supported_skins = ['amber', 'estuary', 'estouchy', 'confluence', 'xonfluence', 'aczg', 'aeon', 'osmc']
    current_skin_path = xbmcvfs.translatePath('special://skin')
    current_skin = os.path.basename(current_skin_path.rstrip('/').rstrip('\\'))

    Logger.info(f'special://skin is [{current_skin_path}]')
    Logger.info(f'current_skin is [{current_skin}]')
    Logger.info(f'CWD is {CWD}')

    skin = None
    destination_skin_xml_folder = None
    skin_specific_xml_source_folder = None

    # TO SUPPORT A NEW SKIN:
    #
    # First, develop the skin files (including testing controls navigate OK!)
    # Then create a folder for the skin & copy the files
    # Add the skin name to the supported skins below
    # Each skin also needs an 'if' below
    #  (skin var in the addon id must match the name of the tweaks file!)
    #  e.g. amber or aeon.nox.silvo etc.

    if 'amber' in current_skin_path:
        Logger.info('Amber in skin folder name -> skin supported.')
        skin = 'amber'
        destination_skin_xml_folder = '1080i'
    if 'estuary' in current_skin_path:
        Logger.info('Estuary in skin folder name -> skin supported.')
        skin = 'estuary'
        destination_skin_xml_folder = 'xml'
    if 'plextuary' in current_skin_path:
        Logger.info('Plextuary in skin folder name -> skin supported (as Estuary).')
        skin = 'estuary'
        destination_skin_xml_folder = 'xml'
    if 'estouchy' in current_skin_path:
        Logger.info('Estouchy in skin folder name -> skin supported.')
        skin = 'estouchy'
        destination_skin_xml_folder = 'xml'
    # Note Confluence changed from 720 -> 1080 with Omega, so handle that here
    # and below when working out the destination folder
    if 'confluence' in current_skin_path:
        Logger.info('confluence in skin folder name -> skin supported.')
        skin = 'confluence'
        # Kodi > Omega, when Confluence became 1080p...
        if int(xbmc.getInfoLabel('System.BuildVersionCode').split(".")[0]) >= 21:
            destination_skin_xml_folder = '1080p'
            skin_specific_xml_source_folder = os.path.join(CWD, 'resources', 'skin-files', skin, '1080p')
        else:
            destination_skin_xml_folder = '720p'
            skin_specific_xml_source_folder = os.path.join(CWD, 'resources', 'skin-files', skin, '720p')
    # Confluence Zeitgeist
    if 'aczg' in current_skin_path:
        Logger.info('Confluence Zeitgeist (aczg) in skin folder name -> skin supported.')
        skin = 'aczg'
        destination_skin_xml_folder = 'xml'
    if 'xonfluence' in current_skin_path:
        Logger.info('xonfluence in skin folder name -> skin supported.')
        skin = 'xonfluence'
        destination_skin_xml_folder = 'xml'
    if 'aeon.nox' in current_skin_path:
        Logger.info('aeon.nox in skin folder name -> skin supported.')
        skin = 'aeon'
        destination_skin_xml_folder = '16x9'
    if 'aeon.tajo' in current_skin_path:
        Logger.info('aeon.tajo in skin folder name -> skin supported.')
        skin = 'aeon'
        destination_skin_xml_folder = '1080i'
    if 'skin.osmc' in current_skin_path:
        Logger.info('osmc in skin folder name -> skin supported.')
        skin = 'osmc'
        destination_skin_xml_folder = 'xml'

    if not skin or not destination_skin_xml_folder:
        Logger.error("Error - skin/skin_xml_folder variable is empty - this should never happen!")
        sys.exit(1)

    skin_independent_xml_source_folder = os.path.join(CWD, 'resources', 'skin-files', 'skin-independent-components')
    # (Confluence already set above due to different 720p/1080p)
    if not skin_specific_xml_source_folder:
        skin_specific_xml_source_folder = os.path.join(CWD, 'resources', 'skin-files', skin)
    xml_destination_folder = os.path.join(current_skin_path, destination_skin_xml_folder)
    current_myweather_xml = os.path.join(xml_destination_folder, 'MyWeather.xml')
    current_videofullscreen_xml = os.path.join(xml_destination_folder, 'VideoFullScreen.xml')
    backup_myweather_xml = os.path.join(xml_destination_folder, 'MyWeather.xml.original')
    backup_videofullscreen_xml = os.path.join(xml_destination_folder, 'VideoFullScreen.xml.original')

    Logger.info(f'Source - Skin independent XML folder is {skin_independent_xml_source_folder}')
    Logger.info(f'Source - Skin specific XML folder is {skin_specific_xml_source_folder}')
    Logger.info(f'Destination - Skin XML folder is {xml_destination_folder}')
    Logger.info(f'Current - MyWeather.xml is {current_myweather_xml}')
    Logger.info(f'Current - VideoFullScreen.xml is {current_videofullscreen_xml}')
    Logger.info(f'Backup - MyWeather.xml will be {backup_myweather_xml}')
    Logger.info(f'Backup - VideoFullScreen.xml will be {backup_videofullscreen_xml}')