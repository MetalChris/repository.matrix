#!/usr/bin/python
#
#
# Written by MetalChris 2024.04.30
# Released under GPL(v2 or later)

import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, re, os
import json
import time
from time import strftime, localtime
import requests
import datetime


today = time.strftime("%Y-%m-%d")


addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'video')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='plugin.video.xumoplay')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
settings = xbmcaddon.Addon(id="plugin.video.xumoplay")
apiUrl = 'https://valencia-app-mds.xumo.com/v2/'
devUrl = 'https://play-dev.xumo.com/_next/data/-tJ2heLKohd5CJOzD6cKF/'
showUrl = 'https://play.xumo.com/_next/data/vYloRlruhjCb1nMLv-3-p/tv-shows/'
movieUrl = 'https://play.xumo.com/_next/data/vYloRlruhjCb1nMLv-3-p/free-movies/'
baseUrl = 'https://play.xumo.com/'
plugin = "Xumo Play"
local_string = xbmcaddon.Addon(id='plugin.video.xumoplay').getLocalizedString
defaultimage = 'special://home/addons/plugin.video.xumoplay/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.xumoplay/resources/media/fanart.jpg'

__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")
sys.path.append(__resource__)

from utilities import *

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 2
else:
	log_level = 1
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)

xbmc.log('TODAY: ' + str(today),level=log_level)
xbmc.log('NOW: ' + str(round(time.time())),level=log_level)
xbmc.log('UTC Offset: ' + str(-time.timezone),level=log_level)

offset = -time.timezone
NOW = (round(time.time()) - offset)
xbmc.log('NOW_OFFSET: ' + str(NOW),level=log_level)

s = requests.Session()


def genres(apiUrl):
	xbmc.log(('GET GENRES'),level=log_level)
	response = s.get(apiUrl + 'proxy/channels/list/10006.json', headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	data = json.loads(response.text);genres = []#;images = []
	for count, item in enumerate(data['channel']['item']):
		genre = item['genre'][0]['value']
		if genre not in genres:
			genres.append(genre)
			#slug = item['guid']['value']
			#image = 'https://image.xumo.com/v1/channels/channel/' + str(slug) + '/600x600.png?type=color_onBlack'
			#images.append(image)
	xbmc.log('GENRES: ' + str(genres),level=log_level)
	for genre in genres:
		title = str(genre)
		#image = image
		streamUrl = 'plugin://plugin.video.xumoplay?mode=3&url=' + urllib.parse.quote_plus(apiUrl) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	addDir2('On Demand TV Shows', baseUrl + 'tv-shows'
	, 18, defaultimage, defaultfanart, infoLabels={'plot':'Stream unlimited TV shows. Watch action, comedy, drama, romance, and timeless classics from our vast collection on Local Now.'})
	addDir2('On Demand Movies', baseUrl + 'free-movies'
	, 18, defaultimage, defaultfanart, infoLabels={'plot':'Stream unlimited free movies. Watch action, comedy, drama, romance, blockbuster films and more on Local Now.'})
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#3
def channels(apiUrl, name):
	response = s.get(apiUrl + 'proxy/channels/list/10006.json', headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['channel']['item']):
		if item['genre'][0]['value'] != name:
			continue
		title = str(item['title'])
		if title == 'Local Now':
			continue
		description = item['description']
		slug = item['guid']['value']
		image = 'https://image.xumo.com/v1/channels/channel/' + str(slug) + '/600x600.webp?type=color_onBlack'
		#xbmc.log('IMAGE: ' + str(image),level=log_level)
		url = apiUrl + 'channels/channel/' + str(slug) + '/broadcast.json?hour=3'
		streamUrl = 'plugin://plugin.video.xumoplay?mode=9&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.addContextMenuItems([('Program Info', 'RunPlugin(%s?mode=82&url=%s)' % (sys.argv[0], (streamUrl)))])
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':description})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


def local_now(name,url):
	xbmc.log(('##### LOCAL NOW #####'),level=log_level)
	response = s.get('http://checkip.dyndns.com/', headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	ipAddress = re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(response.text).group(1)
	xbmc.log('IP: ' + str(ipAddress),level=log_level)
	zipUrl = 'https://ipinfo.io/' + ipAddress + '/json'
	response = s.get(zipUrl, headers = {'User-Agent': ua})
	xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	data = json.loads(response.text)
	zipCode = data['postal']
	xbmc.log('ZIPCODE: ' + str(zipCode),level=log_level)
	response = s.get(url, headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	jsob = (str(response.text))
	data = json.loads(jsob)
	assetId = data['assets'][0]['id']
	streamUrl = apiUrl + 'assets/asset/' + assetId + '.json?f=providers&f=connectorId&f=keywords'
	response = s.get(streamUrl, headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	data = json.loads(response.text)
	name = data['providers'][0]['title']
	stream = data['providers'][0]['sources'][0]['uri']
	url = stream.replace('30101', '75783')
	xbmc.log('STREAM: ' + str(url),level=log_level)
	response = s.get(url, headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	stream = response.text[1:-1] + '|User-Agent=' + ua
	PLAY(name,stream)
	sys.exit()


#6
def get_stream(name,url):
	#xbmc.log('TOKEN: ' + str(token),level=log_level)
	response = s.get(url, headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	jsob = (str(response.text))
	data = json.loads(jsob)
	stream = data['video_m3u8']# + '&ads.xumo_channelId=' +
	PLAY(name,stream)

#9
def live(name,url):
	xbmc.log('LIVE URL: ' + str(url),level=log_level)
	#channel = url.split('/')[-2]
	if name == 'Local Now':
		xbmc.log(('##### LOCAL NOW #####'),level=log_level)
		local_now(name,url)
	response = s.get(url, headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	data = json.loads(response.text)
	if 'ssaiStreamUrl' in data:
		xbmc.log(('### SSAI URL FOUND ###.'),level=log_level)
		stream = data['ssaiStreamUrl']
		PLAY(name,stream)
	else:
		assetId = data['assets'][0]['id']
		streamUrl = apiUrl + 'assets/asset/' + assetId + '.json?f=providers&f=connectorId&f=keywords'
		xbmc.log('LIVE API URL: ' + str(streamUrl),level=log_level)
		response = s.get(streamUrl, headers = {'User-Agent': ua})
		xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
		xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
		#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
		data = json.loads(response.text)
		name = data['providers'][0]['title']
		stream = data['providers'][0]['sources'][0]['uri']# + '&ads.xumo_channelId=' + channel
		#url = stream.partition('&')[0]
		#xbmc.log('### URL: ' + str(url),level=log_level)
		PLAY(name,stream)


def getTargetIds(jsonData):
	xbmc.log(('Check for key'),level=log_level)
	data = json.loads(jsonData)
	xbmc.log('JSONDATA: ' + str(data),level=log_level)
	if 'ssaiStreamUrl' not in data:
		#raise ValueError("No target in given data")
		xbmc.log(('Key does not exist.'),level=log_level)
		return jsonData


#12
def shows(name,url):
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob)#;genres = []
	for count, item in enumerate(data['props']['pageProps']['page']['rails']):
		if item['category']['name'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			c = count
			for count, item in enumerate(data['props']['pageProps']['page']['rails'][c]['cards']):
				title = item['title']
				#xbmc.log(('TITLE: ' + str(title)),level=log_level)
				slug = item['slug']
				showId = item['id']
				url = showUrl + slug + '/' + showId + '.json'
				image = item['image'] + '/640x360.jpg'
				fanart = image.replace('/400x600', '1280x720')
				streamUrl = 'plugin://plugin.video.xumoplay?mode=15&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(name)
				li = xbmcgui.ListItem(title)
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
				li.setArt({'thumb':image,'fanart':fanart})
				li.addContextMenuItems([('Show Info', 'RunPlugin(%s?mode=88&url=%s)' % (sys.argv[0], (url)))])
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#15
def episodes(name,url):
	xbmc.log('URL 15: ' + str(url),level=log_level)
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(response.text)
	total = len(data['pageProps']['page']['entity']['seasons'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for count, item in enumerate(data['pageProps']['page']['entity']['seasons']):
		season = str(item['season']['number'])
		xbmc.log('SEASON: ' + str(season),level=log_level)
		for card, episode in enumerate(item['cards']):
			title = str(season) + 'x' + str(episode['episode']) + ' ' + episode['title']
			image = episode['image'] + '/640x360.jpg'
			fanart = image.replace('640x360', '1280x720')
			description = episode['description']
			episodeId = episode['id']
			url = apiUrl + 'assets/asset/' + str(episodeId) + '.json?f=providers&f=connectorId&f=keywords'
			streamUrl = 'plugin://plugin.video.xumoplay?mode=24&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
			li = xbmcgui.ListItem(title)
			li.setProperty('IsPlayable', 'true')
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':description})
			li.setArt({'thumb':image,'fanart':fanart})
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#18
def mcats(name,url):
	if 'tv-shows' in url:
		mode = '12'
	else:
		mode = '21'
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob);genres = []
	for count, item in enumerate(data['props']['pageProps']['page']['rails']):
		genre = item['category']['name']
		if genre not in genres:
			genres.append(genre)
	xbmc.log('GENRES: ' + str(genres),level=log_level)
	for genre in genres:
		title = genre
		streamUrl = 'plugin://plugin.video.xumoplay?mode=' + mode + '&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#21
def movies(name,url):
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob)#;genres = []
	for count, item in enumerate(data['props']['pageProps']['page']['rails']):
		if item['category']['name'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			c = count
			for count, item in enumerate(data['props']['pageProps']['page']['rails'][c]['cards']):
				title = item['title']
				movieId = item['id']
				slug = item['slug']
				url = apiUrl + 'assets/asset/' + str(movieId) + '.json?f=providers&f=connectorId&f=keywords'
				image = item['image'] + '/400x600.webp'
				#fanart = image.replace('/400x600.webp','1280x720.jpg')
				streamUrl = 'plugin://plugin.video.xumoplay?mode=24&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(name)
				url = baseUrl + 'free-movies/' + slug + '/' + movieId
				li = xbmcgui.ListItem(title)
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
				li.setArt({'thumb':image,'fanart':defaultfanart})
				li.addContextMenuItems([('Movie Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url)))])
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#24
def movie_stream(url):
	response = s.get(url, headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	data = json.loads(response.text)
	name = data['providers'][0]['title']
	stream = data['providers'][0]['sources'][0]['uri']# + '&ads.xumo_channelId=' + channel
	PLAY(name,stream)


#82
def desc(url):
	channel = url.split('/')[-2]
	xbmc.log('CHANNEL: ' + str(channel),level=log_level)
	xbmcgui.Dialog().notification(addonname, 'Fetching Show Info...', defaultimage, time=3000, sound=False)
	xbmc.log('DESC URL: ' + str(url),level=log_level)
	xbmc.log(('GET DESCRIPTION'),level=log_level)
	response = s.get('https://play.xumo.com/')
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	xbmc.log('JSOB LENGTH: ' + str(len(jsob)),level=log_level)
	data = json.loads(jsob)
	for count, item in enumerate(data['props']['pageProps']['page']['channels']):
		#xbmc.log('CHANNEL: ' + str(channel),level=log_level)
		#xbmc.log('ITEMID: ' + str(item['id']),level=log_level)
		if str(item['id']) == channel:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			#c = count
			#xbmc.log('ITEM: ' + str(item),level=log_level)
			title = item['program'][0]['title']
			description = item['program'][0]['description']
			ends = item['program'][0]['ends']
			xbmc.log('ENDS: ' + str(ends),level=log_level)
			epochDif = (int((int(ends) - int(time.time()))))
			xbmc.log(('EPOCH_DIF: ' + str(epochDif)),level=log_level)
			remaining = str(datetime.timedelta(seconds=epochDif))
			xbmc.log(('REMAINING: ' + str(remaining)),level=log_level)
			info = description + '\n\n Time Remaining: ' + remaining# + '  ' + '\n\n' + 'Next: ' + description2
			xbmc.log('DESCRIPTION: ' + str(description),level=log_level)
			program = len(item['program'])
			xbmc.log('PROGRAM: ' + str(program),level=log_level)
			if program > 1:
				title2 = item['program'][1]['title']
				description2 = item['program'][1]['description']
				info = description + '\n\nTime Remaining: ' + remaining + '\n\n' + 'Next: ' + title2 + ' - ' + description2
			xbmcgui.Dialog().textviewer(title, info)


#85
def info(url):
	slugs = url.split('/')
	xbmc.log('SLUGS: ' + str(slugs),level=log_level)
	url = movieUrl + slugs[-2] + '/' + slugs[-1] + '.json?slug=' + slugs[-2] + '?slug=' + slugs[-1]
	xbmcgui.Dialog().notification(addonname, 'Fetching Movie Info...', defaultimage, time=3000, sound=False)
	xbmc.log('URL: ' + str(url),level=log_level)
	xbmc.log(('GET DESCRIPTION'),level=log_level)
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	description = data['pageProps']['page']['entity']['description']
	title = data['pageProps']['page']['entity']['title']
	year = data['pageProps']['page']['entity']['year']
	duration = data['pageProps']['page']['entity']['duration']
	runtime = str(datetime.timedelta(seconds=duration))
	info = str(description) + '\n\nReleased: ' + str(year) + '\n\nDuration: ' + str(runtime)
	xbmc.log('DESCRIPTION: ' + str(description),level=log_level)
	xbmcgui.Dialog().textviewer(title, info)


#88
def vod_desc(url):
	xbmcgui.Dialog().notification(addonname, 'Fetching Program Info...', defaultimage, time=3000, sound=False)
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	data = json.loads(response.text)
	title = data['pageProps']['page']['entity']['title']
	description = data['pageProps']['page']['entity']['description']
	duration = data['pageProps']['page']['entity']['duration']
	runTime = str(datetime.timedelta(seconds=duration))
	info = description + '\n\n Runtime: ' + runTime# + '  ' + '\n\n' + 'Next: ' + description2
	xbmc.log('DESCRIPTION: ' + str(description),level=log_level)
	xbmcgui.Dialog().textviewer(title, info)


#99
def PLAY(name,url):
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log('### SETRESOLVEDURL ###',level=log_level)
	listitem.setProperty('IsPlayable', 'true')
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
slug = None

try:
	url = urllib.parse.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.parse.unquote_plus(params["name"])
except:
	pass
try:
	slug = urllib.parse.unquote_plus(params["slug"])
except:
	pass
try:
	mode = int(params["mode"])
except:
	pass

xbmc.log("Mode: " + str(mode),level=log_level)
xbmc.log("URL: " + str(url),level=log_level)
xbmc.log("Name: " + str(name),level=log_level)

if mode == None or url == None or len(url) < 1:
	xbmc.log(("Get Settings"),level=log_level)
	genres(apiUrl)
elif mode == 3:
	xbmc.log(("Get Channels"),level=log_level)
	channels(url,name)
elif mode == 6:
	xbmc.log(("Get Stream"),level=log_level)
	get_stream(name,url)
elif mode == 9:
	xbmc.log(("Get Live Streams"),level=log_level)
	live(name,url)
elif mode == 12:
	xbmc.log(("Get Shows"),level=log_level)
	shows(name,url)
elif mode == 15:
	xbmc.log(("Get Episodes"),level=log_level)
	episodes(name,url)
elif mode == 18:
	xbmc.log(("Get Movie Categories"),level=log_level)
	mcats(name,url)
elif mode == 21:
	xbmc.log(("Get Movies"),level=log_level)
	movies(name,url)
elif mode == 24:
	xbmc.log(("Get Movie Stream"),level=log_level)
	movie_stream(url)
elif mode == 82:
	xbmc.log(("Get Show Info"),level=log_level)
	desc(url)
elif mode == 85:
	xbmc.log(("Get Movie Info"),level=log_level)
	info(url)
elif mode == 88:
	xbmc.log(("Get VOD Show Info"),level=log_level)
	vod_desc(url)
elif mode == 99:
	xbmc.log("Play Stream", level=log_level)
	PLAY(name,url)

xbmcplugin.endOfDirectory(addon_handle)
