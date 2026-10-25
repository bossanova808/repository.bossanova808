Limp
===================================

`script.limp`

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/bossanova808)

Limp forces software decoding for the videos you choose, then restores your previous hardware decoding setting once playback ends. 

On some platform, hardware decoding just gets some videos wrong (e.g. on CoreELEC, with Amlogic's `amcodec`, rotated phone clips play stretched, old MJPEG AVI clips just won't play at all, and some 50 fps video playback inexplicably drops frames). And sometimes you may just prefer software decoding for some of your videos.

Limp supports Amlogic (CoreELEC), Windows, Apple devices (macOS, iOS, tvOS) and webOS. Apple and webOS are as yet untested - reports welcome.

## Ways to use it

If a rule is on and a video meets the rule, Limp automatically engages software decoding. Rules apply everywhere by default; the Path Limits settings page can be used to limit the application to just the paths you set, if you prefer.

**Automatically** - on the General settings page, choose when Limp should engage software decoding:

- (Offered only on Amlogic platforms) - videos that trigger known Amlogic decoding failures (Amlogic only) - files with a rotation tag, and MJPEG AVI files.
- All videos 1080p and below.

(N.B. for video from add-ons such as Jellyfin, Limp can't pre-decode the file itself, so it can only determine if a video meets the rule using the resolution given by Jellyfin to Kodi.  Thus, the 1080p rule works, but the Amlogic rule can't...so if you're trying to solve issues with your old home videos, direct access (SMB/NFS etc), will be the better option for those).

**By series** - **Limp: software decode series** in the Videos window context menu makes every episode of a TV series use software decoding. **Limp: stop software decoding series** reverses it, and **Manage shows Limp has been set to software decode...** on the By TV Show settings page lists the series and removes any you pick. N.B. Explicitly chosen series ignore the Path Limits.

**On demand** - **Limp: software decode** in the same menu plays _any_ one video with software decoding.

(The context menu items can be disabled in the add-on settings, if you prefer).

## Safety

If Kodi crashes, or the profile is switched, while Limp is forcing software decoding, Limp restores your hardware decoding setting the next time it starts in that profile. It also checks the setting periodically, and logs any change it didn't make.

Developed and tested on Amlogic S9xx (CoreELEC/Ugoos AM6B+) and Windows. Issues and PRs welcome on GitHub - e.g. for other platforms, or other playback problems this could help with.
