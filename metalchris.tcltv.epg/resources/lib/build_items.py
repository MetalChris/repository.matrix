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
#from resources.lib.favorites import list_favorites

addon = xbmcaddon.Addon()
GENRE_FILTER_PROP = "tcltv_epg_genre_filter"
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
MEDIA_PATH = os.path.join(ADDON_PATH, "resources", "media")
USERDATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
THUMBS_PATH = os.path.join(USERDATA_PATH, "thumbs")
ICON   = os.path.join(MEDIA_PATH, "icon.png")
#addon_handle = int(sys.argv[1])
SORT_ALPHA = ADDON.getSettingBool("sort_alpha")
#START_FAVORITES = ADDON.getSettingBool("start_favorites")
EPG_JSON = os.path.join(PROFILE_PATH, "cache", "epg.json")
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


#def build_items(data, thumbs_map, genre_map, epg_window, fav_ids=None):
def build_items(data, thumbs_map, category_map, epg_window, fav_ids=None):
	xbmc.log(f"[build_items] fav_ids = {fav_ids}", xbmc.LOGDEBUG)

	xbmc.log(f"[build_items] TYPE = {type(data)} SAMPLE = {str(data)[:200]}", xbmc.LOGDEBUG)

	# --- Normalize incoming data shape ---
	if isinstance(data, str):
		try:
			data = json.loads(data)
		except Exception:
			xbmc.log("[build_items] data was string but not JSON", xbmc.LOGERROR)
			return [], 0, ""

	if isinstance(data, dict):
		data = data.get("categories") or data.get("data") or data

	if not isinstance(data, list):
		xbmc.log(f"[build_items] Unsupported data type: {type(data)}", xbmc.LOGERROR)
		return [], 0, ""

	categories = data  # <- SINGLE SOURCE OF TRUTH

	bad_entries = 0
	channel_ids = set()

	epg_window.clearProperty("FAVORITES_FILTER")
	
	genre_filter = xbmcgui.Window(10025).getProperty(GENRE_FILTER_PROP)
	genre_filter = genre_filter.lower() if genre_filter else ""
	
	skipped = 0
	kept = 0

	items = []
	sources = []

	# --- MAIN LOOP (FIXED) ---
	for category in categories:

		if not isinstance(category, dict):
			continue

		cat_name = category.get("category", "")
		channels = category.get("channels", [])

		for ch in channels:
			channel_id = ch.get("id")
			if ADDON.getSettingBool("favorites_mode"):
				if channel_id not in fav_ids:
					continue
			title = ch.get("name")
			image = ch.get("logo_color")
			chan_desc = ch.get("description")
			
			source = ch.get("source")
			if not source in sources:
				sources.append(source)

			if not channel_id:
				continue

			if channel_id in channel_ids:
				continue

			channel_ids.add(channel_id)
				
			#log(f"[DEBUG] channelNumber={item.get('channel')} id={channel.get('id')}", xbmc.LOGERROR)
			
			# Initialize variables
			onNow = onNext = now_desc = next_desc = nowstartTime = nextstartTime = nowendTime = nextendTime = ''
			preview = ''
			desc = ''

			# Find first two programs that have not ended
			now_program = None
			next_program = None
			for prog in ch['programs']:
				if not has_program_ended(prog['end']):
					if now_program is None:
						now_program = prog
					elif next_program is None:
						next_program = prog
						break  # found both

			# Fallback if less than two programs available
			now_program = now_program or {'title': '', 'title': '', 'start': '', 'end': '', 'imageUrl': '', 'id': ''}
			next_program = next_program or {'title': '', 'title': '', 'start': '', 'end': '', 'imageUrl': '', 'id': ''}

			# Assign variables
			onNow = now_program['title']
			#now_desc = now_program['title']
			nowstartTime = now_program['start']
			nowendTime = now_program['end']
			now_id = now_program['id']

			onNext = next_program['title']
			#next_desc = next_program['title']
			nextstartTime = next_program['start']
			nextendTime = next_program['end']
			next_id = next_program['id']

			#preview = now_program['imageUrl']
			desc = now_program['title']
			nowstart = format_epg_time(nowstartTime)
			nowend = format_epg_time(nowendTime)
			nextstart = format_epg_time(nextstartTime)
			nextend = format_epg_time(nextendTime)
			url  = ch['media']#.split('&')[0]
			logo = 'https://tcl-channel-cdn.ideonow.com' + ch['logo_color']

			cat_name = category.get("category", "").lower()

			if genre_filter and genre_filter not in cat_name:
				#log(f"[BUILD ITEMS]Skipping chan_id {chan_id} ('{channel_name}') due to genre filter ({genre_filter}) — channel_lang={channel_lang}", xbmc.LOGDEBUG)
				skipped += 1
				continue

			kept += 1

			li = xbmcgui.ListItem(label=title)

			li.setProperty("channel", str(ch['name']))
			li.setProperty("label", onNow)
			li.setProperty("label3", onNext)
			li.setProperty("label2", now_desc)
			li.setProperty("label4", str(nextstart) + ' - ' + str(nextend))
			li.setProperty("label5", onNext)
			li.setProperty("now_start", str(nowstart))
			li.setProperty("now_end", 'Ends at ' + str(nowend))
			li.setProperty("nowendTime", str(nowendTime))
			li.setProperty("next_start", str(nextstart))
			li.setProperty("next_end", str(nextend))
			li.setProperty("channel_id", str(ch['id']))
			li.setProperty("channel_slug", str(ch['id']))
			li.setProperty("chan_desc", str(chan_desc))
			li.setProperty('url', url)
			li.setProperty('IsPlayable', 'true')
			li.setProperty("desc", "desc")
			li.setProperty("now_id", now_id)
			li.setProperty("next_id", next_id)
			#li.setArt({"icon": logo})
			#li.setInfo("video", {"title": title, "plot": now_desc})
			li.setArt({"icon": THUMBS_PATH + '/' + str(ch['id']) + '.png'})
			li.setArt({"preview": logo})
			li.setArt({"bg": "special://home/addons/metalchris.tcltv.epg/resources/media/row_light.png"})
			li.setArt({"focus": "special://home/addons/metalchris.tcltv.epg/resources/media/focus_row.png"})

			#log(f"[BUILD ITEMS] Adding item: {li.getProperty('channel')}", xbmc.LOGDEBUG)
			items.append(li)
			#log(f"[BUILD ITEMS] NOW DESC ID: {now_id}&ids={next_id}", xbmc.LOGDEBUG)
	log(f"[BUILD ITEMS] GENRE: {genre_filter}", xbmc.LOGINFO)
	log(f"[BUILD ITEMS] SOURCES: {sources}", xbmc.LOGDEBUG)
	if SORT_ALPHA:
		items.sort(key=lambda li: (li.getProperty('channel') or '').lower().removeprefix('the '))
	log(f"[BUILD ITEMS] SORT_ALPHA: {SORT_ALPHA}", xbmc.LOGINFO)

	log(f"[BUILD ITEMS] EPG built with: {kept} channels", xbmc.LOGINFO)
	#log(f"[BUILD ITEMS]Channels kept: {kept}, skipped: {skipped}, filter_lang={filter_lang_display}, filter_genre={genre_filter}", xbmc.LOGDEBUG)
	#log(f"[BUILD ITEMS] URL: {url}", xbmc.LOGDEBUG)

	# --- Title ---
	in_favorites = ADDON.getSettingBool("favorites_mode")
	log(f"[BUILD ITEMS] in_favorites: {in_favorites}", xbmc.LOGINFO)
	#if epg_window.getProperty("FAVORITES_FILTER"):
	if in_favorites:
		title = f"TCLTV+ EPG - Favorites ({kept} Channels)"
	elif genre_filter:
		title = f"TCLTV+ EPG - {genre_filter.capitalize()} ({kept} Channels)"
	else:
		title = "TCLTV+ EPG"

	log(f"[BUILD ITEMS] Window title set to: {title}", xbmc.LOGINFO)
	log(f"[BUILD ITEMS] Channels: {len(channel_ids)}", xbmc.LOGINFO)
	# Set the window property so the UI can use it
	epg_window.setProperty("EPG_TITLE", title)

	return items, kept, title
