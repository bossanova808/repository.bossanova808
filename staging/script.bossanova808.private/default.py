import json
import sys

import xbmc
import xbmcaddon
import xbmcgui

ADDON = xbmcaddon.Addon()


def pick_profile():
    """Let the viewer pick the profile the fast-switch button goes to."""
    reply = json.loads(xbmc.executeJSONRPC(
        '{"jsonrpc":"2.0","id":1,"method":"Profiles.GetProfiles","params":{}}'
    ))
    current = xbmc.getInfoLabel("System.ProfileName")
    names = [p["label"] for p in reply.get("result", {}).get("profiles", []) if p["label"] != current]
    chosen = xbmcgui.Dialog().select(ADDON.getLocalizedString(30009), [ADDON.getLocalizedString(30008)] + names)
    if chosen < 0:
        return
    ADDON.setSettingString("fastswitch_target", "" if chosen == 0 else names[chosen - 1])


if len(sys.argv) > 1 and sys.argv[1] == "pick_profile":
    pick_profile()
else:
    xbmcgui.Dialog().ok(
        "Bossanova808 Private",
        "This add-on marks this install as one of Bossanova808's own systems, enabling household-specific skin behaviour.[CR][CR]"
        "If this is not one of Bossanova808's systems, please uninstall it.",
    )
