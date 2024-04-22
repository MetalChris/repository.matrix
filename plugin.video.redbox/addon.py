#!/usr/bin/python
#
#
# Written by MetalChris 2024.04.20
# Released under GPL(v2 or later)

import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, os
import json
import time
from time import strftime, localtime
import requests
import inputstreamhelper


today = time.strftime("%Y-%m-%d")


addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'audio')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='plugin.video.redbox')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
settings = xbmcaddon.Addon(id="plugin.video.redbox")
baseUrl = 'https://www.redbox.com'
apiUrl = 'https://www.redbox.com/gapi/ondemand/hcgraphql/'
plugin = "Redbox"
local_string = xbmcaddon.Addon(id='plugin.video.redbox').getLocalizedString
defaultimage = 'special://home/addons/plugin.video.redbox/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.redbox/resources/media/fanart.jpg'

__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

from utilities import *

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
def cats():
	reels = requests.post(apiUrl, json = tvparams)
	xbmc.log('REELS: ' + str(len(reels.text)),level=log_level)
	data = json.loads(reels.text)
	for count, item in enumerate(data['data']['reelCollection']['reels']):
		#xbmc.log('COUNT: ' + str(count),level=log_level)
		#xbmc.log('ITEM: ' + str(item),level=log_level)
		title = item['name']
		image = defaultimage
		url = apiUrl
		streamUrl = 'plugin://plugin.video.redbox?mode=6&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	addDir2('On Demand Movies', apiUrl
	, 9, defaultfanart, defaultimage, infoLabels={'plot':'Watch Free Movies on Demand from Redbox'})
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#6
def channels(name,url):
	reels = requests.post(apiUrl, json = tvparams)
	xbmc.log('REELS: ' + str(len(reels.text)),level=log_level)
	data = json.loads(reels.text)
	for count, item in enumerate(data['data']['reelCollection']['reels']):
		#xbmc.log(('TITLE: ' + str(item['name'])),level=log_level)
		if item['name'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			c = count
			for count, item in enumerate(data['data']['reelCollection']['reels'][c]['items']):
				title = item['name']
				now = item['onNow']['title']
				description = item['onNow']['description']
				nextUp = item['onNext']['title']
				startTime = item['onNext']['startTime']
				lN = strftime('%H:%M', localtime(startTime))
				image = item['images']['stylized']
				plot = '[B]'+ str(now) +'[/B]' + ' ' + str(description) + '\n\n[NEXT @' + str(lN) + '] ' + '[B]'+ str(nextUp) +'[/B]'
				url = item['url']
				streamUrl = 'plugin://plugin.video.redbox?mode=99&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
				li = xbmcgui.ListItem(title)
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title,"plot":plot})
				li.setArt({'thumb':image,'fanart':defaultfanart})
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#9
def vod():
	reels = requests.post(apiUrl, json = vodparams)
	xbmc.log('REELS: ' + str(len(reels.text)),level=log_level)
	#xbmc.log('X: ' + str(reels.text),level=log_level)
	data = json.loads(reels.text)
	for count, item in enumerate(data['data']['reelCollection']['reelsPage']['reels']):
		#xbmc.log('COUNT: ' + str(count),level=log_level)
		#xbmc.log('ITEM: ' + str(item),level=log_level)
		title = item['name']
		image = defaultimage
		url = apiUrl
		streamUrl = 'plugin://plugin.video.redbox?mode=12&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		li = xbmcgui.ListItem(title)
		li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
		li.setArt({'thumb':image,'fanart':defaultfanart})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=True)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

#12
def movies(name,url):
	reels = requests.post(apiUrl, json = vodparams)
	xbmc.log('REELS: ' + str(len(reels.text)),level=log_level)
	data = json.loads(reels.text)
	for count, item in enumerate(data['data']['reelCollection']['reelsPage']['reels']):
		#xbmc.log(('TITLE: ' + str(item['name'])),level=log_level)
		if item['name'] == name:
			xbmc.log(('MATCH'),level=log_level)
			xbmc.log(('COUNT: ' + str(count)),level=log_level)
			c = count
			for count, item in enumerate(data['data']['reelCollection']['reelsPage']['reels'][c]['items']):
				plotId = item['productPagePath']
				title = item['name']
				image = 'https://images.redbox.com/Images/EPC/boxartvertical/' + item['images']['boxArtVertical']
				if len(str(item['id'])) < 5:
					continue
				videoId = '5' + str(item['id'])[1:]
				streamUrl = 'plugin://plugin.video.redbox?mode=15&url=' + urllib.parse.quote_plus(apiUrl) + '&name=' + urllib.parse.quote_plus(videoId)
				li = xbmcgui.ListItem(title)
				li.addContextMenuItems([('Movie Info', 'RunPlugin(%s?mode=82&url=%s)' % (sys.argv[0], (plotId)))])
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type="Video", infoLabels={"mediatype":"video","title":title})
				li.setArt({'thumb':image,'fanart':defaultfanart})
				xbmcplugin.addDirectoryItem(handle=addon_handle, url=streamUrl, listitem=li, isFolder=False)
	xbmcplugin.setContent(addon_handle, 'episodes')
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)


#15
def mymovie(name,url):

	movieparams = {
	  "query": "\n\tquery AvodStreams($redboxTitleId: String!,$filter:AvodStreamFilter) { \n\t\tavodStreams(redboxTitleId: $redboxTitleId,filter:$filter) {\n\t\t\tviewContentReference\n\t\t\tredboxTitleId\n\t\t\tname\n\t\t\tstreams {\n\t\t\t\tquality\n\t\t\t\tformat\n\t\t\t\tdrmType\n\t\t\t\turl\n\t\t\t\tdrmUrl\n\t\t\t\tlicenseRequestToken\n\t\t\t\tavailability\n\t\t\t\tadsType\n\t\t\t}\n\t\t\tcuePoints\n\t\t\tvmapUrl\n            scrubbers {\n                url\n            }\n\t\t}\n\t}\n",
	  "variables": {
	    "redboxTitleId": "" + str(name) + "",
		"filter": {
		  "drmType": [
			"WIDEVINE"
		  ],
		  "format": [
			"DASH"
		  ]
		}
	  }
	}

	headers = {'User-Agent': ua, 'X-Redbox-Device-Type': 'RedboxWebLinux'}
	reels = requests.post(apiUrl, headers=headers, json = movieparams)
	xbmc.log('REELS: ' + str(len(reels.text)),level=log_level)
	xbmc.log('REELS: ' + str(reels.text)[:200],level=log_level)
	if 'ITEM_NOT_FOUND' in reels.text:
		xbmcgui.Dialog().ok('Redbox Error', 'This video is not available at this time.')
		sys.exit()
	data = json.loads(reels.text)
	streamUrl = str(data['data']['avodStreams']['streams'][0]['url'])
	xbmc.log('STREAMURL: ' + str(streamUrl),level=log_level)
	token = str(data['data']['avodStreams']['streams'][0]['licenseRequestToken'])
	xbmc.log('TOKEN: ' + str(token),level=log_level)
	name = str(data['data']['avodStreams']['name'])
	PLAY(token,streamUrl)
	sys.exit()


def get_id(videoId,idUrl):
	reels = requests.get(idUrl)
	#xbmc.log('X: ' + str(reels.text),level=log_level)
	data = json.loads(reels.text)
	videoId = data['Id']
	return(id)


#82
def desc(plotId):

	infoparams = {
	    "operationName": "fetchTitleWeb",
	    "variables": {
	        "id": "" + url + "",
	        "idType": "PRODUCTPAGEID",
	        "number": 1,
	        "size": 500
	    },
	    "query": "query fetchTitleWeb($id: String!, $idType: ProductIdTypeEnum!, $number: Int!, $size: Int!) {\n  product(id: $id, idType: $idType) {\n    productGroupId\n    name\n    airDate\n    type\n    description {\n      long\n      short\n      __typename\n    }\n    duration\n    genres\n    originalLanguages\n    releaseYear\n    productPage\n    productLevelProgress: progress {\n      progressPercentage\n      progressSeconds\n      viewingComplete\n      firstViewDate\n      __typename\n    }\n    rating {\n      name\n      reason\n      description\n      __typename\n    }\n    children(paging: {number: $number, size: $size}) {\n      total\n      hasMore\n      items {\n        airDate\n        name\n        number\n        type\n        screenFormats\n        soundFormats\n        closedCaptions\n        productPagePath: productPage\n        studios\n        studioSubLabel\n        actors: credits(where: {type_contains: \"Actor\"}) {\n          name\n          __typename\n        }\n        directors: credits(where: {type_contains: \"Director\"}) {\n          name\n          __typename\n        }\n        screenwriter: credits(where: {type_contains: \"ScreenWriter\"}) {\n          name\n          __typename\n        }\n        description {\n          long\n          __typename\n        }\n        images {\n          boxArtSmall\n          boxArtVertical\n          stillFrameHome\n          __typename\n        }\n        lockerContext {\n          entitlementQuality\n          entitlementType\n          progressSeconds\n          progressPercentage\n          expirationDate\n          titleConcurrency {\n            canDownload\n            canStream\n            deviceUsage {\n              device {\n                deviceType\n                id\n                nickName\n                registeredDate\n                __typename\n              }\n              usage\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        productLevelProgress: progress {\n          progressPercentage\n          progressSeconds\n          viewingComplete\n          firstViewDate\n          __typename\n        }\n        orderablePricingPlan {\n          purchaseType\n          quality\n          price\n          basePrice\n          planId: id\n          __typename\n        }\n        titleDetails {\n          redboxTitleId\n          __typename\n        }\n        perksRedemptionPlans: titleDetails {\n          plans: perksRedemptionPlans {\n            purchaseType\n            quality\n            redemptionTypeId\n            __typename\n          }\n          __typename\n        }\n        children(paging: {number: $number, size: $size}) {\n          total\n          hasMore\n          items {\n            productGroupId\n            progress {\n              firstViewDate\n              progressPercentage\n              progressSeconds\n              viewingComplete\n              __typename\n            }\n            name\n            type\n            number\n            airDate\n            description {\n              long\n              __typename\n            }\n            images {\n              stillFrameHome\n              __typename\n            }\n            rating {\n              name\n              __typename\n            }\n            duration\n            lockerContext {\n              entitlementQuality\n              entitlementType\n              progressSeconds\n              progressPercentage\n              expirationDate\n              viewingComplete\n              titleConcurrency {\n                canDownload\n                canStream\n                deviceUsage {\n                  device {\n                    deviceType\n                    id\n                    nickName\n                    registeredDate\n                    __typename\n                  }\n                  usage\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            productLevelProgress: progress {\n              progressPercentage\n              progressSeconds\n              viewingComplete\n              firstViewDate\n              __typename\n            }\n            productPage\n            orderablePricingPlan {\n              purchaseType\n              quality\n              price\n              basePrice\n              planId: id\n              __typename\n            }\n            orderablePricingPlans: orderablePricingPlan {\n              purchaseType\n              quality\n              price\n              basePrice\n              id\n              __typename\n            }\n            titleDetails {\n              closedCaptions\n              mediumType\n              redboxTitleId\n              __typename\n            }\n            parent {\n              number\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    images {\n      boxArtSmall\n      boxArtLarge\n      boxArtVertical\n      stillFrameHome\n      stillHome\n      theatricalPoster\n      __typename\n    }\n    titleTypes: titleDetails {\n      mediumType\n      redboxTitleId\n      redboxReleaseDate\n      subtitles\n      sdhAvailable\n      comingSoon {\n        purchaseType\n        redboxReleaseDate\n        __typename\n      }\n      __typename\n    }\n    trailers\n    closedCaptions\n    studios\n    studioSubLabel\n    screenFormats\n    soundFormats\n    actors: credits(where: {type_contains: \"Actor\"}) {\n      name\n      __typename\n    }\n    directors: credits(where: {type_contains: \"Director\"}) {\n      name\n      __typename\n    }\n    screenwriter: credits(where: {type_contains: \"ScreenWriter\"}) {\n      name\n      __typename\n    }\n    lockerContext {\n      entitlementQuality\n      entitlementType\n      progressSeconds\n      progressPercentage\n      expirationDate\n      titleConcurrency {\n        canDownload\n        canStream\n        deviceUsage {\n          device {\n            deviceType\n            id\n            nickName\n            registeredDate\n            __typename\n          }\n          usage\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    orderablePricingPlan {\n      price\n      basePrice\n      purchaseType\n      quality\n      planId: id\n      __typename\n    }\n    redboxPlusAvailability: titleDetails {\n      date: redboxPlusAvailabilityDate\n      __typename\n    }\n    perksRedemptionPlans: titleDetails {\n      plans: perksRedemptionPlans {\n        purchaseType\n        quality\n        redemptionTypeId\n        __typename\n      }\n      __typename\n    }\n    canPurchasePhysical\n    __typename\n  }\n}\n"
	}

	xbmc.log(('GET DESCRIPTION'),level=log_level)
	reels = requests.post(apiUrl, json = infoparams)
	#xbmc.log('INFOPARAMS: ' + str(infoparams),level=log_level)
	xbmc.log('REELS: ' + str(len(reels.text)),level=log_level)
	#xbmc.log('REELS: ' + str(reels.text),level=log_level)
	data = json.loads(reels.text)
	title = data['data']['product']['name']
	desc = data['data']['product']['description']['long']
	rating = str(data['data']['product']['rating']['name'])
	duration = (data['data']['product']['duration']).lstrip('0')
	genres = data['data']['product']['genres']
	genre = ", ".join(genres)
	actors = data['data']['product']['actors'];a=[]
	for count, item in enumerate(data['data']['product']['actors']):
		actor = (item['name'])
		a.append(actor)
	actors = ", ".join(a)
	xbmc.log('ACTORS: ' + str(actors),level=log_level)
	details = '(' + genre + ') ' + desc + '\n\nCast: ' + actors + '\n\nRated: ' + rating + '\nRuntime: ' + duration
	xbmc.log('DETAILS: ' + str(details),level=log_level)
	xbmcgui.Dialog().textviewer(title, details)


#99
def PLAY(name,url):
	if 'mpd' in url:
		headers = 'User-Agent='+ ua + '&Licenserequesttoken=' + str(name)# + '&Cookie=Validation=e+HBE8/gj83BQnDwnbz9y0shsMYHhx3DHSNGw6mIzYI=; ASP.NET_SessionId=cbp5kvueinhw3jocgmjuu2xj; LBWeb=!VtiCCV4Bky2eO4uNChJyfjJ7LrO2KijYrwkqwTx/fqZ+dT/sSW634DwUCTwSx1VJvPzDcQHMxQrBFA==;'

		lic_url = f"https://www.redbox.com/gapi/ondemand/WidevineRightsManager.aspx"
		license_key = f"{lic_url}|{headers}&Content-Type=application/octet-stream|R{{SSM}}|"
		xbmc.log('LICENSE_KEY: ' +str(license_key),level=log_level)
		is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
		if not is_helper.check_inputstream():
			sys.exit()

		listitem = xbmcgui.ListItem(path=url)
		xbmc.log('### SETRESOLVEDURL ###',level=log_level)
		listitem.setProperty('IsPlayable', 'true')
		listitem.setProperty('inputstream', 'inputstream.adaptive')
		listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
		listitem.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={ua}")
		listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
		listitem.setProperty('inputstream.adaptive.license_key', license_key)
		listitem.setMimeType('application/dash+xml')
		listitem.setContentLookup(False)
		xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
		xbmc.log('URL: ' + str(url), level=log_level)
	else:

		listitem = xbmcgui.ListItem(path=url)
		xbmc.log('### SETRESOLVEDURL ###',level=log_level)
		listitem.setProperty('IsPlayable', 'true')
		xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
		xbmc.log('URL: ' + str(url), level=log_level)
	xbmcplugin.endOfDirectory(addon_handle)


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

def addDir2(name, url, mode, thumbnail, fanart, infoLabels=True):
	u = sys.argv[0] + "?url=" + urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name,})
	liz.setArt({'thumb':thumbnail,'fanart':fanart})
	if url != 'Future':
		liz.setProperty('IsPlayable', 'true')
	else:
		liz.setProperty('IsPlayable', 'false')
	if not fanart:
		fanart=defaultfanart
	liz.setProperty('fanart_image',fanart)
	ok = xbmcplugin.addDirectoryItem(addon_handle, url=u, listitem=liz, isFolder=True)
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
plotId = None

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
	plotId = urllib.parse.unquote_plus(params["plotId"])
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
	xbmc.log(("Get All"),level=log_level)
	cats()
elif mode == 3:
	xbmc.log(("Get All"),level=log_level)
	cats()
elif mode == 6:
	xbmc.log(("Get Channels"),level=log_level)
	channels(name,url)
elif mode == 9:
	xbmc.log(("Get VOD"),level=log_level)
	vod()
elif mode == 12:
	xbmc.log(("Get Movies"),level=log_level)
	movies(name,url)
elif mode == 15:
	xbmc.log(("Get Movie Info"),level=log_level)
	mymovie(name,url)
elif mode == 82:
	xbmc.log(("Get Movie Plot Info"),level=log_level)
	desc(plotId)
elif mode == 99:
	xbmc.log("Play Stream", level=log_level)
	PLAY(name,url)

xbmcplugin.endOfDirectory(addon_handle)
