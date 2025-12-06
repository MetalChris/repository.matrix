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
GENRE_FILTER_PROP = "xumoplay_epg_genre_filter"
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
USERDATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
THUMBS_PATH = "special://profile/addon_data/metal.xumoplay.epg/thumbs"#os.path.join(USERDATA_PATH, "thumbs")
apiUrl = 'https://valencia-app-mds.xumo.com/v2/'
SORT_ALPHA = ADDON.getSettingBool("sort_alpha")
#START_FAVORITES = ADDON.getSettingBool("start_favorites")
PRE_EPG = os.path.join(USERDATA_PATH,"cache/desc_map_programs_logo.json")
map_all_programs_path = os.path.join(CACHE_DIR, "map_all_programs.json")

favorites_filter = ['592', '558', '578', '2118', '2110']

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


#def build_items(data, thumbs_map, genre_map, epg_window, fav_ids=None):
def build_items(data, thumbs_map, desc_map, program_map, genre_map, epg_window, fav_ids=None):
	"""
	Build Kodi ListItem objects from EPG `data`.
	Optional fav_ids (list of string ids) will filter channels to only those IDs.
	"""

	genre_filter = xbmcgui.Window(10025).getProperty(GENRE_FILTER_PROP)
	genre_filter = genre_filter.lower() if genre_filter else ""

	skipped = 0
	kept = 0

	items = []

	try:
	    if xbmcvfs.exists(map_all_programs_path):
	        with open(map_all_programs_path, "r", encoding="utf-8") as f:
	            program_map = json.load(f)
	    else:
	        program_map = {}
	except Exception as e:
	    log(f"[LOAD] Failed to load {map_all_programs_path}: {e}", xbmc.LOGERROR)
	    program_map = {}

	channels = data.get("channel", [])
	log(f"[BUILD_ITEMS] data length: {len(channels)}", xbmc.LOGINFO)
	log(f"[BUILD_ITEMS] Channels type: {type(channels)}", xbmc.LOGINFO)
	if isinstance(channels, dict):
		channels = channels.values()

	for count, item in enumerate(data['channel']['item']):
		chan_id = str(item['number'])
		log(f"[BUILD_ITEMS] Channel: {chan_id}", xbmc.LOGDEBUG)
		genres = (item.get('genre', []))[-1]
		genres = str(genres['value'])
		slug = str(item['guid']['value'])
		if slug == '99991334' or slug == '99991282':
			continue
		#description = item['description']
		channel_info = desc_map.get(chan_id)
		channelId = chan_id
		program_info = program_map.get(channelId) or {}

		if channel_info:

			if not (channel_info["title"]):
				log(f"[BUILD ITEMS] No Channel Title: {channelId}", xbmc.LOGDEBUG)
				continue
			title = (channel_info["title"])
			contentType = 'Channel'
			image = (channel_info["logo"])
			info = (channel_info["chan_desc"])
			if not program_info:
				log(f"[BUILD ITEMS] No Program Info: {channelId}", xbmc.LOGDEBUG)
				continue
			onNow = (program_info["title"])
			now_desc = (program_info["descriptions"])
			onNext = (program_info["title2"])
			next_desc = (program_info["descriptions2"])

			""" Time Formatting """
			#(format_unix_time_kodi(ts))

			nowstart = format_unix_time_kodi(int(program_info["start"]))
			nowend = format_unix_time_kodi(int(program_info["end"]))
			nowtimes = nowstart + ' - ' + nowend
			nextstart = format_unix_time_kodi(int(program_info["start2"]))
			nextend = format_unix_time_kodi(int(program_info["end2"]))
			nexttimes = nextstart + ' - ' + nextend

			slug = (channel_info["slug"])
			url = apiUrl + 'channels/channel/' + str(slug) + '/broadcast.json?hour=3'
			logo = f"special://userdata/addon_data/{ADDON.getAddonInfo('id')}/thumbs/{chan_id}.webp"

			if genre_filter and genre_filter not in genres.lower():
				#log(f"[BUILD ITEMS]Skipping chan_id {chan_id} ('{channel_name}') due to genre filter ({genre_filter}) — channel_lang={channel_lang}", xbmc.LOGDEBUG)
				skipped += 1
				continue

			kept += 1

			li = xbmcgui.ListItem(label=title)

			li.setProperty("channel", title)
			li.setProperty("label", str(onNow))
			li.setProperty("label3", str(nextstart + ' - ' + onNext))
			li.setProperty("label2", str(now_desc))
			li.setProperty("nowtimes", str(nowtimes))
			li.setProperty("label4", str(next_desc))
			li.setProperty("nexttimes", str(nexttimes))
			li.setProperty("label5", str(onNext))
			li.setProperty("next_start", "")
			li.setProperty("channel_id", (channel_info["chan_id"]))
			li.setProperty('url', url)
			li.setProperty('IsPlayable', 'true')
			li.setArt({"icon": logo})
			li.setArt({"bg": "special://home/addons/metalchris.xumoplay.epg/resources/media/row_light.png"})
			li.setArt({"focus": "special://home/addons/metalchris.xumoplay.epg/resources/media/focus_row.png"})
			items.append(li)

	if SORT_ALPHA:
		items.sort(key=lambda li: li.getProperty('channel').lower())
	log(f"[BUILD ITEMS] SORT_ALPHA: {SORT_ALPHA}", xbmc.LOGINFO)

	# --- Title ---
	if epg_window.getProperty("FAVORITES_FILTER"):
		title = f"XumoPlay - Favorites ({kept} Channels)"
	elif genre_filter:
		title = f"XumoPlay EPG - {genre_filter.capitalize()} ({kept} Channels)"
	else:
		title = "XumoPlay EPG"

	log(f"[BUILD ITEMS] Window title set to: {title}", xbmc.LOGINFO)
	# Set the window property so the UI can use it
	epg_window.setProperty("EPG_TITLE", title)

	return items, kept, title
