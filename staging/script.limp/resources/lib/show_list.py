import json
import os

import xbmcgui

from bossanova808.constants import PROFILE
from bossanova808.logger import Logger
from bossanova808.notify import Notify


def title_key(title):
    """
    The key a TV show is stored under: its title, ignoring case and surrounding whitespace.

    :param title: the show's title, as Kodi reports it
    :return: the normalised key
    """
    return title.strip().casefold()


class ShowList:
    """
    A persistent list of TV shows, kept as a small JSON file in the addon's profile folder (e.g.
    shows to ignore, or to treat specially). Each show has a key, used for lookups, and a title, used
    for display - see title_key().

    Deliberately free of anything addon-specific, so it can move into script.module.bossanova808 and
    be shared (e.g. with Check Previous Episode's ignored shows) without changes.
    """

    def __init__(self, filename):
        """
        :param filename: the name of the JSON file, inside the addon's profile folder
        """
        self.path = os.path.join(PROFILE, filename)
        self._shows = {}
        self.load()

    def __len__(self):
        return len(self._shows)

    def load(self):
        """
        (Re)load the list from disk - an unreadable or missing file just gives an empty list.
        """
        self._shows = {}
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            Logger.warning(f'Could not load show list {self.path}: {e}')
            return
        if isinstance(data, dict):
            self._shows = {str(key): str(title) for key, title in data.items()}

    def save(self):
        """
        Write the list to disk, via a temporary file so a half-written file is never left behind.
        """
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        temporary_path = self.path + '.tmp'
        with open(temporary_path, 'w', encoding='utf-8') as f:
            json.dump(self._shows, f, ensure_ascii=False, indent=2)
        os.replace(temporary_path, self.path)

    def contains(self, key):
        """
        :param key: the show's key
        :return: True if the show is on the list
        """
        return key in self._shows

    def add(self, key, title):
        """
        Add a show (or update its title) - call save() to keep the change.
        """
        self._shows[key] = title

    def remove(self, keys):
        """
        Remove shows - call save() to keep the change.

        :param keys: the keys of the shows to remove
        """
        for key in keys:
            self._shows.pop(key, None)

    def items(self):
        """
        :return: (key, title) pairs, sorted by title
        """
        return sorted(self._shows.items(), key=lambda pair: (pair[1].casefold(), pair[0]))

    def manage(self, heading, empty_message):
        """
        Show a dialog listing the shows, and remove the ones the user selects.

        :param heading: the dialog heading
        :param empty_message: what to tell the user if there's nothing on the list
        :return: True if anything was removed
        """
        self.load()
        items = self.items()
        if not items:
            Notify.info(empty_message)
            return False

        selected = xbmcgui.Dialog().multiselect(heading, [title for _, title in items])
        if not selected:
            return False

        removed = [items[index] for index in selected]
        Logger.info(f'Removing from {self.path}: {[title for _, title in removed]}')
        self.remove([key for key, _ in removed])
        self.save()
        return True
