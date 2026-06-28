import xbmc
import xbmcvfs
import sqlite3
import os
import glob
import threading

from bossanova808.logger import Logger
from bossanova808.notify import Notify

# noinspection PyPackages
from .store import Store


def find_profile_video_db():
    """Return the profile-specific path to MyVideos*.db."""
    db_dir = xbmcvfs.translatePath("special://profile/Database/")
    if isinstance(db_dir, bytes):
        db_dir = db_dir.decode("utf-8")

    pattern = os.path.join(db_dir, "MyVideos*.db")
    candidates = sorted(glob.glob(pattern))
    if not candidates:
        Logger.error("Could not find profile MyVideos*.db in %s" % db_dir)
        return None
    return candidates[-1]


def execute_safely(cur, query):
    """Executes code blocks against SQLite cursors safely."""
    try:
        cur.execute(query)
        return cur.rowcount
    except sqlite3.OperationalError as e:
        Logger.debug("Error: %s" % e)
        return 0


def purge_tv_ratings():
    """Wipe all TV show, season, and episode ratings out of the current profile's database."""
    if not Store.clear_ratings:
        return

    db_path = find_profile_video_db()
    if not db_path:
        return

    Logger.info("Now purging ratings.")
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cleared_rows = 0

        # 1. Clear out core rating tables
        cleared_rows += execute_safely(cur, "DELETE FROM rating WHERE media_type IN ('tvshow', 'episode')")

        # 2. Reset personal user ratings
        cleared_rows += execute_safely(cur, "UPDATE episode SET userrating = NULL WHERE userrating IS NOT NULL")
        cleared_rows += execute_safely(cur, "UPDATE tvshow SET userrating = NULL WHERE userrating IS NOT NULL")
        cleared_rows += execute_safely(cur, "UPDATE seasons SET userrating = NULL WHERE userrating IS NOT NULL")

        # 3. Strip legacy embedded metadata column string cells (c03/c04 matches)
        cleared_rows += execute_safely(cur, "UPDATE episode SET c03 = NULL WHERE c03 IS NOT NULL AND c03 != ''")
        cleared_rows += execute_safely(cur, "UPDATE tvshow SET c04 = NULL WHERE c04 IS NOT NULL AND c04 != ''")

        if cleared_rows > 0:
            conn.commit()
            Logger.info(f"Purged {cleared_rows} database records. Refreshing interface view.")
            xbmc.executebuiltin("Container.Refresh")
            # Notify.info(f"Purged {cleared_rows} ratings.")
        else:
            Logger.info("No ratings found, therefore nothing purged.")
    finally:
        conn.close()


def handle_jellyfin_sync_purge():
    """Callback execution entry point intended to fire asynchronously."""
    if Store.clear_ratings:
        threading.Thread(target=purge_tv_ratings, name="JellyfinFixerPurgeWorker", daemon=True).start()