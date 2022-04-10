#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2)

#2022.04.07

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmcplugin, xbmcaddon, xbmcgui, xbmcvfs, sys, os, re
import json
#from datetime import datetime, timedelta as td
import time
from socket import timeout
from bs4 import BeautifulSoup
from six.moves import urllib_parse, urllib_request, urllib_error, http_client
from kodi_six import xbmc
import html
import datetime

today = time.strftime("%m-%d-%Y")

addon_id = 'plugin.video.sportstv'
_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id=addon_id)
translation = selfAddon.getLocalizedString
#addon_version = selfAddon.getAddonInfo('version')
settings = xbmcaddon.Addon(id=addon_id)
__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

from uas import *
#import epg

sort = settings.getSetting(id="sort")

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 1
else:
	log_level = 0
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)
xbmc.log('SORT: ' + str(sort),level=log_level)

defaultimage = 'special://home/addons/plugin.video.sportstv/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.sportstv/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.sportstv/resources/media/icon.png'
artbase = 'special://home/addons/plugin.video.sportstv/resources/media/'
vidbase = 'https://api.myspotlight.tv/dotplayer/video/5ef4a47fc27512184b7d2b62/'
vodbase = 'https://www.sports.tv/_next/data/K-gZ8WhW-DlfrUUAOez8r/on-demand.json'

addon = 'Sports.TV'

addon_handle = int(sys.argv[1])
false_epoch = 10
pattern= r"\D(\d{%d})\D" % false_epoch

#global mini_epg# = []


def CATEGORIES():
	addDir('Sports.TV Live', 'https://www.sports.tv/', 5, defaultimage, defaultfanart)
	addDir('Sports.TV On Demand', 'https://www.sports.tv/on-demand', 15, defaultimage, defaultfanart)
	xbmcplugin.endOfDirectory(addon_handle)


#5
def LIVE(name,url):
	epoch_now = int(time.time())
	xbmc.log('EPOCH_NOW: ' + str(int(epoch_now)),level=log_level)
	html = get_html(url)
	soup = BeautifulSoup(html, 'html.parser')
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	response = re.compile('type="application/json">(.+?)</script>').findall(html.decode('utf-8'))[0]
	data = json.loads(response)
	total = len(data['props']['pageProps']['page']['channels'])
	xbmc.log('TOTAL: ' + str(total),level=log_level);mini_epg=[]
	for i in range(total):
		image = defaultimage
		name = data['props']['pageProps']['page']['channels'][i]['name']
		id = data['props']['pageProps']['page']['channels'][i]['id']
		image = data['props']['pageProps']['page']['channels'][i]['logo']
		slug = data['props']['pageProps']['page']['channels'][i]['slug']
		videoId = data['props']['pageProps']['page']['channels'][i]['videoId']
		program = data['props']['pageProps']['page']['channels'][i]['program'][0]['title']
		epoch_end = data['props']['pageProps']['page']['channels'][i]['program'][0]['ends']
		next = data['props']['pageProps']['page']['channels'][i]['program'][1]['title']
		next_title = str(name) + ' - ' + str(next)
		next_start = data['props']['pageProps']['page']['channels'][i]['program'][1]['starts']
		start_next = time.strftime('%I:%M %p ', time.localtime(int(next_start)))
		next_program = str((start_next + ' - ' + next_title).encode('utf-8'))[2:-1]
		mini_epg.append(next_program)
		title = str(name) + ' - ' + str(program)
		sec = (epoch_end - epoch_now)
		#xbmc.log('SECONDS: ' + str(sec),level=log_level)
		url = vidbase + str(videoId)
		#url = "https://www.sports.tv/channels/" + str(slug)
		curl = 'plugin://plugin.video.sportstv?mode=30&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)

		li.addContextMenuItems([('Next Program', 'RunPlugin(%s?mode=8&url=%s)' % (sys.argv[0], (next_title,next_start))), ('Mini Guide', 'RunPlugin(%s?mode=9&url=%s)' % (sys.argv[0], (mini_epg)))])

		#li.addContextMenuItems([('Mini EPG', 'RunPlugin(%s?mode=8)' % (sys.argv[0]))])
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"duration":sec})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		#li.addContextMenuItems([('Mini EPG', 'RunPlugin(%s?mode=9&url=%s)' % (sys.argv[0], (mini_epg)))])
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=curl, listitem=li, isFolder=False)
		if sort != 'false':
			xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
	#xbmc.log("PROGRAM_INFO: " + str(mini_epg), level=log_level)
	if sort != 'false':
		#mini_epg = sorted(mini_epg, key=lambda x: os.path.splitext(' - ')[1])
		SORT_EPG(mini_epg)
		#WRITE_EPG(mini_epg)
		xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
	else:
		WRITE_EPG(mini_epg)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

def GET_LIVE(name,url):
	response = get_html(url)
	data = json.loads(response)
	url = data['video']['video_m3u8']
	PLAY(name,url)

def SORT_EPG(data):
	#xbmc.log("DATA: " + str(data), level=log_level)
	mini_epg = sorted(data, key = lambda x: x.split(' - ')[1])
	xbmc.log("MINI_EPG: " + str(mini_epg), level=log_level)
	WRITE_EPG(mini_epg)
	return

def WRITE_EPG(data):
	xbmc.log("DATA: " + str(data), level=log_level)
	if not os.path.exists(addon_path_profile):
		os.makedirs(addon_path_profile)
	mini_epg = open(addon_path_profile + 'mini_epg.txt', 'w')
	for element in data:
		mini_epg.write(element)
		mini_epg.write('\n\n')
	mini_epg.close()
	return

#8
def PROGRAM_INFO(mini_epg):
	xbmc.log("PROGRAM_INFO: " + str(mini_epg), level=log_level)
	message = mini_epg.split(',')
	xbmc.log("MESSAGE: " + str(message), level=log_level)
	xbmc.log("MESSAGE1: " + str(message[1]), level=log_level)
	channel = (message[0].split(' - ')[0])[2:]
	#channel = (message[0])[2:]
	program = (message[0].split(' - ')[1])[:-1]
	#program = (message[0])[:-1]
	#try: start = int(message)[1]#.split(': ')[1])[:-2])
	try: start = int(re.findall("\d+", message[1])[0])
	except:
		start = 0000000000
	start_time = time.strftime('%I:%M %p ', time.localtime(start))
	if start_time.startswith('0'):
		start_time = start_time[1:]
	dialog = xbmcgui.Dialog()
	dialog.ok(channel, start_time + ' ' + program)
	return

#9
def MINI_EPG(data):
	data = open(addon_path_profile + 'mini_epg.txt', 'rt')
	mini_epg = data.read()
	data.close()
	dialog = xbmcgui.Dialog()
	dialog.textviewer('Sports.TV Mini Guide', str(mini_epg))
	#xbmc.log("MINI_EPG: " + str(mini_epg), level=log_level)
	return

#15
def GET_CHANNELS(name,url):
	html = get_html(url)
	soup = BeautifulSoup(html, 'html.parser')
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	response = re.compile('type="application/json">(.+?)</script>').findall(html.decode('utf-8'))[0]
	xbmc.log('LENGTH: ' + str(len(response)),level=log_level)
	data = json.loads(response)
	total = len(data['props']['pageProps']['page']['rails'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for i in range(total):
		name = (data['props']['pageProps']['page']['rails'][i]['category']['name'])#.capitalize()
		title = name[0].upper() + name[1:].lower()
		slug = name.lower().replace("'","-").replace(' ','-')
		#id = data[i]['id']
		#image = data[i]['icon']
		url = 'https://www.sports.tv/on-demand/category/' + slug
		curl = 'plugin://plugin.video.sportstv?mode=16&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		#li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':defaultimage,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=curl, listitem=li, isFolder=True)
		if sort != 'false':
			xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#16
def GET_SHOWS(name,url):
	html = get_html('https://www.sports.tv/on-demand')
	soup = BeautifulSoup(html, 'html.parser')
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	response = re.compile('type="application/json">(.+?)</script>').findall(html.decode('utf-8'))[0]
	xbmc.log('LENGTH: ' + str(len(response)),level=log_level)
	data = json.loads(response)
	buildId = (data['buildId'])
	xbmc.log('BUILDID: ' + str(buildId),level=log_level)
	vodbase = 'https://www.sports.tv/_next/data/' + str(buildId) + '/on-demand.json'
	xbmc.log('VODBASE: ' + str(vodbase),level=log_level)
	response = get_html(vodbase)
	data = json.loads(response)
	total = len(data['pageProps']['page']['rails'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for i in range(total):
		if name.lower() == (data['pageProps']['page']['rails'][i]['category']['name']).lower():
			xbmc.log('MATCH',level=log_level)
			xbmc.log('I:' + str(i),level=log_level)
			x = i
	total = len(data['pageProps']['page']['rails'][x]['cards'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for i in range(total):
		title = data['pageProps']['page']['rails'][x]['cards'][i]['title']
		image = data['pageProps']['page']['rails'][x]['cards'][i]['image']
		slug = data['pageProps']['page']['rails'][x]['cards'][i]['slug']
		type = data['pageProps']['page']['rails'][x]['cards'][i]['type']
		if type == 'shows':
			continue
		surl = 'https://www.sports.tv/on-demand/' + slug
		url = 'plugin://plugin.video.sportstv?mode=17&url=' + urllib.parse.quote_plus(surl)
		li = xbmcgui.ListItem(title)
		li.addContextMenuItems([('Description', 'RunPlugin(%s?mode=18&url=%s)' % (sys.argv[0], (url)))])
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})#,"duration":duration})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
		if sort != 'false':
			xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#17
def GET_MOVIE(name,url):
	html = get_html(url)
	soup = re.compile('type="application/json">(.+?)</script>').findall(html.decode('utf-8'))[0]
	data = json.loads(soup)
	videoId = data['props']['pageProps']['page']['pdp']['videoId']
	xbmc.log('VIDEOID: ' + str(videoId),level=log_level)
	url = vidbase + videoId
	xbmc.log('URL: ' + str(url),level=log_level)
	response = get_html(url)
	data = json.loads(response)
	video_m3u8 = data['video']['video_m3u8']
	PLAY(name,video_m3u8)

#18
def PLOT_INFO(url):
	html = get_html(url)
	soup = re.compile('type="application/json">(.+?)</script>').findall(html.decode('utf-8'))[0]
	data = json.loads(soup)
	name = data['props']['pageProps']['page']['pdp']['title']
	duration = data['props']['pageProps']['page']['pdp']['duration']
	if '.' in duration:
		duration = int(duration.split('.')[0])
	runtime = str(datetime.timedelta(seconds = round(int(duration))))
	year = data['props']['pageProps']['page']['pdp']['year']
	rating = data['props']['pageProps']['page']['pdp']['rating']
	descript = data['props']['pageProps']['page']['pdp']['description']
	plot = striphtml(str(descript))
	info = plot + '\n\n' + runtime + '  ' + year + '  ' + rating
	#plot = str(re.compile('<meta property="og:description" content="(.+?)"').findall(html))[2:-2]
	dialog = xbmcgui.Dialog()
	dialog.textviewer(name, info)

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

#99
def PLAY(name,url):
	xbmc.log('PLAY_URL: ' + str(url),level=log_level)
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log('### SETRESOLVEDURL ###',level=log_level)
	listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
	xbmc.log('URL: ' + str(url), level=log_level)
	xbmcplugin.endOfDirectory(addon_handle)


def get_html(url):
	xbmc.log('GET_URL: ' + str(url),level=log_level)
	req = urllib.request.Request(url)
	req.add_header('User-Agent', ua)

	try:
		response = urllib.request.urlopen(req)
	except timeout as e:
		#ResponseData = e.read().decode("utf8", 'ignore')
		xbmc.log('TIMEOUT ERROR: ' + str(e), level=log_level)
		dialog = xbmcgui.Dialog()
		#dialog.ok(addon, translation(30001), ResponseData)
		dialog.ok(addon, str(e))
		sys.exit('A Timeout Occurred')
	except urllib.error.URLError as e:
		#ResponseData = e.read().decode("utf8", 'ignore')
		dialog = xbmcgui.Dialog()
		#dialog.ok(addon, translation(30001), ResponseData)
		dialog.ok(addon, str(e))
		xbmc.log('URLLIB ERROR: ' + str(e), level=log_level)
		response = False
		html = False
		sys.exit('A Urllib Error Occurred')
	else:
		xbmc.log('CODE: ' + str(response.getcode()), level=log_level)
		html = response.read()
		response.close()
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
	liz.setInfo(type="Video", infoLabels={"mediatype":"video","title":name,"genre":"Sports"})
	liz.setArt({'thumb':defaulticon,'icon':defaulticon,'fanart':defaultfanart})
	#liz.setProperty('IsPlayable', 'true')
	#liz.setInfo( type="Video", infoLabels={ "Title": name } )
	if not fanart:
		fanart=defaultfanart
	#liz.setProperty('fanart_image',fanart)
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
mini_epg = None

try:
	url = urllib.parse.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.parse.unquote_plus(params["name"])
except:
	pass
try:
	mini_epg = urllib.parse.unquote_plus(params["mini_epg"])
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
	xbmc.log("Sports.TV Menu")
	CATEGORIES()
elif mode == 5:
	xbmc.log("Sports.TV Live", level=log_level)
	LIVE(name,url)
elif mode == 7:
	xbmc.log("Sports.TV On Demand", level=log_level)
	ON_DEMAND()
elif mode == 8:
	xbmc.log("Sports.TV Program Info", level=log_level)
	PROGRAM_INFO(url)
elif mode == 9:
	xbmc.log("Sports.TV Mini EPG", level=log_level)
	MINI_EPG(url)
elif mode == 10:
	xbmc.log("Sports.TV Get Stream", level=log_level)
	VOD_JSON(url)
elif mode == 15:
	xbmc.log("Sports.TV Video On Demand", level=log_level)
	GET_CHANNELS(name,url)
elif mode == 16:
	xbmc.log("Sports.TV Channel Listing", level=log_level)
	GET_SHOWS(name,url)
elif mode == 17:
	xbmc.log("Sports.TV Get Movie", level=log_level)
	GET_MOVIE(name,url)
elif mode == 18:
	xbmc.log("Sports.TV Get Movie Description", level=log_level)
	PLOT_INFO(url)
elif mode == 20:
	xbmc.log("Sports.TV Get Stream", level=log_level)
	GET_STREAM(url)
elif mode == 30:
	xbmc.log("Sports.TV Get Stream", level=log_level)
	GET_LIVE(name,url)
elif mode == 99:
	xbmc.log("Play Video", level=log_level)
	PLAY(name,url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
