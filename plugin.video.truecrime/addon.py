#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2) or Later

# 2022.01.16

import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, re, sys, xbmcvfs, os
import json
import requests

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id='plugin.video.truecrime')
translation = selfAddon.getLocalizedString
usexbmc = selfAddon.getSetting('watchinxbmc')
settings = xbmcaddon.Addon(id="plugin.video.truecrime")
__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

from uas import *

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 2
else:
	log_level = 1
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)

baseurl = 'https://watch.truecrimenetworktv.com/'
#jsonurl = 'https://prod-api-cached-2.viewlift.com/content/pages?site=justicenetwork&path=%2F&includeContent=true&moduleOffset=16&moduleLimit=4'
jsonurl = 'https://prod-api-cached-2.viewlift.com/content/pages?path=%2F&site=justicenetwork&includeContent=true&moduleOffset=0'

prefix = 'https://prod-api-cached-2.viewlift.com/content/pages?path=%2Fseries%2F'
suffix = '&site=justicenetwork&includeContent=true&moduleOffset=0&moduleLimit=4&languageCode=default&countryCode=US'

defaultimage = 'special://home/addons/plugin.video.truecrime/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.truecrime/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.truecrime/resources/media/icon.png'
addon_handle = int(sys.argv[1])

headers = {'Host': 'prod-api.viewlift.com', 'User-Agent': ua, 'Referer': 'https://watch.truecrimenetworktv.com/', 'x-api-key': 'PBSooUe91s7RNRKnXTmQG7z3gwD2aDTA6TlJp6ef'}

#3
def all_shows():
	response = get_html(jsonurl)
	data = json.loads(response);i=0;m=0
	total = len(data['modules'])#[0]['contentData'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for module in range(total):
		if 'contentType' in (data['modules'][i]):
			contentType = data['modules'][i]['contentType']
			if 'Series' in contentType:
				if not ('title' in (data['modules'][i])) and not ('privacyCheck' in (data['modules'][i]['settings'])):
					xbmc.log('CONTENTTYPE: ' + str(contentType),level=log_level)
					xbmc.log('I: ' + str(i),level=log_level)
					m = i
		i = i + 1
	xbmc.log('I: ' + str(i),level=log_level)
	xbmc.log('M: ' + str(m),level=log_level)
	shows = len(data['modules'][m]['contentData']);titles=[];x=0;i=0
	for show in range(shows):
		title = (data['modules'][m]['contentData'][x]['gist']['title'])
		if not title in titles:
			titles.append(title);x=x+1
	xbmc.log('TITLES: ' + str(titles),level=log_level)
	if 'DRAGNET' in titles:
		shows = shows - 1
	for show in range(shows):
		title = (data['modules'][m]['contentData'][i]['gist']['title'])
		if title == 'DRAGNET':
			i = i + 1
		title = (data['modules'][m]['contentData'][i]['gist']['title'])#.title()
		title = " ".join(word.capitalize() for word in title.split())
		image = data['modules'][m]['contentData'][i]['gist']['videoImageUrl']
		fanart = data['modules'][m]['contentData'][i]['gist']['posterImageUrl']
		permalink = 'https://watch.truecrimenetworktv.com' + data['modules'][m]['contentData'][i]['gist']['permalink']
		something = permalink.split('series/')[-1]
		url = prefix + something + suffix
		description = data['modules'][m]['contentData'][i]['gist']['description']
		addDir(title, url, 6, fanart, image, description);i=i+1
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#6
def get_seasons(url):
	response = get_html(url)
	data = json.loads(response);i=0;s=0
	total = (data['moduleCount']) -1
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for module in range(total):
		if data['modules'][i]['moduleType'] == "ShowDetailModule":
			x = i
			xbmc.log('FOUND: ' + str(x),level=log_level)
			sdata = data['modules'][i]
			total = len(data['modules'][x]['contentData'][0]['seasons'])
			xbmc.log('TOTAL: ' + str(total),level=log_level)
			if total == 1:
				single(data)
				break
		else:
			i = i + 1
			seasons=[]
	for season in range(total):
		title = sdata['contentData'][0]['seasons'][s]['title']
		seasons.append(title)
		xbmc.log('TITLE: ' + str(title),level=log_level)
		xbmc.log('TITLE ID: ' + str(s),level=log_level)
		plot = str(sdata['contentData'][0]['seasons'][s]['episodes'])
		#xbmc.log('URL: ' + str(url),level=log_level)
		thumbnail = sdata['contentData'][0]['images']['_3x4Image']['secureUrl']
		fanart = sdata['contentData'][0]['images']['_16x9Image']['secureUrl']
		url = url + '-' + str(s)
		#xbmc.log('IMAGE: ' + str(thumbnail),level=log_level)
		addDir(title, url, 9, thumbnail, fanart, plot);s=s+1
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#7
def single(data):
	xbmc.log('SINGLE',level=log_level);i=0;e=0
	xbmc.log('DATA: ' + str(len(data)),level=log_level)
	total = len(data['modules'][1]['contentData'][0]['seasons'][0]['episodes'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for episode in range(total):
		title = data['modules'][1]['contentData'][0]['seasons'][0]['episodes'][e]['title']
		title = " ".join(word.capitalize() for word in title.split())
		xbmc.log('TITLE: ' + str(title),level=log_level)
		plot = data['modules'][1]['contentData'][0]['seasons'][0]['episodes'][e]['gist']['description']
		video_id = data['modules'][1]['contentData'][0]['seasons'][0]['episodes'][e]['id']
		url = 'https://prod-api.viewlift.com/entitlement/video/status?id=' + video_id + '&deviceType=web_browser&contentConsumption=web'
		thumbnail = data['modules'][1]['contentData'][0]['seasons'][0]['episodes'][e]['gist']['imageGist']['_16x9']
		key = thumbnail.rpartition('/')[-1].split('.')[0]
		m3u8 = 'https://cdn-ue1-prod.tsv2.amagi.tv/avod/viewlift-tegna-justice/' + key + '/' + key + '.m3u8'
		url = 'plugin://plugin.video.truecrime?mode=20&url=' + urllib.parse.quote_plus(str(url))
		#url = 'plugin://plugin.video.truecrime?mode=99&url=' + urllib.parse.quote_plus(str(m3u8))
		#addDir(title, url, 20, thumbnail, defaultfanart, plot);e=e+1
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"genre":"TV","plot":plot})
		li.setArt({'thumb':thumbnail,'fanart':thumbnail})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False);e=e+1
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#9
def get_episodes(name, url):
	response = get_html(url)
	data = json.loads(response);i=0;e=0
	xbmc.log('DATA: ' + str(len(data)),level=log_level)
	module = int(url.split('-')[-1])#int(name.split(' ')[-1]) - 1
	xbmc.log('MODULE: ' + str(module),level=log_level)
	total = len(data['modules'][1]['contentData'][0]['seasons'][module]['episodes'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for episode in range(total):
		title = data['modules'][1]['contentData'][0]['seasons'][module]['episodes'][e]['title']
		title = " ".join(word.capitalize() for word in title.split())
		xbmc.log('TITLE: ' + str(title),level=log_level)
		plot = data['modules'][1]['contentData'][0]['seasons'][module]['episodes'][e]['gist']['description']
		video_id = data['modules'][1]['contentData'][0]['seasons'][module]['episodes'][e]['id']
		url = 'https://prod-api.viewlift.com/entitlement/video/status?id=' + video_id + '&deviceType=web_browser&contentConsumption=web'
		thumbnail = data['modules'][1]['contentData'][0]['seasons'][module]['episodes'][e]['gist']['imageGist']['_16x9']
		key = thumbnail.rpartition('/')[-1].split('.')[0]
		m3u8 = 'https://cdn-ue1-prod.tsv2.amagi.tv/avod/viewlift-tegna-justice/' + key + '/' + key + '.m3u8'
		url = 'plugin://plugin.video.truecrime?mode=20&url=' + urllib.parse.quote_plus(str(url))
		#addDir(title, url, 20, thumbnail, defaultfanart, plot);e=e+1
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"genre":"TV","plot":plot})
		li.setArt({'thumb':thumbnail,'fanart':thumbnail})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False);e=e+1
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#20
def get_stream(name,url):
	r = requests.get('https://prod-api.viewlift.com/identity/anonymous-token?site=justicenetwork',headers=headers)
	#xbmc.log('AUTHORIZATION TOKEN: ' + str(r.text),level=log_level)
	data = json.loads(str(r.text))
	auth_token = data['authorizationToken']
	xbmc.log('AUTH_TOKEN: ' + str(auth_token),level=log_level)
	headers['Authorization'] = str(auth_token)
	xbmc.log('HEADERS: ' + str(headers),level=log_level)
	r = requests.get(url, headers=headers)
	data = json.loads(str(r.text))
	url = data['video']['streamingInfo']['videoAssets']['hls']
	PLAY(name,url)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#99
def PLAY(name,url):
	addon_handle = int(sys.argv[1])
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log(('### SETRESOLVEDURL ###'),level=log_level)
	listitem.setProperty('IsPlayable', 'true')
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
	liz.setProperty('IsPlayable', 'true')
	if not fanart:
		fanart=defaultfanart
	liz.setProperty('fanart_image',fanart)
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok


def addDataDir(name, edata, mode, thumbnail, fanart, plot):
	u = sys.argv[0] + "?edata=" + urllib.parse.quote_plus(edata) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name, "plot": plot})
	liz.setArt({'thumb':thumbnail,'fanart':defaultfanart})
	#liz.setProperty('IsPlayable', 'true')
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
	xbmc.log(("Get All Shows"),level=log_level)
	all_shows()
	#xbmc.log(("Generate Main Menu"),level=log_level)
	#CATEGORIES()
elif mode == 1:
	xbmc.log(("Indexing Videos"),level=log_level)
	INDEX(url)
elif mode == 2:
	xbmc.log(("Indexing Top Shows"),level=log_level)
	top_shows(url)
elif mode == 3:
	xbmc.log(("Get All Shows"),level=log_level)
	all_shows(url)
elif mode == 4:
	xbmc.log(("Play Video"),level=log_level)
elif mode == 5:
	xbmc.log(("Get More Shows"),level=log_level)
	more_shows(url)
elif mode == 6:
	xbmc.log(("Get Seasons"),level=log_level)
	get_seasons(url)
elif mode == 9:
	xbmc.log(("Get Episodes"),level=log_level)
	get_episodes(name, url)
elif mode == 20:
	xbmc.log(("Get Stream"),level=log_level)
	get_stream(name,url)
elif mode == 99:
	xbmc.log("Play Video", level=log_level)
	PLAY(name,url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
