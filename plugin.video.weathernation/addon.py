#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2)

#2024.02.14

import urllib.request, urllib.parse, urllib.error, urllib.error, urllib.parse, xbmcplugin, xbmcaddon, xbmcgui, xbmcplugin, sys
import json

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='plugin.video.weathernation')
self = xbmcaddon.Addon(id='plugin.video.weathernation')
translation = selfAddon.getLocalizedString
usexbmc = selfAddon.getSetting('watchinxbmc')
settings = xbmcaddon.Addon(id="plugin.video.weathernation")
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
confluence_views = [500,501,502,503,504,508]

plugin = "WeatherNation TV"

defaultimage = 'special://home/addons/plugin.video.weathernation/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.weathernation/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.weathernation/resources/media/icon.png'
base = 'https://www.weathernationtv.com/_next/data/sT6pjIYlFpxmE1GXN4YdG/video-on-demand.json'

local_string = xbmcaddon.Addon(id='plugin.video.weathernation').getLocalizedString
addon_handle = int(sys.argv[1])
pluginhandle = int(sys.argv[1])
QUALITY = settings.getSetting(id="quality")
#LIVE = settings.getSetting(id="live")
confluence_views = [500,501,502,503,504,508,515]

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 1
else:
	log_level = 0
xbmc.log('LOG_NOTICE: ' + str(log_notice), level=log_level)

def categories():
	response = get_html(base)
	data = json.loads(response);i=0
	total = len(data['pageProps']['playlists']);t=0#[0]['contentData'])
	xbmc.log('TOTAL: ' + str(total),level=log_level);titles=[];x=0;i=0
	for cats in range(total):
		title = (data['pageProps']['playlists'][i]['name'])
		image = defaultimage
		url = base
		addDir(title, url, 5, defaultfanart);i=i+1
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

#5
def get_videos(name,url):
	response = get_html(url)
	data = json.loads(response);i=0
	total = len(data['pageProps']['playlists']);t=0#[0]['contentData'])
	xbmc.log('TOTAL: ' + str(total),level=log_level);titles=[];x=0;i=0;v=0
	#vods = len(data['pageProps']['playlists'][i]['vods'][v]['title'])
	#xbmc.log('VODS TOTAL: ' + str(vods),level=log_level)
	for cats in range(total):
		if (data['pageProps']['playlists'][i]['name']) == name:
			vods = len(data['pageProps']['playlists'][i]['vods'])
			xbmc.log('VODS TOTAL: ' + str(vods),level=log_level)#;x=0
			for vod in range(vods):
				if x == vods:
					continue
				title = (data['pageProps']['playlists'][i]['vods'][x]['title'])
				#xbmc.log('TITLE: ' + str(title),level=log_level)
				image = (data['pageProps']['playlists'][i]['vods'][x]['url']['thumbnail'])
				#xbmc.log('IMAGE: ' + str(image),level=log_level)
				url = (data['pageProps']['playlists'][i]['vods'][x]['url']['hls'])
				#xbmc.log('URL: ' + str(url),level=log_level)
				li = xbmcgui.ListItem(title)
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"genre":"Weather"})
				li.setArt({'thumb':image,'fanart':image});x=x+1
				#xbmc.log('X: ' + str(x),level=log_level)
				#xbmc.log('I: ' + str(i),level=log_level)
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
		else:
			i=i+1
	xbmcplugin.endOfDirectory(addon_handle)


def get_html(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent','User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:44.0) Gecko/20100101 Firefox/44.0')

	try:
		response = urllib.request.urlopen(req)
		html = response.read()
		response.close()
	except urllib.error.HTTPError:
		response = False
		html = False
	return html

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


def addDir(name, url, mode, fanart):
	u = sys.argv[0] + "?url=" + urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	if not fanart:
		fanart = ''
	liz.setArt({
		'thumb': defaultimage,
		'icon': "DefaultFolder.png",
		'fanart': fanart
	})
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True, totalItems=70)
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
cookie = None
iconimage = None

try:
	url = urllib.parse.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.parse.unquote_plus(params["name"])
except:
	pass
try:
	iconimage = urllib.parse.unquote_plus(params["iconimage"])
except:
	pass
try:
	mode = int(params["mode"])
except:
	pass

xbmc.log("Mode: " + str(mode), level=log_level)
xbmc.log("URL: " + str(url), level=log_level)
xbmc.log("Name: " + str(name), level=log_level)

if mode == None or url == None or len(url) < 1:
	xbmc.log("Generate Main Menu")
	categories()
elif mode == 5:
	xbmc.log("Get Videos", level=log_level)
	get_videos(name,url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
