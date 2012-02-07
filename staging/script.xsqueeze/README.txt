README v0.0.1 for XSqueeze

Proof of concept for test purposes.

USE AT YOUR OWN RISK AND EXPECT IT TO BE PLENTY ROUGH!!

XSqueeze is a very basic Squeezebox controller that just passes everything on to Squeezeslave, and uses it for audio playback as well.  It's built on the hard work of the SqueezeSlave and Pysqueezecenter folks...

To get this to work:

********************************************************************************
1. Install Squeezeslave on your XBMC system.  

Binaries are available here (use latest version):
http://sourceforge.net/projects/softsqueeze/files/squeezeslave/

...with notes and install/build/etc instructions here:
http://wiki.slimdevices.com/index.php/SqueezeSlave

Openelec users can find a knocked up version here (untest by me):
http://openelec.tv/forum/13-miscellaneous/8027-squeezeserversoftsqueeze-on-openelecxbmc?limit=20&start=20#18826

(read the whole thread and ask in there if you need help, I have no idea about this yet!)


********************************************************************************
2. Run Squeezeslave

e.g. squeezelave.exe 192.168.1.1

....the IP address is your server address

If it conncets, you will not see anything happen, but you also won't see an error message!

squeezeslave -h will give you help if anything goes wrong.

********************************************************************************
3. Install XSqueeze

Use the bossanova808 repo available here:
http://wiki.xbmc.org/index.php?title=Unofficial_add-on_repositories

...download the zip, and install the add on from the zip file

Wait a minute or two (or force-refresh the add on) - the in the repo you will see various installable addons.  Choose XSqueeze

********************************************************************************
4. Configure XSqueeze

In the add on settings, add your server IP address and port, and in the player settings add the MAC.  The port and mac address are pre-filled in with the regular defaults so leave them unchaged unless you've deliberately changed something.

********************************************************************************
5. Run XSqueeze

In XBMC->Programs, run XSqueeze

You should get a vaguely SB like screen.  You can exit with your exit/home button (usually the big green one on MCE remotes).  To navigate, use the up/down/arrows/left/right arrows like on the SB remote etc - and hitting right is generally the 'select' action just like on actual squeezeboxes (select itself will proably also work).

********************************************************************************
6. Experiment and report back!

Obviously I have a lot of plans for this, this is just a very, very basic proof of concept.  All the fancy will come later, like pictures, playlist etc.  At the moment I just want feedback on how it works in terms of raw playback.
 
********************************************************************************
7. SYNC ISSUES - please experiment with sync between your players.  

Squeezeslave is a software player and like all software players, does not support really precise sync like the hardware ones due to all sorts of factors involved (network latency, soundcard drift etc) - that being said, there are some tweaks available in your LMS Settings->Player->Synchronize ... this can improve things and I have so far found sync to be good enough to walk from room to room ok.  Probably not good enough for two players in one room, though.

********************************************************************************
8. IF YOU CAN'T GET IT TO WORK

Try harder!  Try really hard, and if you are then still really stuck, post to the forum thread here:

I am looking for general feesback and ideas, not to spend all my time answering basic support questions at this point. So if this seems beyond, then for the moment it probably is.  Wait a bit until a more solid release comes along.

********************************************************************************



 