import xbmc
import xbmcaddon
import xbmcvfs
import os
import sys
import platform
import stat

#Import the common code - basically the SqueezePlayer class
#which connects to the server and a player
from XSqueezeCommon import *
from b808common import *

################################################################################
#window control IDS - see XSqueezeNowPlaying.xml for matching controls
# only progress bar and volume bar referred to directly, the rest is put into $INFO

MAINCOVERART          = 100
UPCOMING1COVERART     = 101
UPCOMING2COVERART     = 102
UPCOMING3COVERART     = 103
PLAYSTATE             = 104
SLIDESHOW             = 105
CURRENTTITLE          = 200
CURRENTARTIST         = 201
CURRENTALBUM          = 202
CURRENTPROGRESS       = 998 # ***** IMPORTANT!
VOLUMEBAR             = 997 # ***** IMPORTANT!
CURRENTELAPSED        = 204
CURRENTREMAINING      = 205
CURRENTLENGTH         = 206
DISPLAYLINE1          = 1000
DISPLAYLINE2          = 1001
UPCOMING1             = 2001
UPCOMING2             = 2002
UPCOMING3             = 2003

BUTTONEXIT            = 2599
BUTTONSKIPBACK        = 2600
BUTTONREWIND          = 2601
BUTTONPLAYPAUSE       = 2602
BUTTONFASTFORWARD     = 2603
BUTTONSKIPFORWARD     = 2604
BUTTONSTOP            = 2605
BUTTONSHUFFLE         = 2606
BUTTONREPEAT          = 2607
BUTTONVOLUP           = 2608
BUTTONVOLDN           = 2609
BUTTONCHOOSER         = 2610

################################################################################
#useful paths


BIN_PATH = xbmc.translatePath(os.path.join( RESOURCES_PATH, "bin" ))
KEYMAP_PATH = xbmc.translatePath(os.path.join( RESOURCES_PATH, "keymaps" ))
KEYMAPSOURCEFILE = os.path.join(KEYMAP_PATH, "xsqueeze.xml")
KEYMAPDESTFILE = os.path.join(xbmc.translatePath('special://userdata/keymaps'), "xsqueeze.xml")
RUNTOKEN_PATH = xbmc.translatePath("special://userdata/addon_data/script.xsqueeze/runtokens/")

################################################################################
# first run stuff - set once here, then a constant

ISFIRSTRUN=True
#set a runtoken only if we are running the __main__ not the server discovery etc.
runtoken = os.path.join(RUNTOKEN_PATH, "runtoken" + VERSION)
if not xbmcvfs.exists(runtoken):
  if not xbmcvfs.exists(DATA_PATH):
    xbmcvfs.mkdir(DATA_PATH)
  if not xbmcvfs.exists(RUNTOKEN_PATH):
    xbmcvfs.mkdir(RUNTOKEN_PATH)
  ISFIRSTRUN=True
  token = open(runtoken, 'w')
  token.close()
else:
  ISFIRSTRUN=False


################################################################################
# LOCAL PLAYBACK SETTINGS
# LMS is case sensitive and all MACs need to be lower case!!

#are we controlling the local slave or another external player?
if ADDON.getSetting('playback')=="true":
  PLAYBACK = True
else:
  PLAYBACK = False

#always add the MAC adress as an argument, and the audiooutput from teh choosers if used..
PLAYERARGS = []
if PLAYERTYPE=="squeezeslave":
  PLAYERARGS.append("-m" + PLAYERMAC)
  if ADDON.getSetting('autooutputslave')!="":
    PLAYERARGS.append(ADDON.getSetting('autooutputslave'))
else:
  PLAYERARGS.append("-m")
  PLAYERARGS.append(PLAYERMAC)
  if ADDON.getSetting('autooutputlite')!="":
    PLAYERARGS.extend(ADDON.getSetting('autooutputlite').split(" "))

#any extra player arguments supplied for special needs?
if PLAYERTYPE=="squeezeslave":
    tempargs = ADDON.getSetting('slaveargs').split(" ")
else:
    tempargs = ADDON.getSetting('liteargs').split(" ")

if tempargs[0] != '':
  PLAYERARGS.extend(tempargs)



################################################################################
# GET OTHER SETTINGS

if ADDON.getSetting('enableTouch')=="true":
  TOUCHENABLED = True
else:
  TOUCHENABLED = False
if ADDON.getSetting('sendPlayOnStart')=="true":
  PLAYONSTART = True
else:
  PLAYONSTART = False

SECONDS_TO_PAUSE_STARTUP = int(ADDON.getSetting('startuppause'))
SECONDS_TO_PAUSE_EXIT = int(ADDON.getSetting('exitpause'))
SECONDS_TO_PAUSE_CONNECT = int(ADDON.getSetting('connectpause'))
SECONDS_TO_WAIT_FOR_ARTISTSLIDESHOWEXIT = int(ADDON.getSetting('waitOnAS'))

###############################################################################
#GET HDMI CEC SETTINGS

CECSUPPORT = ADDON.getSetting('cecsupport')
TURNONAVR  = ADDON.getSetting('turnonavr')
AVRINPUT   = ADDON.getSetting('avrinput')
TURNOFFTV  = ADDON.getSetting('turnofftv')
ADJUSTVOL  = ADDON.getSetting('adjustvol')
VOLFACTOR  = ADDON.getSetting('volfactor')

#variable to ensure that hdmipower commands are only send once and not all the time
HDMIPOWER = "false"

################################################################################
# Deal with the squeezeslave executeables...

BINWIN    = xbmc.translatePath(BIN_PATH + "\\windows\\" + PLAYERTYPE + ".exe" )
BINOSX    = xbmc.translatePath(BIN_PATH + "/osx/" + PLAYERTYPE )
BINLIN32  = xbmc.translatePath(BIN_PATH + "/linux/" + PLAYERTYPE + "-i386" )
BINLIN64  = xbmc.translatePath(BIN_PATH + "/linux/" + PLAYERTYPE + "-i64" )
BINARM    = xbmc.translatePath(BIN_PATH + "/arm/" + PLAYERTYPE )

# for server discovery we alwayus use squeezeslave, also used for audio output discovery
SLAVEBINWIN    = xbmc.translatePath(BIN_PATH + "\\windows\\squeezeslave.exe" )
SLAVEBINOSX    = xbmc.translatePath(BIN_PATH + "/osx/squeezeslave")
SLAVEBINLIN32  = xbmc.translatePath(BIN_PATH + "/linux/squeezeslave-i386" )
SLAVEBINLIN64  = xbmc.translatePath(BIN_PATH + "/linux/squeezeslave-i64" )
SLAVEBINARM    = xbmc.translatePath(BIN_PATH + "/arm/squeezeslave" )
# for ausio output discovery
LITEBINWIN    = xbmc.translatePath(BIN_PATH + "\\windows\\squeezelite.exe" )
LITEBINOSX    = xbmc.translatePath(BIN_PATH + "/osx/squeezelite")
LITEBINLIN32  = xbmc.translatePath(BIN_PATH + "/linux/squeezelite-i386" )
LITEBINLIN64  = xbmc.translatePath(BIN_PATH + "/linux/squeezelite-i64" )
LITEBINARM    = xbmc.translatePath(BIN_PATH + "/arm/squeezelite" )


#choose the right executable
if SYSTEM.startswith("win"):
  EXE = [BINWIN]
  SLAVEEXE = [SLAVEBINWIN]
  LITEEXE = [LITEBINWIN]
elif SYSTEM.startswith("osx"):
  EXE = [BINOSX]
  SLAVEEXE = [SLAVEBINOSX]
  LITEEXE = [LITEBINOSX]
elif SYSTEM.startswith("arm"):
  EXE = [BINARM]
  SLAVEEXE = [SLAVEBINARM]
  LITEEXE = [LITEBINARM]
else:
  if is_64bits:
    EXE = [BINLIN64]
    SLAVEEXE = [SLAVEBINLIN64]
    LITEEXE = [LITEBINLIN64]
  else:
    EXE = [BINLIN32]
    SLAVEEXE = [SLAVEBINLIN32]
    LITEEXE = [LITEBINLIN32]

#chmod +X the exe file on linux/osx ...

if SYSTEM.startswith("lin") or SYSTEM.startswith("arm"):
  try:
    os.system("chmod a+x " + EXE[0])
    os.system("chmod a+x " + SLAVEEXE[0])
    os.system("chmod a+x " + LITEEXE[0])
    log("(linux/arm) chmod +x the player binaries - success")
  except:
    log("chmod +x the player binaries - failure -> You must do this manually!!")
elif SYSTEM.startswith("osx"):
  try:
    os.chmod(EXE[0], stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    os.chmod(SLAVEEXE[0], stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    os.chmod(LITEEXE[0], stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    log("chmod +x the player binaries - success")
  except:
    log("chmod +x the player binaries - failure -> You must do this manually!!")
else:
  log("Windows or ATV/IOS, so no need to chmod the binaries.")


