#!/usr/bin/python
#
#
# Written by MetalChris 2024.04.17
# Released under GPL(v2 or later)

import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, os
import json
import time
from time import strftime, localtime
import requests


today = time.strftime("%Y-%m-%d")


addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'audio')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='plugin.video.redbox')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
settings = xbmcaddon.Addon(id="plugin.video.redbox")
base = 'https://www.redbox.com/'
plugin = "Redbox"
local_string = xbmcaddon.Addon(id='plugin.video.redbox').getLocalizedString
defaultimage = 'special://home/addons/plugin.video.redbox/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.redbox/resources/media/fanart.jpg'
SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}

__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

from uas import *

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 2
else:
	log_level = 1
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)

xbmc.log('TODAY: ' + str(today),level=log_level)
xbmc.log('NOW: ' + str(time.time()),level=log_level)
xbmc.log('UTC Offset: ' + str(-time.timezone),level=log_level)

myobj = {
  "operationName": "avod",
  "variables": {},
  "query": "fragment ChannelParts on epgItem {  title  episodeTitle  rating  language  contentType  description  startTime  endTime  __typename}query avod {  reelCollection(id: \"livetv-collection-id\") {    name    reels(paging: {number: 1, size: 30}) {      id      name      items(paging: {number: 1, size: 50}) {        ... on LiveTvReelItem {          id          name          urlId          url          source          description          genres          images {            mono            stylized            __typename          }          type          onNow {            id            ...ChannelParts            __typename          }          onNext {            ...ChannelParts            __typename          }          __typename        }        __typename      }      __typename    }    __typename  }}"
}

#3
def cats():
	reels = requests.post('https://www.redbox.com/gapi/ondemand/hcgraphql/', json = myobj)
	xbmc.log('X: ' + str(len(reels.text)),level=log_level)
	data = json.loads(reels.text)
	for count, item in enumerate(data['data']['reelCollection']['reels']):
		#xbmc.log('COUNT: ' + str(count),level=log_level)
		#xbmc.log('ITEM: ' + str(item),level=log_level)
		title = item['name']
		image = defaultimage
		url = 'https://www.redbox.com/gapi/ondemand/hcgraphql/'
		streamUrl = 'plugin://plugin.video.redbox?mode=6&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#6
def channels(name,url):
	reels = requests.post('https://www.redbox.com/gapi/ondemand/hcgraphql/', json = myobj)
	xbmc.log('X: ' + str(len(reels.text)),level=log_level)
	data = json.loads(reels.text)
	for count, item in enumerate(data['data']['reelCollection']['reels']):
		#xbmc.log(('TITLE: ' + str(item['name'])),level=log_level)
		if item['name'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			c = count
			for count, item in enumerate(data['data']['reelCollection']['reels'][c]['items']):
				title = item['name']
				now = item['onNow']['title']
				description = item['onNow']['description']
				nextUp = item['onNext']['title']
				startTime = item['onNext']['startTime']
				lN = strftime('%H:%M', localtime(startTime))
				image = item['images']['stylized']
				plot = '[B]'+ str(now) +'[/B]' + ' ' + str(description) + '\n\n[NEXT @' + str(lN) + '] ' + '[B]'+ str(nextUp) +'[/B]'
				url = item['url']
				streamUrl = 'plugin://plugin.video.redbox?mode=99&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
				li = xbmcgui.ListItem(title)
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"plot":plot})
				li.setArt({'thumb':image,'fanart':defaultfanart})
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#99
def PLAY(name,url):
	addon_handle = int(sys.argv[1])
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log('### SETRESOLVEDURL ###',level=log_level)
	listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
	xbmc.log('URL: ' + str(url), level=log_level)
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
edata = None

try:
	url = urllib.parse.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.parse.unquote_plus(params["name"])
except:
	pass
try:
	edata = urllib.parse.unquote_plus(params["edata"])
except:
	pass
try:
	mode = int(params["mode"])
except:
	pass

xbmc.log("Mode: " + str(mode),level=log_level)
xbmc.log("URL: " + str(url),level=log_level)
xbmc.log("Name: " + str(name),level=log_level)
#xbmc.log("Data: " + str(len(data)),level=log_level)

if mode == None or url == None or len(url) < 1:
	xbmc.log(("Get All"),level=log_level)
	cats()
elif mode == 3:
	xbmc.log(("Get All"),level=log_level)
	cats()
elif mode == 6:
	xbmc.log(("Get Channels"),level=log_level)
	channels(name,url)
elif mode == 99:
	xbmc.log("Play Stream", level=log_level)
	PLAY(name,url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
