#!/usr/bin/python
#
#
# Written by MetalChris 2024.04.02
# Released under GPL(v2 or later)

import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, os, re
from bs4 import BeautifulSoup
import html5lib


addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'audio')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='plugin.video.newsnet')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
settings = xbmcaddon.Addon(id="plugin.video.newsnet")
base = 'https://www.newsnetmedia.com'
plugin = "NEWSnet"
local_string = xbmcaddon.Addon(id='plugin.video.newsnet').getLocalizedString
defaultimage = 'special://home/addons/plugin.video.newsnet/resources/media/icon.png'
fanart = 'special://home/addons/plugin.video.newsnet/resources/media/fanart.png'

__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

from uas import *

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 2
else:
	log_level = 1
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)


#3
def cats():
	response = str(get_html(base))
	liveStreamURL = str(re.compile('liveStreamURL":"(.+?)",').findall(response)[0])
	xbmc.log('LiveStreamURL: ' + str(liveStreamURL),level=log_level)
	liveStreamIMG = str(re.compile('liveStreamSlateURL":"(.+?)",').findall(response)[0])
	liveStreamTitle = 'NEWSnet Live Stream'
	description = liveStreamTitle
	addDir(liveStreamTitle, liveStreamURL, 99, liveStreamIMG, liveStreamIMG, description)#;i=i+1
	soup = BeautifulSoup(response,'html5lib').find_all('li',{'class':''})#[1:]
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	for item in soup[1:-18]:
		url = base + str(item.find('a')['href'])
		title = item.find('a').text
		addDir2(title, url, 6, liveStreamIMG, liveStreamIMG, title)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#6
def get_sections(url):
	response = get_html(url)
	xbmc.log('RESPONSE: ' + str(len(response)), level=log_level)
	soup = BeautifulSoup(response,'html5lib').find_all('div',{'class':'Item'})#[1:]
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	for item in soup:
		if item.find('div',{'class':'Item-imageContainer VideoThumbnail VideoThumbnail-center'}):
			title = item.find('h4').text
			xbmc.log('TITLE: ' + str(title), level=log_level)
			url = item.find('a')['href']
			xbmc.log('URL: ' + str(url), level=log_level)
			image = item.find('img')['data-src']
			xbmc.log('IMAGE: ' + str(image), level=log_level)
			addDir(title, url, 12, image, fanart, title)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#12
def get_video(url):
	response = get_html(url)
	xbmc.log('RESPONSE: ' + str(len(response)), level=log_level)
	video_urls = (re.compile('mobile"},{"url":"(.+?)","filesize').findall(str(response)))
	xbmc.log('VIDEO_URLS: ' + str(video_urls), level=log_level)
	for item in video_urls:
		if 'm3u8' in item:
			url = urllib.parse.unquote(item)
			xbmc.log('VIDEO_URL: ' + str(url), level=log_level)
			PLAY('video',url)
		xbmc.log('NO M3U8 AVAILABLE', level=log_level)
		if '1280x720' in item:
			url = urllib.parse.unquote(item)
			xbmc.log('VIDEO_URL: ' + str(url), level=log_level)
			PLAY('video',url)


#99
def PLAY(name,url):
	addon_handle = int(sys.argv[1])
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log('### SETRESOLVEDURL ###',level=log_level)
	listitem.setProperty('IsPlayable', 'true')
	#background = [{'image':image}]
	#listitem.setAvailableFanart(background)
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
	xbmc.log('URL: ' + str(url), level=log_level)
	xbmcplugin.endOfDirectory(addon_handle)


def get_html(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent', ua)

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


def addDir(name, url, mode, thumbnail, fanart, infoLabels=True):
	u = sys.argv[0] + "?url=" + urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	liz.setArt({'thumb':thumbnail,'fanart':fanart})
	if url != 'Future':
		liz.setProperty('IsPlayable', 'true')
	else:
		liz.setProperty('IsPlayable', 'false')
	if not fanart:
		fanart=defaultfanart
	liz.setProperty('fanart_image',fanart)
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
	return ok

def addDir2(name, url, mode, thumbnail, fanart, infoLabels=True):
	u = sys.argv[0] + "?url=" + urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	liz.setArt({'thumb':thumbnail,'fanart':fanart})
	if url != 'Future':
		liz.setProperty('IsPlayable', 'true')
	else:
		liz.setProperty('IsPlayable', 'false')
	if not fanart:
		fanart=defaultfanart
	liz.setProperty('fanart_image',fanart)
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
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

try:
	url = urllib.parse.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.parse.unquote_plus(params["name"])
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
	xbmc.log(("Get Cats"),level=log_level)
	cats()
elif mode == 3:
	xbmc.log(("Get Cats"),level=log_level)
	cats(url)
elif mode == 6:
	xbmc.log(("Get Sections"),level=log_level)
	get_sections(url)
elif mode == 12:
	xbmc.log(("Get Video"),level=log_level)
	get_video(url)
elif mode == 99:
	xbmc.log("Play Stream", level=log_level)
	PLAY(name,url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
