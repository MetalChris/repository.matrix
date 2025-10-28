import xbmc
import xbmcgui

from resources.lib.uas import ua
from resources.lib.logger import log


def play_episode_isa(title, stream, image, captions, epg_window):
	try:
		#title = ep.get("episode_title") or ep.get("title") or "Unknown"
		#desc  = ep.get("episode_description") or ep.get("description") or ""
		#url   = ep.get("content", {}).get("url")
		#image = ep.get("img_thumbh")

		if not stream:
			xbmcgui.Dialog().notification("DistroTV EPG", "No stream URL", xbmcgui.NOTIFICATION_ERROR, 3000, sound=False)
			return

		li = xbmcgui.ListItem(label=title)
		if image:
			li.setArt({'icon': image, 'thumb': image})
		li.setInfo("video", {"title": title})
		li.setProperty("IsPlayable", "true")

		# InputStream properties
		try:
			li.setProperty("inputstream", "inputstream.adaptive")
			li.setProperty("inputstream.adaptive.manifest_type", "hls")
			li.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={ua}")
			li.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={ua}")
			li.setMimeType('application/vnd.apple.mpegurl')
		except Exception:
			pass

		# Close the EPG window if one was passed
		#try:
			#if epg_window:
				#epg_window.close()
		#except Exception:
			#pass


		xbmc.log(f"[PLAYBACK] Playing with InputStream Adaptive: {title} ({stream})", xbmc.LOGINFO)
		xbmc.Player().play(item=stream, listitem=li)

	except Exception as e:
		xbmc.log(f"[PLAYBACK] play_episode failed: {e}", xbmc.LOGERROR)
