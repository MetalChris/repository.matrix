#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2)

#2019.02.03

import urllib, urllib2, xbmcplugin, xbmcaddon, xbmcgui, htmllib, sys, os, re
import json
import socket

addon_id = 'plugin.video.foxweather'
selfAddon = xbmcaddon.Addon(id=addon_id)
translation = selfAddon.getLocalizedString
#addon_version = selfAddon.getAddonInfo('version')
settings = xbmcaddon.Addon(id=addon_id)

defaultimage = 'special://home/addons/plugin.video.foxweather/icon.png'
defaultfanart = 'special://home/addons/plugin.video.foxweather/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.foxweather/icon.png'
artbase = 'special://home/addons/plugin.video.foxweather/resources/media/'
baseurl = 'https://www.cbssports.com/live/'

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 2
else:
	log_level = 1
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)

plugin = 'FOX Weather'

addon_handle = int(sys.argv[1])


def CATEGORIES():
	addDir('Live', 'https://api3.fox.com/v2.0/screens/foxweather-live', 5, defaultimage)
	addDir('Latest', 'https://www.cbssports.com/live/', 4, defaultimage)
	xbmcplugin.endOfDirectory(addon_handle)


#4
def FOX(url):
	response = get_html(url)
	xbmc.log('RESPONSE: ' + str(response.text),level=log_level)
	jsob = re.compile("channels: JSON.parse\('(.+?)'").findall(str(response))[0].replace('&quot;','"')
	xbmc.log('JSOB: ' + str(jsob),level=log_level)
	names = re.compile('name":"(.+?)",').findall(jsob)
	labels = re.compile('label":"(.+?)",').findall(jsob)
	urls = re.compile('url":"(.+?)",').findall(jsob)
	total = len(urls)
	for name, label, url in zip(names, labels, urls):
		if name == 'live':
			url = 'https://www.cbssports.com/live/'
			url = 'plugin://plugin.video.foxweather?mode=5&url=' + urllib.quote_plus(url)
			li = xbmcgui.ListItem(label)
			li.setProperty('IsPlayable', 'true')
			li.setInfo(type="Video", infoLabels={"mediatype":"video","label":label,"title":label,"genre":"Sports"})
			li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
		else:
			url = url.replace('[playlist]', name).replace('\\','')
			url = 'plugin://plugin.video.foxweather?mode=6&url=' + urllib.quote_plus(url)
			li = xbmcgui.ListItem(label)
			li.setInfo(type="Video", infoLabels={"mediatype":"video","label":label,"title":label,"genre":"Sports"})
			li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#5
def LIVE(name,url):
	response = get_html(url)
	json_url = re.compile("appFeedUrl: '(.+?)'").findall(str(response))[0]
	response = get_html(json_url)
	jdata = json.loads(response)
	channels = jdata[0]['channel'];i = 0
	for channel in jdata:
		if jdata[0]['channel'][i]['label'] == 'LIVE':
			url = jdata[0]['channel'][i]['channel'][0]['dataURL']['url']
		i = i + 1
	xbmc.log('I: ' + str(i),level=log_level)
	xbmc.log('URL: ' + str(url),level=log_level)
	response = get_html(url)
	jdata = json.loads(response)
	events = jdata['data']['event'];i = 0
	for event in events:
		if jdata['data']['event'][i]['is_cbs_sports_now'] == 'true':
			live_stream = jdata['data']['event'][i]['stream'][-1]['desktop_partner_url']
		i = i + 1
	xbmc.log('LIVE STREAM: ' + str(live_stream),level=log_level)
	PLAY(plugin,live_stream)


#6
def VOD(url):
	response = get_html(url)
	data = json.loads(response)
	total = len(data)
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for i in range(total):
		title = data[i]['title']
		image = data[i]['image']['path']
		url_total = len(data[i]['metaData']['files'])
		for u in range(url_total):
			file_type = data[i]['metaData']['files'][u]['type']
			if file_type == 'HLS_VARIANT_TABLET':
				url = data[i]['metaData']['files'][u]['url']
		url = 'plugin://plugin.video.foxweather?mode=25&url=' + urllib.quote_plus(url)
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","label":title,"title":title,"genre":"Sports"})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#25
def get_redirected_data(name,url):
	if 'mp4' in url:
		PLAY(name,url)
	opener = urllib2.build_opener()
	try:request = opener.open(url)
	except urllib2.HTTPError:
		xbmcgui.Dialog().notification(name, 'Stream Not Available', defaultimage, 5000, False)
		sys.exit()
	data = request.read()
	#bitrates = re.findall(r'RESOLUTION.*, ', str(data), flags=re.MULTILINE)#.split(',')[3]
	#xbmc.log('BITRATES: ' + str(sorted(bitrates)),level=log_level)
	bitrates = re.findall(r'x.*, ', str(data), flags=re.MULTILINE)#.split(',')[3]
	#bitrates = ([s.replace('RESOLUTION=', '') for s in bitrates])
	bitrates = ([s.replace(', ', '') for s in bitrates])
	bitrates.sort()
	xbmc.log('BITRATES: ' + str(bitrates),level=log_level)
	streams = re.findall(r'/.*\n', str(data), flags=re.MULTILINE)
	#streams = sorted(streams)
	#xbmc.log('STREAMS: ' + str(streams),level=log_level)
	stream = 'https://cbssportspmd-a.akamaihd.net' + streams[-1].strip()
	PLAY(name,stream)


def TEST_STREAMS(url):
	req = urllib2.Request(url[0])
	req.add_header('User-Agent','Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0')
	try:response = urllib2.urlopen(req, timeout=10)
	except urllib2.HTTPError:
		xbmc.log('* HTTP Error *',level=log_level)
		stream = url[1]
		return stream
	#except socket.timeout:
		#xbmc.log('TIMEOUT', level=xbmc.LOGDEBUG)
		#stream = url[1]
		#return stream
	except socket.error:
		xbmc.log('* SOCKET ERROR *',level=log_level)
		stream = url[1]
		return stream
	stream = url[0]
	return stream


#99
def PLAY(name,url):
	xbmc.log('URL: ' + str(url),level=log_level)
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log('### SETRESOLVEDURL ###',level=log_level)
	listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
	xbmc.log('URL: ' + str(url),level=log_level)
	xbmcplugin.endOfDirectory(addon_handle)



def get_html(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent','Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0')
	req.add_header('X-Api-Key:','pP3tjxCcmc8eoZc8Slwzkmmtz80swn2b')

	try:
		response = urllib2.urlopen(req)
		html = response.read()
		response.close()
	except urllib2.HTTPError:
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
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
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
	url = urllib.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.unquote_plus(params["name"])
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
	xbmc.log("CBS Sports HQ Menu",level=log_level)
	CBS(baseurl)
elif mode == 4:
	xbmc.log("CBS Sports HQ Categories",level=log_level)
	CBS(url)
elif mode == 5:
	xbmc.log("CBS Sports HQ Live",level=log_level)
	LIVE(name,url)
elif mode == 6:
	xbmc.log("CBS Sports HQ On Demand",level=log_level)
	VOD(url)
elif mode == 25:
	xbmc.log("CBS Sports HQ Get Stream",level=log_level)
	get_redirected_data(name,url)
elif mode == 99:
	xbmc.log("Play Video",level=log_level)
	PLAY(name,url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
