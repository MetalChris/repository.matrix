import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, re, os
import json
import time
from time import strftime, localtime
import requests
import concurrent.futures

from resources.lib.logger import *
from resources.lib.uas import *
from resources.lib.playback_hls import play_episode_hls
from resources.lib.playback_isa import play_episode_isa
from resources.lib.uas import ua
from resources.lib.safe_play import *

log(f"[GET_ITEMS] User-Agent: {(ua)}", xbmc.LOGDEBUG)

#addon_handle = int(sys.argv[1])
#xbmcplugin.setContent(addon_handle, 'video')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id='metalchris.cwlive.epg')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
settings = xbmcaddon.Addon(id="metalchris.cwlive.epg")
local_string = xbmcaddon.Addon(id='metalchris.cwlive.epg').getLocalizedString
defaultimage = 'special://home/addons/metalchris.cwlive.epg/resources/media/icon.png'


apiUrl = 'https://data.cwtv.com/feed/app-2/landing/epg/page_1/pagesize_75/device_web/apiversion_24/cacheversion_202510142100'

# Local cache paths
ADDON_ID = "metalchris.cwlive.epg"
PROFILE_PATH = xbmcvfs.translatePath(f"special://profile/addon_data/{ADDON_ID}/")
CACHE_DIR = os.path.join(PROFILE_PATH, "cache")
THUMBS_DIR = os.path.join(PROFILE_PATH, "thumbs")
map_all_programs_path = os.path.join(CACHE_DIR, "map_all_programs.json")

__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

s = requests.Session()

def fetch_channel_program(chan):
    chan_id = str(chan['number'])
    slug = chan['guid']['value']
    title = str(chan['title'])

    url = f"{apiUrl}channels/channel/{slug}/onnowandnext.json?f=asset.title&f=asset.descriptions"

    # check if cached per-channel? Optional
    # if os.path.exists(os.path.join(CACHE_DIR, f"{chan_id}.json")):
    #     return chan_id, json.load(open(os.path.join(CACHE_DIR, f"{chan_id}.json")))

    try:
        response = s.get(url, headers={"User-Agent": ua}, timeout=10)
        if response.status_code != 200:
            return chan_id, None

        data = response.json()
        results = data.get("results", [])
        if not results:
            return chan_id, None

        first = results[0]
        title1 = first.get("title", "")
        episodeTitle1 = first.get("episodeTitle", "")
        desc1 = first.get("descriptions", "No description available")
        if isinstance(desc1, dict):
            desc1 = max(desc1.values(), key=len, default="No description available")
        start1 = str(first.get("start", ""))[:-3]
        end1 = str(first.get("end", ""))[:-3]

        title2 = ""
        episodeTitle2 = ""
        desc2 = ""
        start2 = ""
        end2 = ""
        if len(results) > 1:
            second = results[1]
            title2 = second.get("title", "")
            episodeTitle2 = second.get("episodeTitle", "")
            desc2 = second.get("descriptions", "No description available")
            if isinstance(desc2, dict):
                desc2 = max(desc2.values(), key=len, default="No description available")
            start2 = str(second.get("start", ""))[:-3]
            end2 = str(second.get("end", ""))[:-3]

        return chan_id, {
            "title": title1,
            "episodeTitle": episodeTitle1,
            "descriptions": desc1,
            "start": start1,
            "end": end1,
            "channelId": chan_id,
            "title2": title2,
            "episodeTitle2": episodeTitle2,
            "descriptions2": desc2,
            "start2": start2,
            "end2": end2
        }

    except Exception as e:
        log(f"[GET_ITEMS] Error fetching channel {chan_id}: {e}", xbmc.LOGERROR)
        return chan_id, None


def fetch_all_programs(data):
    #if os.path.exists(map_all_programs_path):
        #log(f"[GET_ITEMS] Cached programs_map exists", xbmc.LOGDEBUG)
        #return

    channels = data.get("channel", {}).get("item", [])
    map_all_programs = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_chan = {executor.submit(fetch_channel_program, chan): chan for chan in channels}
        for future in concurrent.futures.as_completed(future_to_chan):
            chan_id, result = future.result()
            if result:
                map_all_programs[chan_id] = result

    try:
        with open(map_all_programs_path, "w", encoding="utf-8") as f:
            json.dump(map_all_programs, f, indent=2, ensure_ascii=False)
        log(f"[GET_ITEMS] Saved {len(map_all_programs)} channels", xbmc.LOGDEBUG)
    except Exception as e:
        log(f"[GET_ITEMS] Error saving JSON: {e}", xbmc.LOGERROR)



def get_stream(title, stream, image, captions, epg_window=None):
	captions = None
	log('[GET_ITEMS] LIVE URL: ' + str(stream),xbmc.LOGINFO)
	#channel = url.split('/')[-2]
	if 'Local Now' in title:
		log(('##### LOCAL NOW #####'),xbmc.LOGINFO)
		local_now(title, stream, image, captions, epg_window)
	response = s.get(stream, headers = {'User-Agent': ua})
	log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGDEBUG)
	log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGDEBUG)
	#log('RESPONSE: ' + str(response.text),xbmc.LOGDEBUG)
	data = json.loads(response.text)
	if 'ssaiStreamUrl' in data:
		log(('### SSAI URL FOUND ###.'),xbmc.LOGINFO)
		stream = data['ssaiStreamUrl']
		captions = ''
		if epg_window:
		    epg_window.close()
		play_episode_isa(title, stream, image, captions, epg_window)
	else:
		assetId = data['assets'][0]['id']
		streamUrl = apiUrl + 'assets/asset/' + assetId + '.json?f=providers&f=connectorId&f=keywords'
		log('LIVE API URL: ' + str(streamUrl),xbmc.LOGINFO)
		response = s.get(streamUrl, headers = {'User-Agent': ua})
		log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGDEBUG)
		log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGDEBUG)
		#log('RESPONSE: ' + str(response.text),xbmc.LOGDEBUG)
		data = json.loads(response.text)
		name = data['providers'][0]['title']
		stream = data['providers'][0]['sources'][0]['uri']# + '&ads.xumo_channelId=' + channel
		if 'hasEmbeddedCaptions' in data['providers'][0]['sources'][0]:
			log(('***** CAPTIONS *****'),xbmc.LOGINFO)
			#log('CAPTIONS LENGTH: ' + str(len(data['providers'][0]['captions'])),xbmc.LOGDEBUG)
		#log('CAPTIONS?: ' + str(data['providers'][0]['sources'][0]['hasEmbeddedCaptions']),xbmc.LOGDEBUG)
			if data['providers'][0]['sources'][0]['hasEmbeddedCaptions'] == True:
				if 'captions' in data['providers'][0]:
					captions = data['providers'][0]['captions'][1]['url']
					log(('##### CAPTIONS #####'),xbmc.LOGINFO)
		else:
			captions = ''
		#url = stream.partition('&')[0]
		#log('### URL: ' + str(url),xbmc.LOGDEBUG)
		if epg_window:
		    epg_window.close()
		play_episode_isa(title, stream, image, captions, epg_window)

def local_now(title, stream, image, captions, epg_window):
	log(('##### LOCAL NOW #####'),level=xbmc.LOGINFO)
	response = s.get('http://checkip.dyndns.com/', headers = {'User-Agent': ua})
	log('RESPONSE CODE: ' + str(response.status_code),level=xbmc.LOGDEBUG)
	ipAddress = re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(response.text).group(1)
	log('IP: ' + str(ipAddress),level=xbmc.LOGDEBUG)
	zipUrl = 'https://ipinfo.io/' + ipAddress + '/json'
	response = s.get(zipUrl, headers = {'User-Agent': ua})
	log('RESPONSE: ' + str(response.text),level=xbmc.LOGDEBUG)
	data = json.loads(response.text)
	zipCode = data['postal']
	log('ZIPCODE: ' + str(zipCode),level=xbmc.LOGDEBUG)
	response = s.get(stream, headers = {'User-Agent': ua})
	log('RESPONSE CODE: ' + str(response.status_code),level=xbmc.LOGDEBUG)
	jsob = (str(response.text))
	data = json.loads(jsob)
	assetId = data['assets'][0]['id']
	streamUrl = apiUrl + 'assets/asset/' + assetId + '.json?f=providers&f=connectorId&f=keywords'
	response = s.get(streamUrl, headers = {'User-Agent': ua})
	log('RESPONSE CODE: ' + str(response.status_code),level=xbmc.LOGDEBUG)
	log('RESPONSE LENGTH: ' + str(len(response.text)),level=xbmc.LOGDEBUG)
	#log('RESPONSE: ' + str(response.text),level=xbmc.LOGDEBUG)
	data = json.loads(response.text)
	title = data['providers'][0]['title']
	stream = data['providers'][0]['sources'][0]['uri']
	if 'hasEmbeddedCaptions' in data['providers'][0]['sources'][0]:
		log(('***** CAPTIONS *****'),level=xbmc.LOGINFO)
		#log('CAPTIONS LENGTH: ' + str(len(data['providers'][0]['captions'])),level=xbmc.LOGDEBUG)
	#log('CAPTIONS?: ' + str(data['providers'][0]['sources'][0]['hasEmbeddedCaptions']),level=xbmc.LOGDEBUG)
		if data['providers'][0]['sources'][0]['hasEmbeddedCaptions'] == True:
			if 'captions' in data['providers'][0]:
				captions = data['providers'][0]['captions'][1]['url']
				log(('##### CAPTIONS #####'),level=xbmc.LOGINFO)
	else:
		captions = ''
	url = stream.replace('30101', zipCode)
	log('NOT STREAM: ' + str(url),level=xbmc.LOGINFO)
	response = s.get(url, headers = {'User-Agent': ua})
	log('RESPONSE CODE: ' + str(response.status_code),level=xbmc.LOGDEBUG)
	log('RESPONSE LENGTH: ' + str(len(response.text)),level=xbmc.LOGDEBUG)
	log('RESPONSE: ' + str(response.text),level=xbmc.LOGDEBUG)
	stream = response.text[1:-1] + '|User-Agent=' + ua
	log(('##### LOCAL NOW #####'),xbmc.LOGINFO)
	safe_playback(title, stream, image, captions, epg_window)
