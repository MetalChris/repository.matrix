#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2)

#2021.10.09

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmcplugin, xbmcaddon, xbmcgui, string, calendar, re, sys, os
from bs4 import BeautifulSoup
from html.parser import HTMLParser
import json
import html5lib
from urllib.request import urlopen
import datetime
import time
import mechanize

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmc.translatePath(_addon.getAddonInfo('profile'))

selfAddon = xbmcaddon.Addon(id='plugin.video.stadium')
translation = selfAddon.getLocalizedString
#usexbmc = selfAddon.getSetting('watchinxbmc')

defaultimage = 'special://home/addons/plugin.video.stadium/icon.png'
defaultfanart = 'special://home/addons/plugin.video.stadium/fanart.jpg'
defaultvideo = 'special://home/addons/plugin.video.stadium/icon.png'
defaulticon = 'special://home/addons/plugin.video.stadium/icon.png'

addon = 'Stadium'
addon_handle = int(sys.argv[1])
confluence_views = [500,501,502,503,504,508]
settings = xbmcaddon.Addon(id="plugin.video.stadium")
username = settings.getSetting(id="username")
password = settings.getSetting(id="password")
log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 2
else:
	log_level = 1
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)

today = datetime.date.today()
xbmc.log('TODAY: ' + str(today),level=log_level)
todays_date = str(today.month) + '/' + str(today.day)
xbmc.log('TODAYS DAY: ' + str(today.day),level=log_level)

pattern = '%Y-%m-%d'
#epoch = int(time.mktime(time.strptime(str(today), pattern)))
epoch = int(time.time())
xbmc.log('EPOCH: ' + str(epoch),level=log_level)

live = 'BCpkADawqM3WJtaZFwiKMH8ODpFLZ6DppaQl-HBeZ1r8mV5fWDwRAHURNmjNkxKnsHgvYkx0DXxq6orR3EfslqQ4v9_IazoDlrS2cGoPBDfRgHzLUOUHIOKYeDxq-gI7yM0Il5-5X6kjdMhJ'


def CATEGORIES():
	sched = 'https://watchstadium.com/api/stadium/v1/events'
	response = get_html(sched,live)
	data = json.loads(response)#; i = 0
	total = int(len(data['events']))
	xbmc.log('TOTAL: ' + str(total),level=log_level);e = 0
	for i in range(total):
		xbmc.log('IS_LIVE: ' + str(data['events'][i]['is_live']),level=log_level)
		if (data['events'][i]['is_live']) == False:
			continue
		e = e + 1
	m3u8 = 'plugin://plugin.video.stadium?mode=5&url=' + urllib.parse.quote_plus('https://watchstadium.com/')
	li = xbmcgui.ListItem('Stadium TV Live')
	li.setProperty('IsPlayable', 'true')
	li.setInfo(type="Video", infoLabels={"mediatype":"video","title":'Stadium TV Live',"genre":"Sports"})
	li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=m3u8, listitem=li, isFolder=False)
	addDir('Live Now ' + '(' + str(e) + ')', 'https://watchstadium.com/api/stadium/v1/events', 6, defaultimage)
	addDir('Event Schedule', 'https://watchstadium.com/api/stadium/v1/events', 7, defaultimage)
	addDir('On Demand', 'https://watchstadium.com/', 16, defaultimage)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


#5
def LIVE(name,url):
	html = get_html(url,live)
	soup = BeautifulSoup(html,'html5lib').find_all('video')
	xbmc.log('SOUP: ' + str(soup),level=log_level)
	for item in soup:
		account = item.get('data-account')
		id = item.get('data-video-id')
		ad = item.get('data-ad-config-id')
	url = 'https://edge.api.brightcove.com/playback/v1/accounts/' + account + '/videos/' + id + '?ad_config_id=' + ad
	xbmc.log('URL: ' + str(url),level=log_level)
	jsob = get_html(url,live)
	xbmc.log('JSOB: ' + str(jsob),level=log_level)
	data = json.loads(jsob)#; i = 0
	src = data['sources'][0]['src']
	xbmc.log('SRC: ' + str(src),level=log_level)
	PLAY(name,src)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#6
def GET_LIVE_NOW(name,url):
	sports = []
	response = get_html(url,live)
	data = json.loads(response); i = 0
	#xbmc.log('DATA: ' + str(data),level=log_level)
	total = int(len(data['events']))
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	if total > 100:
		total = 99
	tags = []
	for i in range(total):
		#i = str(i)
		try:tag = (data['events'][i]['sports']); x = 0
		except IndexError:
			continue
		except KeyError:
			continue
		#sport = data['events'][i]['sport_name']
		xbmc.log('IS_LIVE: ' + str(data['events'][i]['is_live']),level=log_level)
		if (data['events'][i]['is_live']) == False:
			continue
		sport = data['events'][i]['sports']
		xbmc.log('SPORT: ' + str(sport),level=log_level)
		sportkey = list(sport.keys())[0]
		sport_name = sportkey[-1]
		sport = data['events'][i]['sports'][sportkey]
		try:title = sport + ': ' + str(data['events'][i]['title']).replace("&#8217;","'")
		#xbmc.log('TITLE: ' + str(title),level=log_level)
		except KeyError:
			continue
		if 'Facebook' in title:
			continue
		try: image = 'http:' + (data['events'][i]['thumbnail'])
		except KeyError:
			image = defaultimage
		url = data['events'][i]['permalink']
		m3u8 = 'plugin://plugin.video.stadium?mode=20&url=' + urllib.parse.quote_plus(url)
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"genre":"Sports"})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=m3u8, listitem=li, isFolder=False)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)



#7
def GET_SPORTS(name,url):
	sports = []
	response = get_html(url,live)
	data = json.loads(response); i = 0
	#xbmc.log('DATA: ' + str(data),level=log_level)
	total = int(len(data['events']))
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	if total > 100:
		total = 99
	tags = []
	for i in range(total):
		#i = str(i)
		try:tag = (data['events'][i]['sports']); x = 0
		except IndexError:
			continue
		except KeyError:
			continue
		#sport = data['events'][i]['sport_name']
		sport = data['events'][i]['sports']
		sportkey = list(sport.keys())[0]
		sport_name = sportkey[-1]
		sport = data['events'][i]['sports'][sportkey]
		if not sport in sports:
			sports.append(sport)
	for sport in sorted(sports):
		addDir(sport, url, 10, defaultimage, defaultfanart)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#10
def INDEX(name,url):
	html = get_html(url,live)
	sched = 'https://watchstadium.com/api/stadium/v1/events'
	xbmc.log('SCHED: ' + str(sched),level=log_level)
	response = get_html(sched,live)
	data = json.loads(response)#; i = 0
	total = int(len(data['events']))
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	if total > 100:
		total = 99
	for i in range(total):
		try:title = (data['events'][i]['title']).replace("&#8217;","'")
		#xbmc.log('TITLE: ' + str(title),level=log_level)
		except KeyError:
			continue
		if 'Facebook' in title:
			continue
		p = 0
		#sport = (data['events'][i]['sport_name'])
		sport = data['events'][i]['sports']
		sportkey = list(sport.keys())[0]
		xbmc.log('SPORTKEY: ' + str(sportkey),level=log_level)
		#xbmc.log('SPORT: ' + str(sport),level=log_level)
		sport_name = sportkey[-1]
		sport = data['events'][i]['sports'][sportkey]
		if sport == name:
			#xbmc.log('SPORT: ' + str(sport),level=log_level)
			event_id = str(data['events'][i]['id'])
			title = (data['events'][i]['title']).replace("&#8217;","'")#.encode('ascii', 'ignore')
			#title = sanitize(title)
			etime = (data['events'][i]['start_time'])
			start_date = (data['events'][i]['start_date'])
			end = (data['events'][i]['end_time_ts'])
			xbmc.log('END: ' + str(end),level=log_level)
			if epoch > end:
				continue
			is_Live = (data['events'][i]['is_live'])
			xbmc.log('LIVE: ' + str(is_Live),level=log_level)
			url = (data['events'][i]['permalink'])
			try: image = 'http:' + (data['events'][i]['thumbnail'])
			except KeyError:
				image = defaultimage
			#if is_Live == False:
				#etime = '[' + start + '] '
			if (epoch > end):# and (is_Live != False):
				etime = '[Ended]'
			else:
				etime = etime
			event = str(etime) + ' ' + str(title)# + ' (' + sport_title + ')'
			if str(today.day) in start_date:
				addDir2(event, url, 20, image, defaultfanart)
			else:
				addDir2('[COLOR=ff5b5b5b]'+ etime + ' ' +'[/COLOR]' + title, url, 20, image, defaultfanart)
			p = p + 1
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

class style:
   BOLD = '\033[1m'
   END = '\033[0m'

#15
def ON_DEMAND(url):
	html = get_html(url,live)
	soup = BeautifulSoup(html,'html5lib').find_all('div',{'class':'carouselHeader'})
	for item in soup:
		title = item.find('div',{'class':'carouselTitle'}).text.strip()
		addDir(title, url, 16, defaultimage, defaultfanart)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#16
def GET_VIDEOS(name,url):
	xbmc.log('NAME: ' + str(name),level=log_level)
	html = get_html(url,live)
	soup = BeautifulSoup(html,'html5lib').find_all('div',{'class':'carouselItem'});i = 0
	xbmc.log('SOUP LENGTH: ' + str(len(soup)),level=log_level)
	for item in soup:
		title = item.find('span',{'class':'carouselItemTitle'}).text.encode('ascii', 'ignore').strip()
		url = item.find('a')['href']
		assetId = re.compile('data-asset-id="(.+?)"').findall(str(item))[0]
		image = item.find('img')['data-src'].split(',')[-1].strip()
		if not 'https:' in image:
			image = 'https:' + image
		image = image.rpartition('-')[0] + '.jpg'
		m3u8 = 'plugin://plugin.video.stadium?mode=17&url=' + urllib.parse.quote_plus(url)
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"genre":"Sports"})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=m3u8, listitem=li, isFolder=False)
	xbmc.log('IMAGE: ' + str(image), level=log_level)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#17
def GET_MEDIA_ID(name,url):
	html = get_html(url,live)
	soup = BeautifulSoup(html,'html5lib').find_all('video')
	xbmc.log('SOUP: ' + str(soup),level=log_level)
	for item in soup:
		account = item.get('data-account')
		id = item.get('data-video-id')
	url = 'https://edge.api.brightcove.com/playback/v1/accounts/' + account + '/videos/' + id# + '?ad_config_id=' + ad
	xbmc.log('URL: ' + str(url),level=log_level)
	jsob = get_html(url,live)
	xbmc.log('JSOB: ' + str(jsob),level=log_level)
	data = json.loads(jsob)#; i = 0
	src = data['sources'][0]['src']
	xbmc.log('SRC: ' + str(src),level=log_level)
	PLAY(name,src)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#20
def GET_PAGE(name,url):
	html = get_html(url,live)
	soup = BeautifulSoup(html,'html5lib').find_all('video')
	#xbmc.log('SOUP: ' + str(soup),level=log_level)
	pk_script = BeautifulSoup(html,'html5lib').find_all('script',{'id':'stadium-brightcove-player'})
	#xbmc.log('PK_SCRIPT: ' + str(pk_script),level=log_level)
	#script_url = re.compile('src="(.+?)">').findall(str(pk_script))[0]
	for url in pk_script:
		script_url = url.get('src')
	xbmc.log('SCRIPT_URL: ' + str(script_url),level=log_level)
	js_text = get_html(script_url,live)
	event_pk = re.compile('policyKey:"(.+?)"').findall(str(js_text))[0]
	xbmc.log('EVENT_PK: ' + str(event_pk),level=log_level)
	for item in soup:
		account = item.get('data-account')
		id = item.get('data-video-id')
		ad = item.get('data-ad-config-id')
	url = 'https://edge.api.brightcove.com/playback/v1/accounts/' + account + '/videos/' + id + '?ad_config_id=' + ad
	xbmc.log('URL: ' + str(url),level=log_level)
	jsob = get_html(url,event_pk)
	if jsob == False:
		xbmcgui.Dialog().notification(name, 'Stream Not Available', defaultimage, 5000, False)
		sys.exit()
	#xbmc.log('JSOB: ' + str(jsob),level=log_level)
	data = json.loads(jsob)#; i = 0
	src = data['sources'][0]['src']
	xbmc.log('SRC: ' + str(src),level=log_level)
	PLAY(name,src)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


def get_redirected_url(url):
	opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
	opener.addheaders = [('Host', 'broker.watchstadium.com')]
	opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0')]
	request = opener.open(url)
	try:request = opener.open(url)
	except urllib.error.HTTPError:
		xbmcgui.Dialog().notification(name, 'Stream Not Available', defaultimage, 5000, False)
		sys.exit()
	return request.url


def get_redirected_data(url):
	opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
	try:request = opener.open(url)
	except urllib.error.HTTPError:
		xbmcgui.Dialog().notification(name, 'Stream Not Available', defaultimage, 5000, False)
		sys.exit()
	data = request.read()
	streams = re.findall(r'https.*\n', str(data), flags=re.MULTILINE)
	return streams[0].strip()


#99
def PLAY(name,url):
	listitem = xbmcgui.ListItem(name)
	listitem.setArt({
		'thumb': defaultimage,
		'icon': "DefaultFolder.png",
		'fanart': defaultfanart
	})
	listitem.setInfo(type="Video", infoLabels={"Title": name})
	listitem = xbmcgui.ListItem(path = url)
	xbmc.log(('### SETRESOLVEDURL ###'),level=log_level)
	listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
	xbmc.log('URL: ' + str(url),level=log_level)
	xbmcplugin.endOfDirectory(addon_handle)


def striphtml(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)


def sanitize(data):
	output = ''
	for i in data:
		for current in i:
			if ((current >= '\x20') and (current <= '\xD7FF')) or ((current >= '\xE000') and (current <= '\xFFFD')) or ((current >= '\x10000') and (current <= '\x10FFFF')):
			   output = output + current
	return output



def get_html(url,pk):
	req = urllib.request.Request(url)
	req.add_header('Accept', 'application/json;pk=' + pk)
	req.add_header('User-Agent','Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0')

	try:
		response = urllib.request.urlopen(req)
		html = response.read()
		response.close()
	except urllib.error.HTTPError:
		response = False
		html = False
	return html



def get_data(url):
	xbmc.log('URL: ' + str(url),level=log_level)
	req = urllib.request.Request(url)
	#req.add_header('Host', 'broker.watchstadium.com')
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


def addDir(name, url, mode, thumbnail, fanart=False, infoLabels=True):
	u = sys.argv[0] + "?url=" + urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name) + "&iconimage=" + urllib.parse.quote_plus(thumbnail)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setArt({
		'thumb': thumbnail,
		'icon': "DefaultFolder.png",
		'fanart': fanart
	})
	liz.setInfo(type="Video", infoLabels={"Title": name})
	liz.setProperty('IsPlayable', 'true')
	if not fanart:
		fanart=defaultfanart
	liz.setProperty('fanart_image',fanart)
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok


def addDir2(name, url, mode, thumbnail, fanart=False, infoLabels=True):
	u = sys.argv[0] + "?url=" + urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name) + "&iconimage=" + urllib.parse.quote_plus(thumbnail)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setArt({
		'thumb': thumbnail,
		'icon': "DefaultFolder.png",
		'fanart': fanart
	})
	liz.setInfo(type="Video", infoLabels={"Title": name})
	liz.setProperty('IsPlayable', 'true')
	if not fanart:
		fanart=defaultfanart
	liz.setProperty('fanart_image',fanart)
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
	xbmc.log("Stadium Menu",level=log_level)
	CATEGORIES()
elif mode == 5:
	xbmc.log("Stadium TV Live",level=log_level)
	LIVE(name,url)
elif mode == 6:
	xbmc.log("Get Live Now",level=log_level)
	GET_LIVE_NOW(name,url)
elif mode == 7:
	xbmc.log("Get Stadium Sports",level=log_level)
	GET_SPORTS(name,url)
elif mode == 10:
	xbmc.log("Stadium Schedule",level=log_level)
	INDEX(name,url)
elif mode == 15:
	xbmc.log("Stadium On Demand",level=log_level)
	ON_DEMAND(url)
elif mode == 16:
	xbmc.log("Stadium Get Videos",level=log_level)
	GET_VIDEOS(name,url)
elif mode == 17:
	xbmc.log("Stadium Get Media ID",level=log_level)
	GET_MEDIA_ID(name,url)
elif mode == 20:
	xbmc.log("Stadium Get Stream",level=log_level)
	GET_PAGE(name,url)
elif mode == 99:
	xbmc.log("Play Video",level=log_level)
	PLAY(name,url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
