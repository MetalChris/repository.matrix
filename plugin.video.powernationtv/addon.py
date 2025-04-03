#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2 or Later)

#2025.04.01

import xbmcaddon, urllib.request, urllib.parse, urllib.error, xbmcgui, xbmcplugin, urllib.request, urllib.error, urllib.parse, re, sys, os, xbmcvfs
from bs4 import BeautifulSoup
import html5lib
import http.cookiejar
import ssl
import requests
import urllib3
from urllib3 import poolmanager
import inputstreamhelper

#LOGDEBUG

settings = xbmcaddon.Addon(id="plugin.video.powernationtv")
_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id='plugin.video.powernationtv')
translation = selfAddon.getLocalizedString
__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

from uas import *

CookieJar = http.cookiejar.LWPCookieJar(os.path.join(addon_path_profile, 'cookies.lwp'))


defaultimage = 'special://home/addons/plugin.video.powernationtv/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.powernationtv/resources/media/fanart.jpg'
defaultvideo = 'special://home/addons/plugin.video.powernationtv/resources/media/icon.png'
defaulticon = 'special://home/addons/plugin.video.powernationtv/resources/media/icon.png'
baseurl = 'https://www.powernationtv.com/'
login_url = 'https://www.powernationtv.com/user/login?redir=/'

addon_handle = int(sys.argv[1])
confluence_views = [500,501,503,504,515]
force_views = settings.getSetting(id="force_views")
log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 2
else:
	log_level = 1
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)
plugin = 'PowerNation TV'
xbmc.log('SSL: ' + str(ssl.OPENSSL_VERSION),level=log_level)
xbmc.log('UA: ' + str(ua),level=log_level)

headers = {'Host': 'www.powernationtv.com', 'User-Agent': ua, 'Referer': 'https://www.powernationtv.com/'
}

def CATEGORIES():
	html = get_page(baseurl)
	xbmc.log('HTML: ' + str(len(html)),level=log_level)
	soup = BeautifulSoup(html,'html5lib').find_all('div',{'class':'show_card'})
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	for show in soup:
		url = show.find('a')['href']
		if len(str(url)) < 1:
			continue
		if not 'shows' in url or 'espanol' in url:
			continue
		xbmc.log('URL:: ' + str(url),level=log_level)
		title = show.find('img')['alt'].strip()
		#image = show.find('img')['data-pagespeed-lazy-src']
		image = 'special://home/addons/plugin.video.powernationtv/resources/media/' + title + '.jpg'
		if ('Shorts' in title) or ('Daily' in title):
			continue
		surl = 'plugin://plugin.video.powernationtv?mode=10&url=' + urllib.parse.quote_plus(url)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})#,"genre":"Sports",'plot': plot, 'season': season, 'episode':episode})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=surl, listitem=li, isFolder=True)
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode(500)")
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


#10
def INDEX(url):
	xbmc.log('GET SHOWS',level=log_level); murl = url
	html = get_page(baseurl)
	xbmc.log('MURL: ' + str(murl),level=log_level)
	if 'powernation-' in murl:
		xbmc.log('POWERNATION SHOW',level=log_level)
		PN_SHOW(url)
		sys.exit()
	if 'top-dead-center' in murl:
		TDC(url)
		sys.exit()
	surl = BeautifulSoup(html,'html5lib').find_all('link',{'rel':'alternate'})#[1]
	xbmc.log('SURL: ' + str(surl),level=log_level)
	#s_url = re.compile('href="(.+?)"').findall(str(surl))[0].rpartition('/')[0]
	html = get_page(url)
	ptitle = re.compile('<title>(.+?)</title>').findall(html)
	xbmc.log('PTITLE: ' + str(ptitle),level=log_level)
	seasons = BeautifulSoup(html,'html5lib').find_all('li',{'class':'sublink'})
	xbmc.log('SEASONS: ' + str(len(seasons)),level=log_level)
	#if free != 'false':
		#x = 0
	#else:
		#x = 2
	for s in reversed(seasons):#[x:]:
		season = url + s.find('a')['href']
		xbmc.log('SEASON: ' + str(season),level=log_level)
		xbmc.log('SEASON: ' + str(urllib.parse.quote_plus(season)),level=log_level)
		title = s.find('a').text
		surl = 'plugin://plugin.video.powernationtv?mode=15&url=' + urllib.parse.quote_plus(season) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})#,"genre":"Sports",'plot': plot, 'season': season, 'episode':episode})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=surl, listitem=li, isFolder=True)
		xbmcplugin.setContent(addon_handle, 'episodes')#;titles=[]
	soup = BeautifulSoup(html,'html5lib').find_all('div',{'class':'episode'});titles=[]#;e=0
	for episode in soup:
		#xbmc.log('EPISODE: ' + str(episode),level=log_level)
		#If it's a "coming soon" show, skip it
		if episode.find(class_="coming_soon"):
			continue
		if episode.find(class_='pnplus-episode-logo'):
			continue
		title = episode.find('div', {'class': 'title'}).text.encode('ascii','ignore').strip()
		if title in titles:
			continue
		titles.append(title)
		url = episode.find('a')['href']
		if not 'https:' in url:
			url = 'https:' + episode.find('a')['href']
		#xbmc.log('URL: ' + str(url),level=log_level)
		image = re.compile('src="(.+?)"').findall(str(episode))[0].replace('&amp;','&')#.replace('https','http')
		if episode.find('i') and len(seasons) > 0:
			continue
		elif len(seasons) == 0:
			plot = episode.find('div', {'class':'description'}).text.encode('ascii','ignore').strip()
			season_info = episode.text.strip().splitlines()[-1:]
			season = season_info[0].split(',')[0]
			season = re.sub("\D", "", season)
			episode = season_info[0].split(',')[1]
			episode = re.sub("\D", "", episode)
			xbmc.log('EPISODE: ' + str(season) + 'x' + str(episode),level=log_level)
			surl = 'plugin://plugin.video.powernationtv?mode=20&url=' + urllib.parse.quote_plus(url)
			li = xbmcgui.ListItem(title)
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot': plot, "genre":"Sports", 'season': season, 'episode':episode})
			li.setArt({'thumb':image,'fanart':defaultfanart})
			li.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=surl, listitem=li, isFolder=False)
			xbmcplugin.setContent(addon_handle, 'episodes')
			xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_EPISODE)
		#else:
			#season_info = episode.find('div', {'class':'season'}).text.encode('ascii','ignore').strip()
			#title = title + b' - ' + season_info
			#plot = episode.find('div',{'class':'description'}).text
			#surl = 'plugin://plugin.video.powernationtv?mode=30&url=' + urllib.parse.quote_plus(url)
			#li = xbmcgui.ListItem(title)
			#li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot': plot})#,"genre":"Sports",'plot': plot, 'season': season, 'episode':episode})
			#li.setArt({'thumb':image,'fanart':defaultfanart})
			#xbmcplugin.addDirectoryItem(handle=addon_handle, url=surl, listitem=li, isFolder=True)
			#xbmcplugin.setContent(addon_handle, 'episodes')
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.endOfDirectory(addon_handle)


def TDC(url):
	xbmc.log('TDC',level=log_level)
	html = get_page(url); murl = url
	xbmc.log('MURL: ' + str(murl),level=log_level)
	soup = BeautifulSoup(html,'html5lib').find_all('div',{'class':'episode'})#[1]
	for episode in soup:
		title = episode.find('div', {'class': 'title'}).text.encode('ascii','ignore').strip()
		url = episode.find('a')['href']
		image = re.compile('src="(.+?)"').findall(str(episode))[0].replace('&amp;','&')
		if not episode.find('div', {'class':'season'}):
			continue
		if episode.find('i'):
			#If it has metadata, add it to the episode info
			plot = episode.find('div', {'class':'description'}).text.encode('ascii','ignore').strip()
			season_info = episode.text.strip().splitlines()[-1:]
			#xbmc.log('SEASON INFO: ' + str(season_info),level=log_level)#.strip().split(',')
			#season = season_info[0].split(',')[0]
			season = episode.find('span',{'class':'season-text'}).text.split(' ')[1]
			#season = re.sub("\D", "", season)
			xbmc.log('SEASON: ' + str(season),level=log_level)
			episode = episode.find('span',{'class':'episode-text'}).text.split(' ')[1]
			#episode = season_info[0].split(' ')[1]
			#episode = re.sub("\D", "", episode)
			xbmc.log('EPISODE: ' + str(episode),level=log_level)
			infolabels = {'plot': plot, 'season': season, 'episode':episode}
			surl = 'plugin://plugin.video.powernationtv?mode=20&url=' + urllib.parse.quote_plus(url)
			li = xbmcgui.ListItem(title)
			li.setProperty('IsPlayable', 'true')
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"genre":"Sports",'plot': plot, 'season': season, 'episode':episode})
			li.setArt({'thumb':image,'fanart':defaultfanart})
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=surl, listitem=li, isFolder=False)
		xbmcplugin.setContent(addon_handle, 'episodes')
	#Fix the sort to be proper episode number order
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_EPISODE)
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.endOfDirectory(addon_handle)


def PN_SHOW(url):
	xbmc.log('PN_SHOW',level=log_level)
	html = get_page(url); murl = url
	xbmc.log('MURL: ' + str(murl),level=log_level)
	soup = BeautifulSoup(html,'html5lib').find_all('li',{'class':'sublink'})#[1]
	for sublink in soup:
		url = murl + sublink.find('a')['href']
		if not '-garage' in murl:
			link = PN_LINK(url)
			mode = 20
		else:
			link = url
			mode = 25 #something else
		image = defaultimage
		year = sublink.find('a')['data-year']
		title = sublink.find('a').text + ' ' + year
		if mode == 20:
			xbmc.log('PN_SHOW MODE 20',level=log_level)
			surl = 'plugin://plugin.video.powernationtv?mode=20&url=' + urllib.parse.quote_plus(link)
			li = xbmcgui.ListItem(title)
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot': title, "genre":"Sports", 'season': year, 'episode':1})
			li.setArt({'thumb':image,'fanart':defaultfanart})
			li.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=surl, listitem=li, isFolder=False)
			xbmcplugin.setContent(addon_handle, 'episodes')
		else:
			xbmc.log('PN_SHOW MODE 25',level=log_level)
			surl = 'plugin://plugin.video.powernationtv?mode=25&url=' + urllib.parse.quote_plus(link)
			li = xbmcgui.ListItem(title)
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,'plot': title, "genre":"Sports", 'season': year, 'episode':1})
			li.setArt({'thumb':image,'fanart':defaultfanart})
			#li.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=surl, listitem=li, isFolder=True)
		xbmcplugin.setContent(addon_handle, 'episodes')
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.endOfDirectory(addon_handle)


def PN_LINK(url):
	xbmc.log('PN_LINK',level=log_level)
	html = get_page(url); murl = url
	#xbmc.log('MURL: ' + str(murl),level=log_level)
	soup = BeautifulSoup(html,'html5lib').find_all('div',{'id':'episodes'})
	for video in soup:
		link = video.find('a')['href']
		return link


#15
def BUILD(name, url):
	xbmc.log('BUILD ' ,level=log_level)
	s_num = name.split(' ')[-1]
	xbmc.log('S_NUM: ' + str(s_num),level=log_level)
	if s_num.isnumeric() == False:
		builds(url,s_num)
		sys.exit()
	html = get_page(url)
	soup = BeautifulSoup(html,'html5lib')
	divTag = soup.find_all("div", {"id": "episodes"})
	for tag in divTag:
		tdTags = tag.find_all("div", {"class": "episode"})
	xbmc.log('divTag: ' + str(len(divTag)),level=log_level)
	xbmc.log('tdTags: ' + str(len(tdTags)),level=log_level)
	episodes = tdTags
	EPISODES(episodes,s_num)


#20
def IFRAME(name,url):
	xbmc.log('URL: ' + str(url),level=log_level)
	urls = url.split('/')
	key = urls[4]
	params = {'id': str(key)}
	#params = {'id': 'PNG-0072'}
	params = urllib.parse.urlencode(params)
	xbmc.log('PARAMS: ' + str(params),level=log_level)
	paramsurl = 'https://www.powernationtv.com/episode/meta?' + str(params)
	xbmc.log('PARAMSURL: ' + str(paramsurl),level=log_level)
	session = requests.session()
	session.mount('https://', TLSAdapter())
	ss = session.get(url)
	xbmc.log('SS: ' + str(ss),level=log_level)
	X_CSRF_TOKEN = re.compile('name="csrf-token" content="(.+?)"').findall(ss.text)
	xbmc.log('X_CSRF_TOKEN: ' + str(X_CSRF_TOKEN),level=log_level)
	soup = BeautifulSoup(ss.text,'html5lib').find_all('div',{'class':'embargo'})
	if len(soup) > 0:
		embargo = striphtml(str(soup[0])).replace('\n',' ').strip()
		xbmcgui.Dialog().notification(plugin, embargo, defaultimage, 7500, False)
		sys.exit()
		#pass
	hdrs = {'User-Agent': ua,
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'X-Requested-With': 'XMLHttpRequest',
		'X-CSRF-TOKEN': X_CSRF_TOKEN[0],
		'Host': 'www.powernationtv.com',
		'Referer': url}
	page = session.post(paramsurl, headers=hdrs)#.read()
	xbmc.log('URL:' + str(page.url),level=log_level)
	xbmc.log('HEADERS:' + str(page.headers),level=log_level)
	xbmc.log('PAGE:' + str(page),level=log_level)
	canview = re.compile('canView":(.+?),').findall(str(page.text))[0]
	if canview == 'false':
		xbmc.log('NOT FREE',level=log_level)
		xbmcgui.Dialog().notification(plugin, 'Subsription Required for This Episode', defaultimage, 2500, False)
		sys.exit()
		pass
	stream = re.compile('hls_url":"(.+?)"').findall(page.text)[0].replace('\\','').replace('https','http')
	listitem = xbmcgui.ListItem(name)
	xbmc.log('STREAM: ' + str(stream),level=log_level)
	PLAY(name,stream)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


#25
def PNG(name,url):
	xbmc.log('PNG',level=log_level)
	html = get_page(url)
	code = url.split('?')[-1]
	year = re.compile('year=(.+?)&').findall(code)[0]
	month = re.compile('month=(.+?)#').findall(code)[0]
	soup = BeautifulSoup(html,'html5lib')
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	divTag = soup.find_all('div',{'id':'episodes' +year + month})
	for tag in divTag:
		tdTags = tag.find_all("div", {"class": "episode"})
	xbmc.log('divTag: ' + str(len(divTag)),level=log_level)
	xbmc.log('tdTags: ' + str(len(tdTags)),level=log_level)
	for episode in tdTags:
		title = episode.find('div',{'class':'title'}).text.encode('ascii','ignore').strip()
		image = episode.find('img')['src']
		url = episode.find('a')['href']
		surl = 'plugin://plugin.video.powernationtv?mode=20&url=' + urllib.parse.quote_plus(url)
		plot = episode.find('div',{'class':'description'}).text.encode('ascii','ignore').strip()
		season_info = episode.text.strip().splitlines()[-1:]
		episode = season_info[0].rpartition(' ')[-1]
		xbmc.log('EPISODE: ' + str(episode),level=log_level)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"genre":"Sports",'plot': plot, 'episode':episode, 'season': 0})
		li.setProperty('IsPlayable', 'True')
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=surl, listitem=li, isFolder=False)
		xbmcplugin.setContent(addon_handle, 'episodes')
		xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_EPISODE)
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.endOfDirectory(addon_handle)


#30
def PROJECT(url):
	xbmc.log('PROJECT',level=log_level)
	html = get_page(url); murl = url
	soup = BeautifulSoup(html,'html5lib').find_all('div',{'class':'episode'})
	for episodes in soup:
		if episodes.find('div',{'class':'show'}):
			continue
		title = episodes.find('div',{'class':'title'}).text.encode('ascii','ignore').strip()
		image = episodes.find('img')['src']
		url = episodes.find('a')['href']
		plot = episodes.find('div', {'class':'description'}).text.encode('ascii','ignore').strip()
		season_info = episodes.text.strip().splitlines()[-1:]
		season = season_info[0].split(',')[0]
		season = re.sub("\D", "", season)
		episode = season_info[0].split(',')[1]
		episode = re.sub("\D", "", episode)
		if episodes.find('div',{'class':'show'}):
			continue
		surl = 'plugin://plugin.video.powernationtv?mode=20&url=' + urllib.parse.quote_plus(url)
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"genre":"Sports",'plot': plot, 'season': season, 'episode':episode})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=surl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_EPISODE)
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.endOfDirectory(addon_handle)


def builds(url,s_num):
	xbmc.log('BUILDS ' ,level=log_level)
	html = get_page(url)
	soup = BeautifulSoup(html,'html5lib').find_all('div',{'class':'episodes'})#;e=0#;titles = []
	episodes = soup
	EPISODES(episodes,s_num)


def EPISODES(episodes,s_num):
	xbmc.log('EPISODES ' ,level=log_level)
	for episode in episodes:
		#If it's a "coming soon" show, skip it
		if episode.find(class_="coming_soon"):
			continue
		#If it's a "subscription" show, skip it
		#if free == 'false':
		if episode.find(class_="pnplus-episode-logo"):
			continue
		title = episode.find('div', {'class': 'title'}).text.encode('ascii','ignore').strip()
		url = episode.find('a')['href']
		if not 'https:' in url:
			url = 'https:' + episode.find('a')['href']
		image = re.compile('src="(.+?)"').findall(str(episode))[0].replace('&amp;','&')
		if not episode.find('div', {'class':'season'}):
			continue
		if episode.find('i'):
			#If it has metadata, add it to the episode info
			plot = episode.find('div', {'class':'description'}).text.encode('ascii','ignore').strip()
			if episode.find('div',{'class':'season'}):
				season_info = episode.text.strip().splitlines()[-1:]
				#xbmc.log('SEASON INFO: ' + str(season_info),level=log_level)#.strip().split(',')
				#season = season_info[0].split(',')[0]
				season = episode.find('span',{'class':'season-text'}).text.split(' ')[1]
				#season = re.sub("\D", "", season)
				xbmc.log('SEASON: ' + str(season),level=log_level)
				episode = episode.find('span',{'class':'episode-text'}).text.split(' ')[1]
				#episode = season_info[0].split(' ')[1]
				#episode = re.sub("\D", "", episode)
				xbmc.log('EPISODE: ' + str(episode),level=log_level)
			else:
				season = 'N/A'
				episode = 'N/A'
			#if (s_num == 'Episodes'):
				#pass
			#elif (season != s_num):
				#continue
			infolabels = {'plot': plot, 'season': season, 'episode':episode}
			surl = 'plugin://plugin.video.powernationtv?mode=20&url=' + urllib.parse.quote_plus(url)
			li = xbmcgui.ListItem(title)
			li.setProperty('IsPlayable', 'true')
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"genre":"Sports",'plot': plot, 'season': season, 'episode':episode})
			li.setArt({'thumb':image,'fanart':defaultfanart})
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=surl, listitem=li, isFolder=False)
		xbmcplugin.setContent(addon_handle, 'episodes')
	#Fix the sort to be proper episode number order
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_EPISODE)
	if force_views != 'false':
		xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[int(settings.getSetting(id="views"))])+")")
	xbmcplugin.endOfDirectory(addon_handle)


#99
def PLAY(name,url):
	addon_handle = int(sys.argv[1])
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log(('### SETRESOLVEDURL ###'),level=log_level)
	listitem.setProperty('IsPlayable', 'true')
	listitem.setProperty('inputstream', 'inputstream.adaptive')
	listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
	listitem.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={ua}")
	#listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
	listitem.setContentLookup(False)
	listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
	xbmc.log('URL: ' + str(url), level=log_level)
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


def get_page(url):
	xbmc.log('URL: ' + str(url),level=log_level)
	s = requests.Session()
	s.mount(url, SslOldHttpAdapter())
	html = s.get(url, headers=headers)
	return(html.text)


class SslOldHttpAdapter(requests.adapters.HTTPAdapter):
	def init_poolmanager(self, connections, maxsize, block=False):
		ctx = ssl.create_default_context()
		ctx.set_ciphers('DEFAULT@SECLEVEL=1')

		self.poolmanager = urllib3.poolmanager.PoolManager(
			ssl_version=ssl.PROTOCOL_TLS,
			ssl_context=ctx)


class TLSAdapter(requests.adapters.HTTPAdapter):

	def init_poolmanager(self, connections, maxsize, block=False):
		"""Create and initialize the urllib3 PoolManager."""
		ctx = ssl.create_default_context()
		ctx.set_ciphers('DEFAULT@SECLEVEL=1')
		self.poolmanager = poolmanager.PoolManager(
				num_pools=connections,
				maxsize=maxsize,
				block=block,
				ssl_version=ssl.PROTOCOL_TLS,
				ssl_context=ctx)


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
	xbmc.log("PowerNation TV Menu",level=log_level)
	CATEGORIES()
elif mode == 10:
	xbmc.log("PowerNation TV Videos",level=log_level)
	INDEX(url)
elif mode == 15:
	xbmc.log("PowerNation TV Build Videos",level=log_level)
	BUILD(name,url)
elif mode == 20:
	xbmc.log("PowerNation TV Play Video",level=log_level)
	IFRAME(name,url)
elif mode == 25:
	xbmc.log("PowerNation Garage",level=log_level)
	PNG(name,url)
elif mode == 30:
	xbmc.log("PowerNation Project",level=log_level)
	PROJECT(url)
elif mode == 99:
	xbmc.log("Play PowerNation Stream",level=log_level)
	PLAY(name,url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
