import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup
import xbmc, xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import os
import time

from resources.lib.logger import log
from resources.lib.write_videos import *
from resources.lib.fetching import *
from resources.lib.convert_to_local import format_unix_time_kodi, parse_duration

ADDON      = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
PROFILE_PATH = "special://userdata/addon_data/metalchris.video.nasaplus/"
VIDEOS_FILE = PROFILE_PATH +  ADDON_ID + ".json"

BASE_URL = "https://plus.nasa.gov"
HANDLE = int(sys.argv[1])

TTL = 604800 # 7 days

SERIES_DESCRIPTION_FALLBACK = "No Description Available."

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
			
			
def get_topics_url():
	
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
			log(f"[A TO Z]: found topics url: {url}", xbmc.LOGDEBUG)
			get_topics(url)
	

def get_topics(url):
	"""Scrape Topics landing page (12 topics)."""
	soup = fetch_page(url)
	links = soup.find_all("a", class_="video-grid--link")
	directory_items = []
	topics = []

	for a in links:
		h4 = a.find("h4")
		if not h4:
			continue
		title = h4.get_text(strip=True)
		href = normalize_url(a.get("href"))
		if not href:
			continue

		topics.append((title, href))
		
	log(f"[A TO Z]: found {len(topics)} topics: {topics}", xbmc.LOGDEBUG)
	cycle_topics(topics)
	
	
def cycle_topics(topics):
	
	for topic, url in topics:
		video_list(topic,url)
	
	
def video_list(topic,url):
	log(f"[A TO Z]: cycling topic: {topic}", xbmc.LOGDEBUG)
	"""Scrape a Topic or Series page and list its videos."""
	soup = fetch_page(url)
	videos = soup.find_all("a", class_="video-grid--link")
	descriptions_enabled = load_descriptions_enabled()

	seen = set()  # track URLs we've already added
	items = []
	video_data = {}

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

		video_data[title] = {
			"description": description,
			"url": href,
			"thumb": thumb,
			"duration": duration,
			"topic": topic
		}
		
	write_video_list(video_data,topic)
	#read_videos()				


def read_videos():
	
	now = time.time()
	
	try:
		if xbmcvfs.exists(VIDEOS_FILE):
			with xbmcvfs.File(VIDEOS_FILE, 'r') as f:
				data = json.load(f)
			
			ts = data.get("timestamp")
			file_age = (time.time() - ts) / 3600
			log(f"[A TO Z] {ADDON_NAME.upper()} VIDEOS_FILE is {file_age:.1f} hours old.", xbmc.LOGINFO)
			diff = ((TTL / 3600) - file_age) 
			log(f"[A TO Z] {ADDON_NAME.upper()} VIDEOS_FILE will expire in {diff:.1f} hours.", xbmc.LOGINFO)
			if now - data.get("timestamp", 0) < TTL:
				log("[A TO Z] Loaded data from cache", xbmc.LOGINFO)
			else:
				log("[A TO Z] Refreshing videos list...", xbmc.LOGINFO)
				get_topics_url()
				
			videos = data.get("videos")
			log(f"[A TO Z]: Found {len(videos.keys())} videos", xbmc.LOGINFO)	
			
	except Exception as e:
		xbmc.log(f"[REFRESH] Failed to read metalchris.video.nasaplus.json: {e}", xbmc.LOGERROR)
	
	
	directory_items = []
	try:
		for title, details in data['videos'].items():
			description = details.get("description") or SERIES_DESCRIPTION_FALLBACK
			url = details.get("url")
			thumb = details.get("thumb")
			duration = details.get("duration")
			#log(f"[VIDEO]: Duration: '{duration}'", xbmc.LOGDEBUG)
		
			list_item = xbmcgui.ListItem(label=title)

			if thumb:
				list_item.setArt({"thumb": thumb, "icon": thumb, "poster": thumb, "fanart": thumb})

			list_item.setProperty("IsPlayable", "true")
			info = {
				"title": title,
				"duration": duration,
			}
			#if descriptions_enabled:
			info["plot"] = description
			info["plotoutline"] = description
			#list_item.setInfo("video", info) # Required for Matrix
			video_info_tag = list_item.getVideoInfoTag()
			video_info_tag.setTitle(title)
			video_info_tag.setPlot(description)
			video_info_tag.setDuration(duration)

			#log(f"[VIDEO]: found video menu: title='{title}' href='{url}'", xbmc.LOGDEBUG)
			directory_items.append((get_url(action="play", url=url), list_item, False))
			

		if directory_items:
			xbmcplugin.addDirectoryItems(HANDLE, directory_items, len(directory_items))
			xbmcplugin.setContent(HANDLE, 'episodes')

		xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
		xbmcplugin.endOfDirectory(HANDLE)
			
	except Exception as e:
		xbmc.log(f"[READ VIDEOS] Failed to load items from metalchris.video.nasaplus.json: {e}", xbmc.LOGERROR)
		
		
		
