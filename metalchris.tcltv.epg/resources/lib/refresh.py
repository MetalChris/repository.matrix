import xbmc
import xbmcaddon, os, json, xbmcvfs

from resources.lib.logger import log
from resources.lib.utils_fetch import fetch_all_episode_ids, fetch_epg, get_channel_thumbs, fetch_channel_descriptions, build_category_map
from resources.lib.build_items import build_items
from resources.lib.refresh_addon_settings import sort_alpha
from resources.lib.get_items import *

profile = xbmcaddon.Addon().getAddonInfo("profile")
epg_path = os.path.join(profile, "cache", "epg.json")
os_path = xbmcvfs.translatePath(epg_path)


def refresh_epg_list(epg_window):
	try:
		log(f"[REFRESH][refresh_epg_list] called with FAVORITES_FILTER={epg_window.getProperty('FAVORITES_FILTER')}")

		# --- Load EPG data ---
		fav_filter = epg_window.getProperty("FAVORITES_FILTER")
		fav_ids = [s.strip() for s in fav_filter.split(",") if s.strip()] if fav_filter else None

		data = {}
		if fav_ids:
			# --- Load cached epg.json ---
			if xbmcvfs.exists(epg_path):
				log(f"[REFRESH][refresh_epg_list] epg_path exists", xbmc.LOGDEBUG)
				try:
					with open(os_path, "r", encoding="utf-8") as fh:
						cached = json.load(fh)

					# --- Normalize cached EPG into flat channel list ---
					epg_channels = []

					if "channels" in cached and isinstance(cached["channels"], list):
						epg_channels = cached["channels"]

					elif "data" in cached:

						# Case 1: data is already a flat list of categories (TCL format)
						if isinstance(cached["data"], list):
							for cat in cached["data"]:
								if isinstance(cat, dict):
									epg_channels.extend(cat.get("channels", []))

						# Case 2: data is a dict wrapper
						elif isinstance(cached["data"], dict):

							if "channels" in cached["data"]:
								epg_channels = cached["data"]["channels"]

							elif "categories" in cached["data"]:
								for cat in cached["data"]["categories"]:
									if isinstance(cat, dict):
										epg_channels.extend(cat.get("channels", []))

					else:
						epg_channels = []

					# Build a lookup dict by channel_number
					epg_dict = {str(ch.get("id")): ch for ch in epg_channels if isinstance(ch, dict) and ch.get("id")}
					
					xbmc.log(f"[FAV DEBUG] sample epg keys: {list(epg_dict.keys())[:10]}", xbmc.LOGINFO)
					xbmc.log(f"[FAV DEBUG] fav_ids: {fav_ids}", xbmc.LOGINFO)

					fav_ids = [str(cid) for cid in fav_ids]
					xbmc.log(f"[FAV DEBUG] epg_dict sample keys: {list(epg_dict.keys())[:10]}", xbmc.LOGINFO)
					xbmc.log(f"[FAV DEBUG] fav_ids: {fav_ids}", xbmc.LOGINFO)
					xbmc.log(f"[FAV DEBUG] MATCH COUNT: {len([cid for cid in fav_ids if cid in epg_dict])}", xbmc.LOGINFO)
					favorite_channels = [epg_dict[cid] for cid in fav_ids if cid in epg_dict]

					# ✅ Unwrapped, consistent structure for build_items()
					data = {
						"categories": [
							{
								"categoryCode": "FAV",
								"categoryName": "Favorites",
								"channels": favorite_channels
							}
						]
					}
					

					log(f"[REFRESH][refresh_epg_list] Loaded {len(favorite_channels)} favorite channels", xbmc.LOGINFO)

				except Exception as e:
					log(f"[REFRESH][refresh_epg_list] Failed reading cached epg.json: {e}", xbmc.LOGERROR)
					data = {"categories": []}

		else:
			# --- Load full cached EPG when not filtering favorites ---
			if xbmcvfs.exists(epg_path):
				try:
					with open(os_path, "r", encoding="utf-8") as fh:
						data = json.load(fh)
				except Exception as e:
					log(f"[REFRESH][refresh_epg_list] Failed reading cached epg.json: {e}", xbmc.LOGERROR)
					data = {}
			else:
				log(f"[REFRESH][refresh_epg_list] No cached epg.json found", xbmc.LOGERROR)
				data = {}

		# --- Auxiliary data ---
		thumbs_map = get_channel_thumbs()
		#desc_map = fetch_channel_descriptions(data)
		category_map = build_category_map()
		log(f"[REFRESH] category_map keys: {list(category_map.keys())}", xbmc.LOGDEBUG)

		# --- Preserve filters before rebuild ---
		filter_lang = epg_window.getProperty("FILTER_LANGUAGE")

		# Try both local and global property names for genre
		filter_genre = epg_window.getProperty("FILTER_GENRE")
		if not filter_genre:
			win = xbmcgui.Window(10025)
			filter_genre = win.getProperty("tcltv_epg_genre_filter")
			

		log(f"[REFRESH][refresh_epg_list] Active filters before build: lang={filter_lang}, genre={filter_genre}", xbmc.LOGDEBUG)
		log(f"[REFRESH][refresh_epg_list] data keys: {list(data.keys()) if isinstance(data, dict) else type(data)}", xbmc.LOGDEBUG)

		# --- Normalize genre map and filter for consistent matching ---
		category_map = {k.lower().strip(): v for k, v in category_map.items()}
		filter_genre = filter_genre.lower().strip()
		epg_window.setProperty("FILTER_GENRE", filter_genre)

		log(f"[REFRESH][refresh_epg_list] Normalized genre filter: {filter_genre}", xbmc.LOGDEBUG)
		log(f"[REFRESH][refresh_epg_list] category_map keys: {list(category_map.keys())}", xbmc.LOGDEBUG)

		# --- Normalize TCL EPG structure ONCE ---
		if isinstance(data, dict) and "data" in data:
			data = data["data"]

		# TCL format: data["data"] is already list of categories
		if isinstance(data, list):
			categories = data
		else:
			categories = data.get("categories", [])

		# Normalize into LG-style structure
		data = {"categories": categories}

		# Ensure channelNumber exists (safe + consistent)
		for cat in data.get("categories", []):
			if not isinstance(cat, dict):
				continue
			for ch in cat.get("channels", []):
				if isinstance(ch, dict):
					ch["channelNumber"] = str(ch.get("id"))

		data = {"categories": categories}
				
		log(f"[REFRESH] data type: {type(data)} | sample: {str(data)[:200]}", xbmc.LOGDEBUG)
		for i, c in enumerate(data.get("categories", [])[:10]):  # limit output
			log(f"[DEBUG CAT {i}] type={type(c)} keys={list(c.keys()) if isinstance(c, dict) else 'NOT A DICT'}", xbmc.LOGDEBUG)
			
		# FORCE canonical structure
		if isinstance(data, dict):
			data = data.get("categories") or data.get("data") or data

		if isinstance(data, dict):
			data = data.get("categories", [])

		if not isinstance(data, list):
			xbmc.log(f"[REFRESH] BAD FINAL DATA TYPE: {type(data)}", xbmc.LOGERROR)
			data = []
			
		xbmc.log("[STATE] refresh epg window id = %s" % id(epg_window), xbmc.LOGINFO)

		# --- Build Kodi list items ---
		new_items, kept, title = build_items(data, thumbs_map, category_map, epg_window, fav_ids=fav_ids)


				# --- Restore filters after rebuild ---
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
