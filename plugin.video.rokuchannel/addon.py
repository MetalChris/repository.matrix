#!/usr/bin/python
#
#
# Written by MetalChris 2026.09.21
# Released under GPL(v2 or later)

import urllib.parse, urllib.error, urllib.request, urllib.error, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, re, os
import json
import time
from time import strftime, localtime
import requests
from requests import Request, Session
import datetime
import http.cookiejar
from http.cookiejar import LWPCookieJar
import shutil


today = time.strftime("%Y-%m-%d")


addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'video')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id='plugin.video.rokuchannel')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
addon_version = addon.getAddonInfo("version")
settings = xbmcaddon.Addon(id="plugin.video.rokuchannel")
apiUrl = 'https://therokuchannel.roku.com/api/v2/homescreen/v2/home'
api1Url = 'https://therokuchannel.roku.com/api/v1/navigation/menu'
playbackUrl = 'https://therokuchannel.roku.com/api/v3/playback'
allLive = 'https://therokuchannel.roku.com/api/v2/homescreen/pages/w.DzWLgJdPr1hPM0J89axBs1lBP4jwQzcdedlray1BhAP79Q3q6wTQA4Bx8RMxUYM2Ll2RWGcRDDgRN149tWYwVJAq6oSZjlGydblvFVb0ymJQw5sxmDy6Yj53HeVp9aVwG4f1Qbxd79wg/rendered?limit=99'
plugin = "Roku Channel"
local_string = xbmcaddon.Addon(id='plugin.video.rokuchannel').getLocalizedString
defaultimage = 'special://home/addons/plugin.video.rokuchannel/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.rokuchannel/resources/media/fanart.jpg'

rejects = ['save list','featured', 'watch it again','characters','live tv','late night laughs','featured from starz', 'layout', 'premium', '?', 'recently', 'paramountplus', '+', 'browse premium subscriptions', 'missed a show? catch it here!']

__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")
sys.path.append(__resource__)

from utilities import *
from roku_meta import *
from convert_to_local import *
from check_cache_ttl import *
from logger import *
from epg_info import *
from migrate import *
from file_migrate import *
from favorites import *
#from migration import *

CookieJar = http.cookiejar.LWPCookieJar(os.path.join(addon_path_profile, 'cookies.lwp'))

CookieJson = (os.path.join(addon_path_profile, 'cookies.json'))

confluence_views = [500,501,503,504,515]
force_views = settings.getSetting(id="force_views")
hls = settings.getSetting(id='hls')
first = settings.getSetting(id='first')

if first != 'true':
	addon.openSettings(label="Logging")
	addon.setSetting(id='first',value='true')
	log(f"FIRST RUN",xbmc.LOGINFO)
	create_favorites()

debug_logging = settings.getSetting(id="debug_logging")
#if debug_logging != 'false':
	#log_level = 2
#else:
	#log_level = 1
#log('LOG_NOTICE: ' + str(debug_logging),xbmc.LOGINFO)

#log('TODAY: ' + str(today),xbmc.LOGINFO)
#log('NOW: ' + str(round(time.time())),xbmc.LOGINFO)
#log('UTC Offset: ' + str(-time.timezone),xbmc.LOGINFO)

offset = -time.timezone
NOW = (round(time.time()) - offset)
#log('NOW+OFFSET: ' + str(NOW),xbmc.LOGINFO)


try:
	CookieJar.load()
except:
	pass

s = requests.Session()
s.cookies = CookieJar
season = ''
episode = ''

#migrate_old_addon_data() ## This moves userdata to metalchris.rokuchannel.video
#copy_userdata_files()
#copy_addon_files()

def main_menu():
	addDir2('Saved Items', apiUrl + 'tv-shows', 25, defaultimage, defaultfanart, infoLabels={'plot':''})
	addDir2('Live Channels', apiUrl, 9, defaultimage, defaultfanart, infoLabels={'plot':''})
	addDir2('On Demand Video', apiUrl + 'free-movies', 0, defaultimage, defaultfanart, infoLabels={'plot':''})
	addDir2('Search', apiUrl + 'tv-shows', 20, defaultimage, defaultfanart, infoLabels={'plot':''})
	
	log(f"Roku Channel {addon_version} Debug: {debug_logging}",xbmc.LOGINFO)
	log(f"TODAY: {today}, NOW: {round(time.time())}, UTC Offset: {-time.timezone}, NOW+OFFSET: {NOW}", xbmc.LOGDEBUG)


def categories(apiUrl):
	if is_cache_stale(addon_path_profile + 'api.json') != False:
		log(f"Downloading from API... {apiUrl}",xbmc.LOGINFO)
		with urllib.request.urlopen(apiUrl) as response, open(os.path.join(addon_path_profile, 'api.json'), 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
	with open(os.path.join(addon_path_profile, 'api.json'), 'rb') as f:
		data = json.load(f)

	cats = []
	for count, item in enumerate(data['collections']):
		if 'title' not in item:
			log('No Title',xbmc.LOGINFO)
			continue
		title = str(item['title'])# + ' - ' + str(count)
		if title.lower() in rejects:
			log(('### REJECT TITLE ### ' + str(title)),xbmc.LOGINFO)
			continue
		if title not in cats:
			cats.append(title)
		streamUrl = 'plugin://plugin.video.rokuchannel?mode=3&url=' + urllib.parse.quote_plus(apiUrl) + '&name=' + urllib.parse.quote_plus(title)# + '&count=' + urllib.parse.quote_plus(str(count))
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	log('CATS: ' + str(cats),xbmc.LOGINFO)
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	#xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#3
def channels(apiUrl, name):
	if is_cache_stale(addon_path_profile + 'api.json') != False:
		log(f"Downloading from API... {apiUrl}",xbmc.LOGINFO)
		with urllib.request.urlopen(apiUrl) as response, open(os.path.join(addon_path_profile, 'api.json'), 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
	with open(os.path.join(addon_path_profile, 'api.json'), 'rb') as f:
		data = json.load(f)
	for count, item in enumerate(data['collections']):
		if item['title'] == name:
			log(('MATCH'),xbmc.LOGINFO)
			log(('COUNT: ' + str(count)),xbmc.LOGINFO)
			c = count
			for count, item in enumerate(data['collections'][c]['view']):
				title = str(item['content']['title'])
				#log(('TITLE: ' + str(title)),xbmc.LOGINFO)
				if title == 'See all' or title == 'See All' or title == 'More':
					continue
				image = item['content']['imageMap']['grid']['path']
				fanart = image
				sid = (item['content']['meta'])['sid']
				contentType = item['content']['type']
				if 'releaseYear' in item:
					contentYear = item['content']['releaseYear']
				else:
					contentYear = 'N/A'
				if 'parentalRatings' in item:
					contentRating = item['content']['parentalRatings'][0]['code']
				else:
					contentRating = 'N/A'
				plot = (contentType).title() + '\nReleased: ' + str(contentYear) + '\nRating: ' + contentRating
				url = 'https://therokuchannel.roku.com/api/v2/homescreen/content/' + urllib.parse.quote_plus('https://content.sr.roku.com/content/v1/roku-trc/') + sid
				if contentType == 'movie':
					streamUrl = 'plugin://plugin.video.rokuchannel?mode=6&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(sid)
					li = xbmcgui.ListItem(title)
					li.setProperty('IsPlayable', 'true')
					li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot})
					li.setArt({'thumb':image,'fanart':fanart})
					## Add Context Item
					#li.addContextMenuItems([('Movie Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url)))])
					li.addContextMenuItems([('Movie Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url))),('Save Item', 'RunPlugin(%s?mode=82&url=%s&name=%s&data=%s&image=%s&sid=%s)' % (sys.argv[0], (url), urllib.parse.quote_plus(title), (contentType), (image), (sid)))])
					xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
				if contentType == 'series':
					url = url + '%3Fexpand%3Dseasons.episodes.descriptions.40%252Cseasons.episodes.descriptions.60%252Cseasons.episodes.episodeNumber%252Cseasons.episodes.seasonNumber%252Cseasons.episodes.images%252Cseasons.episodes.imageMap.grid%252Cseasons.episodes.indicators%252Cseasons.episodes.releaseDate%252Cseasons.episodes.viewOptions%252Cepisodes.episodeNumber%252Cepisodes.seasonNumber%252Cepisodes.viewOptions%26filter%3DcategoryObjects%253AgenreAppropriate%252520eq%252520true%252Cseasons.episodes%253A%2528not%252520empty%2528viewOptions%2529%2529%253Aall%26featureInclude%3Dbookmark%252Cwatchlist%252ClinearSchedule'
					streamUrl = 'plugin://plugin.video.rokuchannel?mode=12&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(name)
					li = xbmcgui.ListItem(title)
					li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot})
					li.setArt({'thumb':image,'fanart':fanart})
					## Add Context Item
					#li.addContextMenuItems([('Show Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url)))])
					li.addContextMenuItems([('Show Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url))),('Save Item', 'RunPlugin(%s?mode=82&url=%s&name=%s&data=%s&image=%s&sid=%s)' % (sys.argv[0], (url), urllib.parse.quote_plus(title), (contentType), (image), (sid)))])
					xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
				else:
					continue
				#li = xbmcgui.ListItem(title)
				info = li.getVideoInfoTag()
				#info.setPlot(plot)
				#info.setDuration(timeLeft)
				#info.setPremiered(releaseDate)
	xbmcplugin.setContent(addon_handle, 'episodes')
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#6
def get_pid(url, sid):
	csrfUrl = 'https://therokuchannel.roku.com/watch/' + sid
	response = s.get(csrfUrl)
	csrf = re.compile('csrf: "(.+?)"').findall(str(response.text))[0]
	log('CSRF: ' + str(csrf), xbmc.LOGINFO)

	response = s.get(url)
	log('PID RESPONSE CODE: ' + str(response.status_code), xbmc.LOGINFO)
	log('PID R.COOKIE: ' + str(response.cookies), xbmc.LOGDEBUG)
	log('PID RESPONSE LENGTH: ' + str(len(response.text)), xbmc.LOGDEBUG)

	data = json.loads(response.text)
	playId = data['viewOptions'][0]['playId']
	videos = data['viewOptions'][0]['media']['videos']

	log('PID PLAYID: ' + str(playId), xbmc.LOGINFO)
	log('VIEWOPTIONS LENGTH: ' + str(len(videos)), xbmc.LOGDEBUG)
	log('VIEWOPTIONS URL: ' + str(videos), xbmc.LOGDEBUG)

	if any(item.get('videoType') == 'DASH' for item in videos):
		media_format = 'mpeg-dash'
	else:
		media_format = 'm3u'

	json_data = {
		'adPolicyId': '',
		'bifUrl': None,
		'drmType': 'widevine',
		'mediaFormat': media_format,
		'playId': playId,
		'providerId': 'rokuavod',
		'quality': 'fhd',
		'rokuId': sid,
	}

	log('JSON_DATA: ' + str(json_data), xbmc.LOGDEBUG)
	PLAY(json_data, csrf, sid)


#9
def get_live(url,name):
	response = s.get(api1Url)
	data = json.loads(response.text)
	retry = 0
	while not 'Live TV' in response.text:
		response = s.get(api1Url)
		retry +=1
		time.sleep(5)
		log('RETRY: ' + str(retry),xbmc.LOGINFO)
		if retry > 5:
			xbmcgui.Dialog().notification(addonname, 'Live TV API Not Available. Please Try Again Later.', defaultimage, time=5000, sound=False)
			sys.exit()
	log(('LIVE TV API FOUND'),xbmc.LOGINFO)
	for count, item in enumerate (data['view']):
		if item['title'] == 'Live TV':
			log(('TITLE: ' + str(item['title'])),xbmc.LOGINFO)
			log(('LIVE TV FOUND'),xbmc.LOGINFO)
			#for count, item in enumerate(item['meta']):
			#if item['title'] == 'Live TV':
			pageId = item['meta']['id']
			log('PAGEID: ' + str(pageId),xbmc.LOGINFO)
			Live = 'https://therokuchannel.roku.com/api/v2/homescreen/pages/' + pageId + '/rendered?limit=99'
	#Live = 'https://therokuchannel.roku.com/api/v2/homescreen/pages/w.xWvaD8v8B1HPbvLeY9pWCq4VZGGwoktG5NA1w1WgCVYNBL8D2M/rendered?limit=99'
	if is_cache_stale(addon_path_profile + 'live.json') != False:
		log(f"Downloading from API... {Live}",xbmc.LOGINFO)
		with urllib.request.urlopen(Live) as response, open(os.path.join(addon_path_profile, 'live.json'), 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
	with open(os.path.join(addon_path_profile, 'live.json'), 'rb') as f:
		data = json.load(f)
	cats = []
	for count, item in enumerate(data['collections']):
		if 'title' not in item:
			log('No Title',xbmc.LOGINFO)
			continue
		title = str(item['title'])# + ' - ' + str(count)
		if title.lower() in rejects:
			log(('### REJECT TITLE ### ' + str(title)),xbmc.LOGINFO)
			continue
		if title not in cats:
			cats.append(title)
		streamUrl = 'plugin://plugin.video.rokuchannel?mode=15&url=' + urllib.parse.quote_plus(Live) + '&name=' + urllib.parse.quote_plus(title)# + '&count=' + urllib.parse.quote_plus(str(count))
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	log('CATS: ' + str(cats),xbmc.LOGINFO)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#12
def get_episodes(url,name):
	response = s.get(url)
	log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGINFO)
	log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGDEBUG)
	#log('RESPONSE: ' + str(response.text),xbmc.LOGINFO)
	data = json.loads(response.text)
	for count, item in enumerate(data['episodes']):
		if item['viewOptions'][0]['license'] == 'Subscription':
			continue
		title = item['title']
		image = item['images'][0]['path']
		seasonNumber = item['seasonNumber']
		episodeNumber = item['episodeNumber']
		duration = item['viewOptions'][0]['media']['duration']
		premiered = item['releaseDate']
		#title = str(seasonNumber) + 'x' + str(episodeNumber) + ' ' + title
		plot = item['description']
		sid = item['meta']['sid']
		streamUrl = 'plugin://plugin.video.rokuchannel?mode=6&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(sid)
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot,'season':seasonNumber,'episode':episodeNumber,'duration':duration,'premiered':premiered})
		li.setArt({'thumb':image,'fanart':image})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
		xbmcplugin.setContent(addon_handle, 'episodes')
		if force_views != 'false':
			xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#15
def live_channels(url, name):
	if is_cache_stale(addon_path_profile + 'live.json') != False:
		log(f"Downloading from API... {url}",xbmc.LOGINFO)
		with urllib.request.urlopen(Live) as response, open(os.path.join(addon_path_profile, 'live.json'), 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
	with open(os.path.join(addon_path_profile, 'live.json'), 'rb') as f:
		data = json.load(f)
	for collection in data.get('collections', []):
		if collection.get('title') != name:
			continue

		log('MATCH', xbmc.LOGINFO)

		for item in collection.get('view', []):
			schedule = item.get('features', {}).get('linearSchedule', [])
			title = str(item['content']['title'])
			if title == 'See all' or title == 'See All':
				continue				
			log(('CHANNEL TITLE: ' + str(title)),xbmc.LOGDEBUG)
			image = item['content']['imageMap']['grid']['path']
			contentType = item.get('content', {}).get('type')
			if not contentType:
				continue
			if schedule:
				current = schedule[0]

				infoText = get_meta(item)
				series = current.get('content', {}).get('series', {})
				showTitle = series.get('title', '')
				if showTitle:
					log(('SHOWTITLE: ' + str(showTitle)),xbmc.LOGDEBUG)
				sid = item.get('content', {}).get('meta', {}).get('sid')
				#log('LIVE CHANNEL SID: ' + str(sid), xbmc.LOGDEBUG)
			if schedule:	
				#log('SCHED LENGTH: ' + str(len(item['features']['linearSchedule'])),xbmc.LOGINFO)
				onNow = current['content']['title']
				remaining = time_remaining_text(current['end'])
				if len(schedule) >= 2:
					next_program = schedule[1]
					next_series = next_program.get('content', {}).get('series', {})
					next_show_title = next_series.get('title', '')
					onNext = next_program['content']['title']
					if next_show_title and title.lower() != next_show_title.lower():
						onNext = f'{next_show_title}: {onNext}'
					nextStart = format_unix_time_kodi(next_program['start'])
					nextEnd = format_unix_time_kodi(next_program['end'])
				else:
					onNext = 'Not Available'
					nextStart = 0
					nextEnd = 0
					
				if showTitle and title.lower() != showTitle.lower():
					onNow = f'{showTitle}: {onNow}'
				plot = (
					f'[B]{onNow}[/B] \n'
					f'{infoText[0]} ({remaining})'
					f'\n\nNext: [B]{onNext}[/B]\n'
					f'{infoText[1]} ({nextStart} - {nextEnd})'
				)
			else:
				plot = ''
			url = 'https://therokuchannel.roku.com/api/v2/homescreen/content/' + urllib.parse.quote_plus('https://content.sr.roku.com/content/v1/roku-trc/') + sid
			streamUrl = 'plugin://plugin.video.rokuchannel?mode=6&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(sid)
			li = xbmcgui.ListItem(title)
			li.setProperty('IsPlayable', 'true')
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot})
			li.setArt({'thumb':image,'fanart':image})
			li.addContextMenuItems([('More Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url))),('Save Item', 'RunPlugin(%s?mode=82&url=%s&name=%s&data=%s&image=%s&sid=%s)' % (sys.argv[0], (url), urllib.parse.quote_plus(title), (contentType), (image), (sid)))])
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#20
def search():
	keyb = xbmc.Keyboard('', 'Search by Title')
	keyb.doModal()
	if (keyb.isConfirmed()):
		search = keyb.getText()
		log('SEARCH: ' + str(search),xbmc.LOGINFO)
		json_data = {'query': search.replace(' ','%20'),}
		url = 'https://therokuchannel.roku.com'# + search# + '%29%20AND%20mediatype%3A%28audio%29&page=1'
		response = s.get(url)
		csrf = re.compile('csrf: "(.+?)"').findall(str(response.text))[0]
		headers = {
		'csrf-token': csrf,
		'referer': 'https://therokuchannel.roku.com',
		'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
		}
		log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGINFO)
		cookies = dict(response.cookies)
		log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGDEBUG)
		response = s.post('https://therokuchannel.roku.com/api/v1/search', headers=headers, cookies=cookies, json=json_data)
		log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGINFO)
		log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGDEBUG)
		data = json.loads(response.text)
		for count, item in enumerate(data['view']):
			if (item['content']['type'] == 'zone') or ('Entitlement' in str(item)):
				continue
			title = item['content']['title']#.replace(',','')
			image = item['content']['images'][0]['path']
			contentType = (item['content']['type'])
			if 'descriptions' in item:
				pl = (item['content']['descriptions'])
				pkey = list(pl)[-1]
				plot = '(' + contentType + ') ' + (item['content']['descriptions'][pkey]['text'])
			else:
				plot = '(' + contentType + ') '
			sid = item['content']['meta']['sid']
			url = 'https://therokuchannel.roku.com/api/v2/homescreen/content/' + urllib.parse.quote_plus('https://content.sr.roku.com/content/v1/roku-trc/') + sid
			if contentType == 'movie' or contentType == 'livefeed':
				streamUrl = 'plugin://plugin.video.rokuchannel?mode=6&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(sid)
				li = xbmcgui.ListItem(title)
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot})
				li.setArt({'thumb':image,'fanart':image})
				li.addContextMenuItems([('More Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url))),('Save Item', 'RunPlugin(%s?mode=82&url=%s&name=%s&data=%s&image=%s&sid=%s)' % (sys.argv[0], (url), urllib.parse.quote_plus(title), (contentType), (image), (sid)))])
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
			if contentType == 'series':
				url = url + '%3Fexpand%3Dseasons.episodes.descriptions.40%252Cseasons.episodes.descriptions.60%252Cseasons.episodes.episodeNumber%252Cseasons.episodes.seasonNumber%252Cseasons.episodes.images%252Cseasons.episodes.imageMap.grid%252Cseasons.episodes.indicators%252Cseasons.episodes.releaseDate%252Cseasons.episodes.viewOptions%252Cepisodes.episodeNumber%252Cepisodes.seasonNumber%252Cepisodes.viewOptions%26filter%3DcategoryObjects%253AgenreAppropriate%252520eq%252520true%252Cseasons.episodes%253A%2528not%252520empty%2528viewOptions%2529%2529%253Aall%26featureInclude%3Dbookmark%252Cwatchlist%252ClinearSchedule'
				streamUrl = 'plugin://plugin.video.rokuchannel?mode=12&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(name)
				li = xbmcgui.ListItem(title)
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot})
				li.setArt({'thumb':image,'fanart':image})
				## Add Context Item
				li.addContextMenuItems([('Show Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url))),('Save Item', 'RunPlugin(%s?mode=82&url=%s&name=%s&data=%s&image=%s)' % (sys.argv[0], (url), urllib.parse.quote_plus(title), (contentType), (image)))])
				#li.addContextMenuItems([('Show Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url)))])
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
			else:
				continue
			#li = xbmcgui.ListItem(title)
			info = li.getVideoInfoTag()
			#info.setPlot(plot)
			#info.setDuration(timeLeft)
			#info.setPremiered(releaseDate)
		xbmcplugin.setContent(addon_handle, 'episodes')
		if force_views != 'false':
			xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
		xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
		xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
	else:
		sys.exit()


#25
def saved_items(name,url):
	start_path = os.path.join(addon_path_profile) # current directory
	log('START_PATH: ' + str(start_path),xbmc.LOGINFO)
	for path,dirs,files in os.walk(start_path):
		for filename in files:
			if '.txt' in filename:
				title = urllib.parse.unquote_plus(filename).split('-')[0]
				#log('SAVED ITEM TITLE: ' + str(title),xbmc.LOGINFO)
				with open(os.path.join(addon_path_profile, filename), 'r') as f:
					items = f.read()
				info = re.findall(r"'(.*?)'", items)
				url = info[0]
				image = info[2]
				sid = re.search(r'.*%2F(.*)$', url).group(1)[:32] #info[2].split('/')[8]
				log('SAVED ITEMS SID: ' + str(sid),xbmc.LOGDEBUG)
				#log('SAVED ITEMS SID LENGTH: ' + str(len(sid)),xbmc.LOGDEBUG)
				contentType = info[1]
				#log('CONTENTTYPE: ' + str(contentType),xbmc.LOGINFO)
				if (contentType == 'movie') or (contentType == 'livefeed'):
					mode = 6; folder = False
					if contentType == 'livefeed':
						infoText = find_channel(sid)
						if infoText == None:					
							plot = f" [B]{title}[/B] - {contentType.title()}"
						else:							 
							plot = infoText[0] + '\n\n' + infoText[1]
					else:
						#infoText = find_movie(url)						
						plot = contentType.title()
				if contentType == 'series':
					mode = 12; folder = True
					#infoText = find_movie(url)						
					plot = contentType.title()
				streamUrl = 'plugin://plugin.video.rokuchannel?mode=' + str(mode) + '&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(sid)# + '&count=' + urllib.parse.quote_plus(str(count))
				li = xbmcgui.ListItem(title)
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot})
				li.setArt({'thumb':image,'fanart':image})
				## Add Context Item
				li.addContextMenuItems([('More Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url))),('Delete Item', 'RunPlugin(%s?mode=88&url=%s&name=%s&data=%s&image=%s)' % (sys.argv[0], (url), urllib.parse.quote_plus(title), (contentType), (image)))])
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=folder)
	#log('INFO 0: ' + str(info[0]),xbmc.LOGINFO)
	#log('INFO 1: ' + str(info[1]),xbmc.LOGINFO)
	#log('INFO 2: ' + str(info[2]),xbmc.LOGINFO)
	xbmcplugin.setContent(addon_handle, 'episodes')
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#82
def save_item(url,name,data,image,sid):	
	log('SAVE ITEM NAME: ' + str(name),xbmc.LOGINFO)
	#log('SAVE ITEM: ' + str(url),xbmc.LOGINFO)
	#log('SAVE ITEM CONTENTTYPE: ' + str(data),xbmc.LOGINFO)
	second = urllib.parse.quote_plus(url.split('/',7)[-1])
	log('SECOND: ' + str(second),xbmc.LOGINFO)
	log('SAVE ITEM SID: ' + str(sid),xbmc.LOGDEBUG)
	infoUrl = 'https://therokuchannel.roku.com/api/v2/homescreen/content/' + second
	log('INFOURL: ' + str(infoUrl),xbmc.LOGINFO)
	file_name = urllib.parse.quote_plus(name) + '-' + data + '.txt'
	with open(os.path.join(addon_path_profile, file_name), "w") as text_file:
		text_file.write(f"{infoUrl,data,image}")
	xbmcgui.Dialog().notification(addonname, name + ' Saved', defaultimage, time=3000, sound=False)
	add_favorite(sid, name, infoUrl, image)
	create_favorites()
	copy_userdata_files()
	sys.exit()


#85
def info(url):
	xbmcgui.Dialog().notification(addonname, 'Fetching Info...', defaultimage, time=3000, sound=False)
	second = urllib.parse.quote_plus(url.split('/',7)[-1])
	log('SECOND: ' + str(second),xbmc.LOGINFO)
	infoUrl = 'https://therokuchannel.roku.com/api/v2/homescreen/content/' + second
	log('INFOURL: ' + str(infoUrl),xbmc.LOGINFO)
	response = s.get(infoUrl)
	log(f"RESPONSE CODE: {response.status_code}", xbmc.LOGINFO)
	log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGDEBUG)
	data = json.loads(response.text)
	actors = []
	if 'credits' in data:
		for count, item in enumerate(data['credits']):
			if item['role'] == 'ACTOR':
				actors.append(item['name'])
		log('ACTORS: ' + str(actors),xbmc.LOGDEBUG)
	genres = []
	for count, item in enumerate(data['genres']):
		genres.append(item.title())
	log('GENRES: ' + str(genres),xbmc.LOGINFO)
	log('DESCRIPTION LENGTH: ' + str(len(data['descriptions'])),xbmc.LOGDEBUG)
	if len(data['descriptions']) >= 1:
		descriptions = []
		for count, item in enumerate(data['descriptions']):
			descriptions.append(item)
		log('DESCRIPTION: ' + str(descriptions),xbmc.LOGDEBUG)
		desc = descriptions[-1]
		description = data['descriptions'][desc]['text']
	else:
		description = data['description']
	title = data['title']
	if 'releaseYear' in data:
		year = data['releaseYear']
	else:
		year = 'N/A'
	if 'runTimeSeconds' in data:
		duration = data['runTimeSeconds']
	else:
		duration = 0
	rating = data['parentalRatings'][0]['code']
	runtime = str(datetime.timedelta(seconds=duration))
	info = '(' + str(genres)[1:-1].replace("'","") + ') ' + str(description) + '\n\nCast: ' + str(actors)[1:-1].replace("'","") + '\n\nRated: ' + rating + '\n\nReleased: ' + str(year) + '\n\nDuration: ' + str(runtime)
	log('DESCRIPTION: ' + str(description),xbmc.LOGDEBUG)
	if data['type'] == 'series':
		episodes = len(data['episodes'])
		log('EPISODES: ' + str(episodes),xbmc.LOGDEBUG)
		info = info + '\n\n' + str(episodes) + ' Episodes'
	xbmcgui.Dialog().textviewer(title, info)


#88
def delete_item(url,name,data,image):
	log('DELETE URL: ' + str(url),xbmc.LOGINFO)
	log('DELETE NAME: ' + str(name),xbmc.LOGINFO)
	log('DELETE DATA: ' + str(data),xbmc.LOGINFO)
	log('DELETE IMAGE: ' + str(image),xbmc.LOGINFO)
	yes = xbmcgui.Dialog().yesno(addonname ,'Are you sure you want to delete ' + name + '?  This action cannot be reversed!')
	if not yes:
		log('NOT YES',xbmc.LOGINFO)
		sys.exit()
	else:
		log('YES',xbmc.LOGINFO)
		file_name = os.path.join(addon_path_profile, urllib.parse.quote_plus(name) + '-' + data + '.txt')
		log('FILE_NAME: ' + str(file_name),xbmc.LOGINFO)
		if os.path.exists(os.path.join(addon_path_profile,file_name)):
			os.remove(file_name)
			xbmcgui.Dialog().notification(addonname, name + ' Has been deleted.', defaultimage, time=3000, sound=False)
			xbmc.executebuiltin("Container.Refresh")
			sys.exit()
		else:
			xbmcgui.Dialog().notification(addonname, name.split('--')[0] + ' Already deleted.', defaultimage, time=3000, sound=False)


def getTargetIds(jsonData):
	log(('Check for key'),xbmc.LOGDEBUG)
	data = json.loads(jsonData)
	log('JSONDATA: ' + str(data),xbmc.LOGDEBUG)
	if 'ssaiStreamUrl' not in data:
		#raise ValueError("No target in given data")
		log(('Key does not exist.'),xbmc.LOGDEBUG)
		return jsonData


def ends(endDateTime):
	NOW = time.time()
	epochDif = (int((int(endDateTime) - int(NOW))))
	#log(('EPOCH_DIF: ' + str(epochDif)),xbmc.LOGINFO)
	if epochDif < 0:
		epochDif = epochDif + 7200
	remaining = str(datetime.timedelta(seconds=epochDif))
	#log(('REMAINING: ' + str(remaining)),xbmc.LOGINFO)
	return remaining


#99
def PLAY(json_data,csrf,sid):
	log('CSRF: ' + str(csrf), xbmc.LOGINFO)
	referer = 'https://therokuchannel.roku.com/watch/' + sid
	log('PLAY SID: ' + str(sid),xbmc.LOGDEBUG)
	
	response = s.get(referer)
	csrf = re.compile('csrf: "(.+?)"').findall(str(response.text))[0]
	log('CSRF: ' + str(csrf), xbmc.LOGINFO)

	headers = {
		#'accept': '*/*',
		#'accept-language': 'en-US,en;q=0.6',
		# Already added when you pass json=
		#'content-type': 'application/json',
		#'accept-encoding': 'gzip, deflate, br, zstd',
		#'Host': 'osm.sr.roku.com', #ERROR 421
		'csrf-token': csrf,
		'referer': referer,
		'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
	}
	#log('USER-AGENT: ' + str(ua),xbmc.LOGINFO)
	response = s.post('https://app.roku.com/api/v3/playback', headers=headers, json=json_data)
	log('PLAYBACK RESPONSE CODE: ' + str(response.status_code),xbmc.LOGINFO)
	retry = 0
	while response.status_code != 200:
		response = s.post('https://app.roku.com/api/v3/playback', headers=headers, json=json_data)
		retry +=1
		time.sleep(5)
		log('RETRY: ' + str(retry),xbmc.LOGINFO)
		if retry > 5:
			sys.exit()
	page = response.text
	log('PLAYBACK RESPONSE LENGTH: ' + str(len(page)),xbmc.LOGDEBUG)
	#log('PLAYBACK RESPONSE: ' + str(page),xbmc.LOGINFO)
	data = json.loads(page)
	#log('DATA KEYS: ' + str(list(data.keys())),xbmc.LOGINFO)
	url = data['url']
	log('URL: ' + str(url),xbmc.LOGINFO)
	#url = data['playbackMedia']['videos'][0]['url']
	#log('STREAM URL: ' + str(url),xbmc.LOGINFO)
	if 'drm' in data:
		lic_url = data['drm']['widevine']['licenseServer']
		log('LIC_URL: ' + str(lic_url),xbmc.LOGINFO)
	else:
		lic_url = ''
		url = url.split('&')[0]
	if 'mpd' in url:
		headers = headers

		#lic_url = f"https://wv-license.sr.roku.com/license/v1/license/wv"
		#license_key = f"{lic_url}"#"|{headers}&Content-Type=application/octet-stream|R{{SSM}}|"
		license_key = lic_url + '|User-Agent=' + ua + '&Referer=' + referer +'/&Origin=' + referer + '&csrf-token=' + csrf + '&Content-Type= |R{SSM}|'
		log('LICENSE_KEY: ' +str(license_key),xbmc.LOGINFO)
		#is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
		#if not is_helper.check_inputstream():
			#sys.exit()

		listitem = xbmcgui.ListItem(path=url)
		#listitem.setInfo("video", {"plot": addon_name})
		log('### MPD SETRESOLVEDURL ###',xbmc.LOGINFO)
		#listitem.setProperty('IsPlayable', 'true')
		listitem.setProperty('inputstream', 'inputstream.adaptive')
		listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
		listitem.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={ua}")
		listitem.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={ua}")
		listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
		listitem.setProperty('inputstream.adaptive.license_key', license_key)
		listitem.setMimeType('application/dash+xml')
		listitem.setContentLookup(False)
		xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
		#log('URL: ' + str(url), xbmc.LOGINFO)
		sys.exit()
	else:
		listitem = xbmcgui.ListItem(path=url)
		#listitem.setInfo("video", {"plot": addon_name})
		log('### M3U SETRESOLVEDURL ###',xbmc.LOGINFO)
		if hls != 'false':
			log('### USE INPUTSTREAM FOR HLS ###',xbmc.LOGINFO)
			listitem.setProperty('IsPlayable', 'true')
			listitem.setProperty('inputstream', 'inputstream.adaptive')
			listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
			listitem.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={ua}")
			listitem.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={ua}")
		listitem.setMimeType('application/vnd.apple.mpegurl')
		listitem.setContentLookup(False)
		xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
		#log('URL: ' + str(url), xbmc.LOGINFO)
		sys.exit()
		xbmcplugin.endOfDirectory(addon_handle)


def get_params():
	param = []
	paramstring = sys.argv[2]
	if len(paramstring) >= 2:
		params = sys.argv[2]
		cleanedparams = params.replace('?', '')
		if (params[len(params) - 1] == '/'):
			params = params[0:len(params) - 2]
		pairsofparams = cleanedparams.split('&')
		param = {}
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			if (len(splitparams)) == 2:
				param[splitparams[0]] = splitparams[1]

	return param

def addDir2(name, url, mode, thumbnail, fanart, infoLabels=True):
	u = sys.argv[0] + "?url=" + urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name,})
	liz.setArt({'thumb':thumbnail,'fanart':fanart})
	if url != 'Future':
		liz.setProperty('IsPlayable', 'true')
	else:
		liz.setProperty('IsPlayable', 'false')
	if not fanart:
		fanart=defaultfanart
	liz.setProperty('fanart_image',fanart)
	ok = xbmcplugin.addDirectoryItem(addon_handle, url=u, listitem=liz, isFolder=True)
	return ok

def unescape(s):
	p = htmllib.HTMLParser(None)
	p.save_bgn()
	p.feed(s)
	return p.save_end()


params = get_params()
url = None
name = None
mode = None
count = None
item = None
data = None
image = None
sid = None

try:
	url = urllib.parse.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.parse.unquote_plus(params["name"])
except:
	pass
try:
	count = urllib.parse.unquote_plus(params["count"])
except:
	pass
try:
	item = urllib.parse.unquote_plus(params["item"])
except:
	pass
try:
	data = urllib.parse.unquote_plus(params["data"])
except:
	pass
try:
	image = urllib.parse.unquote_plus(params["image"])
except:
	pass
try:
	sid = urllib.parse.unquote_plus(params["sid"])
except:
	pass
try:
	mode = int(params["mode"])
except:
	pass

log("Mode: " + str(mode),xbmc.LOGINFO)
log("URL: " + str(url),xbmc.LOGINFO)
log("Name: " + str(name),xbmc.LOGINFO)
#log("Count: " + str(count),xbmc.LOGINFO)

if mode == None or url == None or len(url) < 1:
	log(('Main Menu'),xbmc.LOGINFO)
	main_menu()
elif mode == 0:
	log(('Get Categories'),xbmc.LOGINFO)
	categories(apiUrl)
elif mode == 3:
	log(("Get Channels"),xbmc.LOGINFO)
	channels(url,name)
elif mode == 6:
	log(("Get PID"),xbmc.LOGINFO)
	get_pid(url,name)
elif mode == 9:
	log(("Get Live Channels"),xbmc.LOGINFO)
	get_live(url,name)
elif mode == 12:
	log(("Get Episodes"),xbmc.LOGINFO)
	get_episodes(url,name)
elif mode == 15:
	log(("Get Live Channel"),xbmc.LOGINFO)
	live_channels(url,name)
elif mode == 20:
	log("Search",xbmc.LOGINFO)
	search()
elif mode == 25:
	log(("Get Saved Items"),xbmc.LOGINFO)
	saved_items(url,name)
elif mode == 82:
	log(("Save Item"),xbmc.LOGINFO)
	save_item(url,name,data,image,sid)
elif mode == 85:
	log(("Get Movie Info"),xbmc.LOGINFO)
	info(url)
elif mode == 88:
	log(("Delete Item"),xbmc.LOGINFO)
	delete_item(url,name,data,image)
elif mode == 99:
	log("Play Stream", xbmc.LOGINFO)
	PLAY(name,url)

xbmcplugin.endOfDirectory(addon_handle)
