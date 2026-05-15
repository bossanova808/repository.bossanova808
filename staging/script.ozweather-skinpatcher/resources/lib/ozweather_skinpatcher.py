import os
import sys
import glob
import ntpath
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from bossanova808.logger import Logger
from bossanova808.notify import Notify
from bossanova808.constants import ADDON, PROFILE
from bossanova808.utilities import get_setting, get_setting_as_bool, get_addon_version, version_tuple
# noinspection PyPackages
from .store import Store


def _is_recorded_version_current(record_filename: str, current_version: str, label: str) -> bool:
    """Return True iff PROFILE/<record_filename> exists and matches current_version."""
    try:
        with open(os.path.join(PROFILE, record_filename), 'r') as f:
            recorded = f.read()
        if recorded == current_version:
            Logger.info(f'{label} version test OK - current: [{current_version}] == recorded: [{recorded}]')
            return True
        Logger.warning(f'{label} version test NOT OK - current: [{current_version}] != recorded: [{recorded}] - will patch')
        return False
    except (RuntimeError, FileNotFoundError, IOError, OSError, PermissionError, ValueError) as e:
        Logger.warning(f"Unable to determine if {label} is already patched - assuming not, therefore will proceed to patch")
        Logger.warning(e)
        return False


def _check_skin_is_supported() -> bool:
    """Return True iff the current skin is a supported skin."""
    skin_supported = False
    for skin in Store.supported_skins:
        if skin in Store.current_skin_path:
            skin_supported = True

    if not skin_supported:
        Logger.error("ERROR - current skin is not a supported skin!")
        Notify.error('ERROR - current skin is not a supported skin!')

    return skin_supported


# This is 'main', as run by the addon service (i.e. Kodi starts this automatically)
def delayed_autopatch():
    ##########################################################################################################################
    # N.B. CODE IMMEDIATELY BELOW IS RUN _BEFORE_ THE DELAY - so generally don't add anything here...

    Logger.start("(delayed autopatch thread)")
    # Get this here as the skin patcher itself may be updated, and we want to know what version we're running now...
    skinpatcher_version_now = ADDON.getAddonInfo('version')

    ##########################################################################################################################
    # THE DELAY

    # Delay for (default) 40 seconds (to allow for Kodi addon updates to occur)
    # (Note if they haven't finished after the time limit, patching will still happen on the next startup...)
    delay_setting = get_setting('delay_seconds')
    try:
        delay_seconds = int(delay_setting)
    except (TypeError, ValueError):
        delay_seconds = 40
    Logger.info(f"Will automatically patch skin for OzWeather support after a delay of {delay_seconds} seconds from now (to allow Kodi time to update addons)")
    xbmc.sleep(delay_seconds * 1000)

    ##########################################################################################################################
    # BELOW HERE IS EXECUTED _AFTER_ THE DELAY

    # Maybe they have changed skins since we started?  Doublecheck...
    Store.update_from_kodi()
    skin_supported = _check_skin_is_supported()
    if not skin_supported:
        Logger.error("ERROR - currently in use skin is not a supported skin, thus exiting here.")
        return

    # For auto-patching, patch if any of the recorded versions are missing/stale
    need_to_patch = False

    # Patch if the current skin version differs from what was last patched
    if Store.skin_version_now and not _is_recorded_version_current(f"{Store.current_skin}.version", Store.skin_version_now, "Skin"):
        need_to_patch = True

    # Also patch if OzWeather has changed since we last patched
    if not _is_recorded_version_current("ozweather.version", Store.ozweather_version_now, "OzWeather"):
        need_to_patch = True

    # Also re-patch if the Skin Patcher itself has been updated, as bundled skin files may have changed
    if not _is_recorded_version_current("skinpatcher.version", skinpatcher_version_now, "Skin Patcher"):
        need_to_patch = True

    # My friends & family skin includes the patches already (this placed here, so we know what _would_ have happened)
    if 'bossanova808' in Store.current_skin:
        Logger.warning("Bossanova808 skin detected, therefore not actually patching")
        need_to_patch = False

    # OK, so do we actually need to patch?
    if need_to_patch:
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
                f.write(Store.skin_version_now)
            with open(os.path.join(PROFILE, "ozweather.version"), 'w', encoding='utf-8') as f:
                f.write(Store.ozweather_version_now)
            with open(os.path.join(PROFILE, "skinpatcher.version"), 'w', encoding='utf-8') as f:
                f.write(skinpatcher_version_now)
        except (IOError, OSError) as e:
            Notify.error("Failed to write patch records - check logs")
            Logger.error("Failed to write patch records")
            Logger.error(e)

        Logger.info("Reloading skin to pick up changes")
        xbmc.executebuiltin('ReloadSkin()')
        Notify.info('Successful OzWeather skin patch (skin reloaded).')

    Logger.stop("(delayed autopatch thread)")


def autopatch():
    """
    If the user has enabled this, automatically patch the current skin, if needed.
    Returns the autopatch thread so the caller can join() it, keeping the service
    process alive until the work is actually complete.

    :return: threading.Thread if autopatch is running, None otherwise
    """

    # Short circuit if Auto Patching is disabled
    if not get_setting_as_bool('autopatch'):
        Logger.warning("Auto-patching is disabled in settings - doing nothing.")
        return None

    # Otherwise, do the actual autopatch work only after a delay (to allow Kodi to first do its normal update addons work)
    # (Use threading so as not to block Kodi from anything else)
    import threading
    thread = threading.Thread(target=delayed_autopatch)
    thread.start()
    return thread


def patch():
    """
    Back up existing skin files and install the new ones
    Backup occurs only once per skin version, it will not overwrite existing .original files
    (As we don't want to clobber the original backup files if they run this twice for whatever reason)
    N.B. remember - on any skin update, all files are replaced (i.e. any current .original backup files will be removed)
    """
    # Back up original files
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

        # @TODO this is not ideal - it backs up this file even in no changes are made to it (which is most scenarios)
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
        Logger.info("OzWeather is an older version, <= 2.1.5 - use skin file with old radar paths")
        list_of_files_to_copy.extend(glob.glob(os.path.join(Store.skin_independent_xml_source_folder, "Ozw_215", "*.xml")))
    else:
        # Logic for version 2.1.6 and above
        Logger.info("OzWeather is >= 2.1.6 - use new skin files for radar paths")
        list_of_files_to_copy.extend(
            glob.glob(os.path.join(Store.skin_independent_xml_source_folder, "Ozw_216", "*.xml")))

    list_of_files_to_copy.sort()
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

            file_to_write = os.path.join(Store.xml_destination_folder, ntpath.basename(file))
            Logger.info(f"Writing patched file to: {file_to_write}")
            with xbmcvfs.File(file_to_write, 'w') as destination_file:
                result = destination_file.write(new_data)
                Logger.info(f"...done...result: {result}")

        except Exception as inst:
            Logger.error("...failed!  Error writing new skin files.")
            Logger.error(inst)
            Notify.error('Exiting - as error when copying OzWeather skin files - is skin folder writeable?')
            sys.exit(1)

    # Make sure Extended Features is turned on or none of the new magic will actualyl show up...
    addon = xbmcaddon.Addon(id='weather.ozweather')
    addon.setSetting('ExtendedFeaturesToggle', 'true')
    Logger.info("OzWeather ExtendedFeaturesToggle set to true")


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


# This is 'main', if the user runs the addon directly (manually)
# (i.e. is not not by the automatic patching service)
def run():
    Logger.start()
    Store()
    skin_supported = _check_skin_is_supported()

    if not skin_supported:
        Logger.error("ERROR - current skin is not a supported skin, so exiting")
        sys.exit(1)

    dialog = xbmcgui.Dialog()

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

    Aeon (Nox, Silvo etc), Amber, Confluence, Estuary, Plextuary, Estouchy, OSMC, Xonfluence

    Backups of the original files are saved as '.original' files in the skin folder
    & can be also be easily restored by re-running this utility, if needed.    
    """)

    # Now confirm if they actually want to proceed
    mode = dialog.select('OzWeather Skin Patcher', ['Patch', 'Restore', 'Cancel'])
    mode_text = None
    Logger.info(f'Mode is {mode}')

    if mode == 0:
        Logger.info('Patching')
        mode_text = 'patch'
        patch()
    elif mode == 1:
        Logger.info('Restoring')
        mode_text = 'restore'
        restore()
    else:
        Logger.info("User cancelled operation.")

    # If we got here, all _should_ be well - reload the skin to get the new pretty
    if mode == 0 or mode == 1:
        Logger.info("Reloading skin to pick up changes")
        xbmc.executebuiltin('ReloadSkin()')
        Notify.info(f'Successful OzWeather skin {mode_text} - skin reloaded.')

    # and, we're done...
    Logger.stop()