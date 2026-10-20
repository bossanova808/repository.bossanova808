Limp
===================================

`script.limp`

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/bossanova808)

Limp forces software decoding for video that Amlogic's `amcodec` hardware decoder gets wrong, then restores your previous hardware decoding setting once playback ends.

Known problems:

- Rotated phone/camera clips usually play stretched (occasionally with the wrong orientation).
- Old MJPEG AVI clips won't play at all.
- Some 50 fps video drops frames.

Software (FFmpeg) decoding handles all of these correctly.

## Ways to use it

**By path** - Limp runs as a service, watching the paths you set on the By Path settings page (or, less safely, everywhere). Only files with a rotation tag, or MJPEG AVI files, are switched. Other files (such as 4K HDR files, too heavy for the CPU) are ignored.

**By series** - **Limp: software decode series** in the Videos window context menu makes every episode of a TV series use software decoding. **Limp: stop software decoding series** reverses it, and **Manage series using software decoding...** in settings lists the series and removes any you pick.

**On demand** - **Limp: software decode** in the same menu plays any one video with software decoding.

The context menu items can be turned off in settings.

## Safety

If Kodi crashes, or the profile is switched, while Limp is forcing software decoding, Limp restores your hardware decoding setting the next time it starts in that profile. It also checks the setting periodically, and logs any change it didn't make.

Confirmed working on Amlogic S9xx (CoreELEC/Ugoos AM6B+). Issues and PRs welcome on GitHub - e.g. for other platforms, or other playback problems this could help with.
