#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2 or later)

#2024.04.23

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmcplugin, xbmcaddon, xbmcgui, xbmcvfs, string, os, platform, re, xbmcplugin, sys
import json
import requests
import urllib.parse
import html.parser
from bs4 import BeautifulSoup
from urllib.request import urlopen
import html5lib
import mechanize
import http.cookiejar


#live = 'aHR0cDovL29veWFsYWhkMi1mLmFrYW1haWhkLm5ldC9pL25ld3NtYXgwMl9kZWxpdmVyeUAxMTk1NjgvbWFzdGVyLm0zdTg/aGRjb3JlPTIuMTAuMyZnPVdVVFlWRlNWSUVVWQ=='
pre = 'aHR0cDovL3BsYXllci5vb3lhbGEuY29tL3Nhcy9wbGF5ZXJfYXBpL3YxL2F1dGhvcml6YXRpb24vZW1iZWRfY29kZS9Ka2NXczZ2NTNsc1JkR2Z3bENTd2dfYTVDVU12Lw=='
post = 'P2RldmljZT1odG1sNSZkb21haW49d3d3Lm5ld3NtYXh0di5jb20mc3VwcG9ydGVkRm9ybWF0cz1tcDQlMkN3ZWJt'
getv = 'aHR0cDovL3d3dy5uZXdzbWF4dHYuY29tL29veWFsYXNlcnZpY2Uuc3ZjL2dldHBvcHVsYXJ2aWRlb3M/dHlwZT0='
artbase = 'special://home/addons/plugin.video.americasvoice/resources/media/'
_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id='plugin.video.americasvoice')
self = xbmcaddon.Addon(id='plugin.video.americasvoice')
translation = selfAddon.getLocalizedString
usexbmc = selfAddon.getSetting('watchinxbmc')
settings = xbmcaddon.Addon(id="plugin.video.americasvoice")
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
#confluence_views = [500,501,502,503,504,508]
__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

from uas import *

CookieJar = http.cookiejar.LWPCookieJar(os.path.join(addon_path_profile, 'cookies.lwp'))
br = mechanize.Browser()
br.set_handle_robots(False)
br.set_handle_equiv(False)
br.addheaders = [('User-agent', ua)]
br.addheaders = [('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8')]

plugin = "Real America's Voice"

defaultimage = 'special://home/addons/plugin.video.americasvoice/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.americasvoice/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.americasvoice/resources/media/icon.png'
baseurl = 'https://api.americasvoice.news/public/live/feed'

local_string = xbmcaddon.Addon(id='plugin.video.americasvoice').getLocalizedString
addon_handle = int(sys.argv[1])
pluginhandle = int(sys.argv[1])
#QUALITY = settings.getSetting(id="quality")
confluence_views = [500,501,502,503,504,508,515]

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 2
else:
	log_level = 1
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)


def index():
	addDir2('Live', baseurl, 10, defaultimage, defaultfanart)
	addDir('Shows', 'https://americasvoice.news/playlists/', 15, defaultimage, defaultfanart)
	#addDir('Popular', getv.decode('base64'), 25, defaultimage)
	#addDir('Trending', getv.decode('base64'), 25, defaultimage)
	xbmcplugin.endOfDirectory(addon_handle)


#10
def get_live(url):
	page = get_page(url)
	data = json.loads(page)
	stream = data['url']
	page = get_page(stream)
	page = str(page).split('\\n');streams=[]
	#xbmc.log('PAGE: ' + str(page),level=log_level)
	for item in page:
		if item.startswith('https'):
			streams.append(item)
	#streamUrl = re.findall(r'\nhttps (\d\d\d\d)', str(page), flags=re.MULTILINE)
	#xbmc.log('STREAMS: ' + str(streams),level=log_level)
	for stream in streams:
		if 'e.m3u8' in stream:
			play(stream)
	sys.exit()


#15
def shows(url):
	page = get_page(url)
	soup = BeautifulSoup(page,'html5lib').find_all('li',{'class':'styles_listItem___yfJI'})
	#images = BeautifulSoup(page,'html5lib').find_all('img',{'class':'img-responsive'})
	for item in (soup):
		title = item.find('a',{'class':'styles_show__JsZ2z'}).text
		image = item.find('img')['src']
		link = item.find('a',{'class':'styles_show__JsZ2z'})
		url = 'https://americasvoice.news' + link.get('href')
		add_directory2(title,url,20,defaultfanart,image,plot='')
	xbmcplugin.endOfDirectory(addon_handle)


#20
def videos(url):
	page = get_page(url)
	soup = BeautifulSoup(page,'html5lib').find_all('div',{'class':'styles_root__KTs3D'})
	for item in soup:
		title = item.find('img')['alt'].encode('utf-8')
		image = item.find('img')['src']
		url = 'https://americasvoice.news' + item.find('a')['href']#.replace('public/live/feed/','')
		#xbmc.log('URL: ' + str(url),level=log_level)
		addDir2(title,url,30,image,defaultfanart)
	xbmcplugin.endOfDirectory(addon_handle)


#30
def streams(name,url):
	response = get_page(url)
	url = (re.compile('url":"(.+?)"').findall(str(response)))
	#xbmc.log('RESPONSE: ' + str(response),level=log_level)#.decode('base64')
	#thumbnail = defaultimage
	#listitem = xbmcgui.ListItem(name, thumbnailImage=thumbnail)
	#listitem.setProperty('mimetype', 'video/mp4')
	#listitem.addStreamInfo('video', { 'title': name })
	play(url[0])
	#xbmc.Player().play( url, listitem )
	sys.exit()
	xbmcplugin.endOfDirectory(addon_handle)


def striphtml(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)

#999
def play(url):
	xbmc.log('URL: ' + str(url),level=log_level)
	#item = xbmcgui.ListItem(path=url + '&m3u8=yes')
	item = xbmcgui.ListItem(path=url)
	item.setProperty('IsPlayable', 'true')
	return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

#99
def PLAY(name,url):
	listitem = xbmcgui.ListItem(name)
	listitem.setArt({
		'thumb': defaultimage,
		'icon': "DefaultFolder.png",
		'fanart': defaultfanart
	})
	listitem.setInfo(type="Video", infoLabels={"Title": name})
	listitem.setProperty('IsPlayable', 'true')
	#xbmc.Player().play( url + '&m3u8=yes', listitem )
	xbmc.Player().play( url, listitem )
	while xbmc.Player().isPlaying():
		continue
	sys.exit()
	xbmcplugin.endOfDirectory(addon_handle)


def get_page(url):
	br.set_handle_robots( False )
	br.set_cookiejar(CookieJar)
	response = br.open(url)
	for cookie in CookieJar:
		xbmc.log('COOKIE: ' + str(cookie),level=log_level)
		CookieJar.set_cookie(cookie)
	CookieJar.save(ignore_discard=True)
	page = response.get_data()#.encode('utf-8')
	return page


def add_directory(name,url,mode,fanart,thumbnail,plot):
	u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
	liz.setInfo( type="Video", infoLabels={ "Title": name,
											"plot": plot} )
	if not fanart:
		fanart=''
	liz.setProperty('fanart_image',fanart)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False, totalItems=30)
	return ok

def add_directory2(name,url,mode,fanart,thumbnail,plot):
	u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name) + "&iconimage=" + urllib.parse.quote_plus(thumbnail)
	ok=True
	liz=xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	if not fanart:
		fanart = ''
	liz.setArt({
		'thumb': thumbnail,
		'icon': "DefaultFolder.png",
		'fanart': fanart
	})
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	if not fanart:
		fanart=defaultfanart
	#liz.setProperty('fanart_image', artbase + 'fanart5.jpg')
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

def get_html(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent','User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:44.0) Gecko/20100101 Firefox/44.0')
	#req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8')

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


def addDir(name, url, mode, thumbnail, fanart=True, infoLabels=True):
	u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name) + "&iconimage=" + urllib.parse.quote_plus(thumbnail)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	if not fanart:
		fanart = ''
	liz.setArt({
		'thumb': thumbnail,
		'icon': "DefaultFolder.png",
		'fanart': fanart
	})
	liz.setInfo(type="Video", infoLabels={"Title": name})
	liz.setProperty('IsPlayable', 'true')
	if not fanart:
		fanart=defaultfanart
	liz.setProperty('fanart_image', defaultfanart)
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok


def addDir2(name,url,mode,thumbnail, fanart=False, infoLabels=True):
	u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name) + "&iconimage=" + urllib.parse.quote_plus(thumbnail)
	ok=True
	liz=xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	if not fanart:
		fanart = ''
	liz.setArt({
		'thumb': thumbnail,
		'icon': "DefaultFolder.png",
		'fanart': fanart
	})
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	liz.setProperty('IsPlayable', 'true')
	if not fanart:
		fanart=defaultfanart
	liz.setProperty('fanart_image', defaultfanart)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
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

xbmc.log("Mode: " + str(mode),level=log_level)
xbmc.log("URL: " + str(url),level=log_level)
xbmc.log("Name: " + str(name),level=log_level)

if mode == None or url == None or len(url) < 1:
	xbmc.log("Main Menu",level=log_level)
	index()
elif mode == 4:
	xbmc.log("Play Video",level=log_level)
	play(url)
elif mode == 10:
	xbmc.log("Get Live Stream",level=log_level)
	get_live(url)
elif mode==15:
	xbmc.log("RAV Shows",level=log_level)
	shows(url)
elif mode==20:
	xbmc.log("RAV Videos",level=log_level)
	videos(url)
elif mode==25:
	xbmc.log("RAV Get Videos",level=log_level)
	get(name,url)
elif mode==30:
	xbmc.log("RAV Streams",level=log_level)
	streams(name,url)
elif mode==99:
	xbmc.log("RAV Play Stream",level=log_level)
	PLAY(name,url)
elif mode==999:
	xbmc.log("RAV Play Show",level=log_level)
	play(url)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
