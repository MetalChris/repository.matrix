import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, re, os
import json
import time
from time import strftime, localtime
import requests

from resources.lib.logger import *
from resources.lib.uas import *
from resources.lib.playback_hls import play_episode_hls
from resources.lib.playback_isa import play_episode_isa

#addon_handle = int(sys.argv[1])
#xbmcplugin.setContent(addon_handle, 'video')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id='metalchris.localnow.epg')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
settings = xbmcaddon.Addon(id="metalchris.localnow.epg")
baseUrl = 'https://localnow.com/'
TylerUrl = 'https://data-store-trans-cdn.api.cms.amdvids.com/live/epg/US/website?program_size=3&dma=623&market=txTyler'
plugin = "Local Now"
local_string = xbmcaddon.Addon(id='metalchris.localnow.epg').getLocalizedString
defaultimage = 'special://home/addons/metalchris.localnow.epg/resources/media/icon.png'

__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

s = requests.Session()


def get_buildid():
	log(('GET BUILD_ID'),xbmc.LOGINFO)
	response = s.get(baseUrl)
	log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGINFO)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob)
	BUILD_ID = data['buildId']
	log('BUILD_ID: ' + str(BUILD_ID),xbmc.LOGINFO)
	return(BUILD_ID)


def get_token():
	log(('GET TOKEN'),xbmc.LOGINFO)
	response = s.get(baseUrl)
	log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGINFO)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob)
	DSP_TOKEN = data['runtimeConfig']['DSP_TOKEN']
	LN_API_KEY = data['runtimeConfig']['LN_API_KEY']
	BUILD_ID = data['buildId']
	log('BUILD_ID: ' + str(BUILD_ID),xbmc.LOGINFO)
	token = str(re.compile('token":"(.+?)"').findall(DSP_TOKEN)[0])
	return(token)


def get_ln(baseUrl):
	log(('GET LOCATION'),xbmc.LOGINFO)
	response = s.get(baseUrl)
	log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGINFO)
	jsob = re.compile('application/json">(.+?)</script>').findall(response.text)[0]
	data = json.loads(jsob)
	LN_API_KEY = data['runtimeConfig']['LN_API_KEY']
	log('LN_API_KEY: ' + str(LN_API_KEY),xbmc.LOGINFO)
	lnUrl = data['props']['pageProps']['config']['localNow']['geography']['cityEndpointUrl']
	log('LNURL: ' + str(lnUrl),xbmc.LOGINFO)
	headers = {'User-Agent': ua, 'X-Api-Key': str(LN_API_KEY)}
	response = s.get(lnUrl, headers=headers)
	log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGINFO)
	data = json.loads(response.text)
	market = data['city']['market']
	#market = 'txTyler'# data['city']['market']
	log('MARKET: ' + str(market),xbmc.LOGINFO)
	pbsMarkets = data['city']['pbsMarkets']
	zipDma = data['city']['zipDma']
	#zipDma = '623'# data['city']['zipDma']
	url = 'https://data-store-trans-cdn.api.cms.amdvids.com/live/epg/US/website?program_size=3&dma=' + str(zipDma) + '&market=' + str(market)# + ',' + str(pbsMarkets)
	log('CHANNELS URL: ' + str(url),xbmc.LOGINFO)
	return(url)


def channels(TylerUrl):
	response = s.get(TylerUrl, headers = {'User-Agent': ua})
	log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGINFO)
	log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGINFO)
	data = json.loads(response.text)
	return(data)


def get_stream(title, image, url, epg_window):
	log(('GET STREAM'),xbmc.LOGINFO)
	token = get_token()
	log('TOKEN: ' + str(token),xbmc.LOGINFO)
	headers = {'User-Agent': ua, 'X-Access-Token': str(token)}
	response = s.get(url, headers=headers)
	log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGINFO)
	jsob = (str(response.text))
	data = json.loads(jsob)
	stream = data['video_m3u8']
	log('STREAM: ' + str(stream[:150]),xbmc.LOGINFO)
	#return(name, stream)
	use_isa = ADDON.getSettingBool("use_isa")
	xbmc.log(f"[GET_ITEMS] Playing {title} from {stream[:150]}", xbmc.LOGINFO)
	xbmc.log(f"[GET_ITEMS] Image for video {image}", xbmc.LOGINFO)
	if use_isa:
		play_episode_isa(title, stream, image, epg_window)
	else:
		play_episode_hls(title, stream, image, epg_window)


	log(f"[GET_ITEMS] Playback Using {'InputStream Adaptive' if use_isa else 'native HLS (FFmpeg)'}", xbmc.LOGINFO)
