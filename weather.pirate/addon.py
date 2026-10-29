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

# Pirate Weather 10.24.2026

import os, sys, socket, urllib
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import time
import json
import requests
import urllib.parse

s = requests.Session()

from resources.lib.convert_to_local import *
from resources.lib.logger import *

# This is a throwaway variable to deal with a python bug
throwaway = time.strptime('20110101','%Y%m%d')

__addon__      = xbmcaddon.Addon()
__addonname__  = __addon__.getAddonInfo('name')
__addonid__    = __addon__.getAddonInfo('id')
__version__    = __addon__.getAddonInfo('version')
__cwd__        = __addon__.getAddonInfo('path')##.decode("utf-8")
__resource__   = xbmcvfs.translatePath( os.path.join( __cwd__, 'resources', 'lib' ).encode("utf-8") )##.decode("utf-8")

sys.path.append(__resource__)

from utilities import *

LOC_URL          = 'https://nominatim.openstreetmap.org/search?addressdetails=1&q=%s&format=jsonv2'
API_URL          = 'https://api.pirateweather.net/forecast/'
API_KEY	= __addon__.getSetting(id="API_KEY")
WEATHER_ICON     = xbmcvfs.translatePath('special://temp/weather/%s.png')##.decode("utf-8")
WEATHER_WINDOW   = xbmcgui.Window(12600)
NOW = time.time()
LOCAL_TIME = time.localtime(NOW)
HOUR = time.strftime("%H", LOCAL_TIME)
TODAY = time.strftime("%A", LOCAL_TIME)

socket.setdefaulttimeout(10)


def set_property(name, value):
	WEATHER_WINDOW.setProperty(name, value)

def refresh_locations():
	locations = 0
	for count in range(1, 6):
		loc_name = __addon__.getSetting('Location%s' % count)
		if loc_name != '':
			locations += 1
		set_property('Location%s' % count, loc_name)
	set_property('Locations', str(locations))
	log(f"available locations:{locations}",xbmc.LOGDEBUG)

def location(loc):
	items  = []
	locs   = []
	locids = []
	data = find_location(loc)
	total = len(data)
	if total == 0:
		dialog = xbmcgui.Dialog()
		ok = dialog.ok('Kodi', 'No results found.')
		pass
	log('TOTAL: ' + str(total),xbmc.LOGDEBUG)
	cities = []; lls = []
	for i in range(total):
		location = data[i]['display_name']
		lat = data[i]['lat']
		lng = data[i]['lon']
		locationid = str(lat) + ',' + str(lng)
		items.append(location)
		locs.append(location)
		locids.append(locationid)
	return items, locs, locids

def find_location(loc):
	query = urllib.parse.quote(loc)
	log('QUERY: ' + str(query),xbmc.LOGDEBUG)
	url = LOC_URL % query
	log(f"URL: {url}",xbmc.LOGDEBUG)
	headers = {'User-Agent':'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:44.0) Gecko/20100101 Firefox/50.0','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'}

	response = s.get(url, headers=headers)
	if response.status_code == 200:
		data = response.json()
		log(f"DATA: {data}",xbmc.LOGDEBUG)
	else:
		log(f"HTTP: {response.status_code}",xbmc.LOGERROR)
	return data

def parse_data(reply):
	try:
		data = json.loads(reply)
	except:
		log('failed to parse weather data',xbmc.LOGDEBUG)
		data = ''
	return data

def forecast(loc,locid):
	retry = 0
	while (retry < 6) and (not xbmc.Monitor().abortRequested()):
		query = get_forecast(locid)
		if query != '':
			retry = 6
		else:
			retry += 1
			xbmc.sleep(10000)
			log('forecast download failed',xbmc.LOGDEBUG)
	log('forecast data: %s' % query,xbmc.LOGDEBUG)
	if query != '':
		properties(query,loc,locid)
	else:
		clear()

def get_forecast(locid):
	log('GET FORECAST',xbmc.LOGINFO)
	url = API_URL + API_KEY + '/' + str(locid) + '?version=2&units=si&icon='
	log('GET FORECAST URL:' + str(url),xbmc.LOGDEBUG)
	try:
		response = requests.get(url, timeout=15)
		response.raise_for_status()
		data = response.json()
		log(f"RESPONSE: {response.status_code}",xbmc.LOGDEBUG)
		fdata = response.json()
		#req.close()
	except:
		log('EXCEPTION!',xbmc.LOGDEBUG)
		response = ''
	return fdata

def clear():
	log('CLEAR',xbmc.LOGDEBUG)
	set_property('Current.Condition'     , 'N/A')
	set_property('Current.Temperature'   , '0')
	set_property('Current.Wind'          , '0')
	set_property('Current.WindDirection' , 'N/A')
	set_property('Current.Humidity'      , '0')
	set_property('Current.FeelsLike'     , '0')
	set_property('Current.UVIndex'       , '0')
	set_property('Current.DewPoint'      , '0')
	set_property('Current.OutlookIcon'   , 'na.png')
	set_property('Current.FanartCode'    , 'na')
	for count in range (0, 7):
		set_property('Day%i.Title'       % count, 'N/A')
		set_property('Daily%i.Title'       % count, 'N/A')
		set_property('Day%i.HighTemp'    % count, '0')
		set_property('Day%i.LowTemp'     % count, '0')
		set_property('Day%i.Outlook'     % count, 'N/A')
		set_property('Day%i.OutlookIcon' % count, 'na.png')
		set_property('Daily%i.OutlookIcon' % count, 'na.png')
		set_property('Day%i.FanartCode'  % count, 'na')

def properties(data,loc,locid):
	log('PROPERTIES',xbmc.LOGDEBUG)
	weathercode = WEATHER_CODES[(data['currently']['icon'])]
	log('LOC: ' + str(loc),xbmc.LOGDEBUG)
	log('LOCATION: ' + str(location),xbmc.LOGDEBUG)
	log('LOCATIONID: ' + str(locationid),xbmc.LOGDEBUG)
	set_property('Current.Location'      , loc)
	set_property('Current.Condition'     , data['currently']['summary'])
	set_property('Current.Temperature'   , str(data['currently']['temperature']))
	set_property('Current.Wind'          , str(data['currently']['windSpeed']))
	set_property('Current.WindDirection' , bearing_to_direction(data['currently']['windBearing']))
	set_property('Current.WindChill'     , str(data['currently']['apparentTemperature']))
	set_property('Current.Humidity'      , str(data['currently']['humidity']).replace('0.',''))
	set_property('Current.Visibility'    , str(data['currently']['visibility']))
	set_property('Current.Pressure'      , str(data['currently']['pressure']))
	set_property('Current.FeelsLike'     , str(data['currently']['apparentTemperature']))
	set_property('Current.DewPoint'      , str(data['currently']['dewPoint']))
	set_property('Current.UVIndex'       , str(round(data['currently']['uvIndex'])))
	set_property('Current.Precipitation' , str(round(data['currently']['precipProbability'])) + '%')
	set_property('Current.OutlookIcon'   , '%s.png' % weathercode)
	set_property('Current.FanartCode'   , '%s.png' % weathercode)
	#forecast = parse_data(data)
	sunrise = (data['daily']['data'][0]['sunriseTime'])
	sunset = (data['daily']['data'][0]['sunsetTime'])
	log('SUNRISE: ' + str(time.strftime("%H:%M", time.localtime(int(sunrise)))),xbmc.LOGDEBUG)
	set_property('Today.Sunrise'         , str(time.strftime("%H:%M", time.localtime(int(sunrise)))))
	set_property('Today.Sunset'          , str(time.strftime("%H:%M", time.localtime(int(sunset)))))
	set_property('Today.IsFetched', 'true')
	log('HOUR: ' + str(HOUR),xbmc.LOGDEBUG)
	for day, item in enumerate(data['daily']['data']):
		fdate = str(data['daily']['data'][day]['time'])
		fday = format_unix_time_kodi(fdate)
		log('FDAY: ' + str(fday),xbmc.LOGDEBUG)
		title = fday.split(' ')[0]
		if day == 0:
			title = 'Today'
		log('TITLE: ' + str(title),xbmc.LOGDEBUG)		
		set_property('Daily.%i.ShortDate'     % (day + 1), f"[B]{title}[/B]")		
		set_property('Day%i.Title'     % day, f"[B]{title}[/B]")
		#set_property('Daily%i.Title'     % day, str(title))
		#set_property('Daily%i.Outlook'     % day, str(data['daily']['data'][day]['summary']))
		weathercode = WEATHER_CODES[(data['daily']['data'][day]['icon'])]
		set_property('Daily.%i.OutlookIcon' % (day + 1), '%s.png' % weathercode)
		set_property('Day%i.OutlookIcon' % day, '%s.png' % weathercode)
		log('WEATHER_CODE: ' + str(weathercode),xbmc.LOGDEBUG)
		log('ICON: ' + str(data['daily']['data'][day]['icon']),xbmc.LOGDEBUG)
		set_property('Daily.%i.HighTemperature'    % (day + 1), str(format_temp(data['daily']['data'][day]['temperatureHigh'])))
		set_property('Daily.%i.LowTemperature'     % (day + 1), str(format_temp(data['daily']['data'][day]['temperatureLow'])))
		set_property('Day%i.HighTemp'    % day, str(format_temp(data['daily']['data'][day]['temperatureHigh'])))
		set_property('Day%i.LowTemp'     % day, str(format_temp(data['daily']['data'][day]['temperatureLow'])))
		set_property('Daily.%i.Outlook'     % (day + 1), str(data['daily']['data'][day]['summary']))
		set_property('Day%i.Outlook'     % day, str(data['daily']['data'][day]['summary']))
		set_property('Daily.%i.WindSpeed'     % (day + 1), str(format_speed(data['daily']['data'][day]['windSpeed'])))
		set_property('Daily.%i.WindGust'     % (day + 1), str(format_speed(data['daily']['data'][day]['windGust'])))
		set_property('Daily.%i.WindDirection'     % (day + 1), degToCompass(data['daily']['data'][day]['windBearing']))
		set_property('Daily.%i.Precipitation'     % (day + 1), str(round(data['hourly']['data'][day]['precipProbability'])) + '%')
		sunrise = (data['daily']['data'][day]['sunriseTime'])
		sunset = (data['daily']['data'][day]['sunsetTime'])
		log('SUNRISE: ' + str(time.strftime("%H:%M", time.localtime(int(sunrise)))),xbmc.LOGDEBUG)
		set_property('Daily.%i.Sunrise'         , str(time.strftime("%H:%M", time.localtime(int(sunrise)))))
		set_property('Daily.%i.Sunset'          , str(time.strftime("%H:%M", time.localtime(int(sunset)))))
		set_property('Forecast.IsFetched', 'true')
		set_property('Day.IsFetched', 'true')
		set_property('Daily.IsFetched', 'true')
		WEATHER_WINDOW.setProperty('Refresh', '1')

	for hour, item in enumerate(data['hourly']['data']):
		title = format_unix_time_kodi(data['hourly']['data'][hour-1]['time']).split(' ')[-1]
		if title != '00:00':
			title = title.lstrip('0')
		hdate = title.rsplit(' ')[0]
		set_property('Hourly.%i.ShortDate'     % hour, format_unix_time_kodi(data['hourly']['data'][hour-1]['time']).split(' ')[0])
		set_property('Hourly.%i.Time'     % hour, str(title))
		set_property('Hourly.%i.Temperature'    % hour, str(format_temp(data['hourly']['data'][hour-1]['temperature'])))
		set_property('Hourly.%i.Outlook'     % hour, str(data['hourly']['data'][hour-1]['summary']))
		set_property('Hourly.%i.WindGust'     % hour, str(format_speed(data['hourly']['data'][hour-1]['windGust'])))
		set_property('Hourly.%i.WindSpeed'     % hour, str(format_speed(data['hourly']['data'][hour-1]['windSpeed'])))
		set_property('Hourly.%i.WindDirection'     % hour, degToCompass(data['hourly']['data'][hour-1]['windBearing']))
		set_property('Hourly.%i.Humidity'     % hour, str(round(float(data['hourly']['data'][hour-1]['humidity']) * 100)) + '%')
		set_property('Hourly.%i.Precipitation'     % hour, str(round(data['hourly']['data'][hour-1]['precipProbability'])) + '%')
		weathercode = WEATHER_CODES[str(data['hourly']['data'][hour-1]['icon'])]
		set_property('Hourly.%i.OutlookIcon' % hour, '%s.png' %  weathercode)
		set_property('Hourly.IsFetched', 'true')
		
		
log(f"version started: {__version__}",xbmc.LOGINFO)

set_property('WeatherProvider', __addonname__)
set_property('WeatherProviderLogo', xbmcvfs.translatePath(os.path.join(__cwd__, 'resources', 'banner.png')))

if sys.argv[1].startswith('Location'):
	keyboard = xbmc.Keyboard('', xbmc.getLocalizedString(14024), False)
	keyboard.doModal()
	if (keyboard.isConfirmed() and keyboard.getText() != ''):
		text = keyboard.getText()
		items, locs, locids = location(text)
		dialog = xbmcgui.Dialog()
		if locs != []:
			selected = dialog.select(xbmc.getLocalizedString(396), items)
			if selected != -1:
				result = dialog.input("Edit Location Name?", defaultt=locs[selected])
				if not result:
					result = locs[selected]  # cancelled → use original
				__addon__.setSetting(sys.argv[1], result)
				__addon__.setSetting(sys.argv[1] + 'id', locids[selected])
				log('selected location: %s' % locs[selected],xbmc.LOGDEBUG)
		else:
			dialog.ok(__addonname__, xbmc.getLocalizedString(284))
else:
	location = __addon__.getSetting('Location%s' % sys.argv[1])
	locationid = __addon__.getSetting('Location%sid' % sys.argv[1])
	if (locationid == '') and (sys.argv[1] != '1'):
		location = __addon__.getSetting('Location1')
		locationid = __addon__.getSetting('Location1id')
		log('trying location 1 instead',xbmc.LOGDEBUG)
		log(str(location),xbmc.LOGDEBUG)
		log(str(locationid),xbmc.LOGDEBUG)
	if not locationid == '':
		forecast(location, locationid)
	else:
		log('no location found',xbmc.LOGDEBUG)
		clear()
	refresh_locations()

log('finished',xbmc.LOGINFO)
