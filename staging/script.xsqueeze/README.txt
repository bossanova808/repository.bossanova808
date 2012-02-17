README v0.1 for XSqueeze

See http://forum.xbmc.org/showthread.php?t=122199 for discussion/release notificaction!

********************************************************************************
* INTRODUCTIONS:

XSqueeze is a (so far) very basic Squeezebox controller for XBMC.   It was built by me (bossanova808@gamil.com) using some python and building on the hard work of the SqueezeSlave and Pysqueezecenter folks...


XSqueeze can be used in two main ways:

1. As simply a big-screen visualiser/controller for an exisiting Squeezebox player

or 

2. As a player with local playback, and a visualiser - meaning you can have an XBMC/XSqueeze setup in your media room that syncs with with out squeezeboxes in your house, without needing to install a squeezebox in your media room!

Option 2 uses SqueezeSlave, either run directly by the add on or manually installed.  (Note that the player functionality only works on Windows, OSX and Linux 2.6+/Openelec - not iOS/other platforms not listed - basically, the squeezeslave binary must be available for your system for local playback to be possible)

NB - below, LMS = Logitech Media Server, the software that serves up music to Squueze-machines. 

********************************************************************************
* INSTRUCTIONS:

********************************************************************************
1. Install XSqueeze on your XBMC machine (any platform)

Use the bossanova808 repo available here:
http://wiki.xbmc.org/index.php?title=Unofficial_add-on_repositories

...download the repo zip, and install the repo using the zip file

Wait a minute or two (or force-refresh the repo) - then in the repo you will see various installable addons.  Choose XSqueeze and install it.

********************************************************************************
2. Configure XSqueeze

In the add on settings (go to the add on and use the context menu to get to 'configure').  You must set your LMS server IP address and port.

In the Player settings, either fill in the *case sensitive* details of your existing player (you can get your player's mac address from LMS -> Settings -> Information).

If you want local playback, you have two options -

1. (Easiest, default) - You can let XSqueeze start and stop a local Squeezeslave process on demand.  The binaries for this come with the add on, so all you have to do is toggle the Start/Stop local SqueezeSlave option to On.  You can add extra SqueezeSlave arguments if you need anything fancy (like setting an audio output or whatever) - by default, we use the "-m00:00:00:00:00:01" option to set the SqueezeSlave Mac address to the default one used by the add on.  However if you have several XSqueeze installs, you should change this mac address for each installation (and of course set the player MAC to match!)

2. You can instead manually install & run your own Squeezeslave or SqueezePlayer.  Then you just enter the mac address of this software player here just like you would any other player (see below for notes on this).

********************************************************************************
3. Run XSqueeze

In XBMC->Add Ons->Programs, run XSqueeze (note - it doesn't live in the music section as it's not a typical XBMC music plugin, as the playback is external to XBMC's playback systems).  In most skins, you can use the skin settings to add the addon to your home page for easy access of course.

As the add on starts, you will get messages if there are any issues.  Once everthing is ok (and after SqueezeSlave has started if you have chosen local playback option 1 above) - you will get to the main XSqueeze Now Playing screen.

You can exit at any time with your exit/home button (usually the big green one on MCE remotes).  To navigate, use the up/down/arrows/left/right arrows just like on the SB remote etc - and hitting right is generally the 'select' action just like on actual squeezeboxes (select itself will probably also work in most contexts).

The basic layout is a big panel with cover art, progress bar etc. for the current track, and smaller displays for the next three coming tracks.

At the bottom of the screen you have the classic two line SB controller/display that will change as you navigate the virtual squeezebox.

You may see a few as-yet-unsolved glitches:
  - skipping to the next track gives a playlist error pop up from XBMC as the playlist is empty, just ignore this
  - Volume - depends on how yous XBMC is set up/connected.  If your volume controls go to an external device like an amp/receiver, then it will work great.  If you control volume via XBMC itself, you will see XBMC's volume slider as well as the Squeezsbox display changing volume - ignore the XBMC display as it isn't involved.

********************************************************************************
4. Experiment and report back!

Obviously I have a lot of plans for this, this is just a simple beginning.  All the fancy will come later, like playlist building and management etc.  

The thread for discussion/issues etc. is here:
http://forum.xbmc.org/showthread.php?t=122199
 
********************************************************************************
5. SYNC ISSUES - please experiment with sync between your players.  

Squeezeslave is a software player and like all software players, does not 100% support really precise sync like the hardware ones do - this is due to all sorts of factors involved (network latency, soundcard drift etc) 

That being said, there are some tweaks available in your LMS Settings->Player->Synchronize ... this can improve things and I have so far found sync to be good enough to walk from room to room ok.  Probably not good enough for two players in one room, though, athough very close.  It's really pretty good.

********************************************************************************
6. IF YOU CAN'T GET IT TO WORK

Try harder & re-read these instructions!  Try really hard, and if you are then still really stuck, post to the forum thread here: http://forum.xbmc.org/showthread.php?t=122199

Feedback and ideas appreciated!

********************************************************************************
********************************************************************************
********************************************************************************
********************************************************************************
********************************************************************************
********************************************************************************



 
 
 

********************************************************************************
* APPENDIX
* 
*

1. Manual Install of Squeezeslave on your XBMC system.

Generally it's best to jsut use the included SqueezeSlave, but if you have special needs you might want to use a manual install.  

Binaries are available here (use latest version):
http://sourceforge.net/projects/softsqueeze/files/squeezeslave/

...with notes and install/build/etc instructions here:
http://wiki.slimdevices.com/index.php/SqueezeSlave

Openelec users can find a service addon here (untested by me):
http://openelec.tv/forum/13-miscellaneous/8027-squeezeserversoftsqueeze-on-openelecxbmc?limit=20&start=20#18826

For support for those things, please see their own threads in their respective forums.


********************************************************************************
2. Manually Run Squeezeslave

e.g. squeezelave.exe 192.168.1.1

....the IP address is your server address

If it connects, you will not see anything happen, but you also won't see an error message!

squeezeslave -h will give you help/options if anything goes wrong.
