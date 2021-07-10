import xbmc
import json
from .common import *
from .store import Store


class KodiMonitor(xbmc.Monitor):
    """
    Kodi monitor - simple monitor to listen to onScanFinished events
    """

    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        log('KodiMonitor __init__')

    def onScanFinished(self, library):

        log(f'onScanFinished {library}')

        if not get_setting_as_bool('StopRequested') and Store.paths_to_update:
            self.sendLibraryScanRequestForPath(Store.paths_to_update[0])
            (method, path, show_dialog, clean_after) = Store.paths_to_update[0]
            Store.paths_to_update.pop(0)
            # Last path done?  Do we need to clean as well?
            if clean_after:
                # kick off a clean
                if method == 'video':
                    query = 'VideoLibrary.Clean'
                else:
                    query = 'AudioLibrary.Clean'

                command = json.dumps({
                    'jsonrpc': '2.0',
                    'id': 0,
                    'method': query,
                    'params': {
                        'directory': path,
                        'showdialogs': show_dialog
                    }
                })

                send_kodi_json(f'Requesting {method} library clean (show dialog: {show_dialog}), for path: {path}',
                               command)

    @staticmethod
    def sendLibraryScanRequestForPath(arg):
        """
        Send a request to Kodi to update the video library by looking at a specific path.
        @param arg: tuple of method, path and show_dialog
            method: 'video' or 'audio'
            path: the path to scan
            show_dialog: whether or not to show the scanning dialog window
        """

        (method, path, show_dialog, clean_after) = arg

        if method == 'video':
            query = 'VideoLibrary.Scan'
        else:
            query = 'AudioLibrary.Scan'

        command = json.dumps({
            'jsonrpc': '2.0',
            'id': 0,
            'method': query,
            'params': {
                'directory': path,
                'showdialogs': show_dialog
            }
        })

        send_kodi_json(f'Requesting {method} library scan (show dialog: {show_dialog}), for path: {path}', command)

        # This is another, more direct way to do this
        # Pro is that it doesn't require the JSON RPC to be active
        # Con is you can't control whether the update dialog shows
        # xbmc.executebuiltin('UpdateLibrary(video,C:\\XBMC\\Video Files\\TV01\\)')
        # xbmc.executebuiltin('UpdateLibrary(video,C:\\XBMC\\Video Files\\TV02\\)')