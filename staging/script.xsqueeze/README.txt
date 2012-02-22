README v0.3 for XSqueeze

See http://forum.xbmc.org/showthread.php?t=122199 for discussion/release notification!

********************************************************************************
* INTRODUCTIONS:

XSqueeze is Squeezebox player/controller for XBMC.   

It was built by me (bossanova808@gmail.com) using some python and building on the hard work of two handy projects: SqueezeSlave and Pysqueezecenter.

XSqueeze can be used in two main ways:

1. As simply a big-screen visualiser/controller for an existing Squeezebox player installation (all squeezebox models can be visualised, all but Touch and Radio controlled at this stage)

or 

2. As a player with local playback, and a visualiser - meaning you can have an XBMC/XSqueeze setup in your media room that syncs with other squeezebox installations around your house, without needing to install a squeezebox in your media room!

Option 2 - the default - uses SqueezeSlave, either run directly by the add on or manually installed.  (Note that the player functionality only works on Windows, OSX and Linux 2.6+/Openelec - not iOS/other platforms not listed - basically, the squeezeslave binary must be available for your system for local playback to be possible)

NB - below, LMS = Logitech Media Server, the software that serves up music to Squeeze-machines.  PLEASE USE VERSION 7.6+!

********************************************************************************
* INSTRUCTIONS:

1. Install XSqueeze on your XBMC machine (any platform)

Use the bossanova808 repo available here:
http://wiki.xbmc.org/index.php?title=Unofficial_add-on_repositories

...download the repo zip, and install the repo using the zip file

Wait a minute or two (or force-refresh the repo) - then in the repo you will see various installable addons.  Choose XSqueeze and install it.

********************************************************************************
2. Configure XSqueeze

Go to the add on settings (go to the add on and use the context menu to get to 'configure').  

There are 4 tabs:

1. LMS Server

Here's where you put your LMS server details.  In most cases, just click on the 'Discover LMS Server...' field and it should find your server and you choose it.

** Note server auto discovery does not currently work on OSX.

However, if you've changed your LMS server's HTTP (normally 9000) or CLI port (normally 9090), then you will need to manually specify your server details.

2. Local Playback

This is enabled by default as it's the most common scenario.
If you don't want to use local playback, disable the first toggle.

If local playback is enabled you can:
- Change the dummy MAC address squeezeslave uses (if you have multiple installations of XSqueeze for example)
- Add a list of extra Squeezeslave arguments that will be passed on
  (see http://wiki.slimdevices.com/index.php/SqueezeSlave#Command_Line_Switches)
- Most of the time squeezeslave will discover and use the default audio output for your system, however you can manually choose an output if you want to as well.

** Note audio output discovery does not yet work on OSX

3. Controller Only

If you want to use XSqueeze jut as a visualise for an existing player, enable the controller only mode on this tab.

Now, enter the MAC address of the player you want to visualise - you can find this information on your LMS Server->Settings->Information page.

(Tested with SLIMP3, SB2, SB3 and Boom players, I don't have a Radio or Touch to try unfortunately, and I suspect these will not work)

You can also use Controller Only mode if you wish to manually install & run your own Squeezeslave or SqueezePlayer (see appendix A below!).  Then you just enter the mac address of this software player here just like you would any other player.

4. Other Settings

You can choose to disable your screensaver during XSqueeze sessions (off by default, and note I have found this to cause hangs on XSqueeze exit so I don't really recommend it)

********************************************************************************
3. Run XSqueeze

In XBMC->Add Ons->Programs, run XSqueeze 

(Note - it doesn't live in the music section as it's not a typical XBMC music plugin, as the playback itself is external to XBMC's playback systems).  

In most skins, you can use the skin settings to add the addon to your home page for easy access of course.

On your first run of any new version, you may get a message window pop up with any important changes, reminders etc.  This only occurs the first run of each version, but you can find the same information in the addon folder/FIRSTRUN.txt if you need it.

As the add on starts, you will get messages if there are any issues (see below for troubleshooting).  Once everything is ok (and after SqueezeSlave has started if you have chosen the local playback option) - you will get to the main XSqueeze Now Playing screen.

You can exit at any time with your exit/home button (usually the big green one on MCE remotes).  To navigate, use the up/down/arrows/left/right arrows just like on the SB remote etc - and hitting right is generally the 'select' action just like on actual squeezeboxes (select itself will probably also work in most contexts).

The basic layout is a big panel with cover art, progress bar etc. for the current track, and smaller displays for the next three coming tracks.

At the bottom of the screen you have the classic two line SB controller/display that will change as you navigate the 'virtual squeezebox'.

You may see a few as-yet-unsolved glitches:
  - skipping to the next track gives a playlist error pop up from XBMC as the playlist is empty, just ignore this
  - Volume - depends on how your XBMC is set up/connected.  If your volume controls go to an external device like an amp/receiver, then it will work great and as expected.  If you control volume via XBMC's digital volume controls, you will see XBMC's volume slider as well as the Squeezebox display changing volume - ignore the XBMC display as it isn't involved.

********************************************************************************
4. Please experiment and report back!

Obviously I have a lot of plans for this, this is just a simple beginning.  All the fancy will come later, like playlist building and management etc.  

The thread for discussion/issues etc. is here:
http://forum.xbmc.org/showthread.php?t=122199
 
********************************************************************************
5. AUDIO ISSUES (dropouts, no audio etc) 

**** FIRST, ON UNIX TYPE SYSTEMS (Linux, Openelec, OSX) TRY TURNING OFF XBMC MENU SOUNDS!!  If you have these on, XBMC greedily grabs the audio device and won't share.  

If you're not getting audio full stop from the addon then you will probably need to set your output for Squeezeslave up.  This is done in XSqueeze settings -> Local Playback

(You can test all of this from the command line quite easily using the -D switch for squeezeslave, so in full:
squeezeslave -o12 -D yourserveraddress
   
..this will give you a text based Squeezeslave player right on your command line so you can quickly trigger audio to test etc.

********************************************************************************
6. GENERAL ISSUES (can't start server/player errors) 

If you're experiencing general issues, the best thing is to simplify things and make sure squeezeslave outside of XBMC works ok. 

Go to the addon folder/resources/bin/squeezeslave-XXXXX/squeezeslave-SYSTEM directory (where X is the version number, and SYSTEM is win, Linux or OSX)

From the command line, manually run squeezeslave and see if it can find your server, make a connection and play audio.

See:
http://wiki.slimdevices.com/index.php/SqueezeSlave
http://wiki.slimdevices.com/index.php/SqueezeSlave#Command_Line_Switches

..for instructions.

If you are stuck - post a message to the forum thread 
( http://forum.xbmc.org/showthread.php?t=122199 ) 
and remember to always ***INCLUDE YOUR FULL LOGFILE****

********************************************************************************
6. SYNC ISSUES - please experiment with sync between your players.  

Squeezeslave is a software player and like all software players, does not 100% support really precise sync like the hardware ones do - this is due to all sorts of factors (network latency, buffering, soundcard drift etc) 

That being said, there are some tweaks available in your LMS Settings->Player->Synchronize ... this can improve things and I have so far found sync to be good enough to walk from room to room ok.  Probably not good enough for two players in one room, though, although very close.  It's really pretty good.

********************************************************************************
7. IF YOU CAN'T GET IT TO WORK

Try harder & re-read these instructions!  Try really hard, and if you are then still really stuck, post to the forum thread here: http://forum.xbmc.org/showthread.php?t=122199

Feedback and ideas appreciated!

********************************************************************************

 
 
 

********************************************************************************
* APPENDIX
* 
*

1. Manual Install of Squeezeslave on your XBMC system.

Generally it's best to just use the included SqueezeSlave, but if you have special needs you might want to use a manual install.  

Binaries are available here (use latest version):
http://sourceforge.net/projects/softsqueeze/files/squeezeslave/

...with notes and install/build/etc instructions here:
http://wiki.slimdevices.com/index.php/SqueezeSlave

Openelec users can find a service addon here:
http://openelec.tv/forum/13-miscellaneous/8027-squeezeserversoftsqueeze-on-openelecxbmc?limit=20&start=20#18826

For support for those things, please see their own threads in their respective forums.


********************************************************************************
2. Manually Run Squeezeslave

e.g. squeezeslave.exe 192.168.1.1

....the IP address is your server address

If it connects, you will not see anything happen, but you also won't see an error message!

squeezeslave -h will give you help/options if anything goes wrong.
