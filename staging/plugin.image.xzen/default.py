# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING. If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *

#imports
import xbmc
import xbmcplugin
import xbmcgui
from b808common import *

#uses zenapi by Scott Gorling (http://www.scottgorlin.com)
from zenapi import ZenConnection
from zenapi.snapshots import Photo, Group, PhotoSet

################################################################################
# Photo/Set Loaders

#add a thumb for a group
def AddGroupThumb(group, numberOfItems=0):
    try:
        titlePhoto = zen.LoadPhoto(group.TitlePhoto,'Level1')
        urlTitlePhoto = titlePhoto.getUrl(ZEN_URL_QUALITY['Large thumbnail'])

        if group.Title is None:
            title="Untitled"
        else:
            title = "Group: " +  unquoteUni(group.Title)

        url = buildPluginURL({'mode':MENU_USERGALLERIES,'group':str(group.Id)})
        item=xbmcgui.ListItem(title,url,urlTitlePhoto,urlTitlePhoto)
        xbmcplugin.addDirectoryItem(THIS_PLUGIN,url,item,True,numberOfItems)

    except Exception as inst:
        log("AddPhotoSetThumb - Exception!", inst)


#add thumb that links to a set of photos
def AddPhotoSetThumb(photoSet, numberOfItems=0):

    global AUTH

    try:
        titlePhoto = zen.LoadPhoto(photoSet.TitlePhoto,'Level1')
        urlTitlePhoto = titlePhoto.getUrl(ZEN_URL_QUALITY['Large thumbnail'])

        if photoSet.Title is None:
            title="(Untitled Folder)"
        else:
            title = "Set: " + unquoteUni(photoSet.Title)

        url = buildPluginURL({"mode":DISPLAY_GALLERY, "galleryid":str(photoSet.Id)})
        item=xbmcgui.ListItem(title,url,urlTitlePhoto,urlTitlePhoto)
        xbmcplugin.addDirectoryItem(THIS_PLUGIN,url,item,True,numberOfItems)

    except Exception as inst:
        log("AddPhotoSetThumb - Exception!", inst)

#Add thumb that links to an individual photo

def AddPhotoThumb(photo, numberOfItems=0,downloadKey=""):

    global AUTH

    try:
        #get the highest quality url available
        for key, value in ZEN_DOWNLOAD_QUALITY.iteritems():
            if key not in photo.AccessDescriptor['AccessMask']:
                url = photo.getUrl(value, downloadKey, AUTH)
                #log("Added url quality: " + key)
                break;

        urlThumb = photo.getUrl(ZEN_URL_QUALITY['Large thumbnail'],downloadKey, AUTH)

        if photo.Title is None:
            title="Untitled"
        else:
            title = unquoteUni(photo.Title)

        log("AddPhotoThumb: [" + str(photo.Id) + "] title: [" + str(title) + "] url: [" +str(url) + "] urlThumb: [" + str(urlThumb) +"]")

        item=xbmcgui.ListItem(title,str(url),str(urlThumb),str(urlThumb))
        xbmcplugin.addDirectoryItem(THIS_PLUGIN,url,item,False,numberOfItems)

    except Exception as inst:
        log("AddPhotoThumb - Exception!", inst)

#Given a gallery ID, add all the thumbs
def AddGallery(zen,galleryid):

    ps = zen.LoadPhotoSet(galleryid, 'Level1',includePhotos=True)

    #is this a password protected gallery?
    if ps.AccessDescriptor['AccessType'] == 'Password':
        downloadKey = zen.GetDownloadOriginalKey(ps.Photos,"jessie")
        log("Download Key is: " + downloadKey)

    for photo in ps.Photos:
        AddPhotoThumb(photo,len(ps.Photos),downloadKey)

#Add a next page link for the correct mode, and where to start
def AddNextPageLink(mode,startNumber):
    urlNextPage=buildPluginURL({"mode":mode,"offset":startNumber})
    item=xbmcgui.ListItem("Next Page",urlNextPage,"","")
    xbmcplugin.addDirectoryItem(THIS_PLUGIN,urlNextPage,item,True)


################################################################################
# Menu Builders

def BuildMenuRootItem(mode, label):
    url = buildPluginURL({"mode":mode})
    item=xbmcgui.ListItem(label,url,'','')
    xbmcplugin.addDirectoryItem(THIS_PLUGIN,url,item,True)

def BuildMenuRoot(zen):
    if AUTHENTICATED:
        BuildMenuRootItem(MENU_USERGALLERIES        ,"User Galleries")
    BuildMenuRootItem(RECENTPHOTOS                  ,"Recent Photos")
    BuildMenuRootItem(RECENTGALLERIES               ,"Recent Galleries")
    BuildMenuRootItem(RECENTCOLLECTIONS             ,"Recent Collections")
    BuildMenuRootItem(POPPHOTOS                     ,"Popular Photos")
    BuildMenuRootItem(POPGALLERIES                  ,"Popular Galleries")
    BuildMenuRootItem(POPCOLLECTIONS                ,"Popular Collections")
    BuildMenuRootItem(CATEGORIES                    ,"Categories")
    if not AUTHENTICATED:
        BuildMenuRootItem("",                       "(No credentials found in XZen settings, user galleries disabled)")


def BuildUserGallery(zen,group=None):

    global KEYRINGED

    if group is None:
        #load the album hierchy for the user
        #load the cover photos
        #add the links
        h = zen.LoadGroupHierarchy()
##        log("$$$ H Access is " + str(h.AccessDescriptor))
##        if KEYRINGED == False and h.AccessDescriptor['AccessType'] == 'Password':
##            log("Global User Keyring")
##            zen.KeyringAddKeyPlain(realmId= h.AccessDescriptor['RealmId'],password="jessie")
##            KEYRINGED=True

    else:
        #loading a specific group
        h = zen.LoadGroup(group, includeChildren=True)


    for element in h.Elements:
        log("Access is: " + str(element.AccessDescriptor))
        if isinstance(element,PhotoSet):
            log("Add PhotoSet Thumb: " + str(element.Id))
            AddPhotoSetThumb(element,len(h.Elements))
        elif isinstance(element,Group):
            log("Add Group Thumb: " + str(element.Id))
            AddGroupThumb(element)
        elif isinstance(element,Photo):
            log("Add Photo Thumb: " + str(element.Id))
            AddPhotoThumb(element)
        else:
            log("Did not add, not sure what this is: " + element.__name__)


def BuildMenuPopSets(zen,type="Gallery",offset=0,limit=14):
    if type=="Gallery": AddNextPageLink(POPGALLERIES,offset+limit)
    else: AddNextPageLink(POPCOLLECTIONS,offset+limit)
    photosets = zen.GetPopularSets(type,offset,limit)
    for photoset in photosets:
        AddPhotoSetThumb(photoset,len(photosets))

def ShowPopularPhotos(zen,offset=0, limit=14):
    #first add a next page link for quick browsing
    AddNextPageLink(POPPHOTOS,offset+limit)

    #now add the photos of this page
    photos = zen.GetPopularPhotos(offset,limit)
    for photo in photos:
        AddPhotoThumb(photo,len(photos))

def BuildMenuRecentSets(zen,type="Gallery",offset=0,limit=14):
    if type=="Gallery": AddNextPageLink(RECENTGALLERIES,offset+limit)
    else: AddNextPageLink(RECENTCOLLECTIONS,offset+limit)
    photosets = zen.GetRecentSets(type,offset,limit)
    for photoset in photosets:
        AddPhotoSetThumb(photoset,len(photosets))


def AddCategory(category,code,numberOfItems=0):
    url = buildPluginURL({'mode':CATEGORIES,'category':code})
    item=xbmcgui.ListItem(category['DisplayName'],url,'','')
    xbmcplugin.addDirectoryItem(THIS_PLUGIN,url,item,True,numberOfItems)


def frontPadTo9Chars(shortStr):
    while len(shortStr)<9:
        shortStr = "0" + shortStr
    return shortStr

def BuildMenuCategories(zen,parentCode=None):
    categoriesList = zen.GetCategories()
    log(str(categoriesList))
    if parentCode is None:
        log("Parent Code None")
    else:
        parentCode = frontPadTo9Chars(parentCode)
        log("Parent Code incoming is: " + parentCode)

    #category = X000000
    # subcategory = XXXX000
    #   subsubcategory = XXXXXXXXX

    for category in categoriesList:

        #get the code as a string and pad it to the orignal 12 characters
        strCode = str(category['Code'])
        strCode = frontPadTo9Chars(strCode)

        if parentCode is not None:
            log("Seeing if we're adding " + category['DisplayName'] + " code is " + strCode + " and parentCode is: "+ parentCode)
            log("PC " + parentCode[:3] + " SC " + strCode[:3] + " SCL3 " + strCode[-3:])
        else:
            log("Seeing if we're adding " + category['DisplayName'] + " code is " + strCode + " and parentCode is: None")

        if parentCode is None and strCode[-6:]=="000000":
            #this is a parent category as it ends  in 000000
            AddCategory(category,strCode)
        elif parentCode is not None and parentCode!=strCode and parentCode[:3] == strCode[:3] and strCode[-3:]=="000":
            #we have a parent code and it is a category, so we are dealing with sub categories - check if all but the last three chars match
            AddCategory(category,strCode)
        elif parentCode is not None and parentCode!=strCode and parentCode[:6]==strCode[:6] and strCode[-3:]!="000":
            #ok we have a sub-sub category
            AddCategory(category,strCode)
        else:
            pass


##    #build the categories lists
##    stub = '100'
##    for category in categoriesList:
##        #Each category is {u'$type': u'Category', u'Code': 1000000, u'DisplayName': u'Animals'}
##        code = str(category['Code'])
##        if code.startswith(stub):
##           log("Category Group " + category['DisplayName'])
##        #move to the next stub
##        else:
##            log("**** Found new group")
##            stub = code[:3]

#    for category in categoriesList:
#        AddCategory(category,len(categoriesList))

def ShowRecentPhotos(zen,offset=0, limit=14):
    #first add a next page link for quick browsing
    AddNextPageLink(RECENTPHOTOS,offset+limit)

    #now add the photos of this page
    photos = zen.GetRecentPhotos(offset,limit)
    for photo in photos:
        AddPhotoThumb(photo,len(photos))



################################################################################
################################################################################
# MAIN
################################################################################
################################################################################

#ok we're firing up
footprints()

#get the settings & parameters
username=ADDON.getSetting('username')
password=ADDON.getSetting('password')
params=get_params()
log("Parameters parsed: " + str(params))


#LIST MODES
MENU_ROOT = "MENU_ROOT"
CATEGORIES = "CATEGORIES"
CATEGORY_OPTIONS = "CATEGORY_OPTIONS"

#GALLERY MODES
MENU_USERGALLERIES = "MENU_USERGALLERIES"
POPPHOTOS = "POPPHOTOS"
POPGALLERIES = "POPGALLERIES"
POPCOLLECTIONS = "POPCOLLECTIONS"
DISPLAY_GALLERY = "DISPLAY_GALLERY"
RECENTPHOTOS = "RECENTPHOTOS"
RECENTGALLERIES = "RECENTGALLERIES"
RECENTCOLLECTIONS = "RECENTCOLLECTIONS"

#Zenfolio Quality Levels for Images
ZEN_DOWNLOAD_QUALITY = {
                    "ProtectXXLarge" : 6,
                    "ProtectExtraLarge" :5 ,
                    "ProtectLarge" :4,
                    "ProtectMedium" :3
}

ZEN_URL_QUALITY ={
                    "Small thumbnail" : 0,      #Small thumbnail (up to 80 x 80)
                    "Square thumbnail": 1,      #Square thumbnail (60 x 60, cropped square)
                    "Small": 2,                 #Small (up to 400 x 400)
                    "Medium": 3,                #Medium (up to 580 x 450)
                    "Large" : 4,                #Large (up to 800 x 630)
                    "X-Large" : 5,              #X-Large (up to 1100 x 850)
                    "XX-Large" : 6,             #XX-Large (up to 1550 x 960)
                    "Medium thumbnail" : 10,    #Medium thumbnail (up to 120 x 120)
                    "Large thumbnail" : 11      #Large thumbnail (up to 120 x 120)
}

#these modes use the thumbnail view (for playable items)
galleryModes = [\
                MENU_USERGALLERIES,\
                DISPLAY_GALLERY,\
                POPPHOTOS,\
                POPGALLERIES,\
                POPCOLLECTIONS,\
                RECENTPHOTOS,\
                RECENTGALLERIES,\
                RECENTCOLLECTIONS,\
              ]


#zero out data between passes
mode = None
url = None
galleryid=None
group=None
category=None

#try and get data from the paramters
try:
    url=urllib.unquote_plus(params["url"])
except:
    pass

try:
    galleryid=int(params["galleryid"])
except:
    pass

try:
    mode=params["mode"]
except:
    pass

try:
    group=int(params["group"])
except:
    pass

try:
    category=params["category"]
except:
    pass


#if we're paging groups of photos, what is the starting offset?
offset=0
try:
    offset=int(params["offset"])
except:
    pass


#connect to ZenFolio
AUTHENTICATED=False
KEYRINGED=False

zen = ZenConnection(username = username, password = password)
if zen is None:
    notify("Couldn't connect to Zenfolio!!")
    sys.exit()

#try and authenticate, although we can do a lot without this
try:
    AUTH=zen.Authenticate()
    AUTHENTICATED=True
except:
    #if in the root menu the first time, let them know this is just a public browsing session....
    if mode==None:
        notify("Zenfolio Authentication not completed","(Can still browse public galleries etc.)")

#OK the mode variable controls what we're actually doing...
if mode==None or mode==MENU_ROOT:
  log( "Display XZen Root Menu" )
  try:
      BuildMenuRoot(zen)
  except:
      print_exc()

elif mode==MENU_USERGALLERIES:
    #loading the root menu
    try:
        if group is None:
            log( "Display XZen User Gallery Root" )
            BuildUserGallery(zen)
        else:
            log( "Display XZen User Gallery Group/Collection: " + str(group) )
            BuildUserGallery(zen,group)
    except:
          print_exc()

elif mode==POPPHOTOS:
  log( "Display XZen Popular Photos")
  try:
      ShowPopularPhotos(zen,offset)
  except:
      print_exc()

elif mode==POPGALLERIES:
  log( "Display XZen Popular Galleries")
  try:
      BuildMenuPopSets(zen,"Gallery",offset)
  except:
      print_exc()

elif mode==POPCOLLECTIONS:
  log( "Display XZen Popular Collections")
  try:
      BuildMenuPopSets(zen,"Collection", offset)
  except:
      print_exc()

elif mode==RECENTPHOTOS:
  log( "Display XZen Recent Photos")
  try:
      ShowRecentPhotos(zen,offset)
  except:
      print_exc()

elif mode==RECENTGALLERIES:
  log( "Display XZen Recent Galleries")
  try:
      BuildMenuRecentSets(zen,"Gallery",offset)
  except:
      print_exc()

elif mode==RECENTCOLLECTIONS:
  log( "Display XZen Recent Collections")
  try:
      BuildMenuRecentSets(zen,"Collection", offset)
  except:
      print_exc()

elif mode==CATEGORIES:
  log( "Display XZen Categories")
  try:
      BuildMenuCategories(zen,category)
  except:
      print_exc()

elif mode==DISPLAY_GALLERY:
  log( "Display XZen Gallery id: " + str (galleryid) )
  try:
      AddGallery(zen,galleryid)
  except:
      print_exc()



else:
  notify("Shouldn't have got here - a mode was passed, without a matching action!")
  sys.exit()


#if we've just built a list of albums, force thumbnail mode
if mode in galleryModes:
  log("Playable Items -> Trying to set thumnbnail mode...")
  xbmc.executebuiltin('Container.SetViewMode(500)')
else:
  log("List Items -> Trying to set list mode...")
  xbmc.executebuiltin('Container.SetViewMode(50)')

#and tell XBMC we're done...
xbmcplugin.endOfDirectory(THIS_PLUGIN)

#and power this puppy down....
footprints(startup=False)




