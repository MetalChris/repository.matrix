#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2) or Later

# 2021.10.23

import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, re, sys, xbmcvfs, os
import json
from bs4 import BeautifulSoup
import html5lib

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id='plugin.video.vuit')
translation = selfAddon.getLocalizedString
usexbmc = selfAddon.getSetting('watchinxbmc')
settings = xbmcaddon.Addon(id="plugin.video.vuit")
__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

from uas import *

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 2
else:
	log_level = 1
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)

baseurl = 'https://www.vuit.com/'
streambase = 'https://www.vuit.com/api/services/StreamInfo?stationId='

defaultimage = 'special://home/addons/plugin.video.vuit/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.vuit/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.vuit/resources/media/icon.png'
addon_handle = int(sys.argv[1])

headers = {'Host': 'prod-api.viewlift.com', 'User-Agent': ua, 'Referer': 'https://www.vuit.com/', 'x-api-key': 'PBSooUe91s7RNRKnXTmQG7z3gwD2aDTA6TlJp6ef'}

usStates = {'AL':'Alabama','AK':'Alaska','AS':'American Samoa','AZ':'Arizona','AR':'Arkansas','CA':'California','CO':'Colorado','CT':'Connecticut','DE':'Delaware','DC':'District Of Columbia','FM':'Federated States Of Micronesia','FL':'Florida','GA':'Georgia','GU':'Guam','HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas','KY':'Kentucky','LA':'Louisiana','ME':'Maine','MH':'Marshall Islands','MD':'Maryland','MA':'Massachusetts','MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico','NY':'New York','NC':'North Carolina','ND':'North Dakota','MP':'Northern Mariana Islands','OH':'Ohio','OK':'Oklahoma','OR':'Oregon','PW':'Palau','PA':'Pennsylvania','PR':'Puerto Rico','RI':'Rhode Island','SC':'South Carolina','SD':'South Dakota','TN':'Tennessee','TT':'Trust Territory of the Pacific Island','TX':'Texas','UT':'Utah','VT':'Vermont','VI':'Virgin Islands','VA':'Virginia','WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming'}

#1
def main():
	addDir('Live TV', 'https://www.vuit.com/live/', 2, defaultimage, defaultfanart, '')
	addDir('Shows', 'https://www.vuit.com/shows/', 6, defaultimage, defaultfanart, '')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#2
def get_states(url):
	html = get_html(url)
	soup = BeautifulSoup(html,'html5lib').find_all('script',{'type':'text/javascript'})[2]
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	for item in soup:
		if 'viewmodel' in str(soup):
			response = re.compile('models", (.+?)\);\n').findall(str(soup))
			xbmc.log('RESPONSE: ' + str(len(response[0])),level=log_level)
			xbmc.log('RESPONSE: ' + str(response[0])[0:100],level=log_level)
			xbmc.log('RESPONSE: ' + str(response[0])[-100:],level=log_level)
	response = '[' + str(response[0]) + ']'
	data = json.loads(response);i=0;states=[]
	get_simple_keys(data[0])
	#channel = data['channels'][0]
	total = len(data[0]['channels'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for item in range(total):
		state = data[0]['channels'][i]['state'];i=i+1
		if state not in states:
			states.append(state)
	for state in states:
		for key in usStates.keys():
			if key.find(state) > -1:
				name = (usStates[key])
		surl = url + '-' + state
		addDir(name, surl, 3, defaultimage, defaultfanart, '')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#3
def all_live(url):
	USstate = url.split('-')[1]
	xbmc.log('US_STATE: ' + str(USstate),level=log_level)
	url = url.split('-')[0]
	xbmc.log('URL: ' + str(url),level=log_level)
	html = get_html(url)
	soup = BeautifulSoup(html,'html5lib').find_all('script',{'type':'text/javascript'})[2]
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	for item in soup:
		if 'viewmodel' in str(soup):
			response = re.compile('models", (.+?)\);\n').findall(str(soup))
			xbmc.log('RESPONSE: ' + str(len(response[0])),level=log_level)
			xbmc.log('RESPONSE: ' + str(response[0])[0:100],level=log_level)
			xbmc.log('RESPONSE: ' + str(response[0])[-100:],level=log_level)
	response = '[' + str(response[0]) + ']'
	data = json.loads(response);i=0
	get_simple_keys(data[0])
	#channel = data['channels'][0]
	total = len(data[0]['channels'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for item in range(total):
		state = data[0]['channels'][i]['state']
		xbmc.log('STATE: ' + str(state),level=log_level)
		if state == USstate:
			title = (data[0]['channels'][i]['name'])#.title()
			image = ('https://' + data[0]['channels'][i]['images'][2]['url']).replace('64x64', '256x256')
			fanart = 'https://' + data[0]['channels'][i]['images'][0]['url']
			token = data[0]['channels'][i]['token']
			displayLocation = data[0]['channels'][i]['displayLocation']
			stationId = data[0]['channels'][i]['stationId']
			purl = streambase + str(stationId)
			url = 'plugin://plugin.video.vuit?mode=20&url=' + urllib.parse.quote_plus(str(purl))
			li = xbmcgui.ListItem(title + ' - ' + displayLocation)
			li.setProperty('IsPlayable', 'true')
			li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title + ' - ' + displayLocation,"genre":"TV","plot":''})
			li.setArt({'thumb':image,'fanart':fanart})
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False);i=i+1
		else:
			i = i + 1
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#https://www.vuit.com/publishers/458#channel:19134

#6
def get_show_cats(url):
	html = get_html(url)
	soup = BeautifulSoup(html,'html5lib').find_all('script',{'type':'text/javascript'})[2]
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	for item in soup:
		if 'viewmodel' in str(soup):
			response = re.compile('models", (.+?)\);\n').findall(str(soup))
			xbmc.log('RESPONSE: ' + str(len(response[0])),level=log_level)
			xbmc.log('RESPONSE: ' + str(response[0])[0:100],level=log_level)
			xbmc.log('RESPONSE: ' + str(response[0])[-100:],level=log_level)
	response = '[' + str(response[0]) + ']'
	data = json.loads(response);i=0
	total = len(data[0]['groups'])#[0]['shows'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for cat in range(total):
		title = data[0]['groups'][i]['displayName']
		groupId = data[0]['groups'][1]['groupId']
		xbmc.log('TITLE: ' + str(title),level=log_level)
		curl = url + '-' + str(i)
		addDir(title, curl, 7, defaultimage, defaultfanart, '');i=i+1
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#7
def get_shows(url):
	c = int(url.split('-')[1])
	xbmc.log('C: ' + str(c),level=log_level)
	url = url.split('-')[0]
	xbmc.log('URL: ' + str(url),level=log_level)
	html = get_html(url)
	soup = BeautifulSoup(html,'html5lib').find_all('script',{'type':'text/javascript'})[2]
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	for item in soup:
		if 'viewmodel' in str(soup):
			response = re.compile('models", (.+?)\);\n').findall(str(soup))
			xbmc.log('RESPONSE: ' + str(len(response[0])),level=log_level)
			xbmc.log('RESPONSE: ' + str(response[0])[0:100],level=log_level)
			xbmc.log('RESPONSE: ' + str(response[0])[-100:],level=log_level)
	response = '[' + str(response[0]) + ']'
	data = json.loads(response);i=0
	total = len(data[0]['groups'][c]['shows'])
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for show in range(total):
		title = data[0]['groups'][c]['shows'][i]['name']
		showId = data[0]['groups'][c]['shows'][i]['showId']
		xbmc.log('TITLE: ' + str(title),level=log_level)
		xbmc.log('SHOW ID: ' + str(showId),level=log_level)
		plot = str(data[0]['groups'][c]['shows'][i]['description'])
		surl = url + str(showId) + '-' + str(c)
		addDir(title, surl, 9, defaultimage, defaultfanart, plot);i=i+1
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#9
def get_episodes(name, url):
	c = int(url.split('-')[1])
	xbmc.log('C: ' + str(c),level=log_level)
	url = url.split('-')[0]
	xbmc.log('URL: ' + str(url),level=log_level)
	showId = url.split('/')[-1];g=0
	xbmc.log('SHOWID: ' + str(showId),level=log_level)
	html = get_html(url)
	soup = BeautifulSoup(html,'html5lib').find_all('script',{'type':'text/javascript'})[2]
	xbmc.log('SOUP: ' + str(len(soup)),level=log_level)
	for item in soup:
		if 'viewmodel' in str(soup):
			response = re.compile('models", (.+?)\);\n').findall(str(soup))
			xbmc.log('RESPONSE: ' + str(len(response[0])),level=log_level)
			xbmc.log('RESPONSE: ' + str(response[0])[0:100],level=log_level)
			xbmc.log('RESPONSE: ' + str(response[0])[-100:],level=log_level)
	response = '[' + str(response[0]) + ']'
	data = json.loads(response);i=0
	total = len(data[0]['publisher']['publisherGroups'])#;g=0
	xbmc.log('TOTAL: ' + str(total),level=log_level)
	for group in range(total):
		if data[0]['publisher']['publisherGroups'][g]['show'] is None:
			g = g + 1
	xbmc.log('FOUND: ' + str(g),level=log_level)
	e = len(data[0]['publisher']['publisherGroups'][g]['show']['seasons'])
	xbmc.log('SEASONS: ' + str(e),level=log_level);s=0
	xbmc.log('G: ' + str(g),level=log_level)
	if showId == '1349': g = g + 1
	if showId == '1350': g = g + 2
	if showId == '1351': g = g + 3
	xbmc.log('G: ' + str(g),level=log_level)
	e = len(data[0]['publisher']['publisherGroups'][g]['show']['seasons'][s]['episodes'])
	xbmc.log('EPISODES : ' + str(e),level=log_level);s=0
	for episode in range(e):
		title = data[0]['publisher']['publisherGroups'][g]['show']['seasons'][0]['episodes'][episode]['contentTitle']
		xbmc.log('TITLE: ' + str(title),level=log_level)
		plot = data[0]['publisher']['publisherGroups'][g]['show']['seasons'][0]['episodes'][episode]['description']
		contentId = data[0]['publisher']['publisherGroups'][g]['show']['seasons'][0]['episodes'][episode]['contentId']
		purl = 'https://www.vuit.com/api/services/GetContentPlaylistInfo?contentId=' + str(contentId)
		url = 'plugin://plugin.video.vuit?mode=25&url=' + urllib.parse.quote_plus(str(purl))
		li = xbmcgui.ListItem(title)
		li.setProperty('IsPlayable', 'true')
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"genre":"TV","plot":plot})
		li.setArt({'thumb':defaulticon,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)#;e=e+1
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#10
#def get_show_episodes(data, g):

#20
def get_stream(name,url):
	response = get_html(url)
	data = json.loads(response)
	url = data['streamUrl']
	PLAY(name,url)
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#25
def get_episode_stream(name,url):
	response = get_html(url)
	data = json.loads(response)
	url = data['playlistInfo']['playlistUrl']
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


def get_simple_keys(data):
	result = []
	for key in data.keys():
		xbmc.log('KEY: ' + str(key),level=log_level)
		if type(data[key]) != dict:
			result.append(key)
		else:
			result += get_simple_keys(data[key])
	return result


def striphtml(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)


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
	#xbmc.log(("Get All Shows"),level=log_level)
	#all_live()
	xbmc.log(("Generate Main Menu"),level=log_level)
	main()
elif mode == 1:
	xbmc.log(("Indexing Videos"),level=log_level)
	INDEX(url)
elif mode == 2:
	xbmc.log(("Get States"),level=log_level)
	get_states(url)
elif mode == 3:
	xbmc.log(("Get All Live"),level=log_level)
	all_live(url)
elif mode == 4:
	xbmc.log(("Play Video"),level=log_level)
elif mode == 5:
	xbmc.log(("Get More Shows"),level=log_level)
	more_shows(url)
elif mode == 6:
	xbmc.log(("Get Show Categories"),level=log_level)
	get_show_cats(url)
elif mode == 7:
	xbmc.log(("Get Shows"),level=log_level)
	get_shows(url)
elif mode == 9:
	xbmc.log(("Get Episodes"),level=log_level)
	get_episodes(name, url)
elif mode == 20:
	xbmc.log(("Get Stream"),level=log_level)
	get_stream(name,url)
elif mode == 25:
	xbmc.log(("Get Episode Stream"),level=log_level)
	get_episode_stream(name,url)
elif mode == 99:
	xbmc.log("Play Video", level=log_level)
	PLAY(name,url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
