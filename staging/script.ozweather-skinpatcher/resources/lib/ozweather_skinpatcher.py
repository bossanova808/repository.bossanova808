import os
import sys
import glob
import ntpath
import xbmc
import xbmcgui
import xbmcvfs

from bossanova808.logger import Logger
from bossanova808.notify import Notify
from bossanova808.constants import ADDON, PROFILE
from bossanova808.utilities import get_setting, get_setting_as_bool, get_addon_version, version_tuple
# noinspection PyPackages
from .store import Store


def delayed_autopatch():

    Logger.start("(delayed autopatch thread)")
    # My friends & family skin includes the patches already
    if 'bossanova808' in Store.current_skin:
        Logger.debug("Bossanova808 skin detected, not auto-patching")
        return

    # Delay for 40 seconds to allow addon updates
    delay_setting = get_setting('delay_seconds')
    try:
        delay_seconds = int(delay_setting)
    except (TypeError, ValueError):
        delay_seconds = 30
    Logger.info(f"Will automatically patch skin for OzWeather support after a delay of {delay_seconds} seconds from now (to allow Kodi time to update addons)")
    xbmc.sleep(delay_seconds * 1000)

    # For auto-patching, retrieve an existing patch record, if there is one, for the current skin (which contains the skin version that was patched)
    this_skin_version_already_patched = False
    skin_version_now = None
    try:
        skin_version_now = get_addon_version(Store.current_skin)
        if skin_version_now:
            # Read the previously patched skin version from the addon settings directory
            # File is named after the skin (e.g., "skin.amber") and contains just the version, as a string
            with open(os.path.join(PROFILE, f"{Store.current_skin}.version"), 'r') as f:
                skin_version_recorded = f.read()
            if skin_version_recorded == skin_version_now:
                Logger.info(f'This skin version has already been patched - now: [{skin_version_now}] == recorded: [{skin_version_recorded}] - doing nothing.')
                this_skin_version_already_patched = True
            else:
                Logger.info(f'This skin version has NOT been patched: - now: [{skin_version_now}] != recorded: [{skin_version_recorded}]')
                this_skin_version_already_patched = False

    except (RuntimeError, FileNotFoundError, IOError, OSError, PermissionError, ValueError) as e:
        Logger.error("Unable to determine if skin is already patched - assuming it _hasn't_ been patched")
        Logger.error(e)

    if skin_version_now and not this_skin_version_already_patched:

        try:
            patch()
        except SystemExit as e:
            Logger.error(f"Patching failed with exit code {e.code}")
            Notify.error("Automatic skin patching failed - check logs")
            return
        except Exception as e:
            Logger.error("Unexpected error during patching")
            Logger.error(e)
            Notify.error("Automatic skin patching failed - check logs")
            return

        try:
            os.makedirs(PROFILE, exist_ok=True)
            with open(os.path.join(PROFILE, f"{Store.current_skin}.version"), 'w', encoding='utf-8') as f:
                f.write(skin_version_now)
        except (IOError, OSError) as e:
            Logger.error("Failed to write patch record")
            Logger.error(e)

        Logger.info("Reloading skin to pick up changes")
        xbmc.executebuiltin('ReloadSkin()')
        Notify.info('Successful OzWeather skin patch (skin reloaded).')

    Logger.stop("(delayed autopatch thread)")

def autopatch():
    """
    If the user has enabled this, automatically patch the current skin, if needed

    :return:
    """
    Logger.start("(service)")

    # Short circuit if Auto Patching is disabled
    if not get_setting_as_bool('autopatch'):
        Logger.warning("Auto-patching is disabled in settings - doing nothing.")
        Logger.stop("(service)")
        return

    # Otherwise, do the actual autopatch work only after a delay (to allow Kodi to first do it's normal update addons work)
    # (Use threading so as not to block Kodi from anything else)
    import threading
    threading.Thread(target=delayed_autopatch, daemon=True).start()
    Logger.stop("(service)")


# Backup existing skin files, and install the new ones.
# Backup occurs only once per skin version, it will not overwrite existing .original files
# as we don't want to clobber the original backup files if they run this twice for whatever reason...
# This assumes on a skin update that all files are replaced (i.e. any current .original backup files will be removed)
def patch():
    # Backup original files
    try:
        if not xbmcvfs.exists(Store.backup_myweather_xml):
            Logger.info("Backing up current MyWeather.xml to MyWeather.xml.original")
            success = xbmcvfs.copy(Store.current_myweather_xml, Store.backup_myweather_xml)
            if success:
                Logger.info("...done")
            else:
                Logger.error(f"...failed!  Is the skin folder {Store.xml_destination_folder} writeable?")
                Notify.error('Exiting - is skin folder writeable? Error when backing up current MyWeather.xml')
                sys.exit(1)

        if xbmcvfs.exists(Store.current_videofullscreen_xml) and not xbmcvfs.exists(Store.backup_videofullscreen_xml):
            Logger.info("Backing up current VideoFullScreen.xml to VideoFullScreen.xml.original")
            success = xbmcvfs.copy(Store.current_videofullscreen_xml, Store.backup_videofullscreen_xml)
            if success:
                Logger.info("...done")
            else:
                Logger.error(f"...failed!  Is the skin folder {Store.xml_destination_folder} writeable?")
                Notify.error('Exiting - is skin folder writeable? Error when backing up current VideoFullScreen.xml')
                sys.exit(1)

    except Exception as inst:
        Logger.error(inst)
        Notify.error('Exception when backing up current skin files - check logs!')
        sys.exit(1)

    # Prepare to copy new files - grab both the skin independent and skin specific files...
    list_of_files_to_copy = glob.glob(os.path.join(Store.skin_independent_xml_source_folder, "*.xml"))
    list_of_files_to_copy.extend(glob.glob(os.path.join(Store.skin_specific_xml_source_folder, "*.xml")))

    # Need to use the correct paths for radar, they changed with OzWeather 2.1.6
    version = get_addon_version("weather.ozweather")
    if version_tuple(version) <= version_tuple('2.1.5'):
        # Logic for version 2.1.5 and below
        Logger.warning("OzWeather is an older version, <= 2.1.5 - use skin file with old radar paths")
        list_of_files_to_copy.extend(glob.glob(os.path.join(Store.skin_independent_xml_source_folder, "Ozw_215", "*.xml")))
    else:
        # Logic for version 2.1.6 and above
        Logger.warning("OzWeather is >= 2.1.6 - use new skin file for radar paths")
        list_of_files_to_copy.extend(glob.glob(os.path.join(Store.skin_independent_xml_source_folder, "Ozw_216", "*.xml")))

    Logger.info("The list of files to copy is")
    Logger.info(list_of_files_to_copy)

    for file in list_of_files_to_copy:
        Logger.info(f"Patching & copying {file} to {Store.xml_destination_folder}")

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

            file_to_write = Store.xml_destination_folder + "/" + ntpath.basename(file)
            Logger.info(f"Writing patched file to: {file_to_write}")
            with xbmcvfs.File(file_to_write, 'w') as destination_file:
                result = destination_file.write(new_data)
                Logger.info(f"...done...result: {result}")

        except Exception as inst:
            Logger.error("...failed!  Error writing new skin files.")
            Logger.error(inst)
            Notify.error('Exiting - as error when copying OzWeather skin files - is skin folder writeable?')
            sys.exit(1)


# Attempt to restore .original files - we just try and restore both, no matter what the setting is
def restore():
    try:
        Logger.info("Restoring .original skin files")
        if xbmcvfs.exists(Store.backup_myweather_xml):
            Logger.info("Copying back MyWeather.xml from MyWeather.xml.original file")
            success = xbmcvfs.copy(Store.backup_myweather_xml, Store.current_myweather_xml)
            if success:
                Logger.info("...done")
            else:
                Logger.error("...failed!  Is file present? Is the skin folder writeable?")
                Notify.error('Exiting - failed to restore MyWeather.xml.original - is file present?')
                sys.exit(1)
        else:
            Logger.info("Could not find MyWeather.xml.original file, did not restore")

        if xbmcvfs.exists(Store.backup_videofullscreen_xml):
            Logger.info("Copying back VideoFullScreen.xml from VideoFullScreen.xml.original file")
            success = xbmcvfs.copy(Store.backup_videofullscreen_xml, Store.current_videofullscreen_xml)
            if success:
                Logger.info("...done")
            else:
                Logger.error("...failed!  Is file present? Is the skin folder writeable?")
                Notify.error('Exiting - failed to restore VideoFullScreen.xml.original - is file present?')
                sys.exit(1)
        else:
            Logger.error('Could not find VideoFullScreen.xml.original file, did not restore')

    except Exception as inst:
        Logger.error(inst)
        Notify.error('Exception when restoring skin files - check logs!')
        sys.exit(1)


# This is 'main'...
def run():

    Logger.start()
    Store()

    dialog = xbmcgui.Dialog()

    # Basic sanity checking - are they running the right skin?
    skin_supported = False
    for skin in Store.supported_skins:
        if skin in Store.current_skin_path:
            skin_supported = True

    if not skin_supported:
        Logger.error("ERROR - current skin is not a supported skin!")
        Notify.error('ERROR - current skin is not a supported skin!')
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
    Logger.info(f'Mode is {mode}')

    if mode == 0:
        Logger.info('Patching')
        patch()
    elif mode == 1:
        Logger.info('Restoring')
        restore()
    else:
        Logger.info("User cancelled operation.")

    # If we got here, all _should_ be well - reload the skin to get the new pretty
    if mode == 0 or mode == 1:
        Logger.info("Reloading skin to pick up changes")
        xbmc.executebuiltin('ReloadSkin()')
        Notify.info('Successful OzWeather skin patch (skin reloaded).')

    # and, we're done...
    Logger.stop()
