# resources/lib/build_items.py
import xbmc
import xbmcaddon
import xbmcgui
import time
import calendar
from resources.lib.utils_fetch import *
from resources.lib.logger import log  # use custom logger
from resources.lib.convert_to_local import *
from resources.lib.refresh_addon_settings import sort_alpha  # global variable

ADDON = xbmcaddon.Addon()
GENRE_FILTER_PROP = "distro_epg_genre_filter"
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
USERDATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
THUMBS_PATH = os.path.join(USERDATA_PATH, "thumbs")


def _matches_language(channel_lang, selected_lang):
	"""Return True if selected_lang matches channel_lang.
	channel_lang may be a string or a list of strings."""
	if not selected_lang or selected_lang == "All":
		return True

	sel = selected_lang.strip().lower()

	if isinstance(channel_lang, (list, tuple)):
		for g in channel_lang:
			if not isinstance(g, str):
				continue
			if sel == g.strip().lower() or sel in g.strip().lower():
				return True
		return False

	# channel_lang is a string (or other)
	if isinstance(channel_lang, str):
		return sel == channel_lang.strip().lower() or sel in channel_lang.strip().lower()

	return False


def build_items(data, thumbs_map, desc_map, genre_map, epg_window, fav_ids=None):
	"""
	Build Kodi ListItem objects from EPG `data`.
	Optional fav_ids (list of string ids) will filter channels to only those IDs.
	"""
	# Read raw language setting (labelenum stores index as string)
	raw_filter_setting = ADDON.getSetting("filter_language")
	log(f"[BUILD ITEMS]Raw filter_language setting: {raw_filter_setting}", xbmc.LOGDEBUG)

	# Map index -> label if we got an index, otherwise accept the label directly
	lang_values = ["All", "English", "Spanish", "Asian", "African", "Middle Eastern"]
	filter_lang_display = "All"
	try:
		idx = int(raw_filter_setting)
		if 0 <= idx < len(lang_values):
			filter_lang_display = lang_values[idx]
	except Exception:
		if isinstance(raw_filter_setting, str) and raw_filter_setting.strip():
			filter_lang_display = raw_filter_setting.strip()

	log(f"[BUILD ITEMS]Resolved language filter: {filter_lang_display}", xbmc.LOGDEBUG)

	# Genre (session) filter from window property
	genre_filter = xbmcgui.Window(10025).getProperty(GENRE_FILTER_PROP)
	genre_filter = genre_filter.lower() if genre_filter else ""

	items = []
	epg = data.get("epg", {}) if isinstance(data, dict) else {}

	skipped = 0
	kept = 0

	# We iterate epg items; chan_items is list of (chan_id, channel_dict)
	chan_items = list(epg.items())

	# apply alphabetical sort at the channel level if enabled
	if sort_alpha:
		chan_items.sort(key=lambda kv: kv[1].get("title", "").lower())

	for idx, (chan_id, ch) in enumerate(chan_items, start=1):
		try:
			# --- FAVORITES FILTER (same style as genre/language) ---
			if fav_ids is not None:
				# fav_ids expected as strings (channel IDs)
				if str(chan_id) not in fav_ids and chan_id not in fav_ids:
					skipped += 1
					continue

			channel_name = ch.get("title", f"Channel {chan_id}")
			slots = ch.get("slots", [])

			# channel_lang pulled from genre_map (same as before)
			channel_lang = genre_map.get(int(chan_id), "") if genre_map else ""

			# LANGUAGE FILTER (robust)
			if filter_lang_display != "All":
				if not _matches_language(channel_lang, filter_lang_display):
					skipped += 1
					continue

			# GENRE FILTER (session) - normalize genres to lowercase string
			channel_lang_lower = ""
			if isinstance(channel_lang, (list, tuple)):
				channel_lang_lower = " ".join([str(x) for x in channel_lang]).lower()
			elif isinstance(channel_lang, str):
				channel_lang_lower = channel_lang.lower()

			if genre_filter and genre_filter not in channel_lang_lower:
				skipped += 1
				continue

			kept += 1

			now_title = slots[0].get("title", "No data") if slots else "No data"
			next_title = slots[1].get("title", "") if len(slots) > 1 else "No data"

			desc = slots[0].get("description", "") if slots else ""
			desc2 = slots[1].get("description", "") if len(slots) > 1 else ""

			if not desc:
				desc = desc_map.get(int(chan_id), "No description available.") if desc_map else "No description available."
			if not desc2:
				desc2 = desc_map.get(int(chan_id), "No description available.") if desc_map else "No description available."

			next_start_raw = slots[1].get("start", "") if len(slots) > 1 else ""
			next_start = convert_to_local(next_start_raw) if next_start_raw else ""
			next_end_raw = slots[1].get("end", "") if len(slots) > 1 else ""
			next_end = convert_to_local(next_end_raw) if next_start_raw else ""
			now_start = convert_to_local(slots[0].get("start", "")) if slots else ""
			now_end   = convert_to_local(slots[0].get("end", "")) if slots else ""

			now_desc = f"{desc}\n\n{now_start} - {now_end}"
			next_desc = f"{desc2}\n\n{next_start} - {next_end}"

			if next_start and next_title != "No data":
				next_label = f"{next_start} – {next_title}"
			else:
				next_label = "No upcoming program info"

			fallback_label = f"{channel_name} - Now: {now_title}"

			li = xbmcgui.ListItem(label=fallback_label)

			li.setProperty("channel", channel_name)
			li.setProperty("label", now_title)
			li.setProperty("label3", next_label)
			li.setProperty("label2", now_desc)
			li.setProperty("label4", next_desc)
			li.setProperty("label5", next_title)
			li.setProperty("next_start", next_start)
			li.setProperty("channel_id", str(chan_id))
			li.setProperty("channel_slug", str(chan_id))
			#log(f"[DistroTV EPG] Set slug={li.getProperty('channel_slug')} for {channel_name}", xbmc.LOGDEBUG)

			li.setArt({"bg": "special://home/addons/metalchris.distrotv.epg/resources/media/row_light.png"})
			li.setArt({"focus": "special://home/addons/metalchris.distrotv.epg/resources/media/focus_row.png"})

			if thumbs_map:
				# thumbs_map keys are ints in your code; use int() guard
				try:
					logo_url = thumbs_map.get(int(chan_id))
				except Exception:
					logo_url = thumbs_map.get(chan_id)
				if logo_url:
					li.setArt({"icon": os.path.join(THUMBS_PATH, f"{chan_id}.png")})
					li.setProperty("logo", logo_url)

			if idx % 2 == 0:
				li.setProperty("rowbg", "special://home/addons/metalchris.distrotv.epg/resources/media/row_light.png")
				parity = "EVEN"
			else:
				li.setProperty("rowbg", "special://home/addons/metalchris.distrotv.epg/resources/media/row_dark.png")
				parity = "ODD"
			li.setProperty("row_parity", parity)

			items.append(li)
		except Exception as e:
			log(f"[BUILD ITEMS]Error building item for chan_id {chan_id}: {e}", xbmc.LOGERROR)
			skipped += 1

	log(f"[BUILD ITEMS]Channels kept: {kept}, skipped: {skipped}, filter_lang={filter_lang_display}, filter_genre={genre_filter}", xbmc.LOGINFO)

	# --- Title ---
	if epg_window.getProperty("FAVORITES_FILTER"):
		title = f"DistroTV - Favorites ({kept} Channels)"
	elif genre_filter:
		title = f"DistroTV EPG - {genre_filter.capitalize()} ({kept} Channels)"
	else:
		title = "DistroTV EPG"

	log(f"[BUILD ITEMS] Window title set to: {title}", xbmc.LOGDEBUG)
	# Set the window property so the UI can use it
	epg_window.setProperty("EPG_TITLE", title)
	#log(f"[DistroTV Debug] Chan_items: {chan_items}", xbmc.LOGDEBUG)
	log(f"[BUILD ITEMS] chan_id: {chan_id}", xbmc.LOGDEBUG)
	#log(f"[DistroTV Debug] Channel data: {ch}", xbmc.LOGDEBUG)


	return items, kept, title
