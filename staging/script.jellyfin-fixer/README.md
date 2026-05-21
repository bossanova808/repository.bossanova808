
Kodi Jellyfin Fixer
===================================

_script.jellyfin-fixer_

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/bossanova808)


Jellyfin Fixer was created to fix various personal niggles I have with the behaviour of the Kodi Jellyfin Addon.  It's a place for hack fixes, basically!

### USE AT YOUR OWN RISK!

**All fixes are off by default and must be explicitly enabled in the addon settings.**

This addon is provided as-is, is only tested by me locally to work for my specific use cases, and will happily do things like directly manipulate your Kodi sqlite DB.  

### TV show/episode ratings 

I personally dislike and rarely agree with TV show ratings as a general thing. Worse, I routinely saw very weird values in them once I switched to Jellyfin. Presumably as, often, TV episodes arrive to the library before a sensible amount or ratings have been posted.  I choose not to get Jellyfin to refresh library data periodically as this causes issues with slow/overly frequent syncing.  Unfortunately, there doesn't currently seem to be a way to stop Jellyfin from grabbing ratings, or then syncing those rating to Kodi.  So this addon now clears all TV show ratings (of the show itself, seasons, and episodes) – after all Jellyfin sync events (i.e after the initial start-up sync, and again if Jellyfin posts any library updates during that Kodi session).  It is a hack that assumes Jellyfin is your master library.  For performance reasons, it directly manipulates the Kodi sqlite DB instead of using JSON RPC calls.

### Inaccurate Resume points 

Resume points were for some time [very broken](https://github.com/jellyfin/jellyfin-kodi/issues/912#issuecomment-3392922726).  However, the fix this addon provided was essentially made obsolete by my (now integrated) fix addressing the root cause of the defect in the Jellyfin plugin: https://github.com/jellyfin/jellyfin-kodi/pull/1051. This fix has a known issue: it breaks Kodi's native 'Play From Beginning' behaviour.  This fix is currently kept here, in case of future issues, but is **off by default**.  

### Late Appearance of Subtitles 

In many cases, subtitles don't display for many seconds after being enabled (even if on by default at the start of playback).  

The fix previously offered here never worked fully/consistently. **It has thus been removed.**  (If you're an AM6B+ owner, a far better solution has emerged with [Panni's custom CoreELEC builds](https://github.com/pannal/CoreELEC/releases/tag/T3b) (I am using T4 dev currently – for dev versions see TRaSH guides Discord -> Ugoos Mediaplayer -> p3i Test Builds and Discussion thread).









