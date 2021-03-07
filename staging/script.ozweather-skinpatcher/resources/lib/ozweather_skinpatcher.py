# -*- coding: utf-8 -*-

from resources.lib.common import *
import os
import sys
import xbmc
import xbmcvfs

global dialog


# Just a place to store all our config stuff so we don't go crazy with globals
class Config:

    global dialog

    patch_videofullscreen = get_setting_as_bool('patch_videofullscreen')
    current_skin = xbmcvfs.translatePath('special://skin')

    log(f'special://skin Is [{current_skin}]')
    log(f'CWD is {CWD}')
    log(f'Patch VideoFullScreen is {patch_videofullscreen}')

    skin = ''
    skin_xml_folder = ''
    if 'estuary' in current_skin:
        log('Estuary in skin folder name...proceeding...')
        skin = 'estuary'
        skin_xml_folder = 'xml'
    if 'estouchy' in current_skin:
        log('Estouchy in skin folder name...proceeding...')
        skin = 'estouchy'
        skin_xml_folder = 'xml'
    if 'confluence' in current_skin:
        log('Confluence in skin folder name...proceeding..')
        skin = 'confluence'
        skin_xml_folder = '720p'
    if not skin or not skin_xml_folder:
        log("Error - skin/skin_xml_folder variable is empty - this should never happen!")
        sys.exit(1)

    xml_source_folder = os.path.join(CWD, 'resources/skin-files/', skin)
    xml_destination_folder = os.path.join(current_skin, skin_xml_folder)
    current_myweather_xml = os.path.join(xml_destination_folder, 'MyWeather.xml')
    current_videofullscreen_xml = os.path.join(xml_destination_folder, 'VideoFullScreen.xml')
    backup_myweather_xml = os.path.join(xml_destination_folder, 'MyWeather.xml.original')
    backup_videofullscreen_xml = os.path.join(xml_destination_folder, 'VideoFullScreen.xml.original')
    new_myweather_xml = os.path.join(xml_source_folder, 'MyWeather.xml')
    new_videofullscreen_xml = os.path.join(xml_source_folder, 'VideoFullScreen.xml')

    log(f'Skin XML folder is {xml_destination_folder}')
    log(f'Current MyWeather.xml is {current_myweather_xml}')
    log(f'Current VideoFullScreen.xml is {current_videofullscreen_xml}')
    log(f'New MyWeather.xml is {new_myweather_xml}')
    log(f'New VideoFullScreen.xml is {new_videofullscreen_xml}')
    log(f'Backup MyWeather.xml will be {backup_myweather_xml}')
    log(f'Backup VideoFullScreen.xml will be {backup_videofullscreen_xml}')


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
                notify('Exiting - as error when backing up current MyWeather.xml - is skin folder writeable?')
                sys.exit(1)

        if config.patch_videofullscreen and not xbmcvfs.exists(config.backup_videofullscreen_xml):
            log("Backing up current VideoFullScreen.xml to VideoFullScreen.xml.original")
            success = xbmcvfs.copy(config.current_videofullscreen_xml, config.backup_videofullscreen_xml)
            if success:
                log("...done")
            else:
                log("...failed!  Is the skin folder writeable?")
                notify('Exiting - as error when backing up current VideoFullScreen.xml - is skin folder writeable?')
                sys.exit(1)

    except Exception as inst:
        log(inst)
        notify('Exception when backing up current skin files - check logs!')
        sys.exit(1)

    # Copy new files
    try:
        log(f'Copying OzWeather MyWeather.xml to {config.xml_destination_folder}')
        success = xbmcvfs.copy(config.new_myweather_xml, config.current_myweather_xml)
        if success:
            log("...done")
        else:
            log("...failed!  Is the skin folder writeable?")
            notify('Exiting - as error when copying OzWeather MyWeather.xml - is skin folder writeable?')
            sys.exit(1)

        if config.patch_videofullscreen and 'confluence' in config.current_skin:
            log(f'Copying OzWeather VideoFullScreen.xml to {config.xml_destination_folder}')
            success = xbmcvfs.copy(config.new_videofullscreen_xml, config.current_videofullscreen_xml)
            if success:
                log("...done")
            else:
                log("...failed!  Is the skin folder writeable?")
                notify('Exiting - as error when copying OzWeather VideoFullScreen.xml - is skin folder writeable?')
                sys.exit(1)
        else:
            log('Not copying VideoFullScreen.xml, as per addon settings')

    except Exception as inst:
        log(inst)
        notify('Exception when copying OzWeather skin files - check logs!')
        sys.exit(1)


# Attempt to restore .original files - we jsut try and restore both, no matter what the setting is
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
    if 'estuary' not in config.current_skin \
            and 'estouchy' not in config.current_skin \
            and 'confluence' not in config.current_skin:
        log("ERROR - current skin is not a supported skin!")
        notify('Only Estuary, Estouchy and Confluence are supported, sorry!')
        sys.exit(1)

    # Display initial information
    dialog.textviewer('OzWeather Skin Patcher',
                      """ 
<Close this window to proceed to the actual patching stage> 

This utility will patch skin files for OzWeather radar support.\n
Only patches the currently selected skin, and only if that skin is Estuary, Estouchy or Confluence.
(Or mods of those skins that still include 'estuary','estouchy', or 'confluence' in the add-in id).

Backups of the original files are saved as .original files in the skin folder
(& can be also be restored by this utility).

Confluence only - by default patches only MyWeather.xml, but you can also patch VideoFullScreen.xml
to display radar and basic weather info when media info is displayed during playback.
(enable this in the add-on settings if you wish)
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

    # and, we're done..
    footprints(False)
