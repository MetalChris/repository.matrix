import xbmc
import xbmcgui
import xbmcaddon
from resources.lib.utils_fetch import fetch_by_chanid
from resources.lib.playback_hls import play_episode_hls
from resources.lib.playback_isa import play_episode_isa
from resources.lib.logger import *
from resources.lib.get_items import *

ADDON = xbmcaddon.Addon()

def handle_action(epg_window, action):
	"""
	Handle actions (back, context menu, enter/play) for the EPG window.
	"""
	action_id = action.getId()

	# Close on back/escape
	if action_id in (9, 10, 92, 216):
		epg_window.close()
		return

	# Context menu
	if action_id == xbmcgui.ACTION_CONTEXT_MENU:
		epg_window.show_context_menu()
		return

	# OK / Enter -> playback
	if action_id in (7, 100):
		try:
			ctrl = epg_window.getControl(9000)
			if ctrl is None:
				xbmc.log("[ACTIONS] getControl(9000) returned None", xbmc.LOGERROR)
				return

			pos = ctrl.getSelectedPosition()
			if pos is None or pos < 0:
				xbmc.log("[ACTIONS] No list item selected", xbmc.LOGWARNING)
				return

			li = ctrl.getListItem(pos)
			if li is None:
				xbmc.log(f"[ACTIONS] getListItem returned None for pos {pos}", xbmc.LOGWARNING)
				return

			url = li.getProperty("url")
			title = li.getProperty("label")
			description = li.getProperty("desc")
			image = li.getArt("preview")
			xbmc.log(f"[ACTIONS] Image for video {image}", xbmc.LOGINFO)
			if url:
				use_isa = ADDON.getSettingBool("use_isa")
				xbmc.log(f"[ACTIONS] Playing {title} from {url}", xbmc.LOGINFO)
				if use_isa:
					play_episode_isa(title, url, image, epg_window)
				else:
					play_episode_hls(title, url, image, epg_window)


				log(f"[ACTIONS] Playback Using {'InputStream Adaptive' if use_isa else 'native HLS (FFmpeg)'}", xbmc.LOGINFO)

		except Exception as exc:
			xbmc.log(f"[ACTIONS] Error handling OK action: {exc}", xbmc.LOGERROR)
