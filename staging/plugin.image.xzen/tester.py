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
from time import time
import logging
logging.basicConfig(level=logging.DEBUG)
from pprint import pprint

#some handy stuff
#from b808common import *

#uses zenapi by Scott Gorling (http://www.scottgorlin.com)
from zenapi import ZenConnection
from zenapi.snapshots import Group, PhotoSet
from zenapi.updaters import PhotoSetUpdater, GroupUpdater

#ok we're firing up
#footprints()

#get the settings
#username=ADDON.getSetting('username')
#password=ADDON.getSetting('password')
username = "Daalders"
password = "pubcas!!"

#connect to ZenFolio
zen = ZenConnection(username = username, password = password)
zen.Authenticate()

logging.info(str(zen))

if zen is not None:
    #load the album hierchy for the user
    h = zen.LoadGroupHierarchy()
    pprint(vars(h))

    #load the group
    #g = zen.LoadGroup(h)
    #p = zen.LoadPhotoSet(g)
    #print("Group: " + str(g))
    print("Group List: " + str(h.Elements))
    for element in h.Elements:
      if isinstance(element,PhotoSet):
        print("****************  Found a Photoset!! " + str(element))
        pprint(vars(element))
        ps = zen.LoadPhotoSet(element.Id, includePhotos=True)
        pprint(vars(ps))
        for photoElement in ps.Photos:
          photo = zen.LoadPhoto(photoElement.Id)
          pprint(vars(photo))
          break

      break

else:
    logging.warning("**** ZEN IS NONE!!")

#and tell XBMC we're done...
#xbmcplugin.endOfDirectory(THIS_PLUGIN)

#and power this puppy down....
#footprints(startup=False)


