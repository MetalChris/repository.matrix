#!/usr/bin/python
#
#
# Constructed by MetalChris
# Released under GPL(v2) or Later

#11.25.2021

from six.moves import urllib_parse, urllib_request, urllib_error, http_client
from kodi_six import xbmc, xbmcplugin, xbmcaddon, xbmcgui
import re, os
import sys
from bs4 import BeautifulSoup
import json
import requests
import socket
if sys.version_info >= (3, 4, 0):
	import html
	_html_parser = html
	PY2 = False
else:
	from six.moves import html_parser
	_html_parser = html_parser.HTMLParser()
	PY2 = True

settings = xbmcaddon.Addon(id="plugin.audio.internetarchive")
artbase = 'special://home/addons/plugin.audio.internetarchive/resources/media/'
_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='plugin.audio.internetarchive')
translation = selfAddon.getLocalizedString
local_string = xbmcaddon.Addon(id='plugin.audio.internetarchive').getLocalizedString
dsort = settings.getSetting(id="dsort")
ssort = settings.getSetting(id="ssort")
download = settings.getSetting(id="download")
usexbmc = selfAddon.getSetting('watchinxbmc')
settings = xbmcaddon.Addon(id="plugin.audio.internetarchive")
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
baseurl = 'https://archive.org/'
audiourl = 'https://archive.org/details/audio'
__resource__   = xbmc.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)


from uas import *

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
	log_level = 1
else:
	log_level = 0
xbmc.log('LOG_NOTICE: ' + str(log_notice),level=log_level)
xbmc.log('DSORT: ' + str(dsort), level=log_level)

plugin = "Internet Archive [Audio]"

defaultimage = 'special://home/addons/plugin.audio.internetarchive/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.audio.internetarchive/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.audio.internetarchive/resources/media/icon.png'

local_string = xbmcaddon.Addon(id='plugin.audio.internetarchive').getLocalizedString
addon_handle = int(sys.argv[1])
#confluence_views = [500,501,502,503,504,508,515]
#xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[1])+")")

##### Sort Stuff #####
#https://archive.org/details/Film_Noir?sort=-addeddate&page=2
#?sort=-addeddate 1
#?sort=titleSorter 2

if dsort == '0':
	sort_value = ''
if dsort == '1':
	sort_value = '?sort=-addeddate'
if dsort == '2':
	sort_value = '?sort=titleSorter'


#60
def ia_categories():
	data = urllib_request.urlopen(audiourl).read()
	add_directory2('*Search', baseurl, 65, artbase + 'fanart.jpg', artbase + 'icon.png',plot='')
	soup = BeautifulSoup(data,'html.parser')
	for item in soup.find_all(attrs={'class': 'collection-title C C2'}):
		for link in item.find_all('a'):
			l = link.get('href')
			title = link.get('title')
			url = l
			if len(url) <5:
				continue
			if str(url)[0] == '/':
				url = 'https://archive.org' + url
			if title not in link:
				title = link.text
				if len(title) < 1:
					continue
				if ('All Audio' in title) or ('Just' in title):
					# Find a better way #
					title = (title.split(" ", 1))[-1]
				link = str(link)
				#title = re.compile('>(.+?)</a>').findall(link)[0]
				if 'img' in title:
					continue
				if '</span> ' in title:
					title = re.compile('</span> (.+?)</').findall(link)[0]
				if 'All Audio' in title:
					mode = 61
				elif title == 'Live Music Archive':
					mode = 64
				else:
					mode = 62
			url = url + '&page=1'
			title = title.strip()
			xbmc.log('TITLE: ' + str(title),level=log_level)
			#xbmc.log('IA URL: ' + str(url),level=log_level)
			#xbmc.log('MODE: ' + str(mode),level=log_level)
			add_directory2(title, url, mode, artbase + 'fanart.jpg', artbase + 'icon.png',plot='')
			xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
	#xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


#61
def ia_sub_cat(url):
	url = url.replace('?&page=1','')
	#xbmc.log('IA Audio Sub_Cat URL= ' + str(url),level=log_level)
	data = urllib_request.urlopen(url).read()
	soup = BeautifulSoup(data,'html.parser')
	for item in soup.find_all(attrs={'class': 'collection-title'}):
		for link in item.find_all('a'):
			l = link.get('href')
			url = 'https://archive.org' + l + '?&page=1'
			if len(url) <25:
				continue
			link = str(link)
			title = re.sub('\s+',' ',link)
			title = re.compile('<div>(.+)</div>').findall(title)[0]
			title = title.replace('&amp;','&')
			if title == 'Television Archive':
				mode = 61
			else:
				mode = 62
			add_directory2(title,url, mode, artbase + 'fanart.jpg', artbase + 'icon.png',plot='')
	xbmcplugin.setContent(addon_handle, 'episodes')


#62
def ia_sub2_audio(name,url):
	page = (url)[-1]
	xbmc.log('PAGE: ' + str(page),level=log_level)
	thisurl = url[:-7]
	#xbmc.log('thisurl= ' + str(thisurl),level=log_level)
	req = urllib_request.Request(url)
	try: data = urllib_request.urlopen(req, timeout = 5)
	except urllib_request.HTTPError as e:
		xbmc.log('Error Type= ' + str(type(e)),level=log_level)    #not catch
		xbmc.log('Error Args= ' + str(e.args),level=log_level)
		line1 = str(e.args).partition("'")[-1].rpartition("'")[0]
		#dialog = xbmcgui.Dialog()
		xbmcgui.Dialog().ok(addonname, line1, 'Please Try Again')
		return
	except urllib_request.URLError as e:
		xbmc.log('Error Type= ' + str(type(e)),level=log_level)
		xbmc.log('Error Args= ' + str(e.args),level=log_level)
		line1 = str(e.args).partition("'")[-1].rpartition("'")[0]
		#dialog = xbmcgui.Dialog()
		xbmcgui.Dialog().ok(addonname, line1, 'Please Try Again')
		return
	#except socket.timeout , e:
		#xbmc.log('Error Type= ' + str(type(e)),level=log_level)
		#xbmc.log('Error Args= ' + str(e.args),level=log_level)
		#line1 = str(e.args).partition("'")[-1].rpartition("'")[0]
		#dialog = xbmcgui.Dialog()
		#xbmcgui.Dialog().ok(addonname, line1, 'Please Try Again')
		#return
	try: soup = BeautifulSoup(data,'html.parser').find_all('div',{'class': 'item-ttl'})
	except SSLError:
		e = sys.exc_info()[1]
		xbmc.log('ERROR: ' + str(e),level=log_level)
		xbmc.log('Error Type= ' + str(type(e)),level=log_level)    #not catch
		xbmc.log('Error Args= ' + str(e.args),level=log_level)
		line1 = str(e.args).partition("'")[-1].rpartition("'")[0]
		#dialog = xbmcgui.Dialog()
		xbmcgui.Dialog().ok(addonname, line1, 'Please Try Again')
		return
	xbmc.log(('SOUP:' + str(len(soup))),level=log_level)
	for item in soup:
		l = item.find('a')['href']
		purl = 'https://archive.org' + l
		title = item.find('a')['title'].encode('ascii','ignore')
		url = purl
		add_directory3(title,url, 63, artbase + 'fanart.jpg', artbase + 'icon.png',plot='')
		xbmcplugin.setContent(addon_handle, 'episodes')
	page = str(int(page) + 1)
	#thisurl = thisurl.replace('?','')
	url = thisurl + '&page=' + page
	xbmc.log('IA Next Page URL= ' + str(url),level=log_level)
	add_directory2('Next Page', url, 62,  artbase + 'fanart.jpg', artbase + 'icon.png',plot='')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#63
def ia_audio_files(url):
	html = str(get_html(url))
	tracks = re.compile('"title":"(.+?)",').findall(html);	i = 0
	for track in tracks:
		title = striphtml(str(track.split('.')[-1]))
		#title_encode = title.encode("ascii", "ignore")
		#title = title_encode.decode()
		try:song = re.compile('"file":"(.+?)mp3').findall(html)[i]
		except IndexError:
			xbmcgui.Dialog().notification('IA [Audio]', 'No Playable Files Found.', xbmcgui.NOTIFICATION_INFO, 5000, False)
			return
		try:duration = re.compile('duration(.+?)sources').findall(html)[i]
		except IndexError:
			xbmcgui.Dialog().notification('IA [Audio]', 'No Playable Files Found.', xbmcgui.NOTIFICATION_INFO, 5000, False)
			return
		i = i + 1
		tracknumber = int(i)
		url = 'https://archive.org' + str(song) + 'mp3'
		infoLabels = {'title':title, 'duration':duration, 'tracknumber':tracknumber}
		li = xbmcgui.ListItem(title, artbase + 'icon.png', artbase + 'icon.png')
		li.setProperty('fanart_image',  artbase + 'fanart.jpg')
		#li.setProperty(Playcount)
		li.setInfo(type = 'music', infoLabels = infoLabels)
		li.addContextMenuItems([('Download File', 'RunPlugin(%s?mode=80&url=%s)' % (sys.argv[0], url))])
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=70)
		xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle)


#64
def ia_live_audio(name,url):
		page = (url)[-1]
		#xbmc.log('page= ' + str(page),level=log_level)
		thisurl = url[:-7]
		#xbmc.log('thisurl= ' + str(thisurl),level=log_level)
		req = urllib_request.Request(url)
		try: data = urllib_request.urlopen(req, timeout = 5)
		except urllib_request.HTTPError as e:
			xbmc.log('Error Type= ' + str(type(e)),level=log_level)    #not catch
			xbmc.log('Error Args= ' + str(e.args),level=log_level)
			line1 = str(e.args).partition("'")[-1].rpartition("'")[0]
			#dialog = xbmcgui.Dialog()
			xbmcgui.Dialog().ok(addonname, line1, 'Please Try Again')
			return
		except urllib_request.URLError as e:
			xbmc.log('Error Type= ' + str(type(e)),level=log_level)
			xbmc.log('Error Args= ' + str(e.args),level=log_level)
			line1 = str(e.args).partition("'")[-1].rpartition("'")[0]
			#dialog = xbmcgui.Dialog()
			xbmcgui.Dialog().ok(addonname, line1, 'Please Try Again')
			return
		#except socket.timeout , e:
			#xbmc.log('Error Type= ' + str(type(e)),level=log_level)
			#xbmc.log('Error Args= ' + str(e.args),level=log_level)
			#line1 = str(e.args).partition("'")[-1].rpartition("'")[0]
			#dialog = xbmcgui.Dialog()
			#xbmcgui.Dialog().ok(addonname, line1, 'Please Try Again')
			#return
		try: soup = BeautifulSoup(data,'html.parser').find_all('div',{'class': 'collection-title'})
		except SSLError:
			e = sys.exc_info()[1]
			xbmc.log('ERROR: ' + str(e),level=log_level)
			xbmc.log('Error Type= ' + str(type(e)),level=log_level)    #not catch
			xbmc.log('Error Args= ' + str(e.args),level=log_level)
			line1 = str(e.args).partition("'")[-1].rpartition("'")[0]
			#dialog = xbmcgui.Dialog()
			xbmcgui.Dialog().ok(addonname, line1, 'Please Try Again')
			return
		xbmc.log(('SOUP:' + str(len(soup))),level=log_level)
		for item in soup:
			l = item.find('a')['href']
			purl = 'https://archive.org' + l
			title = item.find('a').text.encode('ascii','ignore').strip()
			url = purl + '&page=1'
			add_directory2(title,url, 62, artbase + 'fanart.jpg', artbase + 'icon.png',plot='')
			xbmcplugin.setContent(addon_handle, 'episodes')
		page = str(int(page) + 1)
		#thisurl = thisurl.replace('?','')
		url = thisurl + '&page=' + page
		xbmc.log('IA Next Page URL= ' + str(url),level=log_level)
		add_directory2('Next Page', url, 64,  artbase + 'fanart.jpg', artbase + 'icon.png',plot='')
		xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#81
def lineage(url):
		html = get_html(url)
		xbmc.log('Lineage URL: ' + str(url),level=log_level)
		soup = BeautifulSoup(html,'html.parser').find_all('dl',{'class': 'metadata-definition'})
		#xbmc.log('SOUP: ' + str(soup),level=log_level)
		for item in soup:
			match = item.find('dt')
			if 'Lineage' in match:
				xbmc.log('Lineage Found: ' + str(match),level=log_level)
				lineage = item.find('dd').text
				xbmc.log('Lineage dd: ' + str(lineage),level=log_level)
		#lineage = str(re.compile('Lineage</dt>\n<dd class="">"(.+?)"</').findall(str(html)))[2:-2]
		#xbmc.log('Lineage: ' + str(lineage),level=log_level)
		#lineage = lineage.replace('&gt;','>').replace('&amp;','&')
				if len(lineage) < 5:
					lineage = 'Not Available'
				xbmcgui.Dialog().ok('Lineage', lineage)


#82
def desc(url):
		html = get_html(url)
		desc = str(re.compile('<meta property="og:description" content="(.+?)"/>').findall(html))[2:-2].replace('\\xc2\\xa0',' ').replace('\\xe2\\x80\\x99','\'').replace('\\xe2\\x80\\x98','')
		xbmcgui.Dialog().ok('Description', desc)


def play(name,url):
	url = url.replace(' ','%20')
	xbmc.log(url,level=log_level)
	listitem = xbmcgui.ListItem(name, thumbnailImage = defaultimage)
	xbmc.Player().play( url, listitem )
	sys.exit()
	xbmcplugin.endOfDirectory(addon_handle)


def ia_search():
	keyb = xbmc.Keyboard('', 'Search')
	keyb.doModal()
	if (keyb.isConfirmed()):
		search = urllib_parse.quote_plus(keyb.getText())
		xbmc.log('search= ' + search, level=log_level)
		# https://archive.org/details/audio?query=carmen+mcrae&sin=&sort=-addeddate
		url = 'https://archive.org/details/audio?query=' + search + '&sin=&?' + sort_value + '&page=1' #+ '?sort=-addeddate'
		xbmc.log('IA SEARCH URL= ' + str(url),level=log_level)
		ia_search_audio(url)
	else:
		ia_categories()
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def ia_search_audio(url):
	#page = re.search(r'(\d+)\D+$', url).group(1)
	#xbmc.log('PAGE: ' + str(page),level=log_level)
	page = (url)[-1]
	xbmc.log('PAGE: ' + str(page),level=log_level)
	thisurl = url.split("?")[0]
	xbmc.log('THISURL: ' + str(thisurl),level=log_level)
	#data = urllib_request.urlopen(url).read()
	data = get_html(url)
	soup = BeautifulSoup(data, 'html.parser')
	# xbmc.log('SOUP= ' + str(soup),level=log_level)
	for item in soup.find_all(attrs={'class': 'item-ttl'}):
		# for link in item.find_all('a'):
		l = item.find('a')['href']  # noqa
		purl = 'https://archive.org' + l
		title = (item.find('a')['title'])
		if len(title) < 1:
			continue
		image = 'https://archive.org' + item.find('img')['source']
		try:
			add_directory3(title, purl, 63, defaultfanart, image, plot='')
		except KeyError:
			continue
	page = str(int(page) + 1)
	# thisurl = thisurl.replace('?&sort='+sval+'','')
	url = thisurl + sort_value + '&page=' + page
	xbmc.log('IA Next Page URL= ' + str(url), level=log_level)
	add_directory2('Next Page', url, 66, artbase + 'fanart.jpg', artbase + 'icon.png', plot='')
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


#80
def downloader(url):
	xbmc.log('DOWNLOAD', level=log_level)
	path = addon.getSetting('download')
	if path == "":
		xbmc.executebuiltin("XBMC.Notification(%s,%s,10000,%s)"
							% (translation(30000), translation(30010), defaulticon))
		addon.openSettings()
		path = addon.getSetting('download')
	if path == "":
		return
	#html = get_html(url)
	#xbmc.log('Download URL: ' + str(url), level=log_level)
	#match = re.compile('<meta property="og:video" content="(.+?)">').findall(str(html))
	#xbmc.log('MATCH: ' + str(match), level=log_level)
	#xbmc.log('MATCH[0]: ' + str(match[0]), level=log_level)
	#url = resolve_http_redirect(match[0])
	#url = match[0].replace(' ','%20')
	xbmc.log('FINAL URL: ' + str(url), level=log_level)
	file_name = url.split('/')[-1].replace('%20',' ')
	dlsn = settings.getSetting(id="status")
	bsize = settings.getSetting(id="bsize")
	# xbmc.log('bfr Size= ' + str(bsize),level=log_level)
	ret = xbmcgui.Dialog().yesno("Internet Archive [Video]", 'Download Selected File? ' + str(file_name))
	if ret is False:
		return ia_sub2_video
	else:
		xbmcgui.Dialog().notification('IA [Video]', 'Getting Download URL.', xbmcgui.NOTIFICATION_INFO, 5000, False)
		response = urllib_request.urlopen(url)
		headers = response.getheader('Content-Length')
		xbmc.log('HEADERS: ' + str(headers), level=log_level)
		file_size = float(response.getheader('Content-Length'))
		xbmc.log('FILE_SIZE: ' + str(file_size), level=log_level)
		xbmcgui.Dialog().notification('IA [Video]', 'Download Started.', xbmcgui.NOTIFICATION_INFO, 3000, False)
		xbmc.log('Download Started', level=log_level)
	xbmc.log('URL: ' + str(url), level=log_level)
	xbmc.log('Filename: ' + str(file_name), level=log_level)
	xbmc.log('Download Location: ' + str(download), level=log_level)
	file_size = float(response.headers['Content-Length'])
	xbmc.log('FILE_SIZE: ' + str(file_size), level=log_level)
	with open(path + file_name, 'wb') as f:
		#response = urllib_request.urlretrieve(url)
		response = requests.get(url, stream=True)
		#total = int(response.headers.get('Content-Length'))
		#total = file_size
		MB = round(float(file_size/(1024*1024)),2)
		xbmc.log('TOTAL: ' + str(MB), level=log_level)
		if file_size is None:
			f.write(response.content)
		else:
			downloaded = 0
			file_size = int(file_size)
			for data in response.iter_content(chunk_size=max(int(file_size/1000), 1024*1024)):
				downloaded += len(data)
				f.write(data)
				done = int(100*downloaded/file_size)
				#xbmc.log('DONE: ' + str(done), level=log_level)
				if dlsn != 'false':
					xbmcgui.Dialog().notification('IA [Video] Download in Progress', str(done) + '% of ' + str(MB) + ' MB' , xbmcgui.NOTIFICATION_INFO, 10000, False)
					#xbmcgui.Dialog().notification('IA [Video] Download in Progress', str(done) + '% of ' + str(float(total/1000) / 1024*1024) + ' MB', xbmcgui.NOTIFICATION_INFO, 10000, False)
				else:
					break
	xbmcgui.Dialog().notification('IA [Video]', 'Download Completed.', xbmcgui.NOTIFICATION_INFO, 5000, False)
	xbmc.log('Download Completed', level=log_level)

def striphtml(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)


def add_directory3(name, url, mode, fanart, thumbnail, plot):
	u = sys.argv[0] + "?url=" + urllib_parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib_parse.quote_plus(name)
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
	# commands = []
	# commands.append ----- THIS WORKS! -----
	liz.addContextMenuItems([('Download File', 'RunPlugin(%s?mode=80&url=%s)' % (sys.argv[0], url)), ('Description', 'RunPlugin(%s?mode=81&url=%s)' % (sys.argv[0], url))])
	# liz.addContextMenuItems([('Plot Info', 'XBMC.RunPlugin(%s?mode=81&url=%s)' % (sys.argv[0], url))])
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True, totalItems=70)
	return ok


def add_directory2(name, url, mode, fanart, thumbnail, plot):
	u = sys.argv[0] + "?url=" + urllib_parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib_parse.quote_plus(name)
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


def add_next(name,url,mode,fanart,thumbnail,plot):
		u=sys.argv[0]+"?url="+urllib_parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib_parse.quote_plus(name)
		ok=True
		liz=xbmcgui.ListItem(name, Image="DefaultFolder.png", thumbnailImage=thumbnail)
		liz.setInfo( type="Video", infoLabels={ "Title": name,
												"plot": plot} )
		if not fanart:
			fanart=''
		liz.setProperty('fanart_image',fanart)
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True, totalItems=70)
		return ok


def resolve_http_redirect(url, depth=0):
	if depth > 10:
		raise Exception("Redirected "+depth+" times, giving up.")
	o = urlparse.urlparse(url,allow_fragments=True)
	conn = httplib.HTTPConnection(o.netloc)
	path = o.path
	if o.query:
		path +='?'+o.query
	conn.request("HEAD", path)
	res = conn.getresponse()
	headers = dict(res.getheaders())
	if headers.has_key('location') and headers['location'] != url:
		return resolve_http_redirect(headers['location'], depth+1)
	else:
		return url


def get_html(url):
	req = urllib_request.Request(url)
	req.add_header('User-Agent', ua)
	xbmc.log('USER AGENT: ' + str(ua),level=log_level)

	try:
		response = urllib_request.urlopen(req)
		html = response.read()
		response.close()
	except urllib_error.HTTPError as e:
		xbmc.log('*** HTTP Error ***' + str(e.args),level=log_level)
		xbmcgui.Dialog().ok('Internet Archive [Video]', 'HTTP Error: ' + str(e.args) + '\n\nA general HTTP error has occurred')
		response = False
		html = False
	except socket.timeout as e:
		xbmc.log('*** SOCKET TIMEOUT ***' + str(e.args),level=log_level)
		xbmcgui.Dialog().ok('Internet Archive [Video]', 'Socket Timeout: ' + str(e.args) + '\n\nCaused by slow response from Archive.org')
		sys.exit()
	except urllib_error.URLError as e:
		xbmc.log('*** CONNECTION ERROR ***',level=log_level)
		xbmcgui.Dialog().ok('Internet Archive [Video]', 'Connection Error: ' + str(e.args) + '\n\nCheck your connection')
		sys.exit()
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

try:
	url = urllib_parse.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib_parse.unquote_plus(params["name"])
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
	ia_categories()
elif mode == 1:
	xbmc.log("Indexing Audio",level=log_level)
	index(url)
elif mode == 4:
	xbmc.log("Play Audio",level=log_level)
elif mode == 6:
	xbmc.log("Get Episodes",level=log_level)
	get_episodes(url)
elif mode == 60:
	xbmc.log("Get IA Audio Categories",level=log_level)
	ia_audio(url)
elif mode == 61:
	xbmc.log("Get IA Audio Sub Categories",level=log_level)
	ia_sub_cat(url)
elif mode == 62:
	xbmc.log("Get IA Audio Sub2 Categories",level=log_level)
	ia_sub2_audio(name,url)
elif mode == 63:
	xbmc.log("Get Audio Files",level=log_level)
	ia_audio_files(url)
elif mode == 64:
	xbmc.log("Get IA Audio Live Categories",level=log_level)
	ia_live_audio(name,url)
elif mode == 65:
	xbmc.log("IA Search",level=log_level)
	ia_search()
elif mode == 66:
	xbmc.log("IA Search Audio",level=log_level)
	ia_search_audio(url)
elif mode == 80:
   xbmc.log("IA Download File",level=log_level)
   downloader(url)
elif mode == 81:
   xbmc.log("IA Lineage",level=log_level)
   lineage(url)
elif mode == 82:
   xbmc.log("IA Description",level=log_level)
   desc(url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
