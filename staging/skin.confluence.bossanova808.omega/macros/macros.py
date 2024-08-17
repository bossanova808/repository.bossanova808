import sys
import xbmc
import xbmcgui
import xbmcvfs
import time

xbmc.log("### Python version: %s" % sys.version,xbmc.LOGDEBUG)
xbmc.log(f"### macros.py - bossanov808 run macro: {' '.join(sys.argv[1:])}")

# What macro to run?
# N.B. DO NOT USE 'match' as Kodi Python on Windows still stuck back at 3.8, sigh...

if sys.argv[1] == "switch_to_profile":
    dialog = xbmcgui.Dialog()
    dialog.notification(f"Switching Profile",
                        f"to: {sys.argv[2]}",
                        xbmcvfs.translatePath('special://skin/media/icon_profile.png'),
                        #xbmcgui.NOTIFICATION_INFO,
                        2000)
    # This is needed or the notification won't show.  Testing shows >= 0.2 needed
    time.sleep(0.2)
    xbmc.executebuiltin(f"LoadProfile({sys.argv[2]},)")

# Macro not found...?!
else:
    xbmc.log(f"### macros.py - ERROR - no such macro: {' '.join(sys.argv[1:])}")


xbmc.log(f"### macros.py - bossanov808 end macro: {' '.join(sys.argv[1:])}")

