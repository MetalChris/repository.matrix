# resources/lib/build_items.py
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
import time
from time import strftime, localtime
import calendar
import sys
from resources.lib.utils_fetch import *
from resources.lib.logger import log  # use custom logger
from resources.lib.convert_to_local import *
from resources.lib.refresh_addon_settings import sort_alpha  # global variable
from resources.lib.get_items import *

ADDON = xbmcaddon.Addon()
GENRE_FILTER_PROP = "cwlive_epg_genre_filter"
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
USERDATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
THUMBS_PATH = "special://profile/addon_data/metalchris.cwlive.epg/thumbs"#os.path.join(USERDATA_PATH, "thumbs")
apiUrl = 'https://data.cwtv.com/feed/app-2/landing/epg/page_1/pagesize_75/device_web/apiversion_24/cacheversion_202510142100'
SORT_ALPHA = ADDON.getSettingBool("sort_alpha")
#START_FAVORITES = ADDON.getSettingBool("start_favorites")
PRE_EPG = os.path.join(USERDATA_PATH,"cache/desc_map_programs_logo.json")
map_all_programs_path = os.path.join(CACHE_DIR, "map_all_programs.json")

EPG = os.path.join(USERDATA_PATH,"cache/epg.json")

#favorites_filter = ['592', '558', '578', '2118', '2110']

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


#def build_items(data, thumbs_map, genre_map, program_map, epg_window, fav_ids=None):
def build_items(data, thumbs_map, genre_map, epg_window, fav_ids=None):
	log(f"[BUILD ITEMS] Received {len(data.get('categories', [{}])[0].get('channels', []))} channels for building items", xbmc.LOGDEBUG)
	log(f"[BUILD ITEMS] Received {fav_ids} channels for building items", xbmc.LOGDEBUG)
	log(f"[BUILD ITEMS] Received {type(fav_ids)} channels for building items", xbmc.LOGDEBUG)
	log(f"[BUILD ITEMS][DEBUG] GENRE_FILTER_PROP before filtering: {epg_window.getProperty('GENRE_FILTER_PROP')}", xbmc.LOGDEBUG)

	"""
	Build Kodi ListItem objects from EPG `data`.
	Optional fav_ids (list of string ids) will filter channels to only those IDs.
	"""

	genre_filter = epg_window.getProperty(GENRE_FILTER_PROP)
	genre_filter = genre_filter.lower() if genre_filter else ""
	log(f"[BUILD ITEMS] genre_filter (initial): {genre_filter}")

	# --- If building Favorites, ignore genre filtering entirely ---
	if fav_ids:
		log("[BUILD ITEMS] Favorites mode detected — skipping genre filtering", xbmc.LOGINFO)
		genre_filter = ""  # Prevent filtering later


	skipped = 0
	kept = 0
	items = []

	# Load program map
	try:
		if xbmcvfs.exists(map_all_programs_path):
			with open(map_all_programs_path, "r", encoding="utf-8") as f:
				program_map = json.load(f)
		else:
			program_map = {}
	except Exception as e:
		log(f"[LOAD] Failed to load {map_all_programs_path}: {e}", xbmc.LOGERROR)
		program_map = {}

	# Load EPG data
	try:
		if xbmcvfs.exists(EPG):
			with open(EPG, "r", encoding="utf-8") as f:
				data = json.load(f)
		else:
			data = {}
	except Exception as e:
		log(f"[LOAD] Failed to load {PRE_EPG}: {e}", xbmc.LOGERROR)
		data = {}

	now = int(time.time())  # current Unix timestamp (UTC)

	# --- Filter channels upfront ---
	channels = data.get("data", {}).get("channels", [])

	# Apply favorites filter
	if fav_ids:
		epg_window.clearProperty("GENRE_FILTER_PROP")
		channels = [ch for ch in channels if ch.get("analytics_guid") in fav_ids]

	# Apply genre filter
	if genre_filter:
		filtered_channels = []
		for ch in channels:
			ch_genres = [g.strip().lower() for g in (ch.get("genre") or "").split(",")]
			if genre_filter in ch_genres:
				filtered_channels.append(ch)
			else:
				skipped += 1
		channels = filtered_channels

	log(f"[BUILD ITEMS] Channels after filtering: {len(channels)}")

	# --- Build Kodi ListItems ---
	for channel in channels:
		programs = channel.get("programs", [])
		current_program = None
		next_program = None
		ch_title = channel.get("title", "")
		ch_desc = channel.get("description", "")
		ch_thumb = channel.get("thumbnail_url", "")
		ch_stream = channel.get("stream_url", "")
		ch_guid = channel.get("analytics_guid", "")
		ch_genre = channel.get("genre", "")

		# Sort programs by start time
		programs.sort(key=lambda x: x.get("program_start_ts", 0))

		for p in programs:
			start = int(p.get("program_start_ts", 0))
			end = int(p.get("program_end_ts", 0))

			if start <= now < end:
				current_program = p
			elif start > now and not next_program:
				next_program = p

			if current_program and next_program:
				break

		title_now       = current_program.get("title", "") if current_program else ""
		subtitle_now    = current_program.get("subtitle", "") if current_program else ""
		desc_now        = current_program.get("description", "") if current_program else ""
		start_now       = current_program.get("program_start_ts", 0) if current_program else 0
		end_now         = current_program.get("program_end_ts", 0) if current_program else 0

		title_next      = next_program.get("title", "") if next_program else ""
		subtitle_next   = next_program.get("subtitle", "") if next_program else ""
		desc_next       = next_program.get("description", "") if next_program else ""
		start_next      = next_program.get("program_start_ts", 0) if next_program else 0
		end_next        = next_program.get("program_end_ts", 0) if next_program else 0

		nowstart = format_unix_time_kodi(int(start_now))
		nowend = format_unix_time_kodi(int(end_now))
		nowtimes = nowstart + ' - ' + nowend
		nextstart = format_unix_time_kodi(int(start_next))
		nextend = format_unix_time_kodi(int(end_next))
		nexttimes = nextstart + ' - ' + nextend

		kept += 1

		li = xbmcgui.ListItem(label=ch_title)
		li.setProperty("channel", ch_title)
		li.setProperty("label", title_now)
		li.setProperty("label3", nextstart + ' - ' + title_next)
		li.setProperty("label2", desc_now)
		li.setProperty("nowtimes", nowtimes)
		li.setProperty("label4", desc_next)
		li.setProperty("nexttimes", nexttimes)
		li.setProperty("label5", desc_next)
		li.setProperty("FAVORITE_GUID", ch_guid)
		li.setProperty("channel_id", ch_guid)
		li.setProperty('url', ch_stream)
		li.setProperty('IsPlayable', 'true')
		li.setArt({"icon": THUMBS_PATH + '/' + ch_guid + '.jpg'})
		li.setArt({"bg": "special://home/addons/metalchris.cwlive.epg/resources/media/row_light.png"})
		li.setArt({"focus": "special://home/addons/metalchris.cwlive.epg/resources/media/focus_row.png"})
		items.append(li)

	if SORT_ALPHA:
		items.sort(key=lambda li: li.getProperty('channel').lower())
	log(f"[BUILD ITEMS] SORT_ALPHA: {SORT_ALPHA}", xbmc.LOGINFO)

	# --- Title ---
	if epg_window.getProperty("FAVORITES_FILTER"):
		title = f"CW Live - Favorites ({kept} Channels)"
	elif genre_filter:
		title = f"CW Live EPG - {genre_filter.capitalize()} ({kept} Channels)"
	else:
		title = "CW Live EPG"

	log(f"[BUILD ITEMS] Window title set to: {title}", xbmc.LOGINFO)
	log(f"[BUILD ITEMS] Kept channels: {kept}", xbmc.LOGINFO)

	return items, kept, title
