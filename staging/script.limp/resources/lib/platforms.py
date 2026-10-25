import xbmc

from bossanova808.constants import OS_PLATFORM
from bossanova808.logger import Logger
from bossanova808.utilities import get_kodi_setting

# The Kodi setting that selects hardware vs software video decoding, on each platform we support
AMLOGIC_HARDWARE_SETTING = "videoplayer.useamcodec"
WINDOWS_HARDWARE_SETTING = "videoplayer.usedxva2"
APPLE_HARDWARE_SETTING = "videoplayer.usevtb"
WEBOS_HARDWARE_SETTING = "videoplayer.usestarfishdecoder"


class Platform:
    """
    Which platform we're running on, and so which Kodi setting switches hardware decoding on/off.
    TODO: Android (videoplayer.usemediacodec and usemediacodecsurface, both of which would need to
    be switched off) and Linux (videoplayer.usevaapi, usevdpau, useprimedecoder) each have several
    settings - add them if/when needed.
    """

    # "amlogic", "windows", "apple", "webos", or None if this platform isn't supported
    name = None
    hardware_setting = None

    @staticmethod
    def detect():
        """
        Work out the platform. Windows is the OS platform string, and Apple (macOS, iOS, tvOS) is
        Kodi's own platform check. On Linux, Amlogic and webOS are each the one place their
        setting exists (reading it elsewhere is an error, so only try there).
        """
        os_platform = OS_PLATFORM.lower()
        Platform.name = Platform.hardware_setting = None
        if os_platform.startswith('windows'):
            Platform.name, Platform.hardware_setting = 'windows', WINDOWS_HARDWARE_SETTING
        elif xbmc.getCondVisibility('System.Platform.Darwin'):
            Platform.name, Platform.hardware_setting = 'apple', APPLE_HARDWARE_SETTING
        elif os_platform.startswith('linux'):
            if get_kodi_setting(AMLOGIC_HARDWARE_SETTING) is not None:
                Platform.name, Platform.hardware_setting = 'amlogic', AMLOGIC_HARDWARE_SETTING
            elif get_kodi_setting(WEBOS_HARDWARE_SETTING) is not None:
                Platform.name, Platform.hardware_setting = 'webos', WEBOS_HARDWARE_SETTING

        if Platform.name:
            Logger.info(f'Platform: {Platform.name} (hardware decoding setting: {Platform.hardware_setting})')
        else:
            Logger.warning(f'Unsupported platform ({OS_PLATFORM}) - Limp supports Amlogic, Windows, Apple and webOS only for now.')

    @staticmethod
    def is_amlogic():
        return Platform.name == 'amlogic'
