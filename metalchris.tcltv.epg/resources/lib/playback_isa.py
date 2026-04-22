import xbmc
import xbmcgui

from resources.lib.uas import ua
from resources.lib.logger import *
#from resources.lib.playback_utils import *


def play_episode_isa(title, url, image, epg_window=None):
	
	epg_title = epg_window.getControl(1).getLabel()
	if epg_title:
		epg_window.setProperty("EPG_TITLE", epg_title)
		xbmc.executebuiltin(f'SetProperty(EPG_TITLE,"{epg_title}",home)')
		log(f"[PLAYBACK_ISA] Window Title: {epg_title}", xbmc.LOGINFO)

	list_control = epg_window.getControl(9000)
	index = list_control.getSelectedPosition()
	li = list_control.getSelectedItem()
	if li:
		slug = li.getProperty("channel_slug")
		epg_window.setProperty("LAST_SELECTED_SLUG", slug)
		epg_window.setProperty("LAST_SELECTED_INDEX", str(index))
		log(f"[PLAYBACK_ISA] Last Selected Channel: {index} ({slug})", xbmc.LOGINFO)
	
	try:

		if not url:
			xbmcgui.Dialog().notification("TCLTV+ EPG", "No stream URL", xbmcgui.NOTIFICATION_ERROR, 3000, sound=False)
			return
			
		channel_name = li.getProperty("channel")	
			
		li = xbmcgui.ListItem(label=channel_name)
		li.setArt({'icon': image, 'thumb': image})
		li.setInfo("video", {"title": channel_name})
		li.setProperty("IsPlayable", "true")

		# InputStream properties
		try:
			li.setProperty("inputstream", "inputstream.adaptive")
			li.setProperty("inputstream.adaptive.manifest_type", "hls")
			li.setMimeType('application/vnd.apple.mpegurl')
			#li.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={ua}")
			#li.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={ua}")
		except Exception:
			pass
			
			


		xbmc.log(f"[PLAYBACK] Playing with InputStream Adaptive: {title} ({url})", xbmc.LOGINFO)
		xbmc.Player().play(item=url, listitem=li)

	except Exception as e:
		xbmc.log(f"[PLAYBACK] play_episode failed: {e}", xbmc.LOGERROR)
