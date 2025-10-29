import xbmc
import os, json, xbmcaddon, xbmcvfs, xbmcgui
from resources.lib.logger import log
from resources.lib.utils_fetch import get_channel_thumbs, build_genre_map
from resources.lib.build_items import build_items

ADDON = xbmcaddon.Addon()
USERDATA_PATH = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
EPG_JSON = os.path.join(USERDATA_PATH, "cache/epg.json")

def refresh_epg_list(epg_window):
	try:
		log(f"[REFRESH] refresh_epg_list called with FAVORITES_FILTER={epg_window.getProperty('FAVORITES_FILTER')}")

		# --- Get favorites filter ---
		fav_filter = epg_window.getProperty("FAVORITES_FILTER")
		fav_ids = [s.strip() for s in fav_filter.split(",") if s.strip()] if fav_filter else None
		log(f"[REFRESH] FAVORITES_FILTER='{fav_filter}' -> fav_ids={fav_ids}")

		data = {}
		os_path = xbmcvfs.translatePath(EPG_JSON)
		log(f"[REFRESH][DEBUG] EPG JSON path: {os_path}")
		# --- Load all EPG channels from disk if not cached ---
		if not hasattr(epg_window, "all_epg_channels"):
			if xbmcvfs.exists(os_path):
				try:
					with open(os_path, "r", encoding="utf-8") as fh:
						cached = json.load(fh)

					# CW Live stores channels under cached["data"]["channels"]
					all_channels = cached.get("data", {}).get("channels", [])

					# Ensure each channel has 'analytics_guid' as channel_id
					for ch in all_channels:
						ch["channel_id"] = ch.get("analytics_guid", "").strip()
						#log(f"[DEBUG] Loaded channel: title={ch.get('title')}, analytics_guid='{ch.get('analytics_guid')}'")

					epg_window.all_epg_channels = all_channels
					log(f"[REFRESH] Loaded {len(all_channels)} channels from disk", xbmc.LOGINFO)

				except Exception as e:
					log(f"[REFRESH] Failed reading EPG file: {e}", xbmc.LOGERROR)
					epg_window.all_epg_channels = []
			else:
				log(f"[REFRESH] EPG file does not exist: {os_path}", xbmc.LOGERROR)
				epg_window.all_epg_channels = []

		# --- Debug log for all channels ---
		log(f"[REFRESH] Total channels loaded: {len(epg_window.all_epg_channels)}")

		# --- Filter channels ---
		if fav_ids:
			win = xbmcgui.Window(10000)
			win.clearProperty("GENRE_FILTER_PROP")
			ADDON.setSetting("last_genre", "")

			fav_channels = [
				ch for ch in epg_window.all_epg_channels
				if ch.get("analytics_guid") in fav_ids
			]
			# Log missing favorites
			missing = [fid for fid in fav_ids if fid not in [c.get("analytics_guid") for c in fav_channels]]
			if missing:
				log(f"[REFRESH] Warning: these favorite IDs were not found in EPG: {missing}", xbmc.LOGWARNING)

			data["categories"] = [{"categoryName": "Favorites", "channels": fav_channels}]
			data["channel"] = {"item": fav_channels}
			log(f"[REFRESH] Loaded {len(fav_channels)} favorite channels", xbmc.LOGINFO)
			fav_guids = [ch.get("analytics_guid") for ch in fav_channels]
			log(f"[REFRESH] Favorite channel IDs: {fav_guids}", xbmc.LOGDEBUG)
		else:
			data["categories"] = [{"categoryName": "All Channels", "channels": epg_window.all_epg_channels}]
			data["channel"] = {"item": epg_window.all_epg_channels}
			log(f"[REFRESH] Loaded {len(epg_window.all_epg_channels)} channels for normal view", xbmc.LOGINFO)
			sample_guids = [ch.get("analytics_guid") for ch in epg_window.all_epg_channels[:10]]
			log(f"[REFRESH] Sample channel IDs: {sample_guids}", xbmc.LOGDEBUG)

		# --- Auxiliary data ---
		thumbs_map = get_channel_thumbs(data)
		genre_map = build_genre_map(data)

		# --- Preserve filters ---
		filter_lang = epg_window.getProperty("FILTER_LANGUAGE")
		filter_genre = epg_window.getProperty("FILTER_GENRE")
		log(f"[REFRESH] Active filters before build: lang={filter_lang}, genre={filter_genre}", xbmc.LOGDEBUG)

		log(f"[REFRESH][DEBUG] Before build_items: data keys = {list(data.keys())}", xbmc.LOGDEBUG)
		log(f"[REFRESH][DEBUG] Before build_items: data['channel'] keys = {list(data.get('channel', {}).keys())}", xbmc.LOGDEBUG)
		log(f"[REFRESH][DEBUG] Before build_items: channel count = {len(data.get('channel', {}).get('item') or [])}", xbmc.LOGDEBUG)

		# --- Build Kodi list items ---
		new_items, kept, title = build_items(data, thumbs_map, genre_map, epg_window, fav_ids=fav_ids)

		# --- Restore filters ---
		if filter_lang:
			epg_window.setProperty("FILTER_LANGUAGE", filter_lang)
		if filter_genre:
			epg_window.setProperty("FILTER_GENRE", filter_genre)

		# --- Update Kodi control ---
		ctrl = epg_window.getControl(9000)
		ctrl.reset()
		ctrl.addItems(new_items)
		epg_window.listitems = new_items

		# --- Update heading ---
		heading_ctrl = epg_window.getControl(1)
		if heading_ctrl:
			heading_ctrl.setLabel(title)

		log(f"[REFRESH][refresh_epg_list] EPG list refreshed ({kept} channels)", xbmc.LOGINFO)

	except Exception as e:
		log(f"[REFRESH][refresh_epg_list] Error refreshing list: {e}", xbmc.LOGERROR)
