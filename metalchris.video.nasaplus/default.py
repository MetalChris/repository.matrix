import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import xbmc, xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import os
import json
import time
import hashlib
import threading
from resources.lib.parse_duration import parse_duration
from resources.lib.logger import log
from resources.lib.convert_to_local import format_unix_time_kodi

ADDON      = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
MEDIA_PATH = os.path.join(ADDON_PATH, "resources", "media")

ICON   = os.path.join(MEDIA_PATH, "icon.png")
FANART = os.path.join(MEDIA_PATH, "fanart.jpg")

BASE_URL = "https://plus.nasa.gov"
HANDLE = int(sys.argv[1])

# Cache setup
PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
CACHE_DIR = os.path.join(PROFILE_PATH, 'cache')
if not xbmcvfs.exists(CACHE_DIR):
	xbmcvfs.mkdirs(CACHE_DIR)
CACHE_FILE = os.path.join(CACHE_DIR, 'nasa_plus_cache.json')

# Cache TTLs (time-to-live in seconds)
CACHE_TTL_PAGES = 3600 * 6            # 6 hours for HTML pages
CACHE_TTL_DESCRIPTIONS = 3600 * 24    # 24 hours for series descriptions
SERIES_DESCRIPTION_FALLBACK = "Description unavailable."

# In-memory cache state for this addon run
CACHE_LOCK = threading.Lock()
CACHE_DATA = {}
CACHE_LOADED = False
CACHE_DIRTY = False


#xbmc.log(f"[{ADDON_NAME} v{ADDON_VERSION}] [ADD-ON RUNNING]", xbmc.LOGINFO)

# -------------------
# Helpers
# -------------------

def _cache_key(prefix, url):
	return f"{prefix}:{hashlib.md5(url.encode()).hexdigest()}"


def _cache_ensure_loaded():
	"""Load cache once into memory and purge expired entries."""
	global CACHE_DATA, CACHE_DIRTY, CACHE_LOADED
	if CACHE_LOADED:
		return

	loaded = {}
	if os.path.exists(CACHE_FILE):
		try:
			with open(CACHE_FILE, 'r') as f:
				loaded = json.load(f)
		except Exception as e:
			log(f"[CACHE] Failed to load: {e}")
			loaded = {}

	now = time.time()
	expired = [k for k, v in loaded.items() if v.get('expires', 0) <= now]
	for key in expired:
		del loaded[key]

	CACHE_DATA = loaded
	CACHE_LOADED = True
	if expired:
		CACHE_DIRTY = True


def _cache_flush(force=False):
	"""Flush in-memory cache to disk once per run (or force)."""
	global CACHE_DIRTY
	with CACHE_LOCK:
		_cache_ensure_loaded()
		if not force and not CACHE_DIRTY:
			return
		try:
			tmp_file = CACHE_FILE + ".tmp"
			with open(tmp_file, 'w') as f:
				json.dump(CACHE_DATA, f)
			os.replace(tmp_file, CACHE_FILE)
			CACHE_DIRTY = False
		except Exception as e:
			log(f"[CACHE] Failed to save: {e}")


def cache_get(key):
	"""Get value from cache if valid. Returns None if expired or missing."""
	global CACHE_DIRTY
	with CACHE_LOCK:
		_cache_ensure_loaded()
		entry = CACHE_DATA.get(key)
		if not entry:
			return None
		if entry.get('expires', 0) <= time.time():
			del CACHE_DATA[key]
			CACHE_DIRTY = True
			return None
		return entry.get('value')


def cache_set(key, value, ttl):
	"""Store value in cache with given TTL (seconds)."""
	global CACHE_DIRTY
	with CACHE_LOCK:
		_cache_ensure_loaded()
		CACHE_DATA[key] = {
			'value': value,
			'expires': time.time() + ttl
		}
		CACHE_DIRTY = True


def cache_set_many(entries, ttl):
	"""Store many cache entries in one lock/write cycle."""
	global CACHE_DIRTY
	now = time.time()
	with CACHE_LOCK:
		_cache_ensure_loaded()
		for key, value in entries.items():
			CACHE_DATA[key] = {
				'value': value,
				'expires': now + ttl
			}
		CACHE_DIRTY = True


def get_url(**kwargs):
	"""Build plugin URL with query params."""
	return sys.argv[0] + '?' + urllib.parse.urlencode(kwargs)

def fetch_page(url):
	"""Fetch and parse HTML page with caching."""
	cache_key = _cache_key("page", url)
	
	cached_html = cache_get(cache_key)
	if cached_html:
		return BeautifulSoup(cached_html, "html.parser")
	
	xbmc.log(f"[{ADDON_NAME}] [FETCHING]: {url}", xbmc.LOGINFO)
	resp = requests.get(url, timeout=(3, 10))
	resp.raise_for_status()
	html = resp.text
	
	cache_set(cache_key, html, CACHE_TTL_PAGES)
	
	return BeautifulSoup(html, "html.parser")


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


META_PROGRESS = {}


def notify_meta_progress(scope, done, total):
	"""Show/update top-right background progress text while scraping metadata."""
	if total <= 0:
		return
	percent = int((done * 100) / total)

	if scope == "Series":
		text = f"Loading series descriptions {done}/{total}"
	elif scope == "Videos":
		text = f"Loading video descriptions {done}/{total}"
	else:
		text = f"Loading descriptions {done}/{total}"

	dialog = META_PROGRESS.get(scope)
	if dialog is None:
		dialog = xbmcgui.DialogProgressBG()
		dialog.create(ADDON_NAME, text)
		META_PROGRESS[scope] = dialog
	else:
		dialog.update(percent, ADDON_NAME, text)

	if done >= total:
		try:
			dialog.close()
		except Exception as e:
			log(f"[META] Failed to close progress dialog for '{scope}': {e}", xbmc.LOGWARNING)
		META_PROGRESS.pop(scope, None)


def close_meta_progress(scope):
	"""Force-close metadata progress indicator for scope."""
	dialog = META_PROGRESS.pop(scope, None)
	if dialog is None:
		return
	try:
		dialog.close()
	except Exception as e:
		log(f"[META] Failed to close progress dialog for '{scope}': {e}", xbmc.LOGWARNING)


def fetch_series_og_description(url, session=None):
	"""Fetch og:description text from a single series page."""
	try:
		requester = session or requests
		resp = requester.get(url, timeout=(2, 4))
		resp.raise_for_status()
		soup = BeautifulSoup(resp.text, "html.parser")
		meta = soup.find("meta", attrs={"property": "og:description"}) or soup.find("meta", attrs={"name": "description"})
		if not meta:
			return ""
		content = meta.attrs.get("content", "")
		return content.strip() if isinstance(content, str) else ""
	except Exception as e:
		log(f"[SERIES] Description fetch failed for '{url}': {e}")
		return ""


def fetch_series_descriptions(urls):
	"""Fetch series descriptions with cache-first and fast parallel fallback."""
	results = {}
	unique_urls = [u for u in dict.fromkeys(urls) if u]
	if not unique_urls:
		return results

	missing_urls = []
	for url in unique_urls:
		cached = cache_get(_cache_key("desc", url))
		if cached is not None:
			results[url] = cached
		else:
			missing_urls.append(url)

	if not missing_urls:
		return results

	total_missing = len(missing_urls)
	completed = 0
	next_notify_percent = 25
	notify_meta_progress("Series", 0, total_missing)

	session = requests.Session()
	max_workers = min(12, len(missing_urls))
	fresh_entries = {}
	try:
		with ThreadPoolExecutor(max_workers=max_workers) as executor:
			future_map = {
				executor.submit(fetch_series_og_description, url, session): url
				for url in missing_urls
			}
			for future in as_completed(future_map):
				url = future_map[future]
				try:
					description = future.result() or ""
				except Exception:
					description = ""
				results[url] = description
				fresh_entries[_cache_key("desc", url)] = description
				completed += 1
				current_percent = int((completed * 100) / total_missing)
				if completed == total_missing or current_percent >= next_notify_percent:
					notify_meta_progress("Series", completed, total_missing)
					while next_notify_percent <= current_percent:
						next_notify_percent += 25
	finally:
		session.close()
		close_meta_progress("Series")

	if fresh_entries:
		cache_set_many(fresh_entries, CACHE_TTL_DESCRIPTIONS)

	return results


def fetch_video_page_description(url, session=None):
	"""Fetch meta description text from a single video page."""
	try:
		requester = session or requests
		resp = requester.get(url, timeout=(2, 4))
		resp.raise_for_status()
		soup = BeautifulSoup(resp.text, "html.parser")
		meta = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
		if not meta:
			return ""
		content = meta.attrs.get("content", "")
		return content.strip() if isinstance(content, str) else ""
	except Exception as e:
		log(f"[VIDEO] Description fetch failed for '{url}': {e}")
		return ""


def fetch_video_descriptions(urls):
	"""Fetch video descriptions with cache-first and fast parallel fallback."""
	results = {}
	unique_urls = [u for u in dict.fromkeys(urls) if u]
	if not unique_urls:
		return results

	missing_urls = []
	for url in unique_urls:
		cached = cache_get(_cache_key("vdesc", url))
		if cached is not None:
			results[url] = cached
		else:
			missing_urls.append(url)

	if not missing_urls:
		return results

	total_missing = len(missing_urls)
	completed = 0
	next_notify_percent = 25
	notify_meta_progress("Videos", 0, total_missing)

	session = requests.Session()
	max_workers = min(12, len(missing_urls))
	fresh_entries = {}
	try:
		with ThreadPoolExecutor(max_workers=max_workers) as executor:
			future_map = {
				executor.submit(fetch_video_page_description, url, session): url
				for url in missing_urls
			}
			for future in as_completed(future_map):
				video_url = future_map[future]
				try:
					description = future.result() or ""
				except Exception:
					description = ""
				results[video_url] = description
				fresh_entries[_cache_key("vdesc", video_url)] = description
				completed += 1
				current_percent = int((completed * 100) / total_missing)
				if completed == total_missing or current_percent >= next_notify_percent:
					notify_meta_progress("Videos", completed, total_missing)
					while next_notify_percent <= current_percent:
						next_notify_percent += 25
	finally:
		session.close()
		close_meta_progress("Videos")

	if fresh_entries:
		cache_set_many(fresh_entries, CACHE_TTL_DESCRIPTIONS)

	return results

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
	xbmc.log(f"[{ADDON_NAME} v{ADDON_VERSION}] [ADD-ON STARTED] [DEBUG: {status}]", level=xbmc.LOGINFO)
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

		log(f"[MAIN]: found menu: title='{title}' href='{href}' -> action='{action}'")

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
			
			# ✅ Required for Kodi Matrix
			list_item.setInfo("video", {"title": title})
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

		log(f"[TOPICS]: found menu: title='{title}' href='{href}'")
		directory_items.append((get_url(action="videos", url=href), list_item, True))

	if directory_items:
		xbmcplugin.addDirectoryItems(HANDLE, directory_items, len(directory_items))

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
			#duration = duration_tag.get_text(strip=True)
			#title = f"{title} ({duration})"

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
		list_item.setInfo("video", info)

		log(f"[VIDEO]: found menu: title='{title}' href='{href}'")
		directory_items.append((get_url(action="play", url=href), list_item, False))

	if directory_items:
		xbmcplugin.addDirectoryItems(HANDLE, directory_items, len(directory_items))

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
		list_item.setInfo("video", info)

		log(f"[SERIES]: found menu: title='{title}' href='{href}'")
		directory_items.append((get_url(action="videos", url=href), list_item, True))

	if directory_items:
		xbmcplugin.addDirectoryItems(HANDLE, directory_items, len(directory_items))

	xbmcplugin.endOfDirectory(HANDLE)



def play_video(url):
	use_inputstream = ADDON.getSettingBool("use_inputstream")
	
	"""Resolve and play a NASA+ video page."""
	soup = fetch_page(url)

	# Find the <source> tag with an HLS stream
	source = soup.find("source", {"type": "application/x-mpegURL"})
	if not source or not source.get("src"):
		xbmcgui.Dialog().notification("NASA+ [PLAY VIDEO]", "No video source found", ICON, 3000, False)
		return

	stream_url = source["src"]

	list_item = xbmcgui.ListItem(path=stream_url)
	list_item.setProperty("IsPlayable", "true")
	list_item.setProperty('metalchris.nasaplus', 'true')
	
	if use_inputstream:
		# Enable inputstream.adaptive
		log(f"[PLAYBACK] InputStream", xbmc.LOGINFO)
		list_item.setProperty("inputstream", "inputstream.adaptive")
		list_item.setProperty("inputstream.adaptive.manifest_type", "hls")
	else:
		# --- FFMPEG (Kodi default player) ---
		# Do nothing special — Kodi will use FFmpeg automatically
		log(f"[PLAYBACK] FFMPEG", xbmc.LOGINFO)
		pass

	xbmcplugin.setResolvedUrl(HANDLE, True, list_item)


def stream_video(url):
	use_inputstream = ADDON.getSettingBool("use_inputstream")
	
	"""Fetch the live stream URL from a NASA+ event page."""
	#html = fetch_page(url)  # make sure this returns raw HTML string

	try:
		html = fetch_page(url)
	except Exception as e:
		# 👇 Catch 404 or any fetch failure
		log(f"[LIVE] fetch failed for {url}: {e}")

		# Treat as ended event
		xbmcgui.Dialog().notification(ADDON_NAME,"This event has ended.",ICON,3000,False)
		return
		
	log(f"[LIVE] No Fetch Failure, Continuing...")
		
	date_div = html.find("div", class_="nasatv-event-date")

	is_live = False
	is_upcoming = False

	if date_div and date_div.has_attr("data-event-timestamp"):
		ts_raw = date_div["data-event-timestamp"].strip()

		if ts_raw.isdigit():
			event_ts = int(ts_raw)
			import time
			now = int(time.time())

			if now < event_ts:
				xbmcgui.Dialog().notification(ADDON_NAME,"This event has not yet started.",ICON,3000,False)		
				log(f"[LIVE] Event Not Started.")
				return		
	
        
	"""Fetch the live stream URL from a NASA+ event page."""
	#soup = fetch_page(url)
	
	#start_tag = soup.find("div", id="countdownclock")
	#if start_tag:
		#xbmcgui.Dialog().notification(ADDON_NAME,"This event has not yet started.",ICON,3000,False)
		#return

	video_tag = html.find("video", id="main-video")
	if not video_tag:
		xbmcgui.Dialog().notification(ADDON_NAME,"No Stream URL Found.",ICON,3000,False)
		#return
		return None

	# Prefer the data-video-url attribute, fallback to <source src>
	stream_url = video_tag.get("data-fallback-url")
	if not stream_url:
		source_tag = video_tag.find("source")
		if source_tag and source_tag.get("src"):
			stream_url = source_tag["src"]
			
	log(f"[VIDEO]: found stream: url='{stream_url}'")
	
	list_item = xbmcgui.ListItem()

	list_item.setProperty("IsPlayable", "true")
	list_item.setProperty('metalchris.nasaplus', 'true')

	# Set path AFTER creation
	list_item.setPath(stream_url)
	
	if use_inputstream:
		# Enable inputstream.adaptive
		log(f"[PLAYBACK] InputStream", xbmc.LOGINFO)
		list_item.setProperty("inputstream", "inputstream.adaptive")
		list_item.setProperty("inputstream.adaptive.manifest_type", "hls")
	else:
		# --- FFMPEG (Kodi default player) ---
		# Do nothing special — Kodi will use FFmpeg automatically
		log(f"[PLAYBACK] FFMPEG", xbmc.LOGINFO)
		pass

	xbmcplugin.setResolvedUrl(HANDLE, True, list_item)
	

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
		else:
			get_main_menu()
	finally:
		_cache_flush()


if __name__ == "__main__":
	query = sys.argv[2][1:]  # strip '?'
	params = dict(urllib.parse.parse_qsl(query))
	router(params)
