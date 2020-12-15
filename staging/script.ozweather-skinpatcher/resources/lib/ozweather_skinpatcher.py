# -*- coding: utf-8 -*-

from resources.lib.common import *
import os
import sys
import shutil
import xbmc
import xbmcvfs


def run():

    footprints()
    dialog = xbmcgui.Dialog()
    patch_seekbar = get_setting_as_bool('patchseekbar')

    current_skin = xbmcvfs.translatePath('special://skin')
    log(f'special://skin us [{current_skin}]')
    log(f'CWD is {CWD}')
    log(f'Patch SeekBar is {patch_seekbar}')

    if 'estuary' not in current_skin and 'confluence' not in current_skin:
        log("ERROR - skin is not confluence or estuary")
        dialog.notification('OzWeather Skin Patcher', 'Only Confluence and Estuary are supported', xbmcgui.NOTIFICATION_ERROR, 5000)

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
    new_myweather_xml = os.path.join(xml_source_folder, 'MyWeather.xml')
    new_seekbar_xml = os.path.join(xml_source_folder, 'DialogSeekBar.xml')
    current_myweather_xml = os.path.join(xml_destination_folder, 'MyWeather.xml')
    current_seekbar_xml = os.path.join(xml_destination_folder, 'DialogSeekBar.xml')
    backup_myweather_xml = os.path.join(xml_destination_folder, 'MyWeather.xml.original')
    backup_seekbar_xml = os.path.join(xml_destination_folder, 'DialogSeekBar.xml.original')

    log(f'Skin XML folder is {xml_destination_folder}')
    log(f'Current MyWeather.xml is {current_myweather_xml}')
    log(f'Current DialogSeekBar.xml is {current_seekbar_xml}')
    log(f'New MyWeather.xml is {new_myweather_xml}')
    log(f'New DialogSeekBar.xml is {new_seekbar_xml}')
    log(f'Backup MyWeather.xml will be {backup_myweather_xml}')
    log(f'Backup DialogSeekBar.xml will be {backup_seekbar_xml}')

    # First, backup the existing files...just in case...we only want to do this once for each version of the skin
    # Otherwise we'll be over-writing our backup files if they accidentally run this when not needed
    # (assumes when a skin is updated by Kodi, all files are replaced...?)
    try:
        if not xbmcvfs.exists(backup_myweather_xml):
            log("Backing up current MyWeather.xml to MyWeather.xml.original")
            success = xbmcvfs.copy(current_myweather_xml, backup_myweather_xml)
            log(f'Success: {success}')
        if patch_seekbar and not xbmcvfs.exists(backup_seekbar_xml):
            log("Backing up current DialogSeekBar.xml to DialogSeekBar.xml.original")
            success = xbmcvfs.copy(current_seekbar_xml, backup_seekbar_xml)
            log(f'Success: {success}')
    except:
        dialog.notification('OzWeather Skin Patcher',
                            'Error backing up current skin files - bailing out here!',
                            xbmcgui.NOTIFICATION_ERROR,
                            5000)
        sys.exit(1)

    # Ok, backups done, copy our skin files over...
    try:
        log(f'Copying OzWeather MyWeather.xml to {xml_destination_folder}')
        success = xbmcvfs.copy(new_myweather_xml, current_myweather_xml)
        log(f'Success: {success}')
        if patch_seekbar:
            log(f'Copying OzWeather DialogSeekBar.xml to {xml_destination_folder}')
            success = xbmcvfs.copy(new_seekbar_xml, current_seekbar_xml)
            log(f'Success: {success}')
        else:
            log('Not copying DialogSeekBar.xml, as per addon settings')
    except:
        dialog.notification('OzWeather Skin Patcher',
                            'Error copying OzWeather skin files - bailing out here!',
                            xbmcgui.NOTIFICATION_ERROR,
                            5000)
        sys.exit(1)

    # If we got here, all should be well
    dialog.notification('OzWeather Skin Patcher', 'Reloading skin after successful patch',
                        xbmcgui.NOTIFICATION_INFO, 5000)

    # Reload the skin so we can enjoy the new pretty
    xbmc.executebuiltin('ReloadSkin()')

    footprints(False)




