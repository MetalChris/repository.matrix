#!/usr/bin/python
#
#
# Written by MetalChris 2025.01.06
# Released under GPL(v2 or later)

import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, re, os
import json
import time
from time import strftime, localtime
import requests
import datetime
import inputstreamhelper
from random import randint


today = time.strftime("%Y-%m-%d")


addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'video')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id='plugin.video.xumoplay')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
settings = xbmcaddon.Addon(id="plugin.video.xumoplay")
apiUrl = 'https://valencia-app-mds.xumo.com/v2/'
devUrl = 'https://play-dev.xumo.com/_next/data/-tJ2heLKohd5CJOzD6cKF/'
showUrl = 'https://play.xumo.com/_next/data/vYloRlruhjCb1nMLv-3-p/tv-shows/'
movieUrl = 'https://play.xumo.com/_next/data/vYloRlruhjCb1nMLv-3-p/free-movies/'
vodUrl = 'https://play.xumo.com/_next/data/'
baseUrl = 'https://play.xumo.com/'
plugin = "Xumo Play"
local_string = xbmcaddon.Addon(id='plugin.video.xumoplay').getLocalizedString
defaultimage = 'special://home/addons/plugin.video.xumoplay/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.xumoplay/resources/media/fanart.jpg'

__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")
sys.path.append(__resource__)


CookieJson = (os.path.join(addon_path_profile, 'cookies.json'))

from utilities import *

confluence_views = [500,501,503,504,515]
force_views = settings.getSetting(id="force_views")
#hls = settings.getSetting(id='hls')
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
xbmc.log(('Xumo Play 05.30.2024 - 2024.04.17'),level=log_level)

xbmc.log('TODAY: ' + str(today),level=log_level)
xbmc.log('NOW: ' + str(round(time.time())),level=log_level)
xbmc.log('UTC Offset: ' + str(-time.timezone),level=log_level)

offset = -time.timezone
NOW = (round(time.time()) - offset)
xbmc.log('NOW_OFFSET: ' + str(NOW),level=log_level)

s = requests.Session()


def main_menu():
	addDir2('Saved Items', baseUrl + 'tv-shows', 55, defaultimage, defaultfanart, infoLabels={'plot':''})
	addDir2('Live Channels', apiUrl, 0, defaultimage, defaultfanart, infoLabels={'plot':''})
	addDir2('On Demand TV Shows', baseUrl + 'tv-shows', 18, defaultimage, defaultfanart, infoLabels={'plot':''})
	addDir2('On Demand Movies', baseUrl + 'free-movies', 18, defaultimage, defaultfanart, infoLabels={'plot':''})


def genres(apiUrl):
	#addDir2('Saved Items', baseUrl + 'tv-shows', 55, defaultimage, defaultfanart, infoLabels={'plot':''})
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
	xbmc.log('GENRES: ' + str(genres),level=log_level)
	for genre in genres:
		title = str(genre)
		streamUrl = 'plugin://plugin.video.xumoplay?mode=3&url=' + urllib.parse.quote_plus(apiUrl) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	#addDir2('On Demand TV Shows', baseUrl + 'tv-shows', 18, defaultimage, defaultfanart, infoLabels={'plot':''})
	#addDir2('On Demand Movies', baseUrl + 'free-movies', 18, defaultimage, defaultfanart, infoLabels={'plot':''})
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
		description = item['description']
		slug = item['guid']['value']
		#image = 'https://image.xumo.com/v1/channels/channel/' + str(slug) + '/600x600.webp?type=color_onBlack'
		image = 'https://image.xumo.com/v1/channels/channel/' + str(slug) + '/600x337.webp?type=channelTile'
		url = apiUrl + 'channels/channel/' + str(slug) + '/broadcast.json?hour=3'
		streamUrl = 'plugin://plugin.video.xumoplay?mode=9&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		#li.addContextMenuItems([('Program Info', 'RunPlugin(%s?mode=82&url=%s)' % (sys.argv[0], (streamUrl)))])
		li.addContextMenuItems([('Program Info', 'RunPlugin(%s?mode=82&url=%s)' % (sys.argv[0], (streamUrl))),('Save Item', 'RunPlugin(%s?mode=52&url=%s&name=%s&image=%s)' % (sys.argv[0], (streamUrl), urllib.parse.quote_plus(title + '--live'), (slug)))])
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':description})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
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
	if 'hasEmbeddedCaptions' in data['providers'][0]['sources'][0]:
		xbmc.log(('***** CAPTIONS *****'),level=log_level)
		#xbmc.log('CAPTIONS LENGTH: ' + str(len(data['providers'][0]['captions'])),level=log_level)
	#xbmc.log('CAPTIONS?: ' + str(data['providers'][0]['sources'][0]['hasEmbeddedCaptions']),level=log_level)
		if data['providers'][0]['sources'][0]['hasEmbeddedCaptions'] == True:
			if 'captions' in data['providers'][0]:
				captions = data['providers'][0]['captions'][1]['url']
				xbmc.log(('##### CAPTIONS #####'),level=log_level)
	else:
		captions = ''
	url = stream.replace('30101', zipCode)
	xbmc.log('STREAM: ' + str(url),level=log_level)
	response = s.get(url, headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	stream = response.text[1:-1] + '|User-Agent=' + ua
	PLAY(name,stream,captions)
	sys.exit()


#9
def live(name,url):
	captions = None
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
		captions = ''
		PLAY(name,stream,captions)
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
		if 'hasEmbeddedCaptions' in data['providers'][0]['sources'][0]:
			xbmc.log(('***** CAPTIONS *****'),level=log_level)
			#xbmc.log('CAPTIONS LENGTH: ' + str(len(data['providers'][0]['captions'])),level=log_level)
		#xbmc.log('CAPTIONS?: ' + str(data['providers'][0]['sources'][0]['hasEmbeddedCaptions']),level=log_level)
			if data['providers'][0]['sources'][0]['hasEmbeddedCaptions'] == True:
				if 'captions' in data['providers'][0]:
					captions = data['providers'][0]['captions'][1]['url']
					xbmc.log(('##### CAPTIONS #####'),level=log_level)
		else:
			captions = ''
		#url = stream.partition('&')[0]
		#xbmc.log('### URL: ' + str(url),level=log_level)
		PLAY(name,stream,captions)


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
	xbmc.log(('URL 12: ' + str(url)),level=log_level)
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	prefix = url.partition('collection')[0]
	xbmc.log(('PREFIX: ' + str(prefix)),level=log_level)
	#jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(response.text)#;genres = []
	for count, item in enumerate(data['pageProps']['page']['rail']['cards']):
		title = item['title']
		slug = item['slug']
		showId = item['id']
		url = prefix + slug + '/' + showId + '.json?slug=' + slug + '&slug=' + showId
		image = item['image'] + '/640x360.jpg'
		fanart = image.replace('/400x600', '1280x720')
		streamUrl = 'plugin://plugin.video.xumoplay?mode=15&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(name)
		url = baseUrl + 'tv-shows/' + slug + '/' + showId
		li = xbmcgui.ListItem(title)
		#li.addContextMenuItems([('Show Info', 'RunPlugin(%s?mode=88&url=%s)' % (sys.argv[0], (url)))])
		li.addContextMenuItems([('Show Info', 'RunPlugin(%s?mode=88&url=%s)' % (sys.argv[0], (streamUrl))),('Save Item', 'RunPlugin(%s?mode=52&url=%s&name=%s&image=%s)' % (sys.argv[0], (streamUrl), urllib.parse.quote_plus(title + '--show'), (image)))])
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':image,'fanart':fanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmc.log(('IMAGE: ' + str(image)),level=log_level)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#15
def episodes(name,url):
	xbmc.log('URL 15: ' + str(url),level=log_level)
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['pageProps']['page']['entity']['seasons']):
		season = str(item['season']['number'])
		#xbmc.log('SEASON: ' + str(season),level=log_level)
		for card, episode in enumerate(item['cards']):
			title = str(season) + 'x' + str(episode['episode']) + ' ' + episode['title']
			image = episode['image'] + '/640x360.jpg'
			fanart = image.replace('640x360', '1280x720')
			description = episode['description']
			episodeId = episode['id']
			url = apiUrl + 'assets/asset/' + str(episodeId) + '.json?f=providers&f=connectorId&f=keywords'
			streamUrl = 'plugin://plugin.video.xumoplay?mode=24&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
			li = xbmcgui.ListItem(title)
			#li.addContextMenuItems([('Save Item', 'RunPlugin(%s?mode=52&url=%s&name=%s&image=%s)' % (sys.argv[0], (streamUrl), urllib.parse.quote_plus(title + '--episode'), (image)))])
			li.setProperty('IsPlayable', 'true')
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':description})
			li.setArt({'thumb':image,'fanart':fanart})
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


def get_id(baseUrl):
	xbmc.log(('GET BUILDID'),level=log_level)
	#response = s.get('https://play.xumo.com/live-guide/combat-war-channel')
	response = s.get('https://play.xumo.com')
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#buildId = re.compile('buildId":"(.+?)",').findall(response.text)[0]
	#xbmc.log('BUILDID: ' + str(buildId),level=log_level)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob)
	buildId = data['buildId']
	xbmc.log('BUILDID: ' + str(buildId),level=log_level)
	return(buildId)


#18
def mcats(name,url):
	buildId = get_id(url)
	if 'tv-shows' in url:
		url = vodUrl + buildId + '/tv-shows.json'
		mode = '27'
	else:
		url = vodUrl + buildId + '/free-movies.json'
		mode = '30'
	xbmc.log('URL 18: ' + str(url),level=log_level)
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text);genres = []#;catIds=[];slugs=[]
	for count, item in enumerate(data['pageProps']['page']['rails']):
		genre = item['category']['name']
		if genre not in genres:
			genres.append(genre)
	xbmc.log('GENRES: ' + str(genres),level=log_level)
	for genre in genres:
		title = genre
		if title == 'Recommended For You':
			continue
		streamUrl = 'plugin://plugin.video.xumoplay?mode=' + mode + '&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#21
def movies(name,url):
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	prefix = url.partition('collection')[0]
	xbmc.log(('PREFIX: ' + str(prefix)),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['pageProps']['page']['rail']['cards']):
		title = item['title']
		movieId = item['id']
		slug = item['slug']
		url = apiUrl + 'assets/asset/' + str(movieId) + '.json?f=providers&f=connectorId&f=keywords'
		image = item['image'] + '/400x600.webp'
		streamUrl = 'plugin://plugin.video.xumoplay?mode=24&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(name)
		url = baseUrl + 'free-movies/' + slug + '/' + movieId
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		#li.addContextMenuItems([('Movie Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url)))])
		li.addContextMenuItems([('Movie Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (streamUrl))),('Save Item', 'RunPlugin(%s?mode=52&url=%s&name=%s&image=%s)' % (sys.argv[0], (streamUrl), urllib.parse.quote_plus(title + '--movie'), (slug)))])
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#24
def movie_stream(url):
	captions = None
	response = s.get(url, headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	data = json.loads(response.text)
	name = data['providers'][0]['title']
	if 'hasEmbeddedCaptions' in data['providers'][0]['sources'][0]:
		xbmc.log(('***** CAPTIONS *****'),level=log_level)
		#xbmc.log('CAPTIONS LENGTH: ' + str(len(data['providers'][0]['captions'])),level=log_level)
	#xbmc.log('CAPTIONS?: ' + str(data['providers'][0]['sources'][0]['hasEmbeddedCaptions']),level=log_level)
		if data['providers'][0]['sources'][0]['hasEmbeddedCaptions'] == True:
			if 'captions' in data['providers'][0]:
				captions = data['providers'][0]['captions'][1]['url']
				xbmc.log(('##### CAPTIONS #####'),level=log_level)
	else:
		captions = ''
	stream = data['providers'][0]['sources'][0]['uri']# + '&ads.xumo_channelId=' + channel
	PLAY(name,stream,captions)


#27
def show_collection(url):
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(response.text)#;genres = []
	prefix = url.replace('.json','/')
	for count, item in enumerate(data['pageProps']['page']['rails']):
		if item['category']['name'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			catId = item['category']['id']
			xbmc.log(('CATID: ' + str(catId)),level=log_level)
			c = count
			slug = name.lower().replace(' ','-').replace('&','and')
			xbmc.log(('SLUG: ' + str(slug)),level=log_level)
			url = prefix + 'collection/' + slug + '/' + catId + '.json?slug=' + slug + '&slug=' + catId
			xbmc.log('COLLECTION URL: ' + str(url),level=log_level)
			shows(name,url)


#30
def movie_collection(url):
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(response.text)#;genres = []
	prefix = url.replace('.json','/')
	for count, item in enumerate(data['pageProps']['page']['rails']):
		if item['category']['name'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			catId = item['category']['id']
			xbmc.log(('CATID: ' + str(catId)),level=log_level)
			c = count
			deepLink = item['category']['deepLink']
			xbmc.log(('SLUG: ' + str(deepLink)),level=log_level)
			url = prefix + 'collection/' + deepLink + '.json?slug=' + deepLink
			xbmc.log('COLLECTION URL: ' + str(url),level=log_level)
			movies(name,url)


def random3():
	range_start = 10**(3-1)
	range_end = (10**3)-1
	return randint(range_start, range_end)


#52
def save_item(url,name,image):
	#suffix = random3()
	#xbmc.log('SAVE ITEM SUFFIX: ' + str(suffix),level=log_level)
	xbmc.log('SAVE ITEM NAME: ' + str(name),level=log_level)
	#xbmc.log('SAVE ITEM: ' + str(url),level=log_level)
	xbmc.log('SAVE ITEM IMAGE: ' + str(image),level=log_level)
	second = urllib.parse.quote_plus(url.split('/',7)[-1])
	#xbmc.log('SECOND: ' + str(second),level=log_level)
	file_name = urllib.parse.quote_plus(name) + '.txt'
	if os.path.exists(os.path.join(addon_path_profile,file_name)):
		xbmcgui.Dialog().notification(addonname, name.split('--')[0] + ' Already saved!', defaultimage, time=3000, sound=False)
		sys.exit()
	with open(os.path.join(addon_path_profile, file_name), "w") as text_file:
		#if '--episode' in name:
			#type = 'episode'
			#text_file.write(f"{url,image,type}")
		#else:
		text_file.write(f"{url,image}")
	xbmcgui.Dialog().notification(addonname, name.split('--')[0] + ' Saved', defaultimage, time=3000, sound=False)
	sys.exit()


#55
def saved_items(url,name):
	start_path = os.path.join(addon_path_profile) # current directory
	#xbmc.log('START_PATH: ' + str(start_path),level=log_level)
	for path,dirs,files in os.walk(start_path):
		for filename in files:
			xbmc.log('FILE: ' + str(filename),level=log_level)
			if '.txt' in filename:
				title = urllib.parse.unquote_plus(filename).split('--')[0]
				with open(os.path.join(addon_path_profile, filename), 'r') as f:
					items = f.read()
				xbmc.log('ITEMS: ' + str(items),level=log_level)
				info = re.findall(r"'(.*?)'", items)
				url = info[0]
				xbmc.log('SAVED URL: ' + str(info[0]),level=log_level)
				buildId = get_id(url)
				if '--show' in filename and buildId not in url:
					xbmc.log('### BUILDID FAIL ###',level=log_level)
					url_split = info[0].split('/', 6)
					#xbmc.log('SPLIT URL: ' + str(url_split),level=log_level)
					url = vodUrl + buildId + '/' + url_split[-1]
					xbmc.log('BUILD URL: ' + str(url),level=log_level)
				slug = info[1]
				#xbmc.log('SAVED IMAGE: ' + str(info[1]),level=log_level)
				if 'tv-shows' in url:
					mode = 15; folder = True
					image = slug
					plot = 'TV Show'
				if 'channels' in url:
					mode = 9; folder = False
					image = 'https://image.xumo.com/v1/channels/channel/' + str(slug) + '/600x337.webp?type=channelTile'
					plot = 'Live Channel'
				if 'assets' in url:
					mode = 24; folder = False
					image = defaultfanart
					plot = 'Movie'
				if '--episode' in filename:
					mode = 24; folder = False
					image = slug
					plot = 'TV Show Episode'
					url = url.split('--')[0]
				streamUrl = 'plugin://plugin.video.xumoplay?mode=' + str(mode) + '&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)# + '&count=' + urllib.parse.quote_plus(str(count))
				li = xbmcgui.ListItem(title)
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot})
				li.setArt({'thumb':image,'fanart':image})
				## Add Context Item
				li.addContextMenuItems([('More Info', 'RunPlugin(%s?mode=60&url=%s)' % (sys.argv[0], urllib.parse.quote_plus(url))),('Delete Item', 'RunPlugin(%s?mode=58&url=%s&name=%s)' % (sys.argv[0], urllib.parse.quote_plus(url), urllib.parse.quote_plus(title)))])
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=folder)
	#xbmc.log('INFO 0: ' + str(info[0]),level=log_level)
	#xbmc.log('INFO 1: ' + str(info[1]),level=log_level)
	#xbmc.log('INFO 2: ' + str(info[2]),level=log_level)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#58
def delete_item(url,name):
	yes = xbmcgui.Dialog().yesno(addonname ,'Are you sure you want to delete ' + name + '?  This action cannot be reversed!')
	if not yes:
		xbmc.log('NOT YES',level=log_level)
		sys.exit()
	else:
		xbmc.log('YES',level=log_level)
		if 'tv-shows' in url:
			name = name + '--show'
		if 'channels' in url:
			name = name + '--live'
		if 'assets' in url:
			name = name + '--movie'
		if '--episode' in url:
			name = name + '--episode'
		file_name = os.path.join(addon_path_profile, urllib.parse.quote_plus(name) + '.txt')
		xbmc.log('FILE_NAME: ' + str(file_name),level=log_level)
		if os.path.exists(os.path.join(addon_path_profile,file_name)):
			os.remove(file_name)
			xbmcgui.Dialog().notification(addonname, name.split('--')[0] + ' Has been deleted.', defaultimage, time=3000, sound=False)
			xbmc.executebuiltin("Container.Refresh")
			sys.exit()
		else:
			xbmcgui.Dialog().notification(addonname, name.split('--')[0] + ' Already deleted.', defaultimage, time=3000, sound=False)


#60
def saved_info(url):
	if 'tv-shows' in url:
		vod_desc(url)
	if 'channels' in url:
		desc(url)
	if 'assets' in url:
		info(url)


#82
def desc(url):
	xbmcgui.Dialog().notification(addonname, 'Fetching Program Info...', defaultimage, time=3000, sound=False)
	url = url.rpartition('/')[0] + '/onnowandnext.json?f=asset.title&f=asset.descriptions'
	xbmc.log('DESC URL: ' + str(url),level=log_level)
	xbmc.log(('GET DESCRIPTION'),level=log_level)
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	if 'descriptions' not in response.text:
		title = plugin
		info = 'No description available'
		xbmcgui.Dialog().textviewer(title, info)
	else:
		data = json.loads(response.text)
		results = data['results']
		xbmc.log('RESULTS: ' + str(len(results)),level=log_level)
		for item in data:
			title1 = data['results'][0]['title']
			descriptions = data['results'][0]['descriptions']
			maxDesc = max(descriptions, key=len)
			description1 = data['results'][0]['descriptions'][maxDesc]
			end = str(data['results'][0]['end'])[:-3]
			xbmc.log('END: ' + str(end),level=log_level)
			epochDif = (int((int(end) - int(time.time()))))
			xbmc.log(('EPOCH_DIF: ' + str(epochDif)),level=log_level)
			remaining = str(datetime.timedelta(seconds=epochDif))
			#xbmc.log(('REMAINING: ' + str(remaining)),level=log_level)
			info = description1 + '\n\nTime Remaining: ' + remaining# + '\n\n' + 'Next: [B]' + title2 + '[/B] - ' + description2
			if len(results) > 1:
				title2 = data['results'][1]['title']
				descriptions = data['results'][1]['descriptions']
				maxDesc = max(descriptions, key=len)
				description2 = data['results'][1]['descriptions'][maxDesc]
				info = description1 + '\n\nTime Remaining: ' + remaining + '\n\n' + 'Next: [B]' + title2 + '[/B] - ' + description2
			else:
				info = description1 + '\n\nTime Remaining: ' + remaining# + '\n\n' + 'Next: [B]' + title2 + '[/B] - ' + description2
	xbmcgui.Dialog().textviewer(title1, info)


#85
def info(url):
	buildId = get_id(url)
	slugs = url.split('/')
	xbmc.log('SLUGS: ' + str(slugs),level=log_level)
	url = vodUrl + buildId + '/free-movies/' + slugs[-2] + '/' + slugs[-1] + '.json?slug=' + slugs[-2] + '?slug=' + slugs[-1]
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
	buildId = get_id(url)
	slugs = url.split('/')
	xbmc.log('SLUGS: ' + str(slugs),level=log_level)
	url = vodUrl + buildId + '/tv-shows/' + slugs[-2] + '/' + slugs[-1] + '.json?slug=' + slugs[-2] + '?slug=' + slugs[-1]
	xbmc.log('### GET SHOW INFO ###',level=log_level)
	xbmcgui.Dialog().notification(addonname, 'Fetching Show Info...', defaultimage, time=3000, sound=False)
	xbmc.log('URL: ' + str(url),level=log_level)
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
def PLAY(name,url,captions):
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log('### SETRESOLVEDURL ###',level=log_level)
	if 'm3u8' in url:
		content_type = 'hls'
		xbmc.log('CONTENT_TYPE: ' + str(content_type),level=log_level)
	else:
		content_type = 'mpd'
		xbmc.log('CONTENT_TYPE: ' + str(content_type),level=log_level)


	lic_url = 'https://widevine-dash.ezdrm.com/proxy?pX=5FE38E&CustomData=%7B%22host%22%3A%22valencia-app-mds.xumo.com%22%2C%22deviceId%22%3A%22d183f919-6f19-42e7-8a9b-356a79b48831%22%2C%22clientVersion%22%3A%222.17.0%22%2C%22providerId%22%3A2565%2C%22assetId%22%3A%22XM0YAF26UZNG6X%22%2C%22token%22%3A%225ad11c90-38e1-4441-8d95-bcfceb1219af%22%7D'

	response = s.post(lic_url)
	xbmc.log('LIC_RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('LIC_RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	xbmc.log('LIC_RESPONSE HEADERS: ' + str(response.headers),level=log_level)
	xbmc.log('LIC_RESPONSE: ' + str(response.text),level=log_level)
	headers = response.headers

	referer = 'https://play.xumo.com/'

	license_key = lic_url + '|User-Agent=' + ua + '&Referer=' + referer +'/&Origin=' + referer + '&Content-Type= |R{SSM}|'
	is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
	if not is_helper.check_inputstream():
		sys.exit()

	listitem.setProperty('IsPlayable', 'true')
	#if hls != 'false':
	if captions != '':
		listitem.setSubtitles([captions])
	listitem.setProperty('inputstream', 'inputstream.adaptive')
	listitem.setProperty('inputstream.adaptive.manifest_type', content_type)
	listitem.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={ua}")
	listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
	listitem.setProperty('inputstream.adaptive.license_key', license_key)
	listitem.setMimeType('application/dash+xml')
	listitem.setContentLookup(False)
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
data = None
image = None
captions = None

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

if mode == None or url == None or len(url) < 1:
	xbmc.log(("Get Main Menu"),level=log_level)
	main_menu()
elif mode == 0:
	xbmc.log(("Get Genres"),level=log_level)
	genres(url)
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
elif mode == 27:
	xbmc.log(("Get Show Collection"),level=log_level)
	show_collection(url)
elif mode == 30:
	xbmc.log(("Get Movie Collection"),level=log_level)
	movie_collection(url)
elif mode == 52:
	xbmc.log(("Save Item"),level=log_level)
	save_item(url,name,image)
elif mode == 55:
	xbmc.log(("Saved Items"),level=log_level)
	saved_items(url,name)
elif mode == 58:
	xbmc.log(("Delete Item"),level=log_level)
	delete_item(url,name)
elif mode == 60:
	xbmc.log(("Get Saved Info"),level=log_level)
	saved_info(url)
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
	xbmc.log("Play MPD Stream", level=log_level)
	PLAY(name,url)

xbmcplugin.endOfDirectory(addon_handle)
