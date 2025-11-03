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
GENRE_FILTER_PROP = "localnow_epg_genre_filter"
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
USERDATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
THUMBS_PATH = os.path.join(USERDATA_PATH, "thumbs")
#addon_handle = int(sys.argv[1])
SORT_ALPHA = ADDON.getSettingBool("sort_alpha")
#START_FAVORITES = ADDON.getSettingBool("start_favorites")

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
def build_items(data, thumbs_map, desc_map, genre_map, epg_window, fav_ids=None):
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

	for count, item in enumerate(data['channels']):
		#if item['genres'][0] != name:
			#continue
		title = str(item['channel_number']) + ' ' + item['name']

		#   Skip Key Error Channels
		#if str(item['channel_number']) == '1412':
			#continue


		#if str(item['channel_number']) not in favorites_filter:
			#epg_window.setProperty("FAVORITES_FILTER",str(favorites_filter))
			#continue
		contentType = 'Channel'
		image = item['wallpaper']
		info = item['description']
		language = item['language']
		genres = str(item['genres'])
		onNow = item['program'][0]['program_title']
		now_desc = item['program'][0]['program_description']
		onNext = item['program'][1]['program_title']
		next_desc = item['program'][1]['program_description']
		startTime = item['program'][1]['starts_at']
		lN = strftime('%H:%M', localtime(startTime))
		plot = '[B]'+ str(onNow) +'[/B]' + ' ' + str(now_desc) + '\n\n[NEXT @' + str(lN) + '] ' + '[B]'+ str(onNext) +'[/B]'
		videoId = item['video_id']
		slug = item['slug']
		url ='https://data-store-trans-cdn.api.cms.amdvids.com/video/play/' + str(videoId) + '/1920/1080?page_url=https%253A%252F%252Flocalnow.com%252Fchannels%252F' + str(slug) + '&device_devicetype=desktop_web&app_version=0.0.0'
		streamUrl = 'plugin://plugin.video.localnow?mode=6&url=' + urllib.parse.quote_plus(url) + '&name=' + urllib.parse.quote_plus(title)
		logo = THUMBS_PATH + '/' + str(item['channel_number']) +'.png'

		if genre_filter and genre_filter not in genres.lower():
			#log(f"[BUILD ITEMS]Skipping chan_id {chan_id} ('{channel_name}') due to genre filter ({genre_filter}) — channel_lang={channel_lang}", xbmc.LOGDEBUG)
			skipped += 1
			continue

		kept += 1

		li = xbmcgui.ListItem(label=title)

		li.setProperty("channel", str(item['name']))
		li.setProperty("label", onNow)
		li.setProperty("label3", str(lN) + ' - ' + onNext)
		li.setProperty("label2", now_desc)
		li.setProperty("label4", next_desc)
		li.setProperty("label5", onNext)
		li.setProperty("next_start", str(startTime))
		li.setProperty("channel_id", str(item['channel_number']))
		li.setProperty('url', url)
		li.setProperty('IsPlayable', 'true')
		li.setArt({"icon": logo})
		li.setArt({"bg": "special://home/addons/metalchris.localnow.epg/resources/media/row_light.png"})
		li.setArt({"focus": "special://home/addons/metalchris.localnow.epg/resources/media/focus_row.png"})

		#if thumbs_map:
			# thumbs_map keys are ints in your code; use int() guard
			#try:
				#logo_url = thumbs_map.get(int(chan_id))
			#except Exception:
				#logo_url = thumbs_map.get(chan_id)
			#if logo_url:
				#li.setArt({"icon": os.path.join(THUMBS_PATH, f"{chan_id}.png")})
				#li.setProperty("logo", logo_url)

		#if idx % 2 == 0:
			#li.setProperty("rowbg", "special://home/addons/metalchris.localnow.epg/resources/media/row_light.png")
			#parity = "EVEN"
		#else:
			#li.setProperty("rowbg", "special://home/addons/metalchris.localnow.epg/resources/media/row_dark.png")
			#parity = "ODD"
		#li.setProperty("row_parity", parity)
		#log(f"[BUILD ITEMS] Adding item: {li.getProperty('channel')}", xbmc.LOGINFO)
		items.append(li)
		#log(f"[BUILD ITEMS] ListItem: {li(1)}", xbmc.LOGINFO)
	if SORT_ALPHA:
		items.sort(key=lambda li: li.getProperty('channel').lower())
	log(f"[BUILD ITEMS] SORT_ALPHA: {SORT_ALPHA}", xbmc.LOGINFO)

	#xbmcplugin.setContent(addon_handle, 'episodes')
	#xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_TITLE)
	#except Exception as e:
		#log(f"[BUILD ITEMS]Error building item for chan_id {chan_id}: {e}", xbmc.LOGERROR)
		#skipped += 1

	#log(f"[BUILD ITEMS]Channels kept: {kept}, skipped: {skipped}, filter_lang={filter_lang_display}, filter_genre={genre_filter}", xbmc.LOGINFO)

	# --- Title ---
	if epg_window.getProperty("FAVORITES_FILTER"):
		title = f"LocalNow - Favorites ({kept} Channels)"
	elif genre_filter:
		title = f"LocalNow EPG - {genre_filter.capitalize()} ({kept} Channels)"
	else:
		#title = "LocalNow EPG"
		title = "LocalNow EPG"

	log(f"[BUILD ITEMS] Window title set to: {title}", xbmc.LOGINFO)
	# Set the window property so the UI can use it
	epg_window.setProperty("EPG_TITLE", title)

	#return items, kept, title
	return items, kept, title
