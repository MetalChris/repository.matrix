#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2)

#2021.06.26

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmcplugin, xbmcaddon, xbmcgui, string, os, re, xbmcplugin, sys
from bs4 import BeautifulSoup

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
defaulturl='aHR0cDovL2NkbmFwaS5rYWx0dXJhLmNvbS9odG1sNS9odG1sNWxpYi92Mi40Mi9td0VtYmVkRnJhbWUucGhwPyZ3aWQ9XzkzMTcwMiZ1aWNvbmZfaWQ9Mjg0Mjg3NTEmZW50cnlfaWQ9'
liveurl = 'aHR0cDovL2thbHNlZ3NlYy1hLmFrYW1haWhkLm5ldDo4MC9kYy0wL20vcGEtbGl2ZS1wdWJsaXNoNi9rTGl2ZS9zbWlsOjFfb29yeGNnZTJfYWxsLnNtaWwv'
vidUrl = 'http://www.weathernationtv.com/video/'

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
	addDir('WeatherNation Live', 'http://cdnapi.kaltura.com/html5/html5lib/v2.34/mwEmbedFrame.php?&wid=_931702&uiconf_id=28428751&entry_id=1_oorxcge2', 635, defaultimage)#1_o06v504o
	addDir('WeatherNation Videos', 'http://www.weathernationtv.com/video/', 634, defaultimage)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


#634
def wn_videos(url):
	response = get_html(url)
	soup = BeautifulSoup(response, 'html5lib').find_all('a',{'class':'video-item'})
	xbmc.log('SOUP: ' + str(len(soup)), level=log_level)
	#xbmc.log('SOUP: ' + str(soup), level=log_level)
	for show in soup:#.find_all("div",{"class":"pull-left"}): 0:15, 15:30, 30:56, 56:72
		title = bytes(show.find('h4').text.title().encode('utf-8'))#('img')['alt'].title()
		xbmc.log('TITLE: ' + str(title), level=log_level)
		image = (show.find('div')['style'].split("url('")[-1])[:-2]
		xbmc.log('IMAGE: ' + str(image), level=log_level)
		url = show.get('data-url').encode('utf-8')
		xbmc.log('URL: ' + str(url), level=log_level)
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"genre":"Sports"})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)


#635
def wn_live(name,url):
	response = get_html(url)
	stream = (re.compile('hls","url":"(.+?)"').findall(str(response))[0]).replace('\\','')
	url = get_redirected_url(stream)
	listitem = xbmcgui.ListItem(name, iconImage=defaultimage, thumbnailImage=defaultimage)
	listitem.setProperty('IsPlayable', 'true')
	xbmc.Player().play( url, listitem )
	sys.exit()
	xbmcplugin.endOfDirectory(addon_handle)


def get_redirected_url(url):
	opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
	request = opener.open(url)
	playthis = request.url
	return request.url


def play(url,name):
	jdata = get_html(url)
	data = re.compile('kalturaIframePackageData =(.+?);\n\t\t\tvar isIE8').findall(str(jdata))[0]
	bitkeys = re.compile('2,"id":"(.+?)","entryId').findall(data)
	if QUALITY =='1':
		bitkey = bitkeys[3]
	elif QUALITY =='0':
		bitkey = bitkeys[2]
	else:
		bitkey = bitkeys[5]
	url = 'http://www.kaltura.com/p/243342/sp/24334200/playManifest/entryId/' + url[-10:] + '/flavorId/' + bitkey + '/format/url/protocol/http/a.mp4'
	listitem = xbmcgui.ListItem(name, iconImage=defaultimage, thumbnailImage=defaultimage)
	listitem.setProperty('IsPlayable', 'true')
	xbmc.Player().play( url, listitem )
	sys.exit()
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


def add_directory2(name, url, mode, fanart):
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
	wn_videos(vidUrl)
	#categories()
elif mode == 1:
	xbmc.log("Indexing Videos", level=log_level)
	INDEX(url)
elif mode == 4:
	xbmc.log("Play Video", level=log_level)
elif mode == 6:
	xbmc.log("Get Episodes", level=log_level)
	get_episodes(url)
elif mode==634:
	xbmc.log("WeatherNation Videos", level=log_level)
	wn_videos(url)
elif mode==635:
	xbmc.log("WeatherNation Live", level=log_level)
	wn_live(name,url)
elif mode==636:
	xbmc.log("WeatherNation Play Videos", level=log_level)
	play(url,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
