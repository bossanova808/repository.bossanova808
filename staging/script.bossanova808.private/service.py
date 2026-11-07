"""Keeps the Bossanova808 skins' per-profile settings (custom TV Shows sub-menu, fast profile
switching) in skin strings.

A skin cannot read another add-on's settings, and skin strings are saved per profile and available
the instant the skin loads - so the skin never has to wait for this service to start. The service only
writes a string when it differs, so it does nothing at all in the normal case."""
import xbmc
import xbmcaddon

SLOTS = 5


def set_skin_string(name, value):
    if xbmc.getInfoLabel("Skin.String(%s)" % name) == value:
        return
    if value:
        xbmc.executebuiltin('Skin.SetString(%s,"%s")' % (name, value.replace('"', "")))
    else:
        xbmc.executebuiltin("Skin.Reset(%s)" % name)


def publish():
    addon = xbmcaddon.Addon()
    enabled = addon.getSettingBool("tvmenu_enabled")
    set_skin_string("B808TVMenuEnabled", "true" if enabled else "")
    for i in range(1, SLOTS + 1):
        label = addon.getSettingString("tvmenu_%d_label" % i).strip() if enabled else ""
        path = addon.getSettingString("tvmenu_%d_path" % i).strip() if enabled else ""
        if not path:
            label = ""
        set_skin_string("B808TVMenu%dLabel" % i, label)
        set_skin_string("B808TVMenu%dPath" % i, path)
    set_skin_string("B808FastSwitchTarget", addon.getSettingString("fastswitch_target").strip())


class SettingsMonitor(xbmc.Monitor):
    def onSettingsChanged(self):
        publish()


if __name__ == "__main__":
    publish()
    monitor = SettingsMonitor()
    monitor.waitForAbort()
