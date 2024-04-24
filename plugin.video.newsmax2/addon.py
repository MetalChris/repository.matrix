#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2 or later)

#2023.02.21

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmcplugin, xbmcaddon, xbmcgui, xbmcvfs, string, os, platform, re, xbmcplugin, sys
import json
import requests
import urllib.parse
import html.parser
from bs4 import BeautifulSoup
from urllib.request import urlopen
import html5lib
import http.cookiejar


#live = 'aHR0cDovL29veWFsYWhkMi1mLmFrYW1haWhkLm5ldC9pL25ld3NtYXgwMl9kZWxpdmVyeUAxMTk1NjgvbWFzdGVyLm0zdTg/aGRjb3JlPTIuMTAuMyZnPVdVVFlWRlNWSUVVWQ=='
pre = 'aHR0cDovL3BsYXllci5vb3lhbGEuY29tL3Nhcy9wbGF5ZXJfYXBpL3YxL2F1dGhvcml6YXRpb24vZW1iZWRfY29kZS9Ka2NXczZ2NTNsc1JkR2Z3bENTd2dfYTVDVU12Lw=='
post = 'P2RldmljZT1odG1sNSZkb21haW49d3d3Lm5ld3NtYXh0di5jb20mc3VwcG9ydGVkRm9ybWF0cz1tcDQlMkN3ZWJt'
getv = 'aHR0cDovL3d3dy5uZXdzbWF4dHYuY29tL29veWFsYXNlcnZpY2Uuc3ZjL2dldHBvcHVsYXJ2aWRlb3M/dHlwZT0='
artbase = 'special://home/addons/plugin.video.newsmax2/resources/media/'
_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id='plugin.video.newsmax2')
self = xbmcaddon.Addon(id='plugin.video.newsmax2')
translation = selfAddon.getLocalizedString
usexbmc = selfAddon.getSetting('watchinxbmc')
settings = xbmcaddon.Addon(id="plugin.video.newsmax2")
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
#confluence_views = [500,501,502,503,504,508]
__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

from uas import *

CookieJar = http.cookiejar.LWPCookieJar(os.path.join(addon_path_profile, 'cookies.lwp'))

plugin = "Newsmax TV"

defaultimage = 'special://home/addons/plugin.video.newsmax2/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.newsmax2/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.newsmax2/resources/media/icon.png'
baseurl = 'https://www.newsmaxtv.com'

local_string = xbmcaddon.Addon(id='plugin.video.newsmax2').getLocalizedString
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
xbmc.log(('NewsMax2 Started'),level=log_level)


def index():
	addDir2('Live', baseurl, 10, defaultimage, defaultfanart)
	addDir('Shows', baseurl, 15, defaultimage, defaultfanart)
	#addDir('Popular', getv.decode('base64'), 25, defaultimage)
	#addDir('Trending', getv.decode('base64'), 25, defaultimage)
	xbmcplugin.endOfDirectory(addon_handle)


#10
def get_live(url):
	page = requests.get(baseurl)
	xbmc.log('RESPONSE: ' + str(page),level=log_level)
	#page = get_page(url)
	soup = BeautifulSoup(page.text,'html5lib')
	stream = re.compile('src: "(.+?)",').findall(str(soup.text))
	xbmc.log('STREAM: ' + str(stream),level=log_level)
	PLAY('Newsmax TV Live', stream[1])
	xbmcplugin.endOfDirectory(addon_handle)


#15
def shows(url):
	page = requests.get(url)
	soup = BeautifulSoup(page.text,'html5lib').find_all('a')
	for item in (soup):
		if '/Shows' in str(item):
			title = item.find('h3').text
			#image = baseurl + item.find('img')['src'].split('?')[0].replace('https','http')
			#xbmc.log('IMAGE: ' + str(image),level=log_level)
			url = baseurl + item.get('href')
			add_directory2(title,url,20,defaultfanart,defaultimage,plot='')
	xbmcplugin.endOfDirectory(addon_handle)


#20
def videos(url):
	page = requests.get(url)
	vidUrl = url
	soup = BeautifulSoup(page.text,'html5lib')#.find_all('h6')[1:31]
	endpoint = re.compile("endpoint: '(.+?)',").findall(str(soup))[0]#.split('=')[-1]
	xbmc.log('ENDPOINT: ' + str(endpoint),level=log_level)
	#ooid = re.compile('"ooid=(.+?)"').findall(str(soup))
	#xbmc.log('OOID: ' + str(ooid),level=log_level)
	eurl = baseurl + str(endpoint)
	xbmc.log('EURL: ' + str(eurl),level=log_level)
	page = requests.get(eurl).json()
	#page = get_html(eurl)
	xbmc.log('RESPONSE: ' + str(len(page)),level=log_level)
	data = json.loads(page)#[1:-1]#.encode('utf-8')#.encode('ascii', 'ignore')#.decode('utf-8')#.encode('ascii', 'ignore')
	total = len(data)
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	i=0
	for count, item in enumerate(data['items']):
		title = item['label']#str(extract_key_value(item, "label"))
		image = item['images']['still'][0]['url']
		description = item['description']
		videoId = item['id']
		url = vidUrl + '/vid/' + videoId
		xbmc.log('URL: ' + str(url),level=log_level)
		#title = str(item['items'][count]['label'])
		#url = 'https://nmxmam.nmax.tv/vodservice/?id='# + endpoint
		addDir2(title,url,99,image,defaultfanart)
	xbmcplugin.endOfDirectory(addon_handle)

def extract_key_value(json_data, key):
    """Extracts a specific key-value pair from a JSON data"""
    data = json.loads(json_data)
    value = data.get(key)
    return value

#30
def streams(name,url):
	response = get_html(url)
	url = (re.compile('data":"(.+?)"').findall(str(response))[-1]).decode('base64')
	thumbnail = defaultimage
	listitem = xbmcgui.ListItem(name, thumbnailImage=thumbnail)
	listitem.setProperty('mimetype', 'video/mp4')
	listitem.addStreamInfo('video', { 'title': name })
	xbmc.Player().play( url, listitem )
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


def add_directory(name,url,mode,fanart,thumbnail,plot):
	u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
	liz.setInfo( type="Video", infoLabels={ "Title": name,
											"plot": plot} )
	if not fanart:
		fanart=''
	liz.setProperty('fanart_image',defaultfanart)
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
		'fanart': defaultfanart
	})
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	if not fanart:
		fanart=defaultfanart
	#liz.setProperty('fanart_image', defaultfanart)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

def get_html(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent', ua)
	req.add_header('X-Requested-With', 'XMLHttpRequest')
	req.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')
	#req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8')
	#req.add_header('Host','www.newsmaxtv.com')
	#req.add_header('Cookie','CMSPreferredCulture=en-US; ASP.NET_SessionId=qbxr0uopzsfhqhzbkuwy4arl; BIGipServerORIGIN_NewsmaxTV.app~ORIGIN_NewsmaxTV_pool=1980737728.47873.0000; AKA_A2=A; ak_bmsc=72F8E213B4EC8FC8AC897A362935183C~000000000000000000000000000000~YAAQuPjNFyschAyPAQAARZi3DBcn8j7J1+LOGhscK2HO7+d8PUXMp+bBmXuv+SIGS3ywGLH97aobAnTioqljEJl4rUuVTl67c2nUl4R/sv+oUxJ+SVq1E3KN+TT6MisqKhQ57kcmOhDN3H5zUC3Y3SmcZ7cEJtMDgM1E7eETJSZVBoSPQBONTeACO4oyLjQzNiSTlc4qVz8SO5fUIVb231u0W04ZYkiGx9N7gB1bq/vgTvoM6Lmp26+hy/XfKnkR/gqEx7kp1Be7WgCwNTvRw4ZjDaXUZBbh0mpV/0RPFBumJPL6ikDlIpCM7hbGt0tS8Y9hoeDogMk/Msg5S1tsDOJP4TNUUQf3bxNHgAYASbmoNx0D9EfqNT2SPpcGhN5zsGlCDFia8gBqvVIW0wk0BVLFXi7pVoFoAkmj27Trm80qdCRPcIFcA+uIq5lmpKikZ1zno0jceYvainQ1wGe3Mw==; bm_sv=E14B3E7323932863286133700B1BE516~YAAQyvjNFyo2IOiOAQAAidfKDBcXAtR77ylqVf9yg0++06xkOK0KpElFkWi2worlVjnvgoYBeeGRr+rVos3KR/BIZWLmwuMr+HwYucSJDsSmLpPKIRB0gYFsveztbaxxmlvtfcD3rffR7qZwgs2SrNq1aXHO0p0JzFlKvGoh1h0cnDc34UmH2GxilC2rG55kHk16gs7K7RLHHxfxppIVp92oIctQE1q8KfEha7smFJPbPGG8EWo1xxzNa//3lqWrIeC7~1')

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
		'fanart': defaultfanart
	})
	liz.setInfo(type="Video", infoLabels={"Title": name})
	liz.setProperty('IsPlayable', 'true')
	if not fanart:
		fanart=defaultfanart
	liz.setProperty('fanart_image', defaultfanart)
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok


def addDir2(name,url,mode,thumbnail, fanart=True, infoLabels=True):
	u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name) + "&iconimage=" + urllib.parse.quote_plus(thumbnail)
	ok=True
	liz=xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	if not fanart:
		fanart = ''
	liz.setArt({
		'thumb': thumbnail,
		'icon': "DefaultFolder.png",
		'fanart': defaultfanart
	})
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	if not fanart:
		fanart=defaultfanart
	liz.setProperty('fanart_image', defaultfanart)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
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
	get_live(url)
elif mode == 4:
	xbmc.log("Play Video",level=log_level)
	play(url)
elif mode == 10:
	xbmc.log("Get Live Stream",level=log_level)
	get_live(url)
elif mode==15:
	xbmc.log("Newsmax Shows",level=log_level)
	shows(url)
elif mode==20:
	xbmc.log("Newsmax Videos",level=log_level)
	videos(url)
elif mode==25:
	xbmc.log("Newsmax Get Videos",level=log_level)
	get(name,url)
elif mode==30:
	xbmc.log("Newsmax Streams",level=log_level)
	streams(name,url)
elif mode==99:
	xbmc.log("Newsmax Play Stream",level=log_level)
	PLAY(name,url)
elif mode==999:
	xbmc.log("Newsmax Play Show",level=log_level)
	play(url)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
