import xbmc
import xbmcgui
import requests

from resources.lib.uas import ua
from resources.lib.logger import *
#import inputstreamhelper

s = requests.Session()

def play_episode_isa(title, url, image, captions, epg_window):
	log('[PLAYBACK] TITLE: ' + str(title),xbmc.LOGDEBUG)
	log('[PLAYBACK] IMAGE: ' + str(image),xbmc.LOGDEBUG)
	try:
		li = xbmcgui.ListItem(path=url, label=title)
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


		lic_url = 'https://widevine-dash.ezdrm.com/proxy?pX=5FE38E&CustomData=%7B%22host%22%3A%22valencia-app-mds.xumo.com%22%2C%22deviceId%22%3A%22d183f919-6f19-42e7-8a9b-356a79b48831%22%2C%22clientVersion%22%3A%222.17.0%22%2C%22providerId%22%3A2565%2C%22assetId%22%3A%22XM0YAF26UZNG6X%22%2C%22token%22%3A%225ad11c90-38e1-4441-8d95-bcfceb1219af%22%7D'

		response = s.post(lic_url)
		log('LIC_RESPONSE CODE: ' + str(response.status_code),xbmc.LOGDEBUG)
		log('LIC_RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGDEBUG)
		log('LIC_RESPONSE HEADERS: ' + str(response.headers),xbmc.LOGDEBUG)
		log('LIC_RESPONSE: ' + str(response.text),xbmc.LOGDEBUG)
		headers = response.headers

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
			li.setProperty('inputstream.adaptive.manifest_type', content_type)
			li.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={ua}")
			li.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
			li.setProperty('inputstream.adaptive.license_key', license_key)
			li.setMimeType('application/dash+xml')
			li.setContentLookup(False)
			#log('### SETRESOLVEDURL ###',xbmc.LOGDEBUG)
			#li.setProperty('IsPlayable', 'true')
			#xbmcplugin.setResolvedUrl(addon_handle, True, li)
			log('URL: ' + str(url), xbmc.LOGDEBUG)
		except Exception:
			pass

		# Close the EPG window if one was passed
		#try:
			#if epg_window:
				#epg_window.close()
				#xbmc.sleep(300)
		#except Exception:
			#pass

		log(f"[PLAYBACK] Playing with InputStream Adaptive: {title} ({url})", xbmc.LOGINFO)
		xbmc.Player().play(item=url, listitem=li)

	except Exception as e:
		log(f"[PLAYBACK] play_episode failed: {e}", xbmc.LOGERROR)
