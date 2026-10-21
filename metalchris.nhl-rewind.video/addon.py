#!/usr/bin/python
#
#
# Written by MetalChris 2026.10.20
# Released under GPL(v2 or later)

import urllib.parse, urllib.error, urllib.request, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, os, re
import json
import time
import datetime
import requests
from bs4 import BeautifulSoup
import mechanicalsoup

today = time.strftime("%Y-%m-%d")


HANDLE = int(sys.argv[1])
xbmcplugin.setContent(HANDLE, 'video')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='metalchris.nhl-rewind.video')
translation = selfAddon.getLocalizedString
#settings = xbmcaddon.Addon(id="metalchris.nhl-rewind.video")
base = 'https://api-web.nhle.com/v1/scoreboard/now'
teams_url = 'https://www.nhl.com/info/teams/'
schedule_url = 'https://api-web.nhle.com/v1/club-schedule-season/'
brightcove = 'https://edge.api.brightcove.com/playback/v1/accounts/6415718365001/videos/'
plugin = "NHL Rewind"
local_string = xbmcaddon.Addon(id='metalchris.nhl-rewind.video').getLocalizedString
defaultimage = 'special://home/addons/metalchris.nhl-rewind.video/resources/media/icon.png'
fanart = 'special://home/addons/metalchris.nhl-rewind.video/resources/media/fanart.jpg'

__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

from uas import *
from logger import *

#log_notice = _addon.getSetting(id="log_notice")
#if log_notice != 'false':
	#log_level = 2
#else:
	#log_level = 1
#xbmc.log('LOG_NOTICE: ' + str(log_notice),xbmc.LOGINFO)

xbmc.log('TODAY: ' + str(today),xbmc.LOGINFO)
xbmc.log('NOW: ' + str(time.time()),xbmc.LOGINFO)
xbmc.log('UTC Offset: ' + str(-time.timezone),xbmc.LOGINFO)

browser = mechanicalsoup.Browser(soup_config={'features': 'html.parser'})

browser.session.headers.update({
	'Referer': 'https://www.nhl.com/',
    'User-Agent': ua,
    'Accept': 'application/json;pk=BCpkADawqM3l37Vq8trLJ95vVwxubXYZXYglAopEZXQTHTWX3YdalyF9xmkuknxjBgiMYwt8VZ_OZ1jAjYxz_yzuNh_cjC3uOaMspVTD-hZfNUHtNnBnhVD0Gmsih8TBF8QlQFXiCQM3W_u4ydJ1qK2Rx8ZutCUg3PHb7Q'
    # Add any other headers you need
})

def build_url(query):
	return 'plugin://metalchris.nhl-rewind.video/' + '?' + urllib.parse.urlencode(query)
	
	
#3
def all_teams():
	response = requests.get(teams_url, timeout=15)
	response.raise_for_status()

	soup = BeautifulSoup(response.text, 'html.parser')

	teams = []

	for team in soup.select('div.nhl-c-team-list__team-menu.nhl-c-team-menu'):
		name_link = team.select_one('a.nhl-c-team-menu__link.-team')
		logo = team.select_one('a.nhl-c-team-menu__logo img')
		schedule_link = team.find('a', string=lambda text: text and text.strip() == 'Schedule')

		if not name_link or not schedule_link:
			continue

		teams.append({
			'name': name_link.get_text(strip=True),
			'url': schedule_link.get('href'),
			'logo': logo.get('src') if logo else ''
		})

	for team in teams:

		title = team.get('name').replace('north_east','')

		thumb = 'special://home/addons/metalchris.nhl-rewind.video/resources/media/' + title + '.png'
		#log(f"THUMB: {thumb}",xbmc.LOGINFO)
		
		url = schedule_url + team.get('logo').split('/')[-1].replace('_dark.svg','/20262027')

		li = xbmcgui.ListItem(label=title)
		
		li.setInfo("video",{
			
			})

		li.setArt({
			"thumb": thumb,
			"icon": thumb,
			"poster": thumb
		})

		# pass ONLY identifier forward
		url = build_url({
			"action": "condensed",
			"url": url
		})

		li.setProperty("IsPlayable", "false")

		xbmcplugin.addDirectoryItem(
			handle=HANDLE,
			url=url,
			listitem=li,
			isFolder=True
		)
		
		xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(HANDLE)
	#xbmcplugin.setContent(HANDLE, 'episodes')


def condensed(url):	
	count = 0
	log(f"URL: {url}",xbmc.LOGDEBUG)
	response = requests.get(url, timeout=15)
	response.raise_for_status()
	log(f"CONDENSED RESPONSE: {response.status_code}",xbmc.LOGINFO)
	data = response.json()
	
	for game in reversed(data.get('games')):
		if game.get('condensedGame'):
			gameDate = game.get('gameDate')
			home = game.get('homeTeam').get('commonName').get('default')
			away = game.get('awayTeam').get('commonName').get('default')
			title = f"{home} @ {away} ({gameDate})"
			condensed_url = 'https://www.nhl.com' + game.get('condensedGame')
			video_id = game.get('condensedGame').split('-')[-1]
			url = brightcove + video_id
			count += 1
			#log(f"TITLE: {title}",xbmc.LOGINFO)

			li = xbmcgui.ListItem(label=title)
			
			li.setInfo("video",{
				
				})
				
			thumb = defaultimage
			#thumb = get_images(condensed_url)

			li.setArt({
				"thumb": thumb,
				"icon": thumb,
				"poster": thumb
			})

			# pass ONLY identifier forward
			url = build_url({
				"action": "play",
				"name": title,
				"url": url
			})

			li.setProperty("IsPlayable", "true")

			xbmcplugin.addDirectoryItem(
				handle=HANDLE,
				url=url,
				listitem=li,
				isFolder=False
			)
			
			
			#xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_REVERSE)
	#log(f"GAMES: {count}",xbmc.LOGINFO)
	xbmcplugin.endOfDirectory(HANDLE)
		
	
#6
def get_images(url):
	response = browser.get(url, timeout=15)
	response.raise_for_status()
	log(f"PLAY RESPONSE: {response.status_code}",xbmc.LOGINFO)
	html = response.text
	match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html)
	if match:
		thumb = match.group(1)
	return thumb
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)


#99
def play(name, url):
	response = browser.get(url, timeout=15)
	response.raise_for_status()
	log(f"PLAY RESPONSE: {response.status_code}",xbmc.LOGINFO)
	data = response.json()
	sources = data.get('sources')
	log(f"SOURCES: {sources}",xbmc.LOGDEBUG)
	url = sources[0].get('src')
	thumb = data.get('poster').replace('_size50','_size20')
	
	li = xbmcgui.ListItem(label=name, path=url)
	li.setProperty('IsPlayable', 'true')
	li.setArt({
				"thumb": thumb,
				"icon": thumb,
				"poster": thumb
			})

	li.setProperty('inputstream', 'inputstream.adaptive')
	li.setProperty('inputstream.adaptive.manifest_type', 'hls')
	li.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={ua}")
	li.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
	li.setMimeType('application/vnd.apple.mpegurl')
	li.setContentLookup(False)
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
	#xbmcplugin.setResolvedUrl(HANDLE, True, li)
	#xbmc.log('URL: ' + str(url), xbmc.LOGINFO)
	#xbmcplugin.endOfDirectory(HANDLE)
	

def router(paramstring):
	params = dict(urllib.parse.parse_qsl(paramstring))

	action = params.get("action")

	if action == "condensed":
		log(f"CONDENSED",xbmc.LOGINFO)
		condensed(params.get("url"))
	elif action == "play":
		log(f"NAME: {params.get('name')}, URL: {params.get('url')}",xbmc.LOGDEBUG)
		play(params.get("name"),params.get("url"))
	else:
		all_teams()


if __name__ == "__main__":
	router(sys.argv[2][1:])
