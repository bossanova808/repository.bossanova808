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
from time import time
from pprint import pprint
#some handy stuff
from b808common import *
#uses zenapi by Scott Gorling (http://www.scottgorlin.com)
from zenapi import ZenConnection
from zenapi.snapshots import Group, PhotoSet

################################################################################
# Photo/Set Loaders

#add thumb that links to a set of photos
def AddPhotoSetThumb(photoSet, numberOfItems=0):
    try:
        titlePhoto = zen.LoadPhoto(photoSet.TitlePhoto,'Level1')
        urlTitlePhoto = titlePhoto.getUrl(10)

        if photoSet.Title is None:
            title="Untitled"
        else:
            title = unquoteUni(photoSet.Title)

        url = buildPluginURL({"mode":DISPLAY_GALLERY, "galleryid":str(photoSet.Id)})
        item=xbmcgui.ListItem(title,url,urlTitlePhoto,urlTitlePhoto)
        xbmcplugin.addDirectoryItem(THIS_PLUGIN,url,item,True,numberOfItems)

    except Exception as inst:
        log("AddPhotoSetThumb - Exception!", inst)

#Add thumb that links to an individual photo
def AddPhotoThumb(photo, numberOfItems=0):
    try:

        #be optimistic....
        url = photo.getUrl(6)
        #temper it with realism....
        if 'ProtectMedium' not in photo.AccessDescriptor['AccessMask']:
            url = photo.getUrl(3)
        if 'ProtectLarge' not in photo.AccessDescriptor['AccessMask']:
            url = photo.getUrl(4)
        if 'ProtectExtraLarge' not in photo.AccessDescriptor['AccessMask']:
            url = photo.getUrl(5)
        if 'ProtectXXLarge' not in photo.AccessDescriptor['AccessMask']:
            url = photo.getUrl(6)

        urlThumb = photo.getUrl(10)

        if photo.Title is None:
            title="Untitled"
        else:
            title = unquoteUni(photo.Title)

        log("AddPhotoThumb: [" + str(photo.Id) + "] title: [" + str(title) + "] url: [" +str(url) + "] urlThumb: [" + str(urlThumb) +"]")

        item=xbmcgui.ListItem(title,str(url),'',str(urlThumb),'')
        xbmcplugin.addDirectoryItem(THIS_PLUGIN,url,item,False,numberOfItems)

    except Exception as inst:
        log("AddPhotoThumb - Exception!", inst)

#Given a gallery ID, add all the thumbs
def AddGallery(zen,galleryid):
    ps = zen.LoadPhotoSet(galleryid, 'Level1',includePhotos=True)
    for photo in ps.Photos:
        AddPhotoThumb(photo,len(ps.Photos))

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
    BuildMenuRootItem(MENU_USERGALLERIES            ,"User Galleries")
    BuildMenuRootItem(RECENTPHOTOS                  ,"Recent Photos")
    BuildMenuRootItem(RECENTGALLERIES               ,"Recent Galleries")
    BuildMenuRootItem(RECENTCOLLECTIONS             ,"Recent Collections")
    BuildMenuRootItem(POPPHOTOS                     ,"Popular Photos")
    BuildMenuRootItem(POPGALLERIES                  ,"Popular Galleries")
    BuildMenuRootItem(POPCOLLECTIONS                ,"Popular Collections")

def BuildMenuUserGallery(zen):
    #load the album hierchy for the user
    #load the cover photos
    #add the links
    h = zen.LoadGroupHierarchy()
    for element in h.Elements:
      AddPhotoSetThumb(element,len(h.Elements))

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

def ShowRecentPhotos(zen,offset=0, limit=14):
    #first add a next page link for quick browsing
    AddNextPageLink(RECENTPHOTOS,offset+limit)

    #now add the photos of this page
    photos = zen.GetRecentPhotos(offset,limit)
    for photo in photos:
        AddPhotoThumb(photo,len(photos))


#ok we're firing up
footprints()

#get the settings & parameters
username=ADDON.getSetting('username')
password=ADDON.getSetting('password')
params=get_params()
log("Parameters parsed: " + str(params))


#MENU MODES
MENU_ROOT = "MENU_ROOT"

#GALLERY MODES
MENU_USERGALLERIES = "MENU_USERGALLERIES"
POPPHOTOS = "POPPHOTOS"
POPGALLERIES = "POPGALLERIES"
POPCOLLECTIONS = "POPCOLLECTIONS"
DISPLAY_GALLERY = "DISPLAY_GALLERY"
RECENTPHOTOS = "RECENTPHOTOS"
RECENTGALLERIES = "RECENTGALLERIES"
RECENTCOLLECTIONS = "RECENTCOLLECTIONS"


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

#if we're paging groups of photos, what is the starting offset?
offset=0
try:
    offset=int(params["offset"])
except:
    pass


#connect to ZenFolio
zen = ZenConnection(username = username, password = password)
if zen is None:
    notify("Couldn't connect to Zenfolio!!")
    sys.exit()

#try and authenticate, although we can do a lot without this
try:
    zen.Authenticate()
except:
    notify("Zenfolio Authentication not completed","(Can still browse public galleries etc.)")

#OK the mode variable controls what we're actually doing...
if mode==None or mode==MENU_ROOT:
  log( "Display XZen Root Menu" )
  try:
      BuildMenuRoot(zen)
  except:
      print_exc()

elif mode==MENU_USERGALLERIES:
  log( "Display XZen User Galleries" )
  try:
      BuildMenuUserGallery(zen)
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




