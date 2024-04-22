#!/usr/bin/python
#
#
# Written by MetalChris 2024.04.21
# Released under GPL(v2 or later)

import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, re, os
import json
import time
from time import strftime, localtime
import requests
import inputstreamhelper


today = time.strftime("%Y-%m-%d")


addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'video')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='plugin.video.localnow')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
settings = xbmcaddon.Addon(id="plugin.video.localnow")
apiUrl = 'https://localnow.com/_next/data/qtV7yILDmnCBIm1lP-ToB/'
baseUrl = 'https://localnow.com/'
plugin = "Local Now"
local_string = xbmcaddon.Addon(id='plugin.video.localnow').getLocalizedString
defaultimage = 'special://home/addons/plugin.video.localnow/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.localnow/resources/media/fanart.jpg'

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
xbmc.log('NOW: ' + str(time.time()),level=log_level)
xbmc.log('UTC Offset: ' + str(-time.timezone),level=log_level)

s = requests.Session()


def get_token():
	response = s.get(baseUrl)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob)
	DSP_TOKEN = data['runtimeConfig']['DSP_TOKEN']
	LN_API_KEY = data['runtimeConfig']['LN_API_KEY']
	token = str(re.compile('token":"(.+?)"').findall(DSP_TOKEN)[0])
	return(token)


def get_ln(baseUrl):
	response = s.get(baseUrl)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob)
	LN_API_KEY = data['runtimeConfig']['LN_API_KEY']
	xbmc.log('LN_API_KEY: ' + str(LN_API_KEY),level=log_level)
	lnUrl = data['props']['pageProps']['config']['localNow']['geography']['cityEndpointUrl']
	xbmc.log('LNURL: ' + str(lnUrl),level=log_level)
	headers = {'User-Agent': ua, 'X-Api-Key': str(LN_API_KEY)}
	response = s.get(lnUrl, headers=headers)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	market = data['city']['market']
	pbsMarkets = data['city']['pbsMarkets']
	zipDma = data['city']['zipDma']
	url = 'https://data-store-trans-cdn.api.cms.amdvids.com/live/epg/US/androidtv?program_size=3&dma=' + str(zipDma) + '&market=' + str(market) + ',' + str(pbsMarkets)
	xbmc.log('CHANNELSURL: ' + str(url),level=log_level)
	genres(url)


def genres(url):
	response = s.get(url, headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	data = json.loads(response.text);genres = []
	for count, item in enumerate(data['channels']):
		genre = item['genres'][0]
		if genre not in genres:
			genres.append(genre)
	xbmc.log('GENRES: ' + str(genres),level=log_level)
	for genre in genres:
		title = genre
		streamUrl = 'plugin://plugin.video.localnow?mode=3&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	addDir2('On Demand TV Shows', apiUrl + 'shows.json'
	, 9, defaultimage, defaultfanart, infoLabels={'plot':'Stream unlimited TV shows. Watch action, comedy, drama, romance, and timeless classics from our vast collection on Local Now.'})
	addDir2('On Demand Movies', apiUrl + 'movies.json'
	, 18, defaultimage, defaultfanart, infoLabels={'plot':'Stream unlimited free movies. Watch action, comedy, drama, romance, blockbuster films and more on Local Now.'})
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#3
def channels(url, name):
	response = s.get(url, headers = {'User-Agent': ua})
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['channels']):
		if item['genres'][0] != name:
			continue
		title = str(item['channel_number']) + ' ' + item['name']
		image = item['wallpaper']
		onNow = item['program'][0]['program_title']
		description = item['program'][0]['program_description']
		onNext = item['program'][1]['program_title']
		startTime = item['program'][1]['starts_at']
		lN = strftime('%H:%M', localtime(startTime))
		plot = '[B]'+ str(onNow) +'[/B]' + ' ' + str(description) + '\n\n[NEXT @' + str(lN) + '] ' + '[B]'+ str(onNext) +'[/B]'
		videoId = item['video_id']
		url ='https://data-store-trans-cdn.api.cms.amdvids.com/video/play/' + str(videoId) + '/1920/1080?page_url=https%253A%252F%252Flocalnow.com%252Fchannels%252Fthe-war-channel&device_devicetype=desktop_web&app_version=0.0.0'
		streamUrl = 'plugin://plugin.video.localnow?mode=6&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot})
		li.setArt({'thumb':image,'fanart':image})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#6
def get_stream(name,url):
	token = get_token()
	xbmc.log('TOKEN: ' + str(token),level=log_level)
	headers = {'User-Agent': ua, 'X-Access-Token': str(token)}
	response = s.get(url, headers=headers)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	jsob = (str(response.text))
	data = json.loads(jsob)
	stream = data['video_m3u8']
	PLAY(name,stream)

#9
def rails(url):
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['pageProps']['page']['rails']):
		title = item['category']['name']
		streamUrl = 'plugin://plugin.video.localnow?mode=12&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
		xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#12
def shows(name,url):
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['pageProps']['page']['rails']):
		if item['category']['name'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			c = count
			for count, item in enumerate(data['pageProps']['page']['rails'][c]['cards']):
				title = item['title']
				slug = item['slug']
				url = baseUrl + 'shows/' + slug
				image = item['image']
				streamUrl = 'plugin://plugin.video.localnow?mode=15&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(name)
				li = xbmcgui.ListItem(title)
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
				li.setArt({'thumb':image,'fanart':defaultfanart})
				li.addContextMenuItems([('Show Info', 'RunPlugin(%s?mode=82&url=%s)' % (sys.argv[0], (url)))])
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#15
def episodes(name,url):
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob)
	total = len(data['props']['pageProps']['page']['pdp']['seasons'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for count, item in enumerate(data['props']['pageProps']['page']['pdp']['seasons']):
		season = str(item['season']['number'])
		xbmc.log('SEASON: ' + str(season),level=log_level)
		for card, episode in enumerate(item['cards']):
			title = str(season) + 'x' + str(episode['episode']) + ' ' + episode['title']
			image = episode['image']
			description = episode['description']
			episodeId = episode['id']
			url ='https://data-store-trans-cdn.api.cms.amdvids.com/video/play/' + str(episodeId) + '/1920/1080?page_url=https%253A%252F%252Flocalnow.com%252Fchannels%252Fthe-war-channel&device_devicetype=desktop_web&app_version=0.0.0'
			streamUrl = 'plugin://plugin.video.localnow?mode=6&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
			li = xbmcgui.ListItem(title)
			li.setProperty('IsPlayable', 'true')
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':description})
			li.setArt({'thumb':image,'fanart':image})
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#18
def mcats(name,url):
	response = s.get(apiUrl + 'movies.json')
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text);genres = []
	for count, item in enumerate(data['pageProps']['page']['rails']):
		genre = item['category']['name']
		if genre not in genres:
			genres.append(genre)
	xbmc.log('GENRES: ' + str(genres),level=log_level)
	for genre in genres:
		title = genre
		streamUrl = 'plugin://plugin.video.localnow?mode=21&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#21
def movies(name,url):
	response = s.get(apiUrl + 'movies.json')
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['pageProps']['page']['rails']):
		if item['category']['name'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			c = count
			for count, item in enumerate(data['pageProps']['page']['rails'][c]['cards']):
				title = item['title']
				movieId = item['id']
				slug = item['slug']
				url ='https://data-store-trans-cdn.api.cms.amdvids.com/video/play/' + str(movieId) + '/1920/1080?page_url=https%253A%252F%252Flocalnow.com%252Fchannels%252Fthe-war-channel&device_devicetype=desktop_web&app_version=0.0.0'
				image = item['image']
				fanart = image.replace('2x3','16x9')
				streamUrl = 'plugin://plugin.video.localnow?mode=6&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(name)
				url = baseUrl + 'movies/' + slug
				li = xbmcgui.ListItem(title)
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
				li.setArt({'thumb':image,'fanart':fanart})
				li.addContextMenuItems([('Movie Info', 'RunPlugin(%s?mode=85&url=%s)' % (sys.argv[0], (url)))])
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


def get_id(baseUrl):
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob)
	buildId = data['buildId']
	xbmc.log('BUILDID: ' + str(buildId),level=log_level)
	return(buildId)


#82
def desc(url):
	xbmcgui.Dialog().notification(addonname, 'Fetching Show Info...', defaultimage, time=3000, sound=False)
	xbmc.log('URL: ' + str(url),level=log_level)
	xbmc.log(('GET DESCRIPTION'),level=log_level)
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob)
	description = data['props']['pageProps']['page']['pdp']['description']
	title = data['props']['pageProps']['page']['pdp']['title']
	xbmc.log('DESCRIPTION: ' + str(description),level=log_level)
	xbmcgui.Dialog().ok(title, description)


#85
def info(url):
	xbmcgui.Dialog().notification(addonname, 'Fetching Movie Info...', defaultimage, time=3000, sound=False)
	xbmc.log('URL: ' + str(url),level=log_level)
	xbmc.log(('GET DESCRIPTION'),level=log_level)
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob)
	description = data['props']['pageProps']['page']['pdp']['description']
	title = data['props']['pageProps']['page']['pdp']['title']
	xbmc.log('DESCRIPTION: ' + str(description),level=log_level)
	xbmcgui.Dialog().ok(title, description)


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
	xbmc.log(("Get All"),level=log_level)
	get_ln(baseUrl)
elif mode == 3:
	xbmc.log(("Get Channels"),level=log_level)
	channels(url,name)
elif mode == 6:
	xbmc.log(("Get Stream"),level=log_level)
	get_stream(name,url)
elif mode == 9:
	xbmc.log(("Get Show Categories"),level=log_level)
	rails(url)
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
elif mode == 82:
	xbmc.log(("Get Show Info"),level=log_level)
	desc(url)
elif mode == 85:
	xbmc.log(("Get Movie Info"),level=log_level)
	info(url)
elif mode == 99:
	xbmc.log("Play Stream", level=log_level)
	PLAY(name,url)

xbmcplugin.endOfDirectory(addon_handle)
