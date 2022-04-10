#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2)

#2021.10.11

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmcplugin, xbmcaddon, xbmcgui, sys, re
from bs4 import BeautifulSoup
import html5lib

addon_id = 'plugin.video.nfpf'
selfAddon = xbmcaddon.Addon(id=addon_id)
translation = selfAddon.getLocalizedString
#addon_version = selfAddon.getAddonInfo('version')
settings = xbmcaddon.Addon(id="plugin.video.nfpf")

defaultimage = 'special://home/addons/plugin.video.nfpf/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.nfpf/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.nfpf/resources/media/icon.png'
artbase = 'special://home/addons/plugin.video.nfpf/resources/media/'
baseurl = 'https://www.filmpreservation.org'

plugin = 'National Film Preservation Foundation'

addon_handle = int(sys.argv[1])

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 2
else:
	log_level = 1
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)


def CATEGORIES():
	html = get_html('https://www.filmpreservation.org/preserved-films/screening-room')
	soup = BeautifulSoup(html,'html5lib').find_all('tbody')
	xbmc.log('SOUP: ' + (str(len(soup))),level=log_level)
	for item in soup:
		title = item.find('h5').text
		if 'Johnson' in title:
			continue
		url = baseurl + item.find('a')['href']
		addDir(title, url, 15, defaultimage)
	xbmcplugin.endOfDirectory(addon_handle)


#15
def GET_ITEM(name,url):
	html = get_html(url)
	soup = BeautifulSoup(html,'html5lib').find_all('figure', {'class':'video-thumb'})
	xbmc.log('SOUP: ' + (str(len(soup))),level=log_level)
	for item in soup:
		caption = item.find('figcaption')
		title = caption.find('a').text.encode('utf-8')
		jurl = baseurl + caption.find('a')['href']
		image = item.find('img')['src']
		url = 'plugin://plugin.video.nfpf?mode=20&url=' + urllib.parse.quote_plus(jurl)
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","label":title,"title":title})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
	xbmcplugin.endOfDirectory(addon_handle)


#20
def GET_STREAM(url):
	html = get_html(url)
	soup = BeautifulSoup(html,'html5lib').find_all('div', {'class':'film-player'})
	#xbmc.log('SOUP: ' + (str(soup)), level=xbmc.LOGDEBUG)
	stream = re.compile('data-file="(.+?)"').findall(str(soup))[0].replace('https','http')
	if '10mbps' in stream:
		stream = stream.replace('10mbps','6mbps')
	xbmc.log('STREAM: ' + str(stream),level=log_level)
	xbmc.log('SOUP: ' + (str(len(soup))),level=log_level)
	PLAY(name, stream)


#99
def PLAY(name,url):
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log('### SETRESOLVEDURL ###',level=log_level)
	listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
	xbmc.log('URL: ' + str(url),level=log_level)
	xbmcplugin.endOfDirectory(addon_handle)



def get_html(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent','Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0')

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


def addDir(name,url,mode,iconimage, fanart=False, infoLabels=False):
	u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)
	#ok=True
	liz=xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"mediatype":"video","label":name,"title":name,"genre":"Sports"})
	#liz.setProperty('IsPlayable', 'true')
	#liz.setInfo( type="Video", infoLabels={ "Title": name } )
	if not fanart:
		fanart=defaultfanart
	#liz.setProperty('fanart_image',fanart)
	liz.setArt({'thumb':defaulticon,'fanart':defaultfanart})
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
	xbmc.log("NFPF Menu",level=log_level)
	CATEGORIES()
elif mode == 15:
	xbmc.log("NFPF Get Item",level=log_level)
	GET_ITEM(name,url)
elif mode == 20:
	xbmc.log("NFPF Get Stream",level=log_level)
	GET_STREAM(url)
elif mode == 99:
	xbmc.log("NFPF Play Video",level=log_level)
	PLAY(name,url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
