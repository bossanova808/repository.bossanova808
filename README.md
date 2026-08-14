Kodi Bossanova808 Repository
===================================

`repository.bossanova808`

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/bossanova808) 

## Installation

1. In Kodi, go to **Settings → Media → File manager → Add source**, and add `https://repo.bossanova808.net` as a new source (call it whatever you like, e.g. `bossanova808`).
2. Go to **Add-ons → Install from zip file**, browse to the source you just added, and install the **latest** `repository.bossanova808-x.y.z.zip` (there may be two listed - pick the higher version number).
3. You can now browse and install any of the addons below from **Add-ons → Install from repository → Bossanova808's Kodi Addon Repository** - they'll auto-update from there too.

**Note:** these addons are a bit less polished that the ones I submit to the official Kodi repo and/or contain/do things they don't allow in official add-ons (such as patching skin files, or binary blobs for hardware support).  

## OzWeather Skin Patcher

Automatic skin patcher, to support OzWeather skin changes (giving you e.g. animated Australian BOM weather radars in Kodi, in a number of popular skins) - see the [OzWeather Wiki](https://kodi.wiki/index.php?title=Add-on:Oz_Weather) for full details.

## Jellyfin Fixer

A small addon for various personal Jellyfin-for-Kodi hack-fixes - currently clearing noisy/inconsistent TV show ratings synced from Jellyfin, plus a resume-point fix that's now largely superseded upstream and off by default. All fixes are off by default and must be explicitly enabled - use at your own risk. See the [full README](https://github.com/bossanova808/repository.bossanova808/blob/main/staging/script.jellyfin-fixer/README.md) for details and current status.

## Kodi YoctoDisplay

Script for displaying some simple 'now playing' information (remaining time & current temperature), on an external USB connected [Yocto MaxiDisplay](https://www.yoctopuce.com/EN/products/usb-displays/yocto-maxidisplay).  Unfortunately this can't be released via the official Kodi repository as it includes pre-compiled binaries for driving the Yocto display.

## Bossanova808 Friends & Family Confluence

_(This is probably too personalised to be of general interest)._

Personal customised version of Confluence with modifications including integrated OzWeather support, ClearArt support, better Profile support, comprehensive PlayerProcessInfo support (detailed video/audio/system info, plus HDR/Dolby Vision metadata) when used with custom Amlogic AM6B+ builds such as Panni's `t4c`, and a few other visual and usability tweaks to my personal taste.  
