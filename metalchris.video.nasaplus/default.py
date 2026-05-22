import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup
import xbmc, xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import os

from resources.lib.logger import log
from resources.lib.convert_to_local import format_unix_time_kodi, parse_duration
from resources.lib.caching import fmt_time, fmt_ttl, compute_hash, _cache_key, _cache_ensure_loaded, _cache_flush, cache_get, cache_set, cache_set_many, cache_get_with_meta, normalize_html, CACHE_TTL_PAGES, CACHE_TTL_DESCRIPTIONS, clear_cache
from resources.lib.playback import *
from resources.lib.fetching import *

ADDON      = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
MEDIA_PATH = os.path.join(ADDON_PATH, "resources", "media")

ICON   = os.path.join(MEDIA_PATH, "icon.png")
FANART = os.path.join(MEDIA_PATH, "fanart.jpg")

BASE_URL = "https://plus.nasa.gov"
HANDLE = int(sys.argv[1])


SERIES_DESCRIPTION_FALLBACK = "No Description Available."

# -------------------
# Helpers
# -------------------	

if ADDON.getSetting("first_run") == "true":
    ADDON.openSettings()
    ADDON.setSetting("first_run", "false")

def normalize_url(url):
	"""Convert relative URLs to absolute NASA+ URLs."""
	if not url:
		return url
	return BASE_URL + url if url.startswith("/") else url


def load_descriptions_enabled():
	"""Return whether metadata description scraping is enabled in settings."""
	try:
		return ADDON.getSettingBool("load_descriptions")
	except Exception:
		try:
			return (ADDON.getSetting("load_descriptions") or "true").lower() == "true"
		except Exception:
			return True
		
		
# -------------------
# Root menu
# -------------------

def get_main_menu():
	"""Build the root menu, mapping scraped site links to actions:
	   - '/topics/' or titles containing 'topic' -> 'topics'
	   - '/watch/' or titles containing 'watch'/'live' -> 'live'
	   - '/explore/' or titles containing 'explore'/'series' -> 'series'
	   Falls back to a safe lowercase action if none match.
	"""
	try:
		debug_enabled = ADDON.getSettingBool("debug")
	except Exception:
		debug_enabled = False

	status = "ENABLED" if debug_enabled else "DISABLED"
	log(f"[{ADDON_NAME} v{ADDON_VERSION}] [ADD-ON STARTED] [DEBUG: {status}]", level=xbmc.LOGINFO)
	soup = fetch_page(BASE_URL)
	divs = soup.find_all("div", class_="tablet:grid-col banner--menus-single margin-y-1")

	for div in divs:
		a = div.find("a")
		if not a:
			continue

		title = a.get_text(strip=True)
		href = a.get("href", "")
		url = BASE_URL + href if href.startswith("/") else href

		low_title = title.lower()
		low_href = href.lower()

		# determine action by checking both title and href for keywords
		if "topic" in low_title or "/topics/" in low_href:
			action = "topics"
			display_name = "Topics"
		elif "watch" in low_title or "live" in low_title or "/watch/" in low_href or "/live/" in low_href:
			action = "live"
			display_name = "Live"
		elif "explore" in low_title or "series" in low_title or "/explore/" in low_href:
			action = "series"
			display_name = "Series"
		else:
			# fallback: slugify title a bit (replace spaces with underscores)
			action = low_title.replace(" ", "_")
			display_name = title

		log(f"[MAIN]: found main menu: title='{title}' href='{href}' -> action='{action}'", xbmc.LOGDEBUG)

		list_item = xbmcgui.ListItem(label=display_name)
		list_item.setArt({"thumb": ICON, "icon": ICON, "fanart": FANART})
		xbmcplugin.addDirectoryItem(
			handle=HANDLE,
			url=get_url(action=action, url=url),
			listitem=list_item,
			isFolder=True
		)

	xbmcplugin.endOfDirectory(HANDLE)


# -------------------
# Handlers for each menu
# -------------------
	
def live_menu(url):
	"""Scrape NASA+ Scheduled Events page."""
	import time
	now = int(time.time())

	soup = fetch_page(url)

	events = soup.find_all("article", class_="events-list")

	log(f"[LIVE] Raw events found: {len(events)}")

	seen = set()  # track URLs we've already added
	directory_items = []

	for event in events:
		try:
			# --- TITLE + URL ---
			title_tag = event.find("a", class_="nasatv-video-title")
			if not title_tag:
				continue

			href = normalize_url(title_tag.get("href"))
			if not href:
				continue

			# 🚫 Skip duplicates
			if href in seen:
				continue
			seen.add(href)

			title = title_tag.get_text(strip=True)

			# --- TIMESTAMP LOGIC (SIMPLIFIED) ---
			date_div = event.find("div", class_="nasatv-event-date")

			is_live = False
			is_upcoming = False
			event_time = ""

			if date_div and date_div.has_attr("data-event-timestamp"):
				ts_raw = date_div["data-event-timestamp"].strip()

				if ts_raw.isdigit():
					event_ts = int(ts_raw)
					event_time = format_unix_time_kodi(ts_raw)

					if now < event_ts:
						is_upcoming = True
					else:
						is_live = True

			# --- DATE / TIME ---
			time_text = ""

			if date_div:
				start_date = date_div.find("span", class_="start-date")
				start_time = date_div.find("span", class_="start-time")

				if start_date and start_time:
					time_text = f"{start_date.get_text(strip=True)} {start_time.get_text(strip=True)}"

			if time_text and event_time:
				title = f"({event_time}) {title}"
			elif time_text:
				title = f"({time_text}) {title}"

			# --- APPLY STATUS LABEL ---
			if is_live:
				title = f"[COLOR green][LIVE][/COLOR] {title}"
			elif is_upcoming:
				title = f"{title}"

			# --- THUMBNAIL ---
			thumb = None
			figure = event.find("figure")

			if figure and "style" in figure.attrs:
				style = figure["style"]
				if "url(" in style:
					thumb = style.split("url(")[1].split(")")[0].strip('"')

			# --- LIST ITEM ---
			list_item = xbmcgui.ListItem(label=title, offscreen=True)

			if thumb:
				list_item.setArt({
					"thumb": thumb,
					"icon": thumb,
					"poster": thumb,
					"fanart": thumb
				})
				
			list_item.setProperty("IsPlayable", "true")				
			
			#list_item.setInfo("video", {"title": title}) # Required for Matrix
			video_info_tag = list_item.getVideoInfoTag()
			video_info_tag.setTitle(title)
			list_item.setMimeType("application/vnd.apple.mpegurl")

			log(f"[LIVE] Event: {title}")
			directory_items.append((get_url(action="stream", url=href), list_item, False))

		except Exception as e:
			log(f"[LIVE] Parse error: {e}", xbmc.LOGERROR)

	if directory_items:
		xbmcplugin.addDirectoryItems(HANDLE, directory_items, len(directory_items))

	xbmcplugin.endOfDirectory(HANDLE)
	

def topics_menu(url):
	"""Scrape Topics landing page (12 topics)."""
	soup = fetch_page(url)
	links = soup.find_all("a", class_="video-grid--link")
	directory_items = []

	for a in links:
		h4 = a.find("h4")
		if not h4:
			continue
		title = h4.get_text(strip=True)
		href = normalize_url(a.get("href"))
		if not href:
			continue

		# Extract thumbnail from inline CSS
		figure = a.find("figure")
		thumb = None
		if figure and "style" in figure.attrs:
			style = figure["style"]
			start = style.find("url(")
			end = style.find(")", start)
			if start != -1 and end != -1:
				thumb = style[start+4:end].strip()

		list_item = xbmcgui.ListItem(label=title, offscreen=True)
		if thumb:
			list_item.setArt({"thumb": thumb, "icon": thumb, "fanart": thumb})

		log(f"[TOPICS]: found topic menu: title='{title}' href='{href}'", xbmc.LOGDEBUG)
		directory_items.append((get_url(action="videos", url=href), list_item, True))

	if directory_items:
		xbmcplugin.addDirectoryItems(HANDLE, directory_items, len(directory_items))
		xbmcplugin.setContent(HANDLE, 'episodes')

	xbmcplugin.endOfDirectory(HANDLE)
	

def video_menu(url):
	"""Scrape a Topic or Series page and list its videos."""
	soup = fetch_page(url)
	videos = soup.find_all("a", class_="video-grid--link")
	descriptions_enabled = load_descriptions_enabled()

	seen = set()  # track URLs we've already added
	items = []

	for a in videos:
		href = normalize_url(a.get("href"))
		h4 = a.find("h4")
		title = h4.get_text(strip=True) if h4 else "Untitled"

		if not href:
			continue
		
		# 🚫 Skip duplicates
		if href in seen:
			continue
		seen.add(href)

		# Duration (append to title in parentheses)
		duration_tag = a.find("p", class_="font-family-mono")
		if duration_tag:

			duration_str = duration_tag.get_text(strip=True)
			duration = parse_duration(duration_str)
		else:
			duration = 0


		# Extract thumbnail
		figure = a.find("figure")
		thumb = None
		if figure and "style" in figure.attrs:
			style = figure["style"]
			start = style.find("url(")
			end = style.find(")", start)
			if start != -1 and end != -1:
				thumb = style[start+4:end].strip()

		items.append((title, href, duration, thumb))

	descriptions = {}
	if descriptions_enabled:
		descriptions = fetch_video_descriptions([href for _, href, _, _ in items])
	directory_items = []

	for title, href, duration, thumb in items:
		list_item = xbmcgui.ListItem(label=title, offscreen=True)
		description = descriptions.get(href, "") or SERIES_DESCRIPTION_FALLBACK

		if thumb:
			list_item.setArt({"thumb": thumb, "icon": thumb, "poster": thumb, "fanart": thumb})

		list_item.setProperty("IsPlayable", "true")
		info = {
			"title": title,
			"duration": duration,
		}
		if descriptions_enabled:
			info["plot"] = description
			info["plotoutline"] = description
		#list_item.setInfo("video", info) # Required for Matrix
		video_info_tag = list_item.getVideoInfoTag()
		video_info_tag.setTitle(title)
		video_info_tag.setPlot(description)
		video_info_tag.setDuration(duration)

		log(f"[VIDEO]: found video menu: title='{title}' href='{href}'", xbmc.LOGDEBUG)
		directory_items.append((get_url(action="play", url=href), list_item, False))

	if directory_items:
		xbmcplugin.addDirectoryItems(HANDLE, directory_items, len(directory_items))
		xbmcplugin.setContent(HANDLE, 'episodes')

	xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(HANDLE)




def series_menu(url):
	"""Scrape the NASA+ Series page and list all series."""
	soup = fetch_page(url)
	links = soup.find_all("a", class_="series-grid--link")
	descriptions_enabled = load_descriptions_enabled()

	items = []

	for a in links:
		href = normalize_url(a.get("href"))

		# Title
		h4 = a.find("h4")
		title = h4.get_text(strip=True) if h4 else "Untitled"

		# Episode count
		p = a.find("p")
		if p:
			title = f"{title} ({p.get_text(strip=True)})"

		# Thumbnail
		figure = a.find("figure")
		thumb = None
		if figure and "style" in figure.attrs:
			style = figure["style"]
			start = style.find("url(")
			end = style.find(")", start)
			if start != -1 and end != -1:
				thumb = style[start+4:end].strip()

		# Store data instead of ListItem
		items.append((title, href, thumb))

	# ✅ SORT BEFORE ADDING
	items.sort(key=lambda x: x[0].lower())

	descriptions = {}
	if descriptions_enabled:
		# Fetch descriptions cache-first; network only for missing entries.
		descriptions = fetch_series_descriptions([href for _, href, _ in items])

	directory_items = []
	for title, href, thumb in items:
		list_item = xbmcgui.ListItem(label=title, offscreen=True)
		description = descriptions.get(href, "") or SERIES_DESCRIPTION_FALLBACK

		if thumb:
			list_item.setArt({
				"thumb": thumb,
				"icon": thumb,
				"poster": thumb,
				"fanart": thumb
			})

		info = {
			"title": title,
		}
		if descriptions_enabled:
			info["plot"] = description
			info["plotoutline"] = description
		#list_item.setInfo("video", info) # Required for Matrix
		video_info_tag = list_item.getVideoInfoTag()
		video_info_tag.setTitle(title)
		video_info_tag.setPlot(description)

		log(f"[SERIES]: found series menu: title='{title}' href='{href}'", xbmc.LOGDEBUG)
		directory_items.append((get_url(action="videos", url=href), list_item, True))

	if directory_items:
		xbmcplugin.addDirectoryItems(HANDLE, directory_items, len(directory_items))
		xbmcplugin.setContent(HANDLE, 'episodes')

	xbmcplugin.endOfDirectory(HANDLE)
	
	
# -------------------
# Router
# -------------------

def router(params):
	action = params.get("action")
	url = params.get("url")
	try:
		if action is None:
			get_main_menu()
		elif action == "live":
			live_menu(url)
		elif action == "topics":
			topics_menu(url)
		elif action == "series":
			series_menu(url)
		elif action == "videos":
			video_menu(url)
		elif action == "play":
			play_video(url)
		elif action == "stream":
			stream_video(url)
		if action == "clear_cache":
			if xbmcgui.Dialog().yesno("NASA+", "Clear cached data?"):
				clear_cache()
		else:
			get_main_menu()
	finally:
		_cache_flush()


if __name__ == "__main__":
	query = sys.argv[2][1:]  # strip '?'
	params = dict(urllib.parse.parse_qsl(query))
	router(params)
