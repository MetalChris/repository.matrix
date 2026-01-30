#!/usr/bin/python
#
#
# Written by MetalChris 2024.05.23
# Released under GPL(v2 or later)

import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, os
import json
import time
import requests
from requests import Request, Session
import datetime
import shutil
import tempfile
#import inputstreamhelper

today = time.strftime("%Y-%m-%d")


addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'video')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='plugin.video.lgchannels')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
settings = xbmcaddon.Addon(id="plugin.video.lgchannels")
apiUrl = 'https://api.lgchannels.com/api/v1.0/schedulelist'
plugin = "LG Channels"
local_string = xbmcaddon.Addon(id='plugin.video.lgchannels').getLocalizedString
defaultimage = 'special://home/addons/plugin.video.lgchannels/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.lgchannels/resources/media/fanart.png'

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
xbmc.log(('LG CHANNELS 2024.04.05'),level=log_level)
confluence_views = [500,501,503,504,515]
force_views = settings.getSetting(id="force_views")
first = settings.getSetting(id='first')
hls = settings.getSetting(id='hls')
if first != 'true':
	addon.openSettings(label="Logging")
	addon.setSetting(id='first',value='true')

s = requests.Session()

headers = {
    'user-agent': ua,
    'x-device-country': 'US',
    'x-device-language': 'en',
}

def ensure_content_length(
	url, *args, method='GET', session=None, max_size=2**20,  # 1Mb
	**kwargs
):
	kwargs['stream'] = True
	session = session or requests.Session()
	r = session.request(method, url, *args, **kwargs)
	if 'Content-Length' not in r.headers:
		# stream content into a temporary file so we can get the real size
		spool = tempfile.SpooledTemporaryFile(max_size)
		shutil.copyfileobj(r.raw, spool)
		r.headers['Content-Length'] = str(spool.tell())
		xbmc.log('RESP: ' + str(r.headers),level=log_level)
		spool.seek(0)
		# replace the original socket with our temporary file
		r.raw._fp.close()
		r.raw._fp = spool
		xbmc.log('RESP: ' + str(r.text),level=log_level)
	return r


def genres(apiUrl):
	xbmc.log(('GET GENRES'),level=log_level)
	response = ensure_content_length(apiUrl, headers=headers)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	data = json.loads(response.text);genres = []#;images = []
	for count, item in enumerate(data['categories']):
		genre = item['categoryName']
		if genre not in genres:
			genres.append(genre)
	xbmc.log('GENRES: ' + str(genres),level=log_level)
	for genre in genres:
		title = str(genre)
		streamUrl = 'plugin://plugin.video.lgchannels?mode=3&url=' + urllib.parse.quote_plus(apiUrl) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#3
def channels(apiUrl, name):
	response = s.get(apiUrl, headers = headers)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	data = json.loads(response.text)
	for count, item in enumerate(data['categories']):
		if item['categoryName'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			c = count
			for count, item in enumerate(data['categories'][c]['channels']):
				title = str(item['channelName'])
				image = item['programs'][0]['imageUrl']
				fanart = item['programs'][0]['previewImgUrl']
				if fanart == None:
					fanart = image
				#xbmc.log('IMAGE: ' + str(image),level=log_level)
				description = item['programs'][0]['description']
				programTitle = item['programs'][0]['programTitle']
				endDateTime = item['programs'][0]['endDateTime']
				remaining = ends(endDateTime)
				NextprogramTitle = item['programs'][1]['programTitle']
				#xbmc.log('NEXT: ' + str(NextprogramTitle),level=log_level)
				plot = '[B]' + programTitle + '[/B]: ' + description + ' (Ends in ' + remaining + ')\n\nNext: ' + '[B]' + NextprogramTitle + '[/B]'
				url = item['mediaStaticUrl'].split('?')[0]
				streamUrl = 'plugin://plugin.video.lgchannels?mode=99&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(programTitle)
				li = xbmcgui.ListItem(title)
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot':plot})
				li.setArt({'thumb':image,'fanart':fanart})
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


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
	#xbmc.log('ENDS: ' + str(endDateTime),level=log_level)
	p='%Y-%m-%dT%H:%M:%SZ'
	epoch = int(time.mktime(time.strptime(endDateTime,p)))
	#xbmc.log('EPOCH: ' + str(epoch),level=log_level)
	epochDif = (int((int(epoch) - int(NOW)))) - int(time.timezone) + 3600
	#xbmc.log(('EPOCH_DIF: ' + str(epochDif)),level=log_level)
	if epochDif < 0:
		epochDif = epochDif + 7200
	remaining = str(datetime.timedelta(seconds=epochDif))
	#xbmc.log(('REMAINING: ' + str(remaining)),level=log_level)
	return remaining


#99
def PLAY(name,url):
	response = s.get(url, headers = headers)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),level=log_level)
	xbmc.log('RESPONSE LENGTH: ' + str(len(response.text)),level=log_level)
	#xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log('### SETRESOLVEDURL ###',level=log_level)
	if hls != 'false':
		listitem.setProperty('IsPlayable', 'true')
		listitem.setProperty('inputstream', 'inputstream.adaptive')
		listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
		listitem.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={ua}")
	#listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
	listitem.setContentLookup(False)
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
elif mode == 99:
	xbmc.log("Play Stream", level=log_level)
	PLAY(name,url)

xbmcplugin.endOfDirectory(addon_handle)
