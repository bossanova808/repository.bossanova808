Limp
===================================

`script.limp`

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/bossanova808)

Limp forces software decoding for video files that Amlogic's `amcodec` hardware decoder gets wrong, then restores your previous hardware decoding setting once playback ends.

Two known problems trigger it: rotated phone/camera clips, which usually play stretched (occasionally with the wrong orientation), and old MJPEG AVI clips, which won't play at all on hardware decode. Software (FFmpeg) decoding handles both correctly.

Runs as a service, watching one or more paths you configure in settings (or, less safely, applied everywhere). Only files that actually benefit from software decoding are switched. Other files (such as 4K HDR files, too heavy for the CPU) are ignored.

Confirmed working on Amlogic S9xx (CoreELEC/Ugoos AM6B+). Issues and PRs welcome on GitHub - e.g. for other platforms, or other playback problems this could help with.
