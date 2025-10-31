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

ADDON = xbmcaddon.Addon()
GENRE_FILTER_PROP = "lgchannels_epg_genre_filter"
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
USERDATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
THUMBS_PATH = os.path.join(USERDATA_PATH, "thumbs")
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
def build_items(data, thumbs_map, genre_map, epg_window, fav_ids=None):

	with open(EPG_JSON, "r", encoding="utf-8") as f:
	    epg_data = json.load(f)

	bad_entries = 0

	for category in epg_data.get("categories", []):
	    for ch in category.get("channels", []):
	        chan_name = ch.get("channelName", "Unknown Channel")
	        for prog in ch.get("programs", []):
	            prog_title = prog.get("programTitle", "Unknown Program")

	            for key in ("startDateTime", "endDateTime"):
	                ts = prog.get(key, "")
	                if not ts:
	                    xbmc.log(f"[EPG] ⚠️ Missing {key} for '{prog_title}' on {chan_name}", xbmc.LOGWARNING)
	                    bad_entries += 1
	                    continue

	                try:
	                    # strict check for the expected UTC format
	                    time.strptime(ts.strip(), "%Y-%m-%dT%H:%M:%SZ")
	                except Exception as e:
	                    xbmc.log(f"[EPG] ❌ Malformed {key}: '{ts}' "
	                             f"in '{prog_title}' on {chan_name} ({e})", xbmc.LOGWARNING)
	                    bad_entries += 1

	xbmc.log(f"[EPG] Timestamp validation complete. Found {bad_entries} bad entries.", xbmc.LOGDEBUG)

	"""
	Build Kodi ListItem objects from EPG `data`.
	Optional fav_ids (list of string ids) will filter channels to only those IDs.
	"""

	genre_filter = xbmcgui.Window(10025).getProperty(GENRE_FILTER_PROP)
	genre_filter = genre_filter.lower() if genre_filter else ""

	skipped = 0
	kept = 0

	items = []
	#epg_window.clearProperty("FAVORITES_FILTER")

	for category in data['categories']:
		genres = category['categoryName']
		for count, item in enumerate(category['channels']):
			#title = str(item['channelNumber']) + ' ' + item['channelName']
			title = str(item['channelName'])
			#genres = str(item['channelGenreName'])

			# Initialize variables
			onNow = onNext = now_desc = next_desc = nowstartTime = nextstartTime = nowendTime = nextendTime = ''
			preview = ''
			desc = ''

			# Find first two programs that have not ended
			now_program = None
			next_program = None
			for prog in item['programs']:
				if not has_program_ended(prog['endDateTime']):
					if now_program is None:
						now_program = prog
					elif next_program is None:
						next_program = prog
						break  # found both

			# Fallback if less than two programs available
			now_program = now_program or {'programTitle': '', 'description': '', 'startDateTime': '', 'endDateTime': '', 'imageUrl': ''}
			next_program = next_program or {'programTitle': '', 'description': '', 'startDateTime': '', 'endDateTime': '', 'imageUrl': ''}

			# Assign variables
			onNow = now_program['programTitle']
			now_desc = now_program['description']
			nowstartTime = now_program['startDateTime']
			nowendTime = now_program['endDateTime']

			onNext = next_program['programTitle']
			next_desc = next_program['description']
			nextstartTime = next_program['startDateTime']
			nextendTime = next_program['endDateTime']

			preview = now_program['imageUrl']
			desc = now_program['programTitle']
			nowstart = format_epg_time(nowstartTime)
			nowend = format_epg_time(nowendTime)
			nextstart = format_epg_time(nextstartTime)
			nextend = format_epg_time(nextendTime)
			url  = item['mediaStaticUrl'].split('&')[0]
			logo = item['channelLogoUrl']

			if genre_filter and genre_filter not in genres.lower():
				#log(f"[BUILD ITEMS]Skipping chan_id {chan_id} ('{channel_name}') due to genre filter ({genre_filter}) — channel_lang={channel_lang}", xbmc.LOGDEBUG)
				skipped += 1
				continue

			kept += 1

			li = xbmcgui.ListItem(label=title)

			li.setProperty("channel", str(item['channelName']))
			li.setProperty("label", onNow)
			li.setProperty("label3", str(nextstart) + ' - ' + onNext)
			li.setProperty("label2", now_desc)
			li.setProperty("label4", next_desc)
			li.setProperty("label5", onNext)
			li.setProperty("now_start", str(nowstart))
			li.setProperty("now_end", str(nowend))
			li.setProperty("next_start", str(nextstart))
			li.setProperty("next_end", str(nextend))
			li.setProperty("channel_id", str(item['channelNumber']))
			li.setProperty("channel_slug", str(item['channelNumber']))
			li.setProperty('url', url)
			li.setProperty('IsPlayable', 'true')
			li.setProperty("desc", "desc")
			#li.setArt({"icon": logo})
			#li.setInfo("video", {"title": title, "plot": now_desc})
			li.setArt({"icon": THUMBS_PATH + '/' + str(item['channelNumber']) + '.png'})
			li.setArt({"preview": preview})
			li.setArt({"bg": "special://home/addons/metalchris.lgchannels.epg/resources/media/row_light.png"})
			li.setArt({"focus": "special://home/addons/metalchris.lgchannels.epg/resources/media/focus_row.png"})

			#log(f"[BUILD ITEMS] Adding item: {li.getProperty('channel')}", xbmc.LOGDEBUG)
			items.append(li)
			#log(f"[BUILD ITEMS] ListItem: {li(1)}", xbmc.LOGDEBUG)
	log(f"[BUILD ITEMS] GENRE: {genre_filter}", xbmc.LOGINFO)
	if SORT_ALPHA:
		items.sort(key=lambda li: li.getProperty('channel').lower())
	log(f"[BUILD ITEMS] SORT_ALPHA: {SORT_ALPHA}", xbmc.LOGINFO)

	log(f"[BUILD ITEMS] EPG built with: {kept} channels", xbmc.LOGINFO)
	#log(f"[BUILD ITEMS]Channels kept: {kept}, skipped: {skipped}, filter_lang={filter_lang_display}, filter_genre={genre_filter}", xbmc.LOGDEBUG)
	#log(f"[BUILD ITEMS] URL: {url}", xbmc.LOGDEBUG)

	# --- Title ---
	if epg_window.getProperty("FAVORITES_FILTER"):
		title = f"LG Channels - Favorites ({kept} Channels)"
	elif genre_filter:
		title = f"LG Channels EPG - {genre_filter.capitalize()} ({kept} Channels)"
	else:
		#title = "LG Channels EPG"
		title = "LG Channels EPG"

	log(f"[BUILD ITEMS] Window title set to: {title}", xbmc.LOGINFO)
	# Set the window property so the UI can use it
	epg_window.setProperty("EPG_TITLE", title)

	#return items, kept, title
	return items, kept, title
