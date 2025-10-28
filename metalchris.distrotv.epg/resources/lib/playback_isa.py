import xbmc
import xbmcgui

from resources.lib.uas import ua
from resources.lib.logger import log


def play_episode_isa(ep, epg_window=None):
	try:
		title = ep.get("episode_title") or ep.get("title") or "Unknown"
		desc  = ep.get("episode_description") or ep.get("description") or ""
		url   = ep.get("content", {}).get("url")
		image = ep.get("img_thumbh")

		if not url:
			xbmcgui.Dialog().notification("DistroTV EPG", "No stream URL", xbmcgui.NOTIFICATION_ERROR, 3000, sound=False)
			return

		li = xbmcgui.ListItem(label=title)
		if image:
			li.setArt({'icon': image, 'thumb': image})
		li.setInfo("video", {"title": title, "plot": desc})
		li.setProperty("IsPlayable", "true")

		# InputStream properties
		try:
			li.setProperty("inputstream", "inputstream.adaptive")
			li.setProperty("inputstream.adaptive.manifest_type", "hls")
			li.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={ua}")
			li.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={ua}")
		except Exception:
			pass

		# Close the EPG window if one was passed
		#try:
			#if epg_window:
				#epg_window.close()
		#except Exception:
			#pass
		title = epg_window.getControl(1).getLabel()
		if title:
			epg_window.setProperty("EPG_TITLE", title)
			xbmc.executebuiltin(f'SetProperty(EPG_TITLE,"{title}",home)')
			log(f"[PLAYBACK_ISA] Window Title: {title}", xbmc.LOGDEBUG)

		list_control = epg_window.getControl(9000)
		index = list_control.getSelectedPosition()
		li = list_control.getSelectedItem()
		if li:
			slug = li.getProperty("channel_slug")
			epg_window.setProperty("LAST_SELECTED_SLUG", slug)
			epg_window.setProperty("LAST_SELECTED_INDEX", str(index))
			log(f"[PLAYBACK_ISA] Last Selected Channel: {index} ({slug})", xbmc.LOGDEBUG)

		xbmc.log(f"[PLAYBACK] Playing with InputStream Adaptive: {title} ({url})", xbmc.LOGINFO)
		xbmc.Player().play(item=url, listitem=li)

	except Exception as e:
		xbmc.log(f"[PLAYBACK] play_episode failed: {e}", xbmc.LOGERROR)
