#!/usr/bin/python
#
#
# Written by MetalChris 07.09.2023
# Released under GPL(v2 or later)

from six.moves import urllib_parse
from kodi_six import xbmc, xbmcplugin, xbmcaddon, xbmcgui, xbmcvfs
import urllib, re, sys, os
from bs4 import BeautifulSoup
import mechanize
import requests

if sys.version_info >= (3, 4, 0):
	import html
	_html_parser = html
	PY2 = False
	translatePath = xbmcvfs.translatePath
else:
	from six.moves import html_parser
	_html_parser = html_parser.HTMLParser()
	PY2 = True
	translatePath = xbmc.translatePath

artbase = 'special://home/addons/plugin.video.cflplus/resources/media/'
_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='plugin.video.cflplus')
translation = selfAddon.getLocalizedString
usexbmc = selfAddon.getSetting('watchinxbmc')
settings = xbmcaddon.Addon(id="plugin.video.cflplus")
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib'))

sys.path.append(__resource__)

from uas import *

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = xbmc.LOGNOTICE if PY2 else xbmc.LOGINFO
else:
	log_level = xbmc.LOGDEBUG
xbmc.log('LOG_NOTICE: ' + str(log_notice), level=log_level)

quality = settings.getSetting(id="quality")
xbmc.log('QUALITY: ' + str(quality), level=log_level)


plugin = "CFL Video"

defaultimage = 'special://home/addons/plugin.video.cflplus/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.cflplus/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.cflplus/resources/media/icon.png'
pubId = '4401740954001'

local_string = xbmcaddon.Addon(id='plugin.video.cflplus').getLocalizedString
pluginhandle = int(sys.argv[1])
confluence_views = [500,501,502,503,504,508,515]
baseurl = 'https://www.cfl.ca/plus/'

br = mechanize.Browser()
br.addheaders = [('Host', 'www.cfl.ca')]
br.addheaders = [('User-agent', ua)]
br.addheaders = [('Accept', 'application/json;pk=BCpkADawqM0dhxjC63Ux5MXyiMyIYB1S1bvk0iorISSaD1jFgWDyiv-JAcvE6XduNdDYxMdk_NTQWn91IQI9NLPkXd5UIw3cv49pcyJ5eW9QT0CWTrclSFHBHqSSyJ_9Ysgzc2v-Mw0wxNmZ')]
xbmc.log('UA: ' + str(ua))


def cfl(baseurl):
	br.set_handle_robots( False )
	response = br.open('https://www.cfl.ca/plus/')
	xbmc.log(str(response.code), level=log_level)
	html = response.get_data()
	soup = BeautifulSoup(html, 'html.parser')
	for anchor in soup.find_all("a"):
		if not anchor.find('div', {'class':'item-title'}):
			continue
		title = anchor.find("div",{"class":"item-title"}).text.strip()
		xbmc.log('TITLE: ' + str(title), level=log_level)
		plot = anchor.find("div",{"class":"item-description"}).text.strip()
		xbmc.log('PLOT: ' + str(plot), level=log_level)
		img = anchor.find("div",{"class":"item-image"})#.text.strip()
		xbmc.log('IMAGE: ' + str(img), level=log_level)
		if img is None:
			image = defaulticon
			xbmc.log('IMAGE: ' + str(image), level=log_level)
		else:
			image = (re.compile("\'(.+?)\'").findall(str(img))[0])
			xbmc.log('IMAGE: ' + str(image), level=log_level)
		xbmc.log('ANCHOR: ' + str(anchor)[:100], level=log_level)
		game_url = re.compile('href="(.+?)"').findall(str(anchor))[0]
		xbmc.log('URL: ' + str(game_url), level=log_level)
		url = 'plugin://plugin.video.cflplus?mode=53&url=' + urllib_parse.quote_plus(game_url)
		xbmc.log('URL: ' + str(url), level=log_level)
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		xbmcplugin.setContent(pluginhandle, 'episodes')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"genre":"Sports","plot":plot})
		li.setArt({'thumb':image,'fanart':artbase + 'fanart.jpg'})
		xbmcplugin.addDirectoryItem(handle=pluginhandle, url=url, listitem=li, isFolder=False)
	xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)


#53
def get_stream(url):
	br.set_handle_robots( False )
	response = br.open(url)
	xbmc.log('RESPONSE: ' + str(response.code), level=log_level)
	html = response.get_data()
	videoId = (re.compile('videoId=(.+?)&amp').findall(str(html))[0])
	xbmc.log('videoId: ' + str(videoId), level=log_level)
	url = 'https://edge.api.brightcove.com/playback/v1/accounts/4401740954001/videos/' + str(videoId)
	xbmc.log('URL: ' + str(url), level=log_level)
	br.set_handle_robots( False )
	res = requests.get(url, headers={'Accept':'application/json;pk=BCpkADawqM0dhxjC63Ux5MXyiMyIYB1S1bvk0iorISSaD1jFgWDyiv-JAcvE6XduNdDYxMdk_NTQWn91IQI9NLPkXd5UIw3cv49pcyJ5eW9QT0CWTrclSFHBHqSSyJ_9Ysgzc2v-Mw0wxNmZ'})
	xbmc.log('RESPONSE: ' + str(res.text), level=log_level)
	data = res.json()
	xbmc.log('JSON: ' + str(len(data)), level=log_level)
	xbmc.log('JSON: ' + str(data), level=log_level)
	if 'sources' in str(res.text):
		m3u8 = (data['sources'][0]['src'])
		if quality != '4':
			m3u8 = (data['sources'][0]['src']).replace('playlist.m3u8', 'profile_' + str(quality) + '/chunklist.m3u8')
		xbmc.log('M3U8: ' + str(m3u8), level=log_level)
		PLAY(m3u8)
		xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)
	else:
		xbmc.log(('ACCESS_DENIED'), level=log_level)
		xbmcgui.Dialog().ok(addonname, 'This game is not available in your area.')
		xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

#99
def PLAY(url):
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log('### SETRESOLVEDURL ###', level=log_level)
	listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
	xbmc.log('URL: ' + str(url), level=log_level)
	xbmcplugin.endOfDirectory(pluginhandle)


def striphtml(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)


def get_html(url):
	req = urllib.request.Request(url)
	req.add_header('Host','www.cfl.ca')
	req.add_header('User-Agent','Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0')
	req.add_header('Accept', 'application/json;pk=BCpkADawqM0dhxjC63Ux5MXyiMyIYB1S1bvk0iorISSaD1jFgWDyiv-JAcvE6XduNdDYxMdk_NTQWn91IQI9NLPkXd5UIw3cv49pcyJ5eW9QT0CWTrclSFHBHqSSyJ_9Ysgzc2v-Mw0wxNmZ')

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
	edata = urllib.parse.unquote_plus(params["edata"])
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
	xbmc.log("Generate Main Menu", level=log_level)
	cfl(baseurl)
elif mode == 99:
	play(name,url)
	xbmc.log("Play Video", level=log_level)
elif mode == 53:
	xbmc.log("CFL Get Stream", level=log_level)
	get_stream(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
