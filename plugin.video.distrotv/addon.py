#!/usr/bin/python
#
#
# Written by MetalChris 2024.04.28
# Released under GPL(v2 or later)

import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, os
import json
import time
from time import strftime, localtime, mktime
import requests

today = time.strftime("%Y-%m-%d")


addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'video')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='plugin.video.distrotv')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
settings = xbmcaddon.Addon(id="plugin.video.distrotv")
vodUrl = 'https://tv.jsrdn.com/tv_v5/getfeed.php?type=vod'
channelsUrl = 'https://tv.jsrdn.com/tv_v5/getfeed.php?type=live'
epgUrl = 'https://tv.jsrdn.com/epg/query.php?range=now,2h&id='
baseUrl = 'https://distro.tv/'
plugin = "DistroTV"
local_string = xbmcaddon.Addon(id='plugin.video.distrotv').getLocalizedString
defaultimage = 'special://home/addons/plugin.video.distrotv/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.distrotv/resources/media/fanart.jpg'

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
gmt = time.gmtime()
dt = (mktime(gmt))
xbmc.log('GMT: ' + str(dt),level=log_level)

xbmc.log('UTC Offset: ' + str(time.timezone),level=log_level)

s = requests.Session()


#6
def get_stream(name,url):
	xbmc.log(('GET STREAM'),level=log_level)
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
def vod(url):
	response = s.get(vodUrl)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['topics']):
		title = item['title']
		image = item['img_thumbh']
		streamUrl = 'plugin://plugin.video.distrotv?mode=12&url=' + urllib.parse.quote_plus(str(url)) + '&name=' + urllib.parse.quote_plus(str(title))
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':image,'fanart':image})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#12
def codes(name,url):
	response = s.get(vodUrl)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['topics']):
		if item['title'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			c = count; shows=[]
			for count, item in enumerate(data['topics'][c]['shows']):
				show = str(item)
				if show not in shows:
					shows.append(show)
	show_titles(shows,url)


def show_titles(shows,url):
	xbmc.log(('SHOWS: ' + str(shows)),level=log_level)
	response = s.get(vodUrl)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	for code in shows:
		for count, item in enumerate(data['shows'][code]['seasons'][0]['episodes']):
			enum = (count + 1)
		title = data['shows'][code]['title']
		li = xbmcgui.ListItem(title)
		slug = data['shows'][code]['name']
		description = data['shows'][code]['description']
		image = data['shows'][code]['img_thumbh']
		if enum == 1:
			folder = False
			li.setProperty('IsPlayable', 'true')
			url = (data['shows'][code]['seasons'][0]['episodes'][0]['content']['url'])
			streamUrl = 'plugin://plugin.video.distrotv?mode=99&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(name)
		else:
			folder = True
			streamUrl = 'plugin://plugin.video.distrotv?mode=15&url=' + urllib.parse.quote_plus(vodUrl) + '&code=' + urllib.parse.quote_plus(code)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':description})
		li.setArt({'thumb':image,'fanart':image})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=folder)
		xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#15
def show_episodes(code,url):
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	total = len(data['shows'][code]['seasons'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for count, item in enumerate(data['shows'][code]['seasons']):
		snum = (count + 1)
		xbmc.log('COUNT: ' + str(count),level=log_level)
		for number, episode in enumerate(item['episodes']):
			title = str(snum) + 'x' + str(number + 1) + ' ' + episode['title']
			image = episode['img_thumbh']
			description = episode['description']
			url = episode['content']['url']
			streamUrl = 'plugin://plugin.video.distrotv?mode=99&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
			li = xbmcgui.ListItem(title)
			li.setProperty('IsPlayable', 'true')
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':description})
			li.setArt({'thumb':image,'fanart':image})
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#18
def live_cats(url):
	response = s.get(channelsUrl)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['topics']):
		title = item['title']
		image = item['img_thumbh']
		streamUrl = 'plugin://plugin.video.distrotv?mode=21&url=' + urllib.parse.quote_plus(str(url)) + '&name=' + urllib.parse.quote_plus(str(title))
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':image,'fanart':image})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
		#xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	addDir2('On Demand Video', vodUrl, 9, defaultimage, defaultfanart, infoLabels={'plot':''})
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#21
def channels(name,url):
	response = s.get(channelsUrl)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['topics']):
		if item['title'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			c = count; channels=[]
			for count, item in enumerate(data['topics'][c]['shows']):
				channel = str(item)
				if channel not in channels:
					channels.append(channel)
	get_channel(channels,url)


#24
def get_channel(channels,url):
	response = s.get(channelsUrl)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	for code in channels:
		for count, item in enumerate(data['shows'][code]['seasons'][0]['episodes']):
			title = item['title']
			li = xbmcgui.ListItem(title)
			slug = item['name']
			description = item['description']
			#plot = item['description']
			image = item['img_thumbh']
			if item['id'] is not None:
				epgId = str(item['id'])
				li.addContextMenuItems([('Program Info', 'RunPlugin(%s?mode=82&url=%s)' % (sys.argv[0], (epgId)))])
			url = (data['shows'][code]['seasons'][0]['episodes'][0]['content']['url']) + '|User-Agent=' + ua
			streamUrl = 'plugin://plugin.video.distrotv?mode=99&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(name)
			li.setProperty('IsPlayable', 'true')
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':description})
			li.setArt({'thumb':image,'fanart':image})
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
			xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#82
def desc(url):
	code = url
	url = epgUrl + code
	xbmcgui.Dialog().notification(addonname, 'Fetching Show Info...', defaultimage, time=3000, sound=False)
	xbmc.log('DESC URL: ' + str(url),level=log_level)
	xbmc.log(('GET DESCRIPTION'),level=log_level)
	response = s.get(url)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	data = json.loads(response.text)
	title = data['epg'][code]['title']
	slots = len(data['epg'][code]['slots'])
	xbmc.log('SLOTS: ' + str(slots),level=log_level)
	if slots > 0:
		xbmc.log('NOW: ' + str(round(time.time())),level=log_level)
		NOW = time.time()
		endTime = data['epg'][code]['slots'][0]['end']
		p='%Y-%m-%d %H:%M:%S'
		epoch = int(time.mktime(time.strptime(endTime,p)))
		xbmc.log('END_EPOCH: ' + str(epoch),level=log_level)
		epochDif = (int((int(epoch) - int(NOW)))) - int(time.timezone) + 3600
		xbmc.log('EPOCHDIF: ' + str(epochDif),level=log_level)
		nextTime = round((int(epochDif)/60))
		xbmc.log('NEXTTIME: ' + str(nextTime),level=log_level)
		try:description = '[B]' + data['epg'][code]['slots'][0]['title'] +'[/B] - ' + data['epg'][code]['slots'][0]['description']
		except:
			try:description = '[B]' + data['epg'][code]['slots'][0]['title'] +'[/B]'
			except:
				description = 'No information available.'
		try:onNext = '[B]' + data['epg'][code]['slots'][1]['title'] +'[/B] - ' + data['epg'][code]['slots'][1]['description']
		except:
			try:onNext = '[B]' + data['epg'][code]['slots'][1]['title'] +'[/B]'
			except:
				onNext = 'No information available.'
		info = description + '\n(ends in ' + str(nextTime) + ' minutes...)' + '\n\n' + '[B]Next:  [/B]' + onNext
		#info = description + '\n\n' + '[B]Next:  [/B]' + onNext
		xbmc.log('DESCRIPTION: ' + str(description),level=log_level)
	else:
		title = 'DistroTV'
		info = 'No information available.'
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
shows = None
code = None

try:
	url = urllib.parse.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.parse.unquote_plus(params["name"])
except:
	pass
try:
	shows = urllib.parse.unquote_plus(params["shows"])
except:
	pass
try:
	code = urllib.parse.unquote_plus(params["code"])
except:
	pass
try:
	epgId = urllib.parse.unquote_plus(params["epgId"])
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
	live_cats(url)
elif mode == 6:
	xbmc.log(("Get Stream"),level=log_level)
	get_stream(name,url)
elif mode == 9:
	xbmc.log(("Get Show Categories"),level=log_level)
	vod(url)
elif mode == 12:
	xbmc.log(("Get Shows"),level=log_level)
	codes(name,url)
elif mode == 15:
	xbmc.log(("Get Episodes"),level=log_level)
	show_episodes(code,url)
elif mode == 18:
	xbmc.log(("Get Live Categories"),level=log_level)
	live_cats(url)
elif mode == 21:
	xbmc.log(("Get Channels"),level=log_level)
	channels(name,url)
elif mode == 24:
	xbmc.log(("Get Live Stream"),level=log_level)
	get_channel(name,url)
elif mode == 82:
	xbmc.log(("Get Show Info"),level=log_level)
	desc(url)
elif mode == 99:
	xbmc.log("Play Stream", level=log_level)
	PLAY(name,url)

xbmcplugin.endOfDirectory(addon_handle)
