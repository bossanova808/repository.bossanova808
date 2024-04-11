# -*- coding: utf-8 -*-

from resources.lib.common import *
import os
import sys
import glob
import ntpath
import xbmc
import xbmcvfs

global dialog

# TO SUPPORT A NEW SKIN:
#
# First, develop the skin files (including testing controls navigate ok!)
# Then create a folder for the skin & copy the files
# Add the skin name to the supported skins below
# Each skin also needs an 'if' below
#  (skin var in the addon id must match the name of the tweaks file!)
#  e.g. amber or aeon.nox.silvo etc.


# Just a place to store all our config stuff, so we don't go crazy with globals
class Config:

    global dialog

    supported_skins = ['amber', 'estuary', 'estouchy', 'confluence', 'xonfluence', 'aczg', 'aeon', 'osmc']
    current_skin = xbmcvfs.translatePath('special://skin')

    log(f'special://skin Is [{current_skin}]')
    log(f'CWD is {CWD}')

    skin = None
    destination_skin_xml_folder = None
    skin_specific_xml_source_folder = None

    if 'amber' in current_skin:
        log('Amber in skin folder name...proceeding...')
        skin = 'amber'
        destination_skin_xml_folder = '1080i'
    if 'estuary' in current_skin:
        log('Estuary in skin folder name...proceeding...')
        skin = 'estuary'
        destination_skin_xml_folder = 'xml'
    if 'estouchy' in current_skin:
        log('Estouchy in skin folder name...proceeding...')
        skin = 'estouchy'
        destination_skin_xml_folder = 'xml'
    # Note Confluence changed from 720 -> 1080 with Omega, so handle that here
    # and below when working out the destination folder
    if 'confluence' in current_skin:
        log('confluence in skin folder name...proceeding...')
        skin = 'confluence'
        if KODI_VERSION_FLOAT >= 21:
            destination_skin_xml_folder = '1080p'
            skin_specific_xml_source_folder = os.path.join(CWD, 'resources/skin-files/', skin, '1080p')
        else:
            destination_skin_xml_folder = '720p'
            skin_specific_xml_source_folder = os.path.join(CWD, 'resources/skin-files/', skin, '720p')
    # Confluence Zeitgeist
    if 'aczg' in current_skin:
        log('Confluence Zeitgeist (aczg) in skin folder name...proceeding...')
        skin = 'aczg'
        destination_skin_xml_folder = 'xml'
    if 'xonfluence' in current_skin:
        log('xonfluence in skin folder name...proceeding...')
        skin = 'xonfluence'
        destination_skin_xml_folder = 'xml'
    if 'aeon.nox' in current_skin:
        log('aeon.nox in skin folder name...proceeding...')
        skin = 'aeon'
        destination_skin_xml_folder = '16x9'
    if 'aeon.tajo' in current_skin:
        log('aeon.tajo in skin folder name...proceeding...')
        skin = 'aeon'
        destination_skin_xml_folder = '1080i'
    if 'osmc' in current_skin:
        log('osmc in skin folder name...proceeding...')
        skin = 'osmc'
        destination_skin_xml_folder = 'xml'

    if not skin or not destination_skin_xml_folder:
        log("Error - skin/skin_xml_folder variable is empty - this should never happen!")
        sys.exit(1)

    skin_independent_xml_source_folder = os.path.join(CWD, 'resources/skin-files/', 'skin-independent-components')
    # (Confluence already set above due to different 720p/1080p)
    if not skin_specific_xml_source_folder:
        skin_specific_xml_source_folder = os.path.join(CWD, 'resources/skin-files/', skin)
    xml_destination_folder = os.path.join(current_skin, destination_skin_xml_folder)
    current_myweather_xml = os.path.join(xml_destination_folder, 'MyWeather.xml')
    current_videofullscreen_xml = os.path.join(xml_destination_folder, 'VideoFullScreen.xml')
    backup_myweather_xml = os.path.join(xml_destination_folder, 'MyWeather.xml.original')
    backup_videofullscreen_xml = os.path.join(xml_destination_folder, 'VideoFullScreen.xml.original')

    log(f'Source - Skin independent XML folder is {skin_independent_xml_source_folder}')
    log(f'Source - Skin specific XML folder is {skin_specific_xml_source_folder}')
    log(f'Destination - Skin XML folder is {xml_destination_folder}')
    log(f'Current - MyWeather.xml is {current_myweather_xml}')
    log(f'Current - VideoFullScreen.xml is {current_videofullscreen_xml}')
    log(f'Backup - MyWeather.xml will be {backup_myweather_xml}')
    log(f'Backup - VideoFullScreen.xml will be {backup_videofullscreen_xml}')


# Display a notification from OzWeather Skin Patcher to the Kodi user
# By default, in this case, it's an error notification

def notify(message, notification_type=xbmcgui.NOTIFICATION_ERROR, duration=5000):

    global dialog

    dialog.notification('OzWeather Skin Patcher',
                        message,
                        notification_type,
                        duration)


# Backup existing skin files, and install the new ones.
# Backup occurs only once per skin version, it will not overwrite existing .original files
# as we don't want to clobber the original backup files if they run this twice for whatever reason...
# This assumes on a skin update that all files are replaced (i.e. any current .original backup files will be removed)
def patch(config):

    # Backup original files
    try:
        if not xbmcvfs.exists(config.backup_myweather_xml):
            log("Backing up current MyWeather.xml to MyWeather.xml.original")
            success = xbmcvfs.copy(config.current_myweather_xml, config.backup_myweather_xml)
            if success:
                log("...done")
            else:
                log("...failed!  Is the skin folder writeable?")
                notify('Exiting - is skin folder writeable? Error when backing up current MyWeather.xml - ')
                sys.exit(1)

        if xbmcvfs.exists(config.current_videofullscreen_xml) and not xbmcvfs.exists(config.backup_videofullscreen_xml):
            log("Backing up current VideoFullScreen.xml to VideoFullScreen.xml.original")
            success = xbmcvfs.copy(config.current_videofullscreen_xml, config.backup_videofullscreen_xml)
            if success:
                log("...done")
            else:
                log("...failed!  Is the skin folder writeable?")
                notify('Exiting - is skin folder writeable? Error when backing up current VideoFullScreen.xml ')
                sys.exit(1)

    except Exception as inst:
        log(inst)
        notify('Exception when backing up current skin files - check logs!')
        sys.exit(1)

    # Prepare to copy new files - grab both the skin independent and skin specific files...
    list_of_files_to_copy = glob.glob(config.skin_independent_xml_source_folder + "/*.xml")
    list_of_files_to_copy.extend(glob.glob(config.skin_specific_xml_source_folder + "/*.xml"))

    log("The list of files to copy is")
    log(list_of_files_to_copy)

    for file in list_of_files_to_copy:
        log(f"Patching & copying {file} to {config.xml_destination_folder}")

        try:

            # Skip the file that reminds me to be careful with the addon skin files...
            if "00_" in file:
                continue

            with xbmcvfs.File(file, 'r') as source_file:
                new_data = source_file.read()

            # Patch in the user's choices
            new_data = new_data.replace('_colour_text_default_', ADDON.getSetting('colour_text_default'))
            new_data = new_data.replace('_colour_text_dim_', ADDON.getSetting('colour_text_dim'))
            new_data = new_data.replace('_colour_text_dimmer_', ADDON.getSetting('colour_text_dimmer'))
            new_data = new_data.replace('_colour_text_high_temp_', ADDON.getSetting('colour_text_high_temp'))
            new_data = new_data.replace('_colour_text_low_temp_', ADDON.getSetting('colour_text_low_temp'))
            new_data = new_data.replace('_background_visible_', 'yes' if ADDON.getSettingBool('background_visible_bool') else 'no')
            new_data = new_data.replace('_background_opacity_', ADDON.getSetting('background_opacity'))

            file_to_write = config.xml_destination_folder + "/" + ntpath.basename(file)
            log(f"Writing patched file to: {file_to_write}")
            with xbmcvfs.File(file_to_write, 'w') as destination_file:
                result = destination_file.write(new_data)
                log(f"...done...result: {result}")

        except Exception as inst:
            log("...failed!  Error writing new skin files.")
            log(inst)
            notify('Exiting - as error when copying OzWeather skin files - is skin folder writeable?')
            sys.exit(1)


# Attempt to restore .original files - we just try and restore both, no matter what the setting is
def restore(config):

    try:
        log("Restoring .original skin files")
        if xbmcvfs.exists(config.backup_myweather_xml):
            log("Copying back MyWeather.xml from MyWeather.xml.original file")
            success = xbmcvfs.copy(config.backup_myweather_xml, config.current_myweather_xml)
            if success:
                log("...done")
            else:
                log("...failed!  Is file present? Is the skin folder writeable?")
                notify('Exiting - failed to restore MyWeather.xml.original - is file present?')
                sys.exit(1)
        else:
            log("Could not find MyWeather.xml.original file, did not restore")

        if xbmcvfs.exists(config.backup_videofullscreen_xml):
            log("Copying back VideoFullScreen.xml from VideoFullScreen.xml.original file")
            success = xbmcvfs.copy(config.backup_videofullscreen_xml, config.current_videofullscreen_xml)
            if success:
                log("...done")
            else:
                log("...failed!  Is file present? Is the skin folder writeable?")
                notify('Exiting - failed to restore VideoFullScreen.xml.original - is file present?')
                sys.exit(1)
        else:
            log('Could not find VideoFullScreen.xml.original file, did not restore')

    except Exception as inst:
        log(inst)
        notify('Exception when restoring skin files - check logs!')
        sys.exit(1)


# This is 'main'...
def run():

    global dialog

    footprints()
    config = Config()
    dialog = xbmcgui.Dialog()

    # Basic sanity checking - are they running the right skin?
    skin_supported = False
    for skin in Config.supported_skins:
        if skin in config.current_skin:
            skin_supported = True

    if not skin_supported:
        log("ERROR - current skin is not a supported skin!")
        notify('ERROR - current skin is not a supported skin!')
        sys.exit(1)

    if get_setting_as_bool("show_first_run_info"):

        # Only show this again later if they explicitly turn it back on in settings...
        ADDON.setSetting("show_first_run_info", "false")

        # Display initial information
        dialog.textviewer('OzWeather Skin Patcher',
                          """
    [B]IMPORTANT FIRST RUN INFO (Won't be shown again)[/B]                                                 
    [I](Closing this window will proceed to the actual patching stage)[/I]
    
    This utility will patch skin files for OzWeather radar support.
    Only patches the currently selected skin, and only if that skin is a variant of:
     
    Aeon (Nox, Silvo etc), Amber, Confluence, Estuary, Estouchy, OSMC, Xonfluence
        
    Backups of the original files are saved as '.original' files in the skin folder
    & can be also be easily restored by re-running this utility, if needed.    
    """)

    # Now confirm if they actually want to proceed
    mode = dialog.select('OzWeather Skin Patcher', ['Patch', 'Restore', 'Cancel'])
    log(f'Mode is {mode}')

    if mode == 0:
        log('Patching')
        patch(config)
    elif mode == 1:
        log('Restoring')
        restore(config)
    else:
        log("User cancelled operation.")

    # If we got here, all _should_ be well - reload the skin to get the new pretty
    if mode == 0 or mode == 1:
        log("Reloading skin to pick up changes")
        xbmc.executebuiltin('ReloadSkin()')
        notify('Successful patch - skin reloaded.', xbmcgui.NOTIFICATION_INFO)

    # and, we're done...
    footprints(False)
