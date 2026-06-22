import xbmc
import xbmcgui
import requests
from urllib.parse import urljoin

from resources.lib.uas import ua
from resources.lib.logger import *
#from resources.lib.playback_utils import *
#import inputstreamhelper

s = requests.Session()

def play_episode_isa(title, url, image, captions, addon_info, epg_window):
	log('[PLAYBACK] TITLE: ' + str(title),xbmc.LOGDEBUG)
	log('[PLAYBACK] IMAGE: ' + str(image),xbmc.LOGDEBUG)
	try:
		li = xbmcgui.ListItem(path=url, label=title)		
		li.setInfo("video", {"title": title, "plot": addon_info})
		li.setArt({
			"icon": image,
			"thumb": image,
			"poster": image,
			"fanart": image
		})
		#log('### SETRESOLVEDURL ###',xbmc.LOGDEBUG)
		if 'm3u8' in url:
			content_type = 'hls'
			log('CONTENT_TYPE: ' + str(content_type),xbmc.LOGDEBUG)
		else:
			content_type = 'mpd'
			log('CONTENT_TYPE: ' + str(content_type),xbmc.LOGDEBUG)
			
		response = requests.get(url, allow_redirects=True)
		play_url = response.url


		lic_url = 'https://widevine-dash.ezdrm.com/proxy?pX=5FE38E&CustomData=%7B%22host%22%3A%22valencia-app-mds.xumo.com%22%2C%22deviceId%22%3A%22d183f919-6f19-42e7-8a9b-356a79b48831%22%2C%22clientVersion%22%3A%222.17.0%22%2C%22providerId%22%3A2565%2C%22assetId%22%3A%22XM0YAF26UZNG6X%22%2C%22token%22%3A%225ad11c90-38e1-4441-8d95-bcfceb1219af%22%7D'

		referer = 'https://play.xumo.com/'

		license_key = lic_url + '|User-Agent=' + ua + '&Referer=' + referer +'/&Origin=' + referer + '&Content-Type= |R{SSM}|'
		#is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
		#if not is_helper.check_inputstream():
			#sys.exit()

		li.setProperty('IsPlayable', 'true')
		#li.setProperty('title', title)
		#if hls != 'false':
		if captions != '':
			li.setSubtitles([captions])
		try:
			li.setProperty('inputstream', 'inputstream.adaptive')
			li.setProperty('inputstream.adaptive.manifest_type', 'hls')
			#li.setProperty('inputstream.adaptive.manifest_type', content_type)
			#li.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={ua}")
			#li.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
			#li.setProperty('inputstream.adaptive.license_key', license_key)
			#li.setMimeType('application/dash+xml')
			li.setMimeType('application/vnd.apple.mpegurl')
		except Exception:
			pass


		log(f"[PLAYBACK] Playing with InputStream Adaptive: {title}", xbmc.LOGINFO)
		log("FINAL PLAYBACK URL: " + play_url, xbmc.LOGDEBUG)
		xbmc.Player().play(item=play_url, listitem=li)

	except Exception as e:
		log(f"[PLAYBACK] play_episode failed: {e}", xbmc.LOGERROR)


def get_variant(url):
	# your existing logic that produced:
	# https://.../manifest/.../0.m3u8
	
	from urllib.parse import urljoin
	import requests

	variant = "../../../manifest/3fec3e5cac39a52b2132f9c66c83dae043dc17d4/prod_default_xumo-ams-aws/726e37ea-fd94-4276-b0a0-c8be943cee44/0.m3u8"

	variant_url = urljoin(url, variant)

	r = requests.get(variant_url)

	log("VARIANT URL: " + variant_url, xbmc.LOGDEBUG)
	log("VARIANT STATUS: " + str(r.status_code), xbmc.LOGDEBUG)
	log("VARIANT HEADERS: " + str(r.headers), xbmc.LOGDEBUG)
	log("VARIANT TEXT: " + r.text[:300], xbmc.LOGDEBUG)
		
		
	r = requests.get(url, allow_redirects=True)
	
	for line in r.text.splitlines():
		if '.m3u8' in line:
			log(f"PLAYLIST_ENTRY: {line}", xbmc.LOGDEBUG)

	log(f"TEST STATUS: {r.status_code}", xbmc.LOGDEBUG)
	log(f"TEST URL: {r.url}", xbmc.LOGDEBUG)
	log(f"TEST HEADERS: {r.headers}", xbmc.LOGDEBUG)
	log(f"TEST TEXT: {r.text[:500]}", xbmc.LOGDEBUG)
	
	return resolved_variant_url
