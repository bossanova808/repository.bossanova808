# -*- coding: utf-8 -*-

from resources.lib.common import *
import os
import sys
import xbmc
import xbmcvfs

global dialog


class Config:

    global dialog

    patch_seekbar = get_setting_as_bool('patchseekbar')
    current_skin = xbmcvfs.translatePath('special://skin')

    log(f'special://skin Is [{current_skin}]')
    log(f'CWD is {CWD}')
    log(f'Patch SeekBar is {patch_seekbar}')

    skin = ''
    skin_xml_folder = ''
    if 'estuary' in current_skin:
        log('Estuary in skin folder name...proceeding...')
        skin = 'estuary'
        skin_xml_folder = 'xml'
    if 'confluence' in current_skin:
        log('Confluence in skin folder name...proceeding..')
        skin = 'confluence'
        skin_xml_folder = '720p'
    if not skin or not skin_xml_folder:
        log("Error - skin/skin_xml_folder variable is empty - this should never happen!")

    xml_source_folder = os.path.join(CWD, 'resources/skin-files/', skin)
    xml_destination_folder = os.path.join(current_skin, skin_xml_folder)
    current_myweather_xml = os.path.join(xml_destination_folder, 'MyWeather.xml')
    current_seekbar_xml = os.path.join(xml_destination_folder, 'DialogSeekBar.xml')
    backup_myweather_xml = os.path.join(xml_destination_folder, 'MyWeather.xml.original')
    backup_seekbar_xml = os.path.join(xml_destination_folder, 'DialogSeekBar.xml.original')
    new_myweather_xml = os.path.join(xml_source_folder, 'MyWeather.xml')
    new_seekbar_xml = os.path.join(xml_source_folder, 'DialogSeekBar.xml')

    log(f'Skin XML folder is {xml_destination_folder}')
    log(f'Current MyWeather.xml is {current_myweather_xml}')
    log(f'Current DialogSeekBar.xml is {current_seekbar_xml}')
    log(f'New MyWeather.xml is {new_myweather_xml}')
    log(f'New DialogSeekBar.xml is {new_seekbar_xml}')
    log(f'Backup MyWeather.xml will be {backup_myweather_xml}')
    log(f'Backup DialogSeekBar.xml will be {backup_seekbar_xml}')


# Backup existing skin files, and install the new ones.
# Backup occurs only once per sklin version, it will not overwrite existing .original files.
# This assume on a skin update that all files are replaced (?)
def patch(config):

    # Backup original files
    try:
        if not xbmcvfs.exists(config.backup_myweather_xml):
            log("Backing up current MyWeather.xml to MyWeather.xml.original")
            success = xbmcvfs.copy(config.current_myweather_xml, config.backup_myweather_xml)
            log("...done") if success else log("...failed!")
        if config.patch_seekbar and not xbmcvfs.exists(config.backup_seekbar_xml):
            log("Backing up current DialogSeekBar.xml to DialogSeekBar.xml.original")
            success = xbmcvfs.copy(config.current_seekbar_xml, config.backup_seekbar_xml)
            log("...done") if success else log("...failed!")
    except:
        dialog.notification('OzWeather Skin Patcher',
                            'Error backing up current skin files - bailing out here!',
                            xbmcgui.NOTIFICATION_ERROR,
                            5000)
        sys.exit(1)

    # Copy new files
    try:
        log(f'Copying OzWeather MyWeather.xml to {config.xml_destination_folder}')
        success = xbmcvfs.copy(config.new_myweather_xml, config.current_myweather_xml)
        log("...done") if success else log("...failed!")
        if config.patch_seekbar:
            log(f'Copying OzWeather DialogSeekBar.xml to {config.xml_destination_folder}')
            success = xbmcvfs.copy(config.new_seekbar_xml, config.current_seekbar_xml)
            log("...done") if success else log("...failed!")
        else:
            log('Not copying DialogSeekBar.xml, as per addon settings')
    except:
        dialog.notification('OzWeather Skin Patcher',
                            'Error copying OzWeather skin files - bailing out here!',
                            xbmcgui.NOTIFICATION_ERROR,
                            5000)
        sys.exit(1)


# Attempt to restore .original files
def restore(config):
    pass


def cancel():
    pass


# This is 'main'...
def run():

    global dialog

    footprints()
    config = Config()
    dialog = xbmcgui.Dialog()

    # Basic sanity checking - are they running the right skin?
    if 'estuary' not in config.current_skin and 'confluence' not in config.current_skin:
        log("ERROR - current skin is not confluence or estuary!")
        dialog.notification('OzWeather Skin Patcher', 'Only Confluence and Estuary are supported',
                            xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit(1)

    # Display initial information
    dialog.textviewer('OzWeather Skin Patcher',
                      """ 
This utility will patch skin files for OzWeather radar support.\n
Only patches the currently selected skin, and only supports Estuary and Confluence.
Backups of the original files are saved as .original files in the skin folder
(& can be restored by thus utility).

By default patches only MyWeather.xml, but you can also have it patch DialogSeekBar.xml
to display radar and basic weather info when media is paused.
(must be enabled in the addon settings))
""")

    # Now confirm if the want to proceed
    result = dialog.select('OzWeather Skin Patcher', ['Patch', 'Restore', 'Cancel'])
    log(f'Result is {result}')

    if result == 1:
        patch(config)
    elif result == 2:
        restore(config)
    else:
        log("User cancelled operation.")

    # If we got here, all should be well - reload the skin to get the new pretty
    if result == 1 or result == 2:
        dialog.notification('OzWeather Skin Patcher', 'Reloading skin after successful modification',
                            xbmcgui.NOTIFICATION_INFO, 5000)
        xbmc.executebuiltin('ReloadSkin()')

    # and, we're done..
    footprints(False)
