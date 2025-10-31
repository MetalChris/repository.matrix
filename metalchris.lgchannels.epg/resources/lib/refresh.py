import xbmc
import xbmcaddon, os, json, xbmcvfs

from resources.lib.logger import log
from resources.lib.utils_fetch import fetch_all_episode_ids, fetch_epg, get_channel_thumbs, fetch_channel_descriptions, build_genre_map
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

					# Handle both old and new formats
					if "channels" in cached and isinstance(cached["channels"], list):
						epg_channels = cached["channels"]
					elif "data" in cached and "channels" in cached["data"]:
						epg_channels = cached["data"]["channels"]
					elif "data" in cached and "categories" in cached["data"]:
						# Most LG EPGs look like this
						epg_channels = []
						for cat in cached["data"]["categories"]:
							epg_channels.extend(cat.get("channels", []))
					else:
						epg_channels = []

					# Build a lookup dict by channel_number
					epg_dict = {str(ch.get("channel_number") or ch.get("channelNumber")): ch for ch in epg_channels if isinstance(ch, dict)}

					fav_ids = [str(cid) for cid in fav_ids]
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
			# Normal fetch
			#episode_ids = fetch_all_episode_ids()
			#if episode_ids:
			#epg_url = get_api(apiUrl)
			##data = os.path.join(profile, "cache", "epg.json")#fetch_epg(epg_url)
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
		genre_map = build_genre_map()
		log(f"[REFRESH] genre_map keys: {list(genre_map.keys())}", xbmc.LOGDEBUG)

		# --- Preserve filters before rebuild ---
		filter_lang = epg_window.getProperty("FILTER_LANGUAGE")

		# Try both local and global property names for genre
		filter_genre = epg_window.getProperty("FILTER_GENRE")
		if not filter_genre:
			win = xbmcgui.Window(10025)
			filter_genre = win.getProperty("lgchannels_epg_genre_filter")

		log(f"[REFRESH][refresh_epg_list] Active filters before build: lang={filter_lang}, genre={filter_genre}", xbmc.LOGDEBUG)


		log(f"[REFRESH][refresh_epg_list] Active filters before build: lang={filter_lang}, genre={filter_genre}", xbmc.LOGDEBUG)
		log(f"[REFRESH][refresh_epg_list] data keys: {list(data.keys()) if isinstance(data, dict) else type(data)}", xbmc.LOGDEBUG)

		# --- Normalize genre map and filter for consistent matching ---
		genre_map = {k.lower().strip(): v for k, v in genre_map.items()}
		filter_genre = filter_genre.lower().strip()
		epg_window.setProperty("FILTER_GENRE", filter_genre)

		log(f"[REFRESH][refresh_epg_list] Normalized genre filter: {filter_genre}", xbmc.LOGDEBUG)
		log(f"[REFRESH][refresh_epg_list] genre_map keys: {list(genre_map.keys())}", xbmc.LOGDEBUG)

		# --- Unwrap inner EPG data if needed ---
		if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
			data = data["data"]

		# --- Build Kodi list items ---
		new_items, kept, title = build_items(data, thumbs_map, genre_map, epg_window, fav_ids=fav_ids)


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
