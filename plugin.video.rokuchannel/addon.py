#!/usr/bin/python
#
#
# Written by MetalChris 2025.06.27
# Released under GPL(v2 or later)

import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, re, os
import json
import time
from time import strftime, localtime
import requests
from requests import Request, Session
import datetime
import inputstreamhelper
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
settings = xbmcaddon.Addon(id="plugin.video.rokuchannel")
apiUrl = 'https://therokuchannel.roku.com/api/v2/homescreen/v2/home'
api1Url = 'https://therokuchannel.roku.com/api/v1/navigation/menu'
playbackUrl = 'https://therokuchannel.roku.com/api/v3/playback'
allLive = 'https://therokuchannel.roku.com/api/v2/homescreen/pages/w.DzWLgJdPr1hPM0J89axBs1lBP4jwQzcdedlray1BhAP79Q3q6wTQA4Bx8RMxUYM2Ll2RWGcRDDgRN149tWYwVJAq6oSZjlGydblvFVb0ymJQw5sxmDy6Yj53HeVp9aVwG4f1Qbxd79wg/rendered?limit=99'
plugin = "Roku Channel"
local_string = xbmcaddon.Addon(id='plugin.video.rokuchannel').getLocalizedString
defaultimage = 'special://home/addons/plugin.video.rokuchannel/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.rokuchannel/resources/media/fanart.jpg'

__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")
sys.path.append(__resource__)

from utilities import *

CookieJar = http.cookiejar.LWPCookieJar(os.path.join(addon_path_profile, 'cookies.lwp'))
#CookieJar = (os.path.join(addon_path_profile, 'cookies.lwp'))

CookieJson = (os.path.join(addon_path_profile, 'cookies.json'))

confluence_views = [500,501,503,504,515]
force_views = settings.getSetting(id="force_views")
hls = settings.getSetting(id='hls')
first = settings.getSetting(id='first')
if first != 'true':
	addon.openSettings(label="Logging")
	addon.setSetting(id='first',value='true')

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 2
else:
	log_level = 1
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)
xbmc.log(('Roku Channel 2025-06-01 BETA'),level=log_level)

xbmc.log('TODAY: ' + str(today),level=log_level)
xbmc.log('NOW: ' + str(round(time.time())),level=log_level)
xbmc.log('UTC Offset: ' + str(-time.timezone),level=log_level)

offset = -time.timezone
NOW = (round(time.time()) - offset)
xbmc.log('NOW+OFFSET: ' + str(NOW),level=log_level)

try:
	CookieJar.load()
except:
	pass

s = requests.Session()
s.cookies = CookieJar
#s.cookies = http.cookiejar.LWPCookieJar(os.path.join(addon_path_profile, 'cookies.lwp'))
season = ''
episode = ''


def main_menu():
	addDir2('Saved Items', apiUrl + 'tv-shows', 25, defaultimage, defaultfanart, infoLabels={'plot':''})
	addDir2('Live Channels', apiUrl, 9, defaultimage, defaultfanart, infoLabels={'plot':''})
	addDir2('On Demand Video', apiUrl + 'free-movies', 0, defaultimage, defaultfanart, infoLabels={'plot':''})
	addDir2('Search', apiUrl + 'tv-shows', 20, defaultimage, defaultfanart, infoLabels={'plot':''})


def categories(apiUrl):
	response = s.get(apiUrl)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	with urllib.request.urlopen(apiUrl) as response, open(os.path.join(addon_path_profile, 'api.json'), 'wb') as out_file:
		shutil.copyfileobj(response, out_file)
	with open(os.path.join(addon_path_profile, 'api.json'), 'rb') as f:
		data = json.load(f)
	rejects = ['save list','featured', 'watch it again','characters','live tv','late night laughs','featured from starz']

	### Search ###
	#li = xbmcgui.ListItem('Search')
	#streamUrl = 'plugin://plugin.video.rokuchannel?mode=20&url=' + urllib.parse.quote_plus(apiUrl) + '&name=' + urllib.parse.quote_plus('Search')# + '&count=' + urllib.parse.quote_plus(str(count))
	#li.setInfo(type="Video", infoLabels={"mediatype":"video","title":'Search'})
	#li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
	#xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)

	### Saved Items ###
	#li = xbmcgui.ListItem('Saved Items')
	#streamUrl = 'plugin://plugin.video.rokuchannel?mode=25&url=' + urllib.parse.quote_plus(apiUrl) + '&name=' + urllib.parse.quote_plus('Saved Items')# + '&count=' + urllib.parse.quote_plus(str(count))
	#li.setInfo(type="Video", infoLabels={"mediatype":"video","title":'Saved Items'})
	#li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
	#xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)

	### Live TV ###
	#li = xbmcgui.ListItem('Live TV')
	#streamUrl = 'plugin://plugin.video.rokuchannel?mode=9&url=' + urllib.parse.quote_plus(apiUrl) + '&name=' + urllib.parse.quote_plus('Live TV')# + '&count=' + urllib.parse.quote_plus(str(count))
	#li.setInfo(type="Video", infoLabels={"mediatype":"video","title":'Live TV'})
	#li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
	#xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)

	cats = []
	for count, item in enumerate(data['collections']):
		if 'title' not in item:
			xbmc.log('No Title',level=log_level)
			continue
		title = str(item['title'])# + ' - ' + str(count)
		#if 'live tv' in title.lower():
		if 'layout' in item:
			xbmc.log(('### SKIP PREMIUM ### ' + str(title)),level=log_level)
			continue
		if ('Premium' in title) or ('+' in title) or ('paramountplus' in title):
			xbmc.log(('### PREMIUM TITLE ### ' + str(title)),level=log_level)
			continue
		if title.lower() in rejects:
			xbmc.log(('### REJECT TITLE ### ' + str(title)),level=log_level)
			continue
		if title not in cats:
			cats.append(title)
		streamUrl = 'plugin://plugin.video.rokuchannel?mode=3&url=' + urllib.parse.quote_plus(apiUrl) + '&name=' + urllib.parse.quote_plus(title)# + '&count=' + urllib.parse.quote_plus(str(count))
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmc.log('CATS: ' + str(cats),level=log_level)
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	#xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#3
def channels(apiUrl, name):
	with open(os.path.join(addon_path_profile, 'api.json'), 'rb') as f:
		data = json.load(f)
	for count, item in enumerate(data['collections']):
		if item['title'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			c = count
			for count, item in enumerate(data['collections'][c]['view']):
				title = str(item['content']['title'])
				#xbmc.log(('TITLE: ' + str(title)),level=log_level)
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
					li.addContextMenuItems([('Movie Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url))),('Save Item', 'RunPlugin(%s?mode=82&url=%s&name=%s&data=%s&image=%s)' % (sys.argv[0], (url), urllib.parse.quote_plus(title), (contentType), (image)))])
					xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
				if contentType == 'series':
					url = url + '%3Fexpand%3Dseasons.episodes.descriptions.40%252Cseasons.episodes.descriptions.60%252Cseasons.episodes.episodeNumber%252Cseasons.episodes.seasonNumber%252Cseasons.episodes.images%252Cseasons.episodes.imageMap.grid%252Cseasons.episodes.indicators%252Cseasons.episodes.releaseDate%252Cseasons.episodes.viewOptions%252Cepisodes.episodeNumber%252Cepisodes.seasonNumber%252Cepisodes.viewOptions%26filter%3DcategoryObjects%253AgenreAppropriate%252520eq%252520true%252Cseasons.episodes%253A%2528not%252520empty%2528viewOptions%2529%2529%253Aall%26featureInclude%3Dbookmark%252Cwatchlist%252ClinearSchedule'
					streamUrl = 'plugin://plugin.video.rokuchannel?mode=12&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(name)
					li = xbmcgui.ListItem(title)
					li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot})
					li.setArt({'thumb':image,'fanart':fanart})
					## Add Context Item
					#li.addContextMenuItems([('Show Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url)))])
					li.addContextMenuItems([('Show Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url))),('Save Item', 'RunPlugin(%s?mode=82&url=%s&name=%s&data=%s&image=%s)' % (sys.argv[0], (url), urllib.parse.quote_plus(title), (contentType), (image)))])
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
def get_pid(url,sid):
	csrfUrl = 'https://therokuchannel.roku.com/watch/' + sid
	response = s.get(csrfUrl)
	csrf = re.compile('csrf: "(.+?)"').findall(str(response.text))[0]
	xbmc.log('CSRF: ' + str(csrf),level=log_level)
	response = s.get(url)
	xbmc.log('PID RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('PID R.COOKIE: ' + str(response.cookies),level=log_level)
	xbmc.log('PID RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	playId = data['viewOptions'][0]['playId']
	xbmc.log('PID PLAYID: ' + str(playId),level=log_level)
	for count, item in enumerate(data['viewOptions'][0]['media']['videos']):
		if 'DASH' in item['videoType']:
			xbmc.log(('##### DASH #####'),level=log_level)
			mediaType = 'mpeg-dash'
			make_json_data(sid,playId,mediaType,csrf)
	json_data = {
		'rokuId': sid,
		'playId': playId,
		#'mediaFormat': mediaType,
		'mediaFormat': 'm3u',
		'drmType': 'widevine',
		'quality': 'fhd',
		'bifUrl': None,
		'adPolicyId': '',
		'providerId': 'rokuavod',
	}
	xbmc.log('JSON_DATA: ' + str(json_data),level=log_level)
	PLAY(json_data,csrf,sid)


#9
def get_live(url,name):
	response = s.get(api1Url)
	data = json.loads(response.text)
	retry = 0
	while not 'Live TV' in response.text:
		response = s.get(api1Url)
		retry +=1
		time.sleep(5)
		xbmc.log('RETRY: ' + str(retry),level=log_level)
		if retry > 5:
			xbmcgui.Dialog().notification(addonname, 'Live TV API Not Available. Please Try Again Later.', defaultimage, time=5000, sound=False)
			sys.exit()
	xbmc.log(('LIVE TV API FOUND'),level=log_level)
	for count, item in enumerate (data['view']):
		if item['title'] == 'Live TV':
			xbmc.log(('TITLE: ' + str(item['title'])),level=log_level)
			xbmc.log(('LIVE TV FOUND'),level=log_level)
			#for count, item in enumerate(item['meta']):
			#if item['title'] == 'Live TV':
			pageId = item['meta']['id']
			xbmc.log('PAGEID: ' + str(pageId),level=log_level)
			Live = 'https://therokuchannel.roku.com/api/v2/homescreen/pages/' + pageId + '/rendered?limit=99'
	#Live = 'https://therokuchannel.roku.com/api/v2/homescreen/pages/w.xWvaD8v8B1HPbvLeY9pWCq4VZGGwoktG5NA1w1WgCVYNBL8D2M/rendered?limit=99'
	response = s.get(Live)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	cats = []
	for count, item in enumerate(data['collections']):
		if 'title' not in item:
			xbmc.log('No Title',level=log_level)
			continue
		title = str(item['title'])# + ' - ' + str(count)
		if 'layout' in item:
			xbmc.log(('### SKIP PREMIUM ###' + str(title)),level=log_level)
			continue
		if 'Premium' in title:
			xbmc.log(('### PREMIUM TITLE ### ' + str(title)),level=log_level)
			continue
		if 'Recently' in title:
			continue
		if title not in cats:
			cats.append(title)
		streamUrl = 'plugin://plugin.video.rokuchannel?mode=15&url=' + urllib.parse.quote_plus(Live) + '&name=' + urllib.parse.quote_plus(title)# + '&count=' + urllib.parse.quote_plus(str(count))
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmc.log('CATS: ' + str(cats),level=log_level)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#12
def get_episodes(url,name):
	response = s.get(url)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
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
	response = s.get(url)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['collections']):
		if item['title'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			c = count
			for count, item in enumerate(data['collections'][c]['view']):
				title = str(item['content']['title'])
				if title == 'See all' or title == 'See All':
					continue
				image = item['content']['imageMap']['grid']['path']
				contentType = (item['content']['type'])
				fanart = image
				sid = (item['content']['meta'])['sid']
				if 'features' in item:
					#xbmc.log('SCHED LENGTH: ' + str(len(item['features']['linearSchedule'])),level=log_level)
					onNow = item['features']['linearSchedule'][0]['content']['title']
					endDateTime = item['features']['linearSchedule'][0]['end']
					NOW = time.time()
					timeLeft = (int((int(endDateTime) - int(NOW))))
					remaining = ends(endDateTime)
					duration = item['features']['linearSchedule'][0]['duration']
					if len(item['features']['linearSchedule']) >= 2:
						onNext = item['features']['linearSchedule'][1]['content']['title']
					else:
						onNext = 'Not Available'
					plot = '[B]' + onNow + '[/B] ' + ' (Ends in ' + str(remaining) + ')\n\nNext: ' + '[B]' + onNext + '[/B]'
				else:
					plot = '';timeLeft = ''
				url = 'https://therokuchannel.roku.com/api/v2/homescreen/content/' + urllib.parse.quote_plus('https://content.sr.roku.com/content/v1/roku-trc/') + sid
				streamUrl = 'plugin://plugin.video.rokuchannel?mode=6&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(sid)
				li = xbmcgui.ListItem(title)
				info = li.getVideoInfoTag()
				#info.setPlot(plot)
				#info.setDuration(timeLeft)
				#info.setPremiered(releaseDate)
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot})
				li.setArt({'thumb':image,'fanart':fanart})
				li.addContextMenuItems([('More Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url))),('Save Item', 'RunPlugin(%s?mode=82&url=%s&name=%s&data=%s&image=%s)' % (sys.argv[0], (url), urllib.parse.quote_plus(title), (contentType), (image)))])
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
		xbmc.log('SEARCH: ' + str(search),level=log_level)
		json_data = {'query': search.replace(' ','%20'),}
		url = 'https://therokuchannel.roku.com'# + search# + '%29%20AND%20mediatype%3A%28audio%29&page=1'
		response = s.get(url)
		csrf = re.compile('csrf: "(.+?)"').findall(str(response.text))[0]
		headers = {
		'csrf-token': csrf,
		'referer': 'https://therokuchannel.roku.com',
		'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
		}
		xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
		cookies = dict(response.cookies)
		xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
		response = s.post('https://therokuchannel.roku.com/api/v1/search', headers=headers, cookies=cookies, json=json_data)
		xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
		xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
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
				li.addContextMenuItems([('More Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url))),('Save Item', 'RunPlugin(%s?mode=82&url=%s&name=%s&data=%s&image=%s)' % (sys.argv[0], (url), urllib.parse.quote_plus(title), (contentType), (image)))])
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
	xbmc.log('START_PATH: ' + str(start_path),level=log_level)
	for path,dirs,files in os.walk(start_path):
		for filename in files:
			if '.txt' in filename:
				title = urllib.parse.unquote_plus(filename).split('-')[0]
				#xbmc.log('SAVED ITEM TITLE: ' + str(title),level=log_level)
				with open(os.path.join(addon_path_profile, filename), 'r') as f:
					items = f.read()
				info = re.findall(r"'(.*?)'", items)
				url = info[0]
				image = info[2]
				sid = info[2].split('/')[8]
				#xbmc.log('SID: ' + str(sid),level=log_level)
				contentType = info[1]
				#xbmc.log('CONTENTTYPE: ' + str(contentType),level=log_level)
				plot = contentType.title()
				if (contentType == 'movie') or (contentType == 'livefeed'):
					mode = 6; folder = False
				if contentType == 'series':
					mode = 12; folder = True
				streamUrl = 'plugin://plugin.video.rokuchannel?mode=' + str(mode) + '&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(sid)# + '&count=' + urllib.parse.quote_plus(str(count))
				li = xbmcgui.ListItem(title)
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot})
				li.setArt({'thumb':image,'fanart':image})
				## Add Context Item
				li.addContextMenuItems([('More Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url))),('Delete Item', 'RunPlugin(%s?mode=88&url=%s&name=%s&data=%s&image=%s)' % (sys.argv[0], (url), urllib.parse.quote_plus(title), (contentType), (image)))])
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=folder)
	#xbmc.log('INFO 0: ' + str(info[0]),level=log_level)
	#xbmc.log('INFO 1: ' + str(info[1]),level=log_level)
	#xbmc.log('INFO 2: ' + str(info[2]),level=log_level)
	xbmcplugin.setContent(addon_handle, 'episodes')
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#82
def save_item(url,name,data,image):
	xbmc.log('SAVE ITEM NAME: ' + str(name),level=log_level)
	#xbmc.log('SAVE ITEM: ' + str(url),level=log_level)
	#xbmc.log('SAVE ITEM CONTENTTYPE: ' + str(data),level=log_level)
	second = urllib.parse.quote_plus(url.split('/',7)[-1])
	#xbmc.log('SECOND: ' + str(second),level=log_level)
	infoUrl = 'https://therokuchannel.roku.com/api/v2/homescreen/content/' + second
	xbmc.log('INFOURL: ' + str(infoUrl),level=log_level)
	file_name = urllib.parse.quote_plus(name) + '-' + data + '.txt'
	with open(os.path.join(addon_path_profile, file_name), "w") as text_file:
		text_file.write(f"{infoUrl,data,image}")
	xbmcgui.Dialog().notification(addonname, name + ' Saved', defaultimage, time=3000, sound=False)
	sys.exit()


#85
def info(url):
	xbmcgui.Dialog().notification(addonname, 'Fetching Info...', defaultimage, time=3000, sound=False)
	second = urllib.parse.quote_plus(url.split('/',7)[-1])
	xbmc.log('SECOND: ' + str(second),level=log_level)
	infoUrl = 'https://therokuchannel.roku.com/api/v2/homescreen/content/' + second
	xbmc.log('INFOURL: ' + str(infoUrl),level=log_level)
	response = s.get(infoUrl)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	actors = []
	if 'credits' in data:
		for count, item in enumerate(data['credits']):
			if item['role'] == 'ACTOR':
				actors.append(item['name'])
		xbmc.log('ACTORS: ' + str(actors),level=log_level)
	genres = []
	for count, item in enumerate(data['genres']):
		genres.append(item.title())
	xbmc.log('GENRES: ' + str(genres),level=log_level)
	xbmc.log('DESCRIPTION LENGTH: ' + str(len(data['descriptions'])),level=log_level)
	if len(data['descriptions']) >= 1:
		descriptions = []
		for count, item in enumerate(data['descriptions']):
			descriptions.append(item)
		xbmc.log('DESCRIPTION: ' + str(descriptions),level=log_level)
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
	xbmc.log('DESCRIPTION: ' + str(description),level=log_level)
	if data['type'] == 'series':
		episodes = len(data['episodes'])
		xbmc.log('EPISODES: ' + str(episodes),level=log_level)
		info = info + '\n\n' + str(episodes) + ' Episodes'
	xbmcgui.Dialog().textviewer(title, info)


#88
def delete_item(url,name,data,image):
	xbmc.log('DELETE URL: ' + str(url),level=log_level)
	xbmc.log('DELETE NAME: ' + str(name),level=log_level)
	xbmc.log('DELETE DATA: ' + str(data),level=log_level)
	xbmc.log('DELETE IMAGE: ' + str(image),level=log_level)
	yes = xbmcgui.Dialog().yesno(addonname ,'Are you sure you want to delete ' + name + '?  This action cannot be reversed!')
	if not yes:
		xbmc.log('NOT YES',level=log_level)
		sys.exit()
	else:
		xbmc.log('YES',level=log_level)
		file_name = os.path.join(addon_path_profile, urllib.parse.quote_plus(name) + '-' + data + '.txt')
		xbmc.log('FILE_NAME: ' + str(file_name),level=log_level)
		if os.path.exists(os.path.join(addon_path_profile,file_name)):
			os.remove(file_name)
			xbmcgui.Dialog().notification(addonname, name + ' Has been deleted.', defaultimage, time=3000, sound=False)
			xbmc.executebuiltin("Container.Refresh")
			sys.exit()
		else:
			xbmcgui.Dialog().notification(addonname, name.split('--')[0] + ' Already deleted.', defaultimage, time=3000, sound=False)


def make_json_data(sid,playId,mediaType,csrf):
	json_data = {
		'rokuId': sid,
		'playId': playId,
		'mediaFormat': mediaType,
		#'mediaFormat': 'm3u',
		'drmType': 'widevine',
		'quality': 'fhd',
		'bifUrl': None,
		'adPolicyId': '',
		'providerId': 'rokuavod',
	}
	xbmc.log('JSON_DATA: ' + str(json_data),level=log_level)
	PLAY(json_data,csrf,sid)


def getTargetIds(jsonData):
	xbmc.log(('Check for key'),level=log_level)
	data = json.loads(jsonData)
	xbmc.log('JSONDATA: ' + str(data),level=log_level)
	if 'ssaiStreamUrl' not in data:
		#raise ValueError("No target in given data")
		xbmc.log(('Key does not exist.'),level=log_level)
		return jsonData


def ends(endDateTime):
	NOW = time.time()
	epochDif = (int((int(endDateTime) - int(NOW))))
	#xbmc.log(('EPOCH_DIF: ' + str(epochDif)),level=log_level)
	if epochDif < 0:
		epochDif = epochDif + 7200
	remaining = str(datetime.timedelta(seconds=epochDif))
	#xbmc.log(('REMAINING: ' + str(remaining)),level=log_level)
	return remaining


#99
def PLAY(json_data,csrf,sid):
	referer = 'https://therokuchannel.roku.com/watch/' + sid

	headers = {
		#'accept': '*/*',
		#'accept-language': 'en-US,en;q=0.6',
		# Already added when you pass json=
		#'content-type': 'application/json',
		'csrf-token': csrf,
		'referer': referer,
		'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
	}
	#xbmc.log('USER-AGENT: ' + str(ua),level=log_level)
	response = s.post('https://therokuchannel.roku.com/api/v3/playback', headers=headers, json=json_data)
	xbmc.log('PLAYBACK RESPONSE CODE: ' + str(response.status_code),level=log_level)
	retry = 0
	while response.status_code != 200:
		response = s.post('https://therokuchannel.roku.com/api/v3/playback', headers=headers, json=json_data)
		retry +=1
		time.sleep(5)
		xbmc.log('RETRY: ' + str(retry),level=log_level)
		if retry > 5:
			sys.exit()
	page = response.text
	xbmc.log('PLAYBACK RESPONSE LENGTH: ' + str(len(page)),level=log_level)
	#xbmc.log('PLAYBACK RESPONSE: ' + str(page),level=log_level)
	data = json.loads(page)
	#xbmc.log('DATA: ' + str(data),level=log_level)
	url = data['url']
	xbmc.log('URL: ' + str(url),level=log_level)
	url = data['playbackMedia']['videos'][0]['url']
	xbmc.log('STREAM URL: ' + str(url),level=log_level)
	if 'drm' in data:
		lic_url = data['drm']['widevine']['licenseServer']
		xbmc.log('LIC_URL: ' + str(lic_url),level=log_level)
	else:
		lic_url = ''
		url = url.split('&')[0]
	if 'mpd' in url:
		headers = headers

		#lic_url = f"https://wv-license.sr.roku.com/license/v1/license/wv"
		license_key = f"{lic_url}"#"|{headers}&Content-Type=application/octet-stream|R{{SSM}}|"
		license_key = lic_url + '|User-Agent=' + ua + '&Referer=' + referer +'/&Origin=' + referer + '&csrf-token=' + csrf + '&Content-Type= |R{SSM}|'
		xbmc.log('LICENSE_KEY: ' +str(license_key),level=log_level)
		is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
		if not is_helper.check_inputstream():
			sys.exit()

		listitem = xbmcgui.ListItem(path=url)
		xbmc.log('### MPD SETRESOLVEDURL ###',level=log_level)
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
		xbmc.log('URL: ' + str(url), level=log_level)
		sys.exit()
	else:

		#license_key = f"{lic_url}"#"|{headers}&Content-Type=application/octet-stream|R{{SSM}}|"
		#license_key = lic_url + '|User-Agent=' + ua + '&Referer=' + referer +'/&Origin=' + referer + '&csrf-token=' + csrf + '&Content-Type= |R{SSM}|'
		#xbmc.log('LICENSE_KEY: ' +str(license_key),level=log_level)
		#is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
		#if not is_helper.check_inputstream():
			#sys.exit()
		listitem = xbmcgui.ListItem(path=url)
		xbmc.log('### M3U SETRESOLVEDURL ###',level=log_level)
		if hls != 'false':
			xbmc.log('### USE INPUTSTREAM FOR HLS ###',level=log_level)
			listitem.setProperty('IsPlayable', 'true')
			listitem.setProperty('inputstream', 'inputstream.adaptive')
			listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
			listitem.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={ua}")
			listitem.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={ua}")
		#listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
		#listitem.setProperty('inputstream.adaptive.license_key', license_key)
		listitem.setMimeType('application/vnd.apple.mpegurl')
		#listitem.setContentLookup(False)
		xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
		xbmc.log('URL: ' + str(url), level=log_level)
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
	mode = int(params["mode"])
except:
	pass

xbmc.log("Mode: " + str(mode),level=log_level)
xbmc.log("URL: " + str(url),level=log_level)
xbmc.log("Name: " + str(name),level=log_level)
#xbmc.log("Count: " + str(count),level=log_level)

if mode == None or url == None or len(url) < 1:
	xbmc.log(('Main Menu'),level=log_level)
	main_menu()
elif mode == 0:
	xbmc.log(('Get Categories'),level=log_level)
	categories(apiUrl)
elif mode == 3:
	xbmc.log(("Get Channels"),level=log_level)
	channels(url,name)
elif mode == 6:
	xbmc.log(("Get JSON Data"),level=log_level)
	get_pid(url,name)
elif mode == 9:
	xbmc.log(("Get Live Channels"),level=log_level)
	get_live(url,name)
elif mode == 12:
	xbmc.log(("Get Episodes"),level=log_level)
	get_episodes(url,name)
elif mode == 15:
	xbmc.log(("Get Live Channel"),level=log_level)
	live_channels(url,name)
elif mode == 20:
	xbmc.log("Search",level=log_level)
	search()
elif mode == 25:
	xbmc.log(("Get Saved Items"),level=log_level)
	saved_items(url,name)
elif mode == 82:
	xbmc.log(("Save Item"),level=log_level)
	save_item(url,name,data,image)
elif mode == 85:
	xbmc.log(("Get Movie Info"),level=log_level)
	info(url)
elif mode == 88:
	xbmc.log(("Delete Item"),level=log_level)
	delete_item(url,name,data,image)
elif mode == 99:
	xbmc.log("Play Stream", level=log_level)
	PLAY(name,url)

xbmcplugin.endOfDirectory(addon_handle)
