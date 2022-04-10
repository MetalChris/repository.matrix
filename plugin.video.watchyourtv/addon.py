#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2)

#2022.01.11

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmcplugin, xbmcaddon, xbmcgui, xbmcvfs, sys, os, re
import json
#from datetime import datetime, timedelta as td
import time
from socket import timeout

today = time.strftime("%m-%d-%Y")

addon_id = 'plugin.video.watchyourtv'
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

defaultimage = 'special://home/addons/plugin.video.watchyourtv/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.watchyourtv/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.watchyourtv/resources/media/icon.png'
artbase = 'special://home/addons/plugin.video.watchyourtv/resources/media/'

addon = 'WatchYour.TV'

addon_handle = int(sys.argv[1])
false_epoch = 10
pattern= r"\D(\d{%d})\D" % false_epoch

#global mini_epg# = []


def CATEGORIES():
	addDir('WatchYour.TV Live', 'https://www.watchyour.tv/guide.json', 5, defaultimage, defaultfanart)
	addDir('WatchYour.TV On Demand', 'https://www.watchyour.tv/guide.json', 15, defaultimage, defaultfanart)
	xbmcplugin.endOfDirectory(addon_handle)


#5
def LIVE(name,url):
	epoch_now = int(time.time())
	xbmc.log('EPOCH_NOW: ' + str(int(epoch_now)),level=log_level)
	response = get_html(url)
	data = json.loads(response)
	total = len(data)
	xbmc.log('TOTAL: ' + str(total),level=log_level);mini_epg=[]
	for i in range(total):
		image = defaultimage
		channel = data[i]['name']
		id = data[i]['id']
		image = data[i]['icon']
		shows = len(data[i]['shows'])
		#xbmc.log('SHOWS: ' + str(shows),level=log_level)
		for s in range(shows):
			epoch_start = int(data[i]['shows'][s]['tms'])# + 68400
			#xbmc.log('EPOCH_start: ' + str(int(epoch_start)),level=log_level)
			duration = int(data[i]['shows'][s]['duration'])
			epoch_end = (duration * 60) + epoch_start
			if (epoch_now > epoch_start) and (epoch_now < epoch_end):
				title = str(channel) + ': ' + str(data[i]['shows'][s]['name'])
				try: next_title = str(channel) + ': ' + str(data[i]['shows'][s+1]['name'])
				except:
					next_title = str(channel) + ': Programming Not Avaliable'
				try: next_start = data[i]['shows'][s+1]['tms']
				except:
					next_start = 0000000000
				start_next = time.strftime('%I:%M %p ', time.localtime(int(next_start)))
				if start_next.startswith('0'):
					start_next = start_next[1:]
				next_program = start_next + ' - ' + next_title
				mini_epg.append(next_program)
				#xbmc.log('EPOCH_END: ' + str(int(epoch_end)),level=log_level)
				url = data[i]['shows'][s]['url']
				#xbmc.log('URL: ' + str(url),level=log_level)
				#tms = re.findall(pattern, url)[0]
				tms = data[i]['shows'][s]['tms']
				#xbmc.log('TMS: ' + str(tms),level=log_level)
				sec = (epoch_end - epoch_now)# * 60
				url = url.replace(tms, str(epoch_now))
				url = re.sub('index.*?.m3u8','index.m3u8',url, flags=re.DOTALL)
				curl = 'plugin://plugin.video.watchyourtv?mode=99&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
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
	channel = (message[0].split(': ')[0])[2:]
	program = (message[0].split(': ')[1])[:-1]
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
	dialog.textviewer('WatchYour.TV Mini Guide', str(mini_epg))
	#xbmc.log("MINI_EPG: " + str(mini_epg), level=log_level)
	return

#15
def GET_CHANNELS(name,url):
	response = get_html(url)
	data = json.loads(response)
	total = len(data)
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for i in range(total):
		title = data[i]['name']
		id = data[i]['id']
		image = data[i]['icon']
		if not data[i]['shows']:
			continue
		curl = 'plugin://plugin.video.watchyourtv?mode=16&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		#li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=curl, listitem=li, isFolder=True)
		if sort != 'false':
			xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#16
def GET_SHOWS(name,url):
	response = get_html(url)
	data = json.loads(response)
	total = len(data);vod_shows=[]
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for i in range(total):
		if name != data[i]['name']:
			continue
		shows = len(data[i]['shows'])
		xbmc.log('SHOWS: ' + str(shows),level=log_level)
		for s in range(shows):
			title = data[i]['shows'][s]['name']
			if title in vod_shows:
				continue
			vod_shows.append(title)
			image = defaultimage
			surl = data[i]['shows'][s]['url']
			duration = (int(data[i]['shows'][s]['duration'])) * 60
			url = 'plugin://plugin.video.watchyourtv?mode=99&url=' + urllib.parse.quote_plus(surl)
			li = xbmcgui.ListItem(title)
			li.setProperty('IsPlayable', 'true')
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"duration":duration})
			li.setArt({'thumb':image,'fanart':defaultfanart})
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
			if sort != 'false':
				xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#99
def PLAY(name,url):
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log('### SETRESOLVEDURL ###',level=log_level)
	listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
	xbmc.log('URL: ' + str(url), level=log_level)
	xbmcplugin.endOfDirectory(addon_handle)


def get_html(url):
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
	xbmc.log("WatchYour.TV Menu")
	CATEGORIES()
elif mode == 5:
	xbmc.log("WatchYour.TV Live", level=log_level)
	LIVE(name,url)
elif mode == 7:
	xbmc.log("WatchYour.TV On Demand", level=log_level)
	ON_DEMAND()
elif mode == 8:
	xbmc.log("WatchYour.TV Program Info", level=log_level)
	PROGRAM_INFO(url)
elif mode == 9:
	xbmc.log("WatchYour.TV Mini EPG", level=log_level)
	MINI_EPG(url)
elif mode == 10:
	xbmc.log("WatchYour.TV Get Stream", level=log_level)
	VOD_JSON(url)
elif mode == 15:
	xbmc.log("WatchYour.TV Video On Demand", level=log_level)
	GET_CHANNELS(name,url)
elif mode == 16:
	xbmc.log("WatchYour.TV Channel Listing", level=log_level)
	GET_SHOWS(name,url)
elif mode == 20:
	xbmc.log("WatchYour.TV Get Stream", level=log_level)
	GET_STREAM(url)
elif mode == 99:
	xbmc.log("Play Video", level=log_level)
	PLAY(name,url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
