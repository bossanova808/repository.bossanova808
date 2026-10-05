import json

import xbmc

from bossanova808.constants import HOME_WINDOW
from bossanova808.logger import Logger
from bossanova808.utilities import send_kodi_json, set_property
# noinspection PyPackages
from .decoder_override import DecoderOverride
# noinspection PyPackages
from .messages import NOTIFY_SENDER, NOTIFY_MESSAGE, ACK_PROPERTY
# noinspection PyPackages
from .store import Store

# Library item types the context menu can hand us, and the Player.Open id each one is opened by
LIBRARY_ID_KEYS = {'movie': 'movieid', 'episode': 'episodeid', 'musicvideo': 'musicvideoid'}


class KodiEventMonitor(xbmc.Monitor):

    def __init__(self):
        super().__init__()
        Logger.debug('KodiEventMonitor __init__')

    def onSettingsChanged(self):
        Logger.info('onSettingsChanged - reload them.')
        Store.load_config_from_settings()
        DecoderOverride.recheck('Settings changed')

    def onNotification(self, sender, method, data):
        """
        Handle the context menu's "software decode" request: force software decode, then play the
        item - in that order, from here, so the setting is in place before the file is opened.
        """
        if sender != NOTIFY_SENDER or not method.endswith(NOTIFY_MESSAGE):
            return

        try:
            request = json.loads(data)
            request_id = request['id']
        except (TypeError, ValueError, KeyError):
            Logger.error(f'Ignoring malformed software decode request: {data}')
            return

        item = self._item_from_request(request)
        if not item:
            Logger.error(f'Ignoring software decode request with nothing to play: {request}')
            return

        Logger.info(f'Context menu request - playing with software decode: {request.get("file")}')
        if not DecoderOverride.request_manual_force():
            Logger.error('Could not force software decode - not playing.')
            return

        response = send_kodi_json('Play with software decode', {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "Player.Open",
                "params": {"item": item, "options": {"resume": True}},
        })
        if not response or 'error' in response:
            Logger.error('Could not start playback for software decode request.')
            return

        set_property(HOME_WINDOW, ACK_PROPERTY, request_id)

    @staticmethod
    def _item_from_request(request):
        """
        The Player.Open item for a request: a library item by its id where possible (so it plays
        just as if selected normally - watched state, resume point and so on), otherwise by file.

        :param request: the request dict sent by the context menu script
        :return: a Player.Open item dict, or None if the request doesn't identify anything
        """
        id_key = LIBRARY_ID_KEYS.get(request.get('dbtype'))
        if id_key and request.get('dbid'):
            return {id_key: request['dbid']}
        if request.get('file'):
            return {'file': request['file']}
        return None
