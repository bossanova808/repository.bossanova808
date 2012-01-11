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

 
import os, sys, urllib, urllib2, socket
import xbmc, xbmcvfs, xbmcgui, xbmcaddon
import CommonFunctions
import re

# plugin constants
version = "0.1.1"
plugin = "OzWeather-" + version
author = "Bossanova808"
url = "www.bossanova808.net"

#parseDOM setup
dbg = True # Set to false if you don't want debugging
dbglevel = 3 # Do NOT change from 3
common = CommonFunctions.CommonFunctions()
common.plugin = plugin

#addon setup
__addon__      = xbmcaddon.Addon()
__provider__   = __addon__.getAddonInfo('name')
__cwd__        = __addon__.getAddonInfo('path')
__resource__   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib'))
sys.path.append (__resource__)

#import the tables that map conditions to icon number and short days to long days
from utilities import *

#Constants
WEATHER_WINDOW  = xbmcgui.Window(12600)
WeatherZoneURL = 'http://www.weatherzone.com.au'


def set_property(name, value):
    WEATHER_WINDOW.setProperty(name, value)

def refresh_locations():
    location_set1 = __addon__.getSetting('Location1')
    location_set2 = __addon__.getSetting('Location2')
    location_set3 = __addon__.getSetting('Location3')
    locations = 0
    if location_set1 != '':
        locations += 1
        set_property('Location1', location_set1)
    else:
        set_property('Location1', '')
    if location_set2 != '':
        locations += 1 
        set_property('Location2', location_set2)
    else:
        set_property('Location2', '')
    if location_set3 != '':
        locations += 1
        set_property('Location3', location_set3)
    else:
        set_property('Location3', '')
    set_property('Locations', str(locations))

def forecast(url):
    #build the data urllib
    print 'Getting weather from ', url
    data = common._fetchPage({"link":url})
    if data != '':
       radarURL, satelliteURL = propertiesPDOM(data["content"])
    #ok now we want to build the radar
    buildImages(radarURL, satelliteURL)
    
def buildImages(radarURL, satelliteURL):

    return
    
    
       
def striplist(l, chars):
    return([x.strip(chars) for x in l])
        
def propertiesPDOM(page):

    #pull data from the current observations table
    ret = common.parseDOM(page, "div", attrs = { "class": "details_lhs" })
    observations = common.parseDOM(ret, "td", attrs = { "class": "hilite bg_yellow" }) 
    #Observations now looks like - ['18.3&deg;C', '4.7&deg;C', '18.3&deg;C', '41%', 'SSW 38km/h', '48km/h', '1015.7hPa', '-', '0.0mm / -']   
    temperature = str.strip(observations[0], '&deg;C')
    dewPoint = str.strip(observations[1], '&deg;C')
    feelsLike = str.strip(observations[2], '&deg;C')
    humidity = str.strip(observations[3], '%')
    windTemp = observations[4].partition(' ');
    windDirection = windTemp[0]
    windSpeed = str.strip(windTemp[2], 'km/h')
    #there's no UV so we get that from the forecast, see below
 
    #pull the basic data from the forecast table  
    ret = common.parseDOM(page, "div", attrs = { "class": "boxed_blue_nopad" })
    #create lists of each of the maxes, mins, and descriptions
    #Get the days UV in text form like 'Extreme' and number '11'
    UVchunk = common.parseDOM(ret, "td", attrs = { "style": "text-align: center;" })
    UVtext = common.parseDOM(UVchunk, "span")
    UVnumber = common.parseDOM(UVchunk, "span", ret = "title")
    UV = UVtext[0] + ' (' + UVnumber[0] + ')'
    #get the 7 day max min forecasts
    maxMin = common.parseDOM(ret, "td", attrs = { "title": "source: BoM" })
    maxList = striplist(maxMin[-21:-14],'&deg;C');
    minList = striplist(maxMin[-14:-7],'&deg;C');
    #and the short forecasts
    shortDesc = common.parseDOM(ret, "td", attrs = { "class": "bg_yellow" })
    shortDesc = common.parseDOM(ret, "span", attrs = { "style": "font-size: 0.9em;" })
    shortDesc = shortDesc[0:7]
    for count, desc in enumerate(shortDesc):
      shortDesc[count] = str.replace(shortDesc[count], '-<br />','')
      #shortDesc[count] = str.replace(shortDesc[count], '<br />','')
    
    #and the names of the days
    days = common.parseDOM(ret, "span", attrs = { "style": "font-size: larger;" })
    days = common.parseDOM(ret, "span", attrs = { "class": "bold" })
    days = days[0:7]
    for count, day in enumerate(days):
        days[count] = DAYS[day]
 
    #get the longer current forecast for the day
    # or jsut use the short one if this is disabled in settings
    useLong = __addon__.getSetting('LongForecastToggle')
    if useLong == "true":
        longDayCast = common.parseDOM(page, "div", attrs = { "class": "top_left" })
        #print '@@@@@@@@@ Long 1', longDayCast
        longDayCast = common.parseDOM(longDayCast, "p" )
        #print '@@@@@@@@@ Long 2', longDayCast
        #new method - just strip the crap (e.g. tabs) out of the string and use a colon separator for the 'return' as we don't have much space
        longDayCast = common.stripTags(longDayCast[0])
        #print longDayCast       
        longDayCast = str.replace(longDayCast, '\t','')
        longDayCast = str.replace(longDayCast, '\r',' ')
        #print '@@@@@@@@@ Long 4', longDayCast    
        longDayCast = longDayCast[:-1]
        longDayCast = longDayCast + " fire danger." 
        
        """
            Old Methdod - split the string on the weird tabs and work on the parts separately        
                chunks = longDayCast[0].partition('\t\t\t\t')
                print '@@@@@@@@@ Long 3', chunks        
                longDayCast = common.stripTags(chunks[0]) + ': ' +common.stripTags(chunks[2])
                longDayCast = str.replace(longDayCast, '\t','')
                longDayCast = str.replace(longDayCast, '\r','')
                print '@@@@@@@@@ Long 4', longDayCast    
        """
        
    else:
        longDayCast = shortDesc[0]

 
    #if for some reason the codes change return a neat 'na' response
    try:
        weathercode = WEATHER_CODES[shortDesc[0]]   
    except:
        weathercode = 'na'
    
    #now set all the XBMC properties
    set_property('Current.Condition'     , longDayCast)
    set_property('Current.Temperature'   , temperature)
    set_property('Current.Wind'          , windSpeed)
    set_property('Current.WindDirection' , windDirection)
    set_property('Current.Humidity'      , humidity)
    set_property('Current.FeelsLike'     , feelsLike)
    set_property('Current.DewPoint'      , dewPoint)
    set_property('Current.UVIndex'       , UV)
    set_property('Current.OutlookIcon'   , '%s.png' % weathercode)
    set_property('Current.FanartCode'    , weathercode)
    for count, desc in enumerate(shortDesc):
        try:
            weathercode = WEATHER_CODES[shortDesc[count]]
        except:
            weathercode = 'na'
        
        day = days[count]
        set_property('Day%i.Title'       % count, day)
        set_property('Day%i.HighTemp'    % count, maxList[count])
        set_property('Day%i.LowTemp'     % count, minList[count])
        set_property('Day%i.Outlook'     % count, desc)
        set_property('Day%i.OutlookIcon' % count, '%s.png' % weathercode)
        set_property('Day%i.FanartCode'  % count, weathercode)
        if count == 3:
            break                
    
    #get the URLS and return them
    radarURL = WeatherZoneURL + (common.parseDOM(page, "a", attrs = { "id": "animator_rad_link" }, ret="href" ))[0]
    satelliteURL = WeatherZoneURL + (common.parseDOM(page, "a", attrs = { "id": "animator_sat_link" }, ret="href" ))[0]
    print "~~~~~~~~~~~~ RADAR URL " + radarURL + ' ~~~~~~~~~ SATELLITE URL ' + satelliteURL
    return radarURL, satelliteURL
    
##############################################
### NOW RUN THIS PUPPY    

socket.setdefaulttimeout(10)      

#being called from the settings section where they choose their postcodes    
if sys.argv[1].startswith('Location'):
    keyboard = xbmc.Keyboard('', xbmc.getLocalizedString(14024), False)
    keyboard.doModal()
    if (keyboard.isConfirmed() and keyboard.getText() != ''):
        text = keyboard.getText()

        #need to submit the postcode to the weatherzone search
        searchURL = 'http://weatherzone.com.au/search/'
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        host = 'www.weatherzone.com.au'
        headers = { 'User-Agent' : user_agent, 'Host' : host }
        values = {'q' : text, 't' : '3' }
        data = urllib.urlencode(values)
        req = urllib2.Request(searchURL, data, headers)
        response = urllib2.urlopen(req)
        resultPage = str(response.read())
        #was there only one match?  If so it returns the page for that match so we need to check the URL
        responseurl = response.geturl()
        if responseurl != 'http://weatherzone.com.au/search/':
            #we were redirected to an actual result page
            locationName = common.parseDOM(resultPage, "h1", attrs = { "class": "unenclosed" })
            locationName = str.split(locationName[0], ' Weather')
            locations = [locationName[0] + ', ' + text]
            locationids = [responseurl]
        else:        
            #we got back a page to choose a more specific location
            skimmed = common.parseDOM(resultPage, "ul", attrs = { "class": "typ2" })
            #ok now get two lists - one of the friendly names
            #and a matchin one of the URLs to store
            locations = common.parseDOM(skimmed[0], "a")
            templocs = common.parseDOM(skimmed[0], "a", ret="href")
            #build the full urls
            locationids = []
            for count, loc in enumerate(templocs):
                locationids.append(WeatherZoneURL + loc)
            #if we did not get enough data back there are no locations with this postcode 
            if len(skimmed)<=1:
                locations = []
                locationids = []
      
        #now get them to choose an actual location
        dialog = xbmcgui.Dialog()
        if locations != []:
            selected = dialog.select(xbmc.getLocalizedString(396), locations)
            if selected != -1: 
                __addon__.setSetting(sys.argv[1], locations[selected])
                __addon__.setSetting(sys.argv[1] + 'id', locationids[selected])
        else:
            dialog.ok(__provider__, xbmc.getLocalizedString(284))


#script is being called in general use, not from the settings page            
#get the currently selected location and grab it's forecast
else:
    location = __addon__.getSetting('Location%sid' % sys.argv[1])
    forecast(location)

refresh_locations()
set_property('WeatherProvider', 'BOM Australia via WeatherZone')

