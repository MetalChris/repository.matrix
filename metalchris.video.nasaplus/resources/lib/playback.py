import xbmcgui
import xbmcaddon
import xbmcplugin
import os
import sys

from resources.lib.logger import *
from resources.lib.fetching import *

ADDON      = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
MEDIA_PATH = os.path.join(ADDON_PATH, "resources", "media")

ICON   = os.path.join(MEDIA_PATH, "icon.png")
FANART = os.path.join(MEDIA_PATH, "fanart.jpg")

HANDLE = int(sys.argv[1])

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
