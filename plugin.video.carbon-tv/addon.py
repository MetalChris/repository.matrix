#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2) or Later
# 2021.11.19

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmcplugin, xbmcaddon, xbmcgui, re, sys, os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import html5lib
import http.cookiejar
import requests, pickle
import json

artbase = 'special://home/addons/plugin.video.carbon-tv/resources/media/'
_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmc.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id='plugin.video.carbon-tv')
self = xbmcaddon.Addon(id='plugin.video.carbon-tv')
translation = selfAddon.getLocalizedString
usexbmc = selfAddon.getSetting('watchinxbmc')
settings = xbmcaddon.Addon(id="plugin.video.carbon-tv")
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
xbmc_monitor = xbmc.Monitor()
__resource__   = xbmc.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)
#import uas
from uas import *

plugin = "CarbonTV"

defaultimage = 'special://home/addons/plugin.video.carbon-tv/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.carbon-tv/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.carbon-tv/resources/media/icon.png'

local_string = xbmcaddon.Addon(id='plugin.video.carbon-tv').getLocalizedString
addon_handle = int(sys.argv[1])
download = settings.getSetting(id="download")
username = settings.getSetting(id="username")
password = settings.getSetting(id="password")
log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 1
else:
	log_level = 0
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)

login_url = 'https://www.carbontv.com/users/login'
shows_url = 'https://www.carbontv.com/shows'

s = requests.Session()
headers = {'User-Agent': ua, 'origin': 'https://www.carbontv.com'
}

xbmc.log('CarbonTV Version: 2021.09.27',level=log_level)

#5
def login(shows_url):
	r = s.get('https://www.carbontv.com', headers=headers)
	xbmc.log('RESPONSE_CODE: ' + str(r.status_code),level=log_level)
	#xbmc.log(str(r.text.encode('utf-8')[:7500]),level=log_level)
	#xbmc.log('SESSION_COOKIES: ' + str((s.cookies.get_dict())),level=log_level)
	cookie_file = os.path.join(addon_path_profile, 'cookies.txt')
	with open(cookie_file, 'wb') as f:
		pickle.dump(s.cookies.get_dict(), f)
	csrfToken = re.compile("csrfToken': '(.+?)'").findall(str((s.cookies.get_dict())))[0]
	payload = {
		'_method': 'POST',
		'_csrfToken': csrfToken,
		'email' : username,
		'password' : password,
		'remember_me' : '0'
		}
	p = s.post('https://www.carbontv.com/users/login', data=payload, cookies=s.cookies.get_dict(), headers=headers)
	xbmc.log('RESPONSE_CODE: ' + str(r.status_code),level=log_level)
	r = s.get('https://www.carbontv.com', cookies=s.cookies.get_dict())
	xbmc.log('RESPONSE_CODE: ' + str(r.status_code),level=log_level)
	#xbmc.log(str(r.text.encode('utf-8')[:10000]),level=log_level)
	if 'Signup/Login' in str(r.text.encode('utf-8')):
	    xbmcgui.Dialog().notification(plugin, 'Login Failed', defaultimage, 5000, False)
	else:
		xbmcgui.Dialog().notification(plugin, 'Login Successful', defaultimage, 2500, False)
		cats(shows_url)


#10
def cats(url):
	r = s.get(shows_url, cookies=s.cookies.get_dict())
	xbmc.log('SHOWS_URL: ' + str(shows_url),level=log_level)
	html = r.text.encode('utf-8')
	soup = BeautifulSoup(html,'html5lib').find_all('div',{'id':'navbar-item-login-signup'})
	#xbmc.log('SOUP: ' + str(soup),level=log_level)
	#check = soup[0].find('span').text.strip()
	#xbmc.log('CHECK: ' + str(check),level=log_level)
	#if 'Signup/Login' in str(soup):
		#xbmc.log('STATUS: ' + 'Logged Out',level=log_level)
	soup = BeautifulSoup(html,'html5lib').find_all('div',{'class':'menu'})
	for item in soup:
		title = item.get('data-menu-name')
		if title == 'All' or title == 'Sort':
			continue
		key = item.get('data-menu-id')
		url = 'https://www.carbontv.com/shows/more?type=channel&id=' + str(key) + '&sort=asc&limit=100&offset=0'
		xbmc.log('URL: ' + str(url),level=log_level)
		if key == '9' or  key == '10':
			url = url.replace('channel','network')
		if 'cams' in url:
			continue
		add_directory2(title,url,15,defaultfanart,defaultimage,plot='')
	xbmcplugin.endOfDirectory(addon_handle)


#15
def shows(url):
	r = s.get(url, cookies=s.cookies.get_dict())
	html = r.text.encode('utf-8')
	soup = BeautifulSoup(html,'html5lib').find_all('div',{'class':'show'})
	xbmc.log('SOUP: ' + str(soup[0]),level=log_level)
	for item in soup:
		title = item.find('div',{'class':'show-name truncate'}).text.strip()#.string.encode('utf-8').strip()
		#xbmc.log('TITLE: ' + str(title),level=log_level)
		iconimage = item.find('img',{'class':'show-thumb'})['src']
		url = 'http://www.carbontv.com' + item.find('a')['href']
		add_directory2(title,url,20,defaultfanart,iconimage,plot='')
	xbmcplugin.endOfDirectory(addon_handle)


#20
def seasons(url):
	r = s.get(url, cookies=s.cookies.get_dict())
	response = r.text.encode('utf-8')
	url = url.split('?')[0]
	season_number = BeautifulSoup(response,'html5lib')
	if season_number.find('span',{'class':'season-number'}):
		xbmc.log('FOUND', level=log_level)
		soup = BeautifulSoup(response,'html5lib').find_all('div',{'tabindex':'0'})
		xbmc.log('SOUP: ' + str(soup),level=log_level)
		seasons = BeautifulSoup(str(soup),'html5lib').find_all('div',{'menu-item'})
		for season in seasons:
			season = season.text
			title = 'Season ' + season
			xbmc.log('SEASON: ' + str(season),level=log_level)
			surl = url + 'seasons/' + season + '/episodes/?limit=100&offset=0'
			xbmc.log('URL: ' + str(surl),level=log_level)
			add_directory2(title,surl,25,defaultfanart,defaultimage,plot='')
	else:
		xbmc.log('EPISODES ONLY', level=log_level)
		surl = url + 'episodes/?limit=100&offset=0'
		xbmc.log('URL: ' + str(surl),level=log_level)
		videos(surl)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#25
def videos(url):
	r = s.get(url, cookies=s.cookies.get_dict())
	response = r.text#.encode('utf-8')
	jsob = re.compile('"content">\n(.+?)</').findall(response)[0]
	data = json.loads(str(jsob))
	#xbmc.log('DATA: ' + str(data),level=log_level)
	total = (data['currentCount']) + 1; titles = []
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for i in range(total):
		try:title = (data['items'][i]['name']).encode('utf-8')
		except IndexError:
			continue
		if title in titles:
			continue
		titles.append(title)
		xbmc.log('TITLE: ' + str(title),level=log_level)
		dtitle = re.sub('[^0-9a-zA-Z]+', '_', title.decode('utf-8'))
		try:embed_code = (data['items'][i]['embed_code'])
		except KeyError:
			continue
		xbmc.log('EMBED_CODE: ' + str(embed_code),level=log_level)
		#downloadUrl = 'http://cdnapi.kaltura.com/p/1897241/sp/189724100/playManifest/entryId/' + embed_code + '/format/download/protocol/http/flavorParamIds/0'
		url = 'http://www.carbontv.com' + data['items'][i]['path']
		duration = data['items'][i]['duration']
		runtime = (duration/1000)
		thumbnail = data['items'][i]['preview_image_url']
		thumb = s.get(thumbnail).url
		xbmc.log('IMAGE: ' + str(thumb),level=log_level)
		season = data['items'][i]['season_number']
		episode = data['items'][i]['video_number']
		#key = thumbnail.split('=')[-1].split('/')[-1].split('-')[0]
		stream = 'https://cdn.jwplayer.com/manifests/' + embed_code + '.m3u8'
		xbmc.log('STREAM: ' + str(stream),level=log_level)
		#xbmc.log('KEY: ' + str(key),level=log_level)
		purl = 'plugin://plugin.video.carbon-tv?mode=30&url=' + urllib.parse.quote_plus(stream) + "&name=" + urllib.parse.quote_plus(title) + "&iconimage=" + urllib.parse.quote_plus(defaultimage)
		xbmc.log('PURL: ' + str(purl),level=log_level)
		li = xbmcgui.ListItem(title, defaultimage, defaultimage)
		li.addStreamInfo('video', { 'duration': runtime })
		li.setProperty('fanart_image', defaultfanart)
		li.setProperty('mimetype', 'video/mp4')
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="video", infoLabels={ 'Title': title, 'Plot': '', 'season': season, 'episode': episode })
		#li.addContextMenuItems([('Download File', 'RunPlugin(%s?mode=80&url=%s&name=%s)' % (sys.argv[0], downloadUrl,dtitle))])
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=purl, listitem=li, isFolder=False)
		xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_EPISODE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#30
def streams(name,url):
	r = s.get(url, cookies=s.cookies.get_dict())
	html = r.text#.encode('utf-8')
	xbmc.log('HTML: ' + str(html),level=log_level)
	soup = BeautifulSoup(html,'html5lib')
	streams = re.findall(r'https.*', soup.text, re.MULTILINE); keys=[]
	for stream in streams:
		if '.m4a' in stream:
			streams.remove(stream)
	streams.sort()
	xbmc.log('STREAMS: ' + str(streams),level=log_level)
	for stream in streams:
		key = stream.split('/')[-1].split('.mp4')[0]
		keys.append(key)
		keys.sort()
	xbmc.log('KEYS: ' + str(keys),level=log_level)
	stream = streams[-1]
	listitem = xbmcgui.ListItem(name, defaultimage, path=stream)
	listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)


#80
#def downloader(url,name):


def get_sec(time_str):
	try: h, m, s = time_str.split(':')
	except ValueError:
		m, s = time_str.split(':')
		return int(m) * 60 + int(s)
	return int(h) * 3600 + int(m) * 60 + int(s)


def striphtml(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)


def add_directory2(name, url, mode, fanart, thumbnail, plot):
    u = sys.argv[0] + "?url=" + urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setInfo(type="Video", infoLabels={"Title": name,
                                          "plot": plot})
    if not fanart:
        fanart = ''
    liz.setArt({
        'thumb': thumbnail,
        'icon': "DefaultFolder.png",
        'fanart': fanart
    })
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True, totalItems=70)
    return ok


def get_html(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent','Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:44.0) Gecko/20100101 Firefox/44.0')

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
	xbmc.log("Generate Main Menu",level=log_level)
	cats(url)
elif mode == 4:
	xbmc.log("Play Video",level=log_level)
elif mode==10:
	xbmc.log('CarbonTV Categories',level=log_level)
	cats(url)
elif mode==15:
	xbmc.log('CarbonTV Shows',level=log_level)
	shows(url)
elif mode==20:
	xbmc.log("CarbonTV Seasons",level=log_level)
	seasons(url)
elif mode==25:
	xbmc.log("CarbonTV Videos",level=log_level)
	videos(url)
elif mode==30:
	xbmc.log("CarbonTV Streams",level=log_level)
	streams(name,url)
elif mode == 80:
	xbmc.log("CarbonTV Download File",level=log_level)
	downloader(url,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
