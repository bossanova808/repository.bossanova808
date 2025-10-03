
Kodi Jellyfin Fixer
===================================

_script.jellyfin-fixer_

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/bossanova808)

_<Currently in development!>_

## Problems the Jellyfin Fixer Attempts to Solve
Hacked together add-on to try and solve some very annoying Jellyfin for Kodi problems:
- Resume point is almost always wrong - randomly from some seconds to several minutes prior to actual resume point!
- Resume point occasionally seems to be randomly cleared, and playback will go back to the start
- Kodi doesn't display subtitles without a long delay (https://github.com/jellyfin/jellyfin-kodi/issues/35, https://github.com/xbmc/xbmc/issues/21086 etc), this improves after a seek

## How Does Jellyfin Fixer Work?

This addon detects the start of playback, then:
- If Kodi is playing back a library item (episode or movie), and there is a known resume point - force Kodi to seek to the Kodi known resume point (minus 4 seconds)
- If no resume point, or the resume point is set at less than 20s, perform an immediate seek to 0.0, to try and cause the display of subtitles to occur earlier

## Known Issues

- This currently breaks the 'play from beginning' method that Kodi offers - playback always resumes from the known resume point.







