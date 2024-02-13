#!/usr/bin/python
#
#
# Written by MetalChris 2024.01.28
# Released under GPL(v2 or later)

import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, re, sys, xbmcvfs, os
import json
import requests
import time

today = time.strftime("%Y-%m-%d")


addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'audio')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='plugin.audio.nhl-radio')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
settings = xbmcaddon.Addon(id="plugin.audio.nhl-radio")
base = 'https://api-web.nhle.com/v1/scoreboard/now'
plugin = "NHL Radio"
local_string = xbmcaddon.Addon(id='plugin.audio.nhl-radio').getLocalizedString
defaultimage = 'special://home/addons/plugin.audio.nhl-radio/resources/media/icon.png'
fanart = 'special://home/addons/plugin.audio.nhl-radio/resources/media/fanart.jpg'
SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}

__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

from uas import *

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 2
else:
	log_level = 1
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)

xbmc.log('TODAY: ' + str(today),level=log_level)
xbmc.log('NOW: ' + str(time.time()),level=log_level)
xbmc.log('UTC Offset: ' + str(-time.timezone),level=log_level)


#3
def all_games():
	response = get_html(base)
	data = json.loads(response);i=0;m=0
	total = len(data['gamesByDate']);t=0#[0]['contentData'])
	xbmc.log('TOTAL: ' + str(total),level=log_level);titles=[];x=0;i=0
	#games = len(data['gamesByDate'][t]['games'])
	#xbmc.log('GAMES: ' + str(games),level=log_level)
	days = (data['gamesByDate'][t]['date'])
	for day in days:
		gameDate = (data['gamesByDate'][t]['date'])
		xbmc.log('GAMEDATE: ' + str(gameDate),level=log_level)
		if gameDate != today:
			t=t+1
			games = len(data['gamesByDate'][t]['games'])
			xbmc.log('GAMES: ' + str(games),level=log_level)
			continue
	for game in range(games):
		if (data['gamesByDate'][t]['games'][x]['gameState']) == 'OFF':
			x=x+1
			continue
		if (data['gamesByDate'][t]['games'][x]['gameState']) == 'FINAL':
			x=x+1
			continue
		awayTeam = (data['gamesByDate'][t]['games'][x]['awayTeam']['name']['default'])
		homeTeam = (data['gamesByDate'][t]['games'][x]['homeTeam']['name']['default'])
		id = (data['gamesByDate'][t]['games'][x]['id'])
		xbmc.log('GAME ID: ' + str(id),level=log_level)
		url = 'https://api-web.nhle.com/v1_1/gamecenter/' + str(id) + '/landing'
		if (data['gamesByDate'][t]['games'][x]['gameState']) == 'FUT':
			url = 'Future'
		title = awayTeam + ' @ ' + homeTeam
		startTimeUTC = (data['gamesByDate'][t]['games'][x]['startTimeUTC']).replace('T',' ').replace('Z','')#.replace('-',',').replace(':',',')
		xbmc.log('startTimeUTC: ' + str(startTimeUTC),level=log_level)
		#startTimeUTC = startTimeUTC.replace('T',' ').replace('Z','')
		p='%Y-%m-%d %H:%M:%S'
		epoch = int(time.mktime(time.strptime(startTimeUTC,p)))
		xbmc.log('EPOCH: ' + str(epoch),level=log_level)
		gameTimeEpoch = int(epoch) + (-time.timezone)
		xbmc.log('gameTimeEpoch: ' + str(gameTimeEpoch),level=log_level)
		localgameTime = time.strftime("%-I:%M %p", time.localtime(gameTimeEpoch))
		xbmc.log('localgameTime: ' + str(localgameTime),level=log_level)
		if (data['gamesByDate'][t]['games'][x]['gameState']) == 'FUT':
			title = title + ' [' + str(localgameTime) + ']'
			url = 'Future'
		if (data['gamesByDate'][t]['games'][x]['gameState']) == 'PRE':
			title = title + ' [Pregame]'
		if (data['gamesByDate'][t]['games'][x]['gameState']) == 'LIVE':
			if (data['gamesByDate'][t]['games'][x]['period']) == 4:
				period = 'OT'
				title = title + ' [OT]'
			else:
				period = ordinal(data['gamesByDate'][t]['games'][x]['period'])
				title = title + ' [' + str(period) + ' Period]'
		if not title in titles:
			titles.append(title);x=x+1
		xbmc.log('TITLE: ' + str(title),level=log_level)
		xbmc.log('GAMES: ' + str(len(titles)),level=log_level)
		description = title
		addDir(title, url, 6, defaultimage, fanart, description);i=i+1
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#6
def get_streams(url):
	if url == 'Future':
		xbmc.log('URL: ' + str(url),level=log_level)
		dialog = xbmcgui.Dialog()
		ret = dialog.notification(heading=xbmcaddon.Addon().getAddonInfo('name'), message='This Game Has Not Yet Started', icon=defaultimage, time=3000, sound=False)
		xbmc.log('Game Has Not Started',level=log_level)
		sys.exit(1)
	response = get_html(url)
	data = json.loads(response);i=0;s=0
	id = (data['id'])
	xbmc.log('GAME ID: ' + str(id),level=log_level)
		#xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
	awayTeam = (data['awayTeam']['name']['default'])
	try:
		awayRadio = (data['awayTeam']['radioLink'])
		xbmc.log('Away Radio: ' + str(awayRadio),level=log_level)
	except:
		dialog = xbmcgui.Dialog()
		dialog.notification(heading=xbmcaddon.Addon().getAddonInfo('name'), message='No Away Stream Available',time=3000, sound=False)
	awayLogo = (data['awayTeam']['logo'])
	homeTeam = (data['homeTeam']['name']['default'])
	try:
		homeRadio = (data['homeTeam']['radioLink'])
		xbmc.log('Home Radio: ' + str(homeRadio),level=log_level)
	except:
		dialog = xbmcgui.Dialog()
		dialog.notification(heading=xbmcaddon.Addon().getAddonInfo('name'), message='No Home Stream Available', time=3000, sound=False)
	homeLogo = (data['homeTeam']['logo'])
	title = awayTeam + ' @ ' + homeTeam
	dialog = xbmcgui.Dialog()
	ret = dialog.contextmenu([str(awayTeam) + ' Radio', str(homeTeam) + ' Radio'])
	xbmc.log('RET: ' + str(ret),level=log_level)
	if ret == 0:
		PLAY(title, awayRadio)
	if ret == 1:
		PLAY(title, homeRadio)
	sys.exit()
	#xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#99
def PLAY(name,url):
	addon_handle = int(sys.argv[1])
	listitem = xbmcgui.ListItem(path=url)
	xbmc.log('### SETRESOLVEDURL ###',level=log_level)
	listitem.setProperty('IsPlayable', 'true')
	#background = [{'image':image}]
	#listitem.setAvailableFanart(background)
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
	xbmc.log('URL: ' + str(url), level=log_level)
	xbmcplugin.endOfDirectory(addon_handle)


def ordinal(num):
    # I'm checking for 10-20 because those are the digits that
    # don't follow the normal counting scheme.
    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        # the second parameter is a default.
        suffix = SUFFIXES.get(num % 10, 'th')
    return str(num) + suffix


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
	if url != 'Future':
		liz.setProperty('IsPlayable', 'true')
	else:
		liz.setProperty('IsPlayable', 'false')
	if not fanart:
		fanart=defaultfanart
	liz.setProperty('fanart_image',fanart)
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
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
	xbmc.log(("Get All Games"),level=log_level)
	all_games()
elif mode == 3:
	xbmc.log(("Get All Games"),level=log_level)
	all_games(url)
elif mode == 6:
	xbmc.log(("Get Streams"),level=log_level)
	get_streams(url)
elif mode == 99:
	xbmc.log("Play Stream", level=log_level)
	PLAY(name,url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
