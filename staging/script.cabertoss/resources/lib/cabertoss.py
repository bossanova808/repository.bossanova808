# -*- coding: utf-8 -*-
from importlib.metadata import files

from bossanova808.common import *
from resources.lib.store import Store
# from .monitor import KodiEventMonitor
# from .player import KodiPlayer

import os
import sys
import glob
import ntpath
import xbmc
import xbmcvfs


def gather_log_files():
    # Basic log files
    log_files = [['log', Store.kodi_log_file], ['oldlog', Store.kodi_log_file]]
    # Can we find a crashlog?
    # @TODO - add support for CoreElec, Windows (regular & portable), & Android if possible...we're not posting these, so might as well copy them
    crashlog_path = ''
    items = []
    filematch = None
    if xbmc.getCondVisibility('system.platform.osx'):
        crashlog_path = os.path.join(os.path.expanduser('~'), 'Library/Logs/DiagnosticReports/')
        filematch = 'Kodi'
    elif xbmc.getCondVisibility('system.platform.ios'):
        crashlog_path = '/var/mobile/Library/Logs/CrashReporter/'
        filematch = 'Kodi'
    elif xbmc.getCondVisibility('system.platform.linux'):
        crashlog_path = os.path.expanduser('~')  # not 100% accurate (crashlogs can be created in the dir kodi was started from as well)
        filematch = 'kodi_crashlog'
    elif xbmc.getCondVisibility('system.platform.windows'):
        log(LANGUAGE(32023))
    elif xbmc.getCondVisibility('system.platform.android'):
        log(LANGUAGE(32023))
    if crashlog_path and os.path.isdir(crashlog_path):
        lastcrash = None
        dirs, possible_crashlog_files = xbmcvfs.listdir(crashlog_path)
        for item in possible_crashlog_files:
            if filematch in item and os.path.isfile(os.path.join(crashlog_path, item)):
                items.append(os.path.join(crashlog_path, item))
                items.sort(key=lambda f: os.path.getmtime(f))
                lastcrash = items[-1]
        if lastcrash:
            log_files.append(['crashlog', lastcrash])

    return log_files


def copy_log_files(log_files: []):
    pass


# This is 'main'...
def run():

    footprints()

    Store.load_config_from_settings()
    Store.log_configuration()

    log_file_list = gather_log_files()
    log("Found these log files to copy:")
    log(log_file_list)

    copy_log_files(log_file_list)

    # and, we're done...
    footprints(startup=False)
