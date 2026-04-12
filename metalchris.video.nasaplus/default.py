import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup
import xbmc, xbmcplugin
import xbmcgui
import xbmcaddon
import os
from resources.lib.parse_duration import *
from resources.lib.logger import *
from resources.lib.convert_to_local import *

ADDON      = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
MEDIA_PATH = os.path.join(ADDON_PATH, "resources", "media")

ICON   = os.path.join(MEDIA_PATH, "icon.png")
FANART = os.path.join(MEDIA_PATH, "fanart.jpg")

BASE_URL = "https://plus.nasa.gov"
HANDLE = int(sys.argv[1])


#xbmc.log(f"[{ADDON_NAME} v{ADDON_VERSION}] [ADD-ON RUNNING]", xbmc.LOGINFO)

# -------------------
# Helpers
# -------------------

def get_url(**kwargs):
	"""Build plugin URL with query params."""
	return sys.argv[0] + '?' + urllib.parse.urlencode(kwargs)

def fetch_page(url):
	xbmc.log(f"[{ADDON_NAME}] [FETCHING]: {url}", xbmc.LOGINFO)

	"""Fetch and parse HTML page."""
	resp = requests.get(url)
	resp.raise_for_status()
	return BeautifulSoup(resp.text, "html.parser")

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

	for event in events:
		try:
			# --- TITLE + URL ---
			title_tag = event.find("a", class_="nasatv-video-title")
			if not title_tag:
				continue

			href = title_tag.get("href")
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

			if date_div and date_div.has_attr("data-event-timestamp"):
				ts_raw = date_div["data-event-timestamp"].strip()

				if ts_raw.isdigit():
					event_ts = int(ts_raw)

					if now < event_ts:
						is_upcoming = True
					else:
						is_live = True

			# --- DATE / TIME ---
			time_text = ""

			if date_div:
				start_date = date_div.find("span", class_="start-date")
				start_time = date_div.find("span", class_="start-time")
				event_time = format_unix_time_kodi(ts_raw)

				if start_date and start_time:
					time_text = f"{start_date.get_text(strip=True)} {start_time.get_text(strip=True)}"

			if time_text:
				title = f"({event_time}) {title}"

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
			list_item = xbmcgui.ListItem(label=title)

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

			xbmcplugin.addDirectoryItem(
				handle=HANDLE,
				url=get_url(action="stream", url=href),
				listitem=list_item,
				isFolder=False
			)

		except Exception as e:
			log(f"[LIVE] Parse error: {e}", error=True)

	xbmcplugin.endOfDirectory(HANDLE)
	

def topics_menu(url):
	"""Scrape Topics landing page (12 topics)."""
	soup = fetch_page(url)
	links = soup.find_all("a", class_="video-grid--link")

	for a in links:
		title = a.find("h4").get_text(strip=True)
		href = a["href"]

		# Extract thumbnail from inline CSS
		figure = a.find("figure")
		thumb = None
		if figure and "style" in figure.attrs:
			style = figure["style"]
			start = style.find("url(")
			end = style.find(")", start)
			if start != -1 and end != -1:
				thumb = style[start+4:end].strip()

		list_item = xbmcgui.ListItem(label=title)
		if thumb:
			list_item.setArt({"thumb": thumb, "icon": thumb, "fanart": thumb})

		log(f"[TOPICS]: found menu: title='{title}' href='{href}'")

		xbmcplugin.addDirectoryItem(
			handle=HANDLE,
			url=get_url(action="videos", url=href),
			listitem=list_item,
			isFolder=True
		)

	xbmcplugin.endOfDirectory(HANDLE)
	

def video_menu(url):
	"""Scrape a Topic or Series page and list its videos."""
	soup = fetch_page(url)
	videos = soup.find_all("a", class_="video-grid--link")

	seen = set()  # track URLs we've already added

	for a in videos:
		href = a.get("href")
		h4 = a.find("h4")
		title = h4.get_text(strip=True) if h4 else "Untitled"
		
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

		list_item = xbmcgui.ListItem(label=title)
		if thumb:
			list_item.setArt({"thumb": thumb, "icon": thumb, "poster": thumb, "fanart": thumb})

		list_item.setProperty("IsPlayable", "true")
		list_item.setInfo("video", {
			"title": title,
			"duration": duration,
		})

		log(f"[VIDEO]: found menu: title='{title}' href='{href}'")

		xbmcplugin.addDirectoryItem(
			handle=HANDLE,
			url=get_url(action="play", url=href),
			listitem=list_item,
			isFolder=False
		)

	xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(HANDLE)




def series_menu(url):
	"""Scrape the NASA+ Series page and list all series."""
	soup = fetch_page(url)
	links = soup.find_all("a", class_="series-grid--link")

	items = []

	for a in links:
		href = a.get("href")

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

	# Now add to Kodi
	for title, href, thumb in items:
		list_item = xbmcgui.ListItem(label=title)

		if thumb:
			list_item.setArt({
				"thumb": thumb,
				"icon": thumb,
				"poster": thumb,
				"fanart": thumb
			})

		log(f"[SERIES]: found menu: title='{title}' href='{href}'")

		xbmcplugin.addDirectoryItem(
			handle=HANDLE,
			url=get_url(action="videos", url=href),
			listitem=list_item,
			isFolder=True
		)

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


if __name__ == "__main__":
	query = sys.argv[2][1:]  # strip '?'
	params = dict(urllib.parse.parse_qsl(query))
	router(params)
