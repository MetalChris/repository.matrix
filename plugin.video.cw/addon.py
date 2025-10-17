#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2 or later)

#2024.09.11

import urllib.request, urllib.parse, urllib.error, xbmcplugin, xbmcaddon, xbmcgui, re, sys, os
import xbmcvfs
import json
import requests
from bs4 import BeautifulSoup
import inputstreamhelper

ADDON = xbmcaddon.Addon()
ADDON_ID = "metalchris.cwlive.epg"
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
artbase = 'special://home/addons/plugin.video.cw/resources/media/'
_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id='plugin.video.cw')
self = xbmcaddon.Addon(id='plugin.video.cw')
translation = selfAddon.getLocalizedString
usexbmc = selfAddon.getSetting('watchinxbmc')
settings = xbmcaddon.Addon(id="plugin.video.cw")
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
confluence_views = [500,501,502,503,504,508]
__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ).encode("utf-8") )

sys.path.append(__resource__)

from uas import *

xbmc.log(f"Loaded ADDON_ID = {ADDON_ID}, VERSION = {ADDON_VERSION}", xbmc.LOGINFO)

headers = {
"User-Agent": ua,
"Accept": "application/json;pk=BCpkADawqM0t2qFXB_K2XdHv2JmeRgQjpP6De9_Fl7d4akhL5aeqYwErorzsAxa7dyOF2FdxuG5wWVOREHEwb0DI-M8CGBBDpqwvDBEPfDKQg7kYGnccdNDErkvEh2O28CrGR3sEG6MZBlZ03I0xH7EflYKooIhfwvNWWw",
"Referer": "https://www.cwtv.com/",

}

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 1
else:
	log_level = 0
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)

plugin = "CW TV Network"

defaultimage = 'special://home/addons/plugin.video.cw/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.cw/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.cw/resources/media/icon.png'


local_string = xbmcaddon.Addon(id='plugin.video.cw').getLocalizedString
addon_handle = int(sys.argv[1])

apiUrl = 'https://cwtv-prod-elb.digitalsmiths.net/sd/cwtv/screens/series?userId=-2415179020856985572&deviceType=html5&offset=0&limit=20'
showsUrl = 'https://cwtv-prod-elb.digitalsmiths.net/sd/cwtv/screens/series?userId=-2415179020856985572&deviceType=html5&offset=0&limit=25'
moviesUrl = 'https://cwtv-prod-elb.digitalsmiths.net/sd/cwtv/screens/movies?userId=-2415179020856985572&deviceType=html5&offset=0&limit=20'

s = requests.Session()

#533
def sites():
	addDir('CW TV VOD', showsUrl, 633, defaultimage)
	addDir('CW Movies', moviesUrl, 633, defaultimage)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


#633
def get_cats(url):
	response = s.get(url)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGINFO)
	xbmc.log('RESPONSE: ' + str(response.text[:200]),xbmc.LOGINFO)
	data = json.loads(response.content)
	top_name = data.get("name")
	# Extract "name" and "path" from each element in "rows"
	for row in data.get("rows", []):
		title = row.get("name")
		#url = 'https://www.cwtv.com/series' + row.get("path")# + '/?viewContext=Series+Swimlane'
		stuff = row.get("items", [])
		plot = row.get("description")
		image = defaultimage
		add_directory2(title,url,30,defaultfanart,image,plot)
		xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle)

#https://www.cwtv.com/series/penn-teller-fool-us/?viewContext=Series+Swimlane
#30
def get_shows(name,url,iconimage):
	response = s.get(url)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGINFO)
	xbmc.log('RESPONSE: ' + str(response.text[:200]),xbmc.LOGINFO)
	data = json.loads(response.content)
	for row in data.get("rows", []):
		row_name = row.get("name")
		if name == row_name:
			xbmc.log(f"MATCH: {row_name}", xbmc.LOGDEBUG)

			items = row.get("items", [])
			xbmc.log(f"SHOWS: {len(items)}", xbmc.LOGDEBUG)

			for show in items:
				title_dict = show.get("title", {})
				title_en = title_dict.get("en")
				xbmc.log(f"SHOW: {title_en}", xbmc.LOGDEBUG)
				#xbmc.log('TITLE: ' + str(title),level=log_level)
				try:
					artwork = show["images"][-1]["url"]
				except (IndexError, KeyError, TypeError):
					artwork = defaultfanart
				desc = show.get("description")
				plot = desc["en"]
				meta = show.get("metadata")
				slug = meta["slug"]
				if "movies" in url:
					mode = 45
					url = 'https://www.cwtv.com/movies/' + slug
					add_directory2(title_en,url,mode,artwork,artwork,plot)
				else:
					mode = 40
					url = 'https://www.cwtv.com/series/' + slug
					add_directory2(title_en,url,mode,artwork,artwork,plot)
			xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle)



#40
def get_eps(name,url,iconimage):
	xbmc.log('[GET EPS] NAME: ' + str(name),xbmc.LOGINFO)
	response = s.get(url)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGINFO)
	xbmc.log('RESPONSE: ' + str(response.text[:200]),xbmc.LOGINFO)
	html = response.content
	soup = BeautifulSoup(html, "html.parser")
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	divs = soup.find_all("div", {'class':'videowrapped thumbgrow slide'})
	xbmc.log('DIVS: ' + str(len(divs)),level=log_level)
	for div in divs:
		url = str('https://www.cwtv.com' + div.find('a')['href'])
		#xbmc.log('URL: ' + str(url),level=log_level)
		a_tag = div.find('a')
		if not (a_tag and a_tag.has_attr('data-eptitle')):
			continue
		title = (div.find('a')['data-eptitle'])
		#xbmc.log('TITLE: ' + str(title),level=log_level)
		artwork = div.find('img')['data-src']
		plot = " "
		plot = str(div.find('a').text)
		streamUrl = 'plugin://plugin.video.cw?mode=45&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title) + '&iconimage=' + urllib.parse.quote_plus(artwork)

		li = xbmcgui.ListItem(title)
		li.setArt({'icon': artwork, 'thumb': artwork})
		li.setProperty('fanart_image', artwork)
		li.setInfo(type="Video", infoLabels={"Title": title, "Plot": plot})#, "Episode": ep, "Premiered": airdate})
		#li.addStreamInfo('video', { 'duration': duration })
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li)
		xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle)


#45
def video_id(name,url,iconimage):
	xbmc.log('URL: ' + str(url),xbmc.LOGINFO)
	response = s.get(url)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGINFO)
	xbmc.log('RESPONSE: ' + str(response.text[:200]),xbmc.LOGINFO)
	html = response.content
	soup = BeautifulSoup(html, "html.parser")
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	videoId = re.search(r"curPlayingBCVideoId\s*=\s*'([^']+)'", str(soup)).group(1)
	xbmc.log('VIDEOID: ' + str(videoId),xbmc.LOGINFO)
	url = 'https://edge.api.brightcove.com/playback/v1/accounts/6415823816001/videos/' + videoId
	xbmc.log('URL: ' + str(url),xbmc.LOGINFO)
	get_stuff(name,url,iconimage)


#50
def get_stuff(name,url,iconimage):
	xbmc.log('[GET STUFF] URL: ' + str(url),xbmc.LOGINFO)
	response = s.get(url, headers=headers)
	xbmc.log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGINFO)
	xbmc.log('RESPONSE: ' + str(response.text[:200]),xbmc.LOGINFO)
	html = response.content
	data = json.loads(response.content)
	sources = data.get("sources",[])
	#for source in sources:
	source = sources[-1]
	key_systems = source.get("key_systems",{})
	license_url = key_systems['com.widevine.alpha']['license_url']
	xbmc.log('SOURCE: ' + str(license_url),level=log_level)
	url = source.get("src")
	xbmc.log('URL: ' + str(url),level=log_level)
	referer = 'https://www.cwtv.com/'

	license_key = license_url + '|User-Agent=' + ua + '&Referer=' + referer +'/&Origin=' + referer + '&Content-Type= |R{SSM}|'
	xbmc.log('LICENSE KEY: ' + str(license_key),level=log_level)
	is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
	if not is_helper.check_inputstream():
		sys.exit()
	listitem = xbmcgui.ListItem(path=url, label=name)
	listitem.setProperty('IsPlayable', 'true')
	listitem.setArt({'icon': iconimage, 'thumb': iconimage})
	#xbmc.Player().play(item=url, listitem=listitem)
	#if hls != 'false':
	#if captions != '':
		#listitem.setSubtitles([captions])
	listitem.setProperty('inputstream', 'inputstream.adaptive')
	#listitem.setProperty('inputstream.adaptive.manifest_type', "mpd")
	listitem.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={ua}")
	listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
	listitem.setProperty('inputstream.adaptive.license_key', license_key)
	listitem.setMimeType('application/dash+xml')
	listitem.setContentLookup(False)
	xbmc.log('### SETRESOLVEDURL ###',level=log_level)
	listitem.setProperty('IsPlayable', 'true')
	#xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
	xbmc.log('URL: ' + str(url), level=log_level)
	#sys.exit()
	xbmc.Player().play(item=url, listitem=listitem)
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


def striphtml(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)


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

def add_directory2(name,url,mode,fanart,thumbnail,plot,showcontext=False):
	if mode == 45:
		folder = False
	else:
		folder = True
	u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name) + "&iconimage=" + urllib.parse.quote_plus(thumbnail)
	ok=True
	liz=xbmcgui.ListItem(name)
	liz.setArt({'icon': thumbnail})
	liz.setArt({'thumb': thumbnail})
	info = liz.getVideoInfoTag()
	info.setTitle(name)
	info.setPlot(plot)
	if not fanart:
		fanart=''
	liz.setProperty('fanart_image',fanart)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder, totalItems=40)
	#xbmc.log('[ADD DIR2] MODE: ' + str(mode),xbmc.LOGDEBUG)
	#xbmc.log('[ADD DIR2] Folder: ' + str(folder),xbmc.LOGDEBUG)
	return ok


def addDir(name, url, mode, iconimage, fanart=False, infoLabels=False):
	u = sys.argv[0] + "?url=" + urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name) + "&iconimage=" + urllib.parse.quote_plus(iconimage)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setArt({'icon': iconimage})
	liz.setArt({'thumb': iconimage})
	info = liz.getVideoInfoTag()
	info.setTitle(name)
	#info.setPlot(plot)
	liz.setProperty('IsPlayable', 'true')
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
	sites()
elif mode == 4:
	xbmc.log("Play Video",level=log_level)
elif mode==533:
	xbmc.log("CW TV Network Main Menu",level=log_level)
	sites()
elif mode==633:
	xbmc.log("CW TV Network Main Menu",level=log_level)
	get_cats(url)
elif mode==30:
	xbmc.log("CW TV Shows JSON",level=log_level)
	get_shows(name,url,iconimage)
elif mode==40:
	xbmc.log("CW TV Episodes JSON",level=log_level)
	get_eps(name,url,iconimage)
elif mode==45:
	xbmc.log("CW TV Get VideoId",level=log_level)
	video_id(name,url,iconimage)
elif mode==50:
	xbmc.log("CW TV Get Stuff",level=log_level)
	get_stuff(name,url,iconimage)
elif mode==31:
	xbmc.log("CW TV Clips JSON",level=log_level)
	get_clips(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
