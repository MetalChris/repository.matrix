import xbmc
import xbmcgui
from resources.lib.logger import log

def play_episode(ep, epg_window=None):
	"""
	Play a video stream directly without using InputStream Adaptive.
	"""
	try:
		title = ep.get("episode_title") or ep.get("title") or "Unknown"
		desc  = ep.get("episode_description") or ep.get("description") or ""
		url   = ep.get("content", {}).get("url")
		image = ep.get("img_thumbh")

		if not url:
			xbmcgui.Dialog().notification(
				"DistroTV EPG",
				"No stream URL",
				xbmcgui.NOTIFICATION_ERROR,
				3000,
				sound=False
			)
			return

		# Create ListItem
		li = xbmcgui.ListItem(label=title)
		if image:
			li.setArt({'icon': image, 'thumb': image})
		li.setInfo("video", {"title": title, "plot": desc})
		li.setProperty("IsPlayable", "true")

		# Close the EPG window if one was passed
		#if epg_window:
			#try:
				#epg_window.close()
			#except Exception:
				#pass
		title = epg_window.getControl(1).getLabel()
		if title:
			epg_window.setProperty("EPG_TITLE", title)
			xbmc.executebuiltin(f'SetProperty(EPG_TITLE,"{title}",home)')
			log(f"[PLAYBACK] Window Title: {title}", xbmc.LOGDEBUG)

		list_control = epg_window.getControl(9000)
		index = list_control.getSelectedPosition()
		li = list_control.getSelectedItem()
		if li:
			slug = li.getProperty("channel_slug")
			epg_window.setProperty("LAST_SELECTED_SLUG", slug)
			epg_window.setProperty("LAST_SELECTED_INDEX", str(index))
			log(f"[PLAYBACK] Last Selected Channel: {index} ({slug})", xbmc.LOGDEBUG)

		xbmc.log(f"[PLAYBACK] Playing directly: {title} ({url})", xbmc.LOGINFO)
		xbmc.Player().play(item=url, listitem=li)

	except Exception as e:
		xbmc.log(f"[PLAYBACK] play_episode failed: {e}", xbmc.LOGERROR)
