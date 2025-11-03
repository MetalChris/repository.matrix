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

			stream = li.getProperty("url")
			title = li.getProperty("label")
			image = li.getArt("icon")
			xbmc.log(f"[ACTIONS] Image for video {image}", xbmc.LOGINFO)

			# --- Save current EPG state on the window (existing approach) ---
			title_ctrl = epg_window.getControl(1)
			if title_ctrl:
				current_title = title_ctrl.getLabel()
				epg_window.setProperty("EPG_TITLE", current_title)
				log(f"[ACTIONS] Window Title: {current_title}", xbmc.LOGDEBUG)

			# Save selected channel index and slug
			list_ctrl = epg_window.getControl(9000)
			if list_ctrl:
				sel_idx = list_ctrl.getSelectedPosition()
				epg_window.setProperty("LAST_SELECTED_INDEX", str(sel_idx))
				# try to save slug from the selected ListItem
				li = list_ctrl.getListItem(sel_idx) if sel_idx is not None and sel_idx >= 0 else None
				if li:
					slug = li.getProperty("channel_slug") or li.getProperty("channel_id") or ""
					epg_window.setProperty("LAST_SELECTED_SLUG", slug)
					log(f"[ACTIONS] Last Selected Channel: {slug} (index {sel_idx})", xbmc.LOGDEBUG)

			# --- ALSO save title/index to Kodi global properties so they persist across playback ---
			# Quote the title to avoid breaking the builtin call when title contains quotes
			_safe_title = current_title.replace('"', '\\"') if title_ctrl else ""
			if _safe_title:
				xbmc.executebuiltin('SetProperty(EPG_TITLE,"{}" ,home)'.format(_safe_title))

			# Save index and slug globally as well (home window scope)
			if list_ctrl:
				try:
					xbmc.executebuiltin('SetProperty(LAST_SELECTED_INDEX,{},home)'.format(sel_idx if sel_idx is not None else -1))
				except Exception:
					pass
				if li and slug:
					xbmc.executebuiltin('SetProperty(LAST_SELECTED_SLUG,"{}" ,home)'.format(slug.replace('"','\\"')))



			get_stream(title, image, stream, epg_window)

		except Exception as exc:
			xbmc.log(f"[ACTIONS] Error handling OK action: {exc}", xbmc.LOGERROR)
