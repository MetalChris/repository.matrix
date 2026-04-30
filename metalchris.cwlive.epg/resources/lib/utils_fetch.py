import xbmc
import xbmcgui
import xbmcvfs
import urllib.request
import json
import time
import os
from xbmcaddon import Addon
import shutil
import requests
#from PIL import Image

s = requests.Session()

from resources.lib.logger import *
from resources.lib.uas import *
from resources.lib.get_items import *
from resources.lib.uas import ua
from resources.lib.get_items import *

log(f"[UTILS_FETCH] User-Agent: {(ua)}", xbmc.LOGDEBUG)

ADDON = Addon("metalchris.cwlive.epg")
apiUrl = 'https://data.cwtv.com/feed/app-2/landing/epg/page_1/pagesize_75/device_web/apiversion_24/cacheversion_202510142100'
FEED_URL = 'https://data.cwtv.com/feed/app-2/landing/epg/page_1/pagesize_75/device_web/apiversion_24/cacheversion_202510142100'

# Read TTL from settings (slider returns string → cast to int)
try:
	CACHE_TTL = int(ADDON.getSetting("cache_ttl")) * 60
except Exception:
	CACHE_TTL = 900  # fallback 15 min

log(f"[UTILS FETCH] Using cache TTL: {CACHE_TTL // 60} minutes", xbmc.LOGINFO)


# initialize cache dict so it's always available
_feed_cache = {
	"data": None,
	"timestamp": 0,
}

# Local cache paths
ADDON_ID = "metalchris.cwlive.epg"
PROFILE_PATH = xbmcvfs.translatePath(f"special://profile/addon_data/{ADDON_ID}/")
CACHE_DIR = os.path.join(PROFILE_PATH, "cache")
THUMBS_DIR = os.path.join(PROFILE_PATH, "thumbs")
desc_map_path = os.path.join(CACHE_DIR, "desc_map_programs_logo.json")
USERDATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
PRE_EPG = os.path.join(USERDATA_PATH,"cache/desc_map_programs_logo.json")
EPG = os.path.join(USERDATA_PATH,"cache/epg.json")

for path in [CACHE_DIR, THUMBS_DIR]:
	if not xbmcvfs.exists(path):
		xbmcvfs.mkdirs(path)

HEADERS = {"User-Agent": ua}

def _cache_path(name):
	return os.path.join(CACHE_DIR, name + ".json")


def build_genre_map(epg_data):
	"""Return {channel_id: genre} mapping from EPG JSON."""
	genre_map = {}
	channels = epg_data.get("channels", []) if isinstance(epg_data, dict) else epg_data

	for ch in channels:
		chan_id = ch.get("analytics_guid")# or ch.get("id") or ch.get("slug")
		#genre = ch.get("genre")
		genre = ch.get("genre")# or ch.get("category") or ""
		if chan_id and genre:
			genre_map[chan_id] = genre.strip()

	log(f"[GENRE_MAP] Built genre_map with {len(genre_map)} entries", xbmc.LOGDEBUG)
	#log(f"[GENRE_MAP] Built genre_map with: {(genre_map)} entries", xbmc.LOGDEBUG)
	return genre_map



def fetch_channel_descriptions(data):
	log(f"[UTILS FETCH] fetch_channel_descriptions started", xbmc.LOGDEBUG)

	if os.path.exists(desc_map_path):
		log(f"[UTILS FETCH] Cached desc_map_programs_logo.json exists", xbmc.LOGDEBUG)
		return

	desc_map_programs = {}
	try:
		channels = data.get("channel", [])
		log(f"Channels type: {type(channels)}", xbmc.LOGDEBUG)
		log(f"Channels length: {len(channels)}", xbmc.LOGDEBUG)

		for count, item in enumerate(data['channel']['item']):
			chan_id = str(item['number'])
			title = str(item['title'])
			slug = item['guid']['value']
			description = item['description']
			try:
				#desc_map_programs.append({
				desc_map_programs[chan_id] = {
					"chan_id": chan_id,
					"title": title,
					"slug": slug,
					"chan_desc": description,
					"programs_url":  apiUrl + 'channels/channel/' + slug + '/onnowandnext.json?f=asset.title&f=asset.descriptions',
					"logo": 'https://image.xumo.com/v1/channels/channel/' + slug + '/600x337.webp?type=channelTile'
				}
				#})
				#desc_map[int(chan_id)] = chan_desc
			except Exception:
				continue
		# --- Write JSON safely using xbmcvfs ---
		try:
			with open(desc_map_path, "w", encoding="utf-8") as f:
				json.dump(desc_map_programs, f, indent=2, ensure_ascii=False)
			log(f"[DESC_MAP] Saved {len(desc_map_programs)} channels to {desc_map_path}", xbmc.LOGDEBUG)
		except Exception as e:
			log(f"[DESC_MAP] Error saving desc_map.json: {e}", xbmc.LOGERROR)

	except Exception as e:
		log(f"[UTILS FETCH] Error building desc_map: {e}", xbmc.LOGERROR)

	return desc_map_programs


def get_channel_thumbs(data):
	"""Download channel thumbnails (JPG) using analytics_guid as ID."""
	try:
		thumbs_dir = THUMBS_DIR  # already defined globally
		os.makedirs(thumbs_dir, exist_ok=True)

		missing = []
		for channel in data.get("channels", []):
			#log(f"[THUMBS] Channel keys: {list(channel.keys())}", xbmc.LOGDEBUG)
			chan_id = channel.get("analytics_guid")
			img_url = channel.get("thumbnail_url", "").strip()
			#log(f"[THUMBS] {chan_id=} {img_url=}", xbmc.LOGDEBUG)

			if not chan_id or not img_url:
				continue

			local_jpg = os.path.join(thumbs_dir, f"{chan_id}.jpg")
			if not os.path.exists(local_jpg):
				missing.append((chan_id, img_url))

		log(f"[THUMBS] Found {len(missing)} missing thumbnails", xbmc.LOGDEBUG)


		if not missing:
			log("[THUMBS] All channel thumbnails already cached — skipping download", xbmc.LOGDEBUG)
			return

		total = len(missing)
		dlg = xbmcgui.DialogProgress()
		dlg.create("EPG", "Downloading channel thumbnails...")

		for i, (chan_id, img_url) in enumerate(missing, 1):
			if dlg.iscanceled():
				break

			local_jpg = os.path.join(thumbs_dir, f"{chan_id}.jpg")

			try:
				req = urllib.request.Request(img_url, headers=HEADERS)
				with urllib.request.urlopen(req, timeout=15) as resp:
					data_bytes = resp.read()
				with open(local_jpg, "wb") as out:
					out.write(data_bytes)
				log(f"[THUMBS] Downloaded thumbnail for {chan_id}", xbmc.LOGDEBUG)

			except Exception as e:
				log(f"[THUMBS] Failed to download {img_url}: {e}", xbmc.LOGWARNING)

			# Update progress bar every 10 items or on completion
			if i % 10 == 0 or i == total:
				pct = int((i / total) * 100)
				dlg.update(pct, f"Downloaded {i}/{total} thumbnails")

		dlg.close()
		xbmcgui.Dialog().notification(
			"EPG",
			f"Downloaded {total} new channel thumbnails",
			xbmcgui.NOTIFICATION_INFO,
			3000,
			sound=False
		)
		log(f"[THUMBS] Cached {total} new thumbnails", xbmc.LOGINFO)

	except Exception as e:
		log(f"[THUMBS] Error building thumbnail cache: {e}", xbmc.LOGERROR)


def fetch_all_episode_ids():
	ids = []
	try:
		feed = _get_feed()
		if not feed:
			log("[UTILS FETCH] No feed data available for fetch_all_episode_ids", xbmc.LOGERROR)
			return ids

		shows = feed.get("shows") if isinstance(feed, dict) else None
		if not shows:
			log("[UTILS FETCH] Feed has no 'shows' section", xbmc.LOGERROR)
			return ids

		for show_id, show in shows.items():
			for season in show.get("seasons", []):
				for ep in season.get("episodes", []):
					ep_id = ep.get("id")
					if ep_id:
						ids.append(ep_id)

		log(f"[UTILS FETCH] Collected {len(ids)} episode IDs", xbmc.LOGDEBUG)
		return ids

	except Exception as e:
		log(f"[UTILS FETCH] Error in fetch_all_episode_ids: {e}", xbmc.LOGERROR)
		return ids


def fetch_show_ids():
	show_ids = []
	try:
		feed = _get_feed()
		if not feed:
			log("[UTILS FETCH] No feed data available for fetch_show_ids", xbmc.LOGERROR)
			return show_ids

		shows = feed.get("shows") if isinstance(feed, dict) else None
		if not shows:
			log("[UTILS FETCH] Feed has no 'shows' section", xbmc.LOGERROR)
			return show_ids

		for show_id in shows.keys():
			show_ids.append(show_id)

		log(f"[UTILS FETCH] Collected {len(show_ids)} show IDs", xbmc.LOGDEBUG)
	except Exception as e:
		log(f"[UTILS FETCH] Error in fetch_show_ids: {e}", xbmc.LOGERROR)
	return show_ids


def debug_topics():
	try:
		feed = _get_feed()
		if not feed:
			log("[UTILS FETCH] No feed data available for debug_topics", xbmc.LOGERROR)
			return

		topics = feed.get("topics", [])
		log(f"[UTILS FETCH] Topics: {topics}", xbmc.LOGDEBUG)
	except Exception as e:
		log(f"[UTILS FETCH] Error in debug_topics: {e}", xbmc.LOGERROR)


def fetch_by_chanid(chan_id):
	try:
		feed = _get_feed()
		if not feed:
			log("[UTILS FETCH] No feed data available for fetch_by_chanid", xbmc.LOGERROR)
			return None

		shows = feed.get("shows") if isinstance(feed, dict) else None
		if not shows:
			log("[UTILS FETCH] Feed has no 'shows' section", xbmc.LOGERROR)
			return None

		for show_id, show in shows.items():
			for season in show.get("seasons", []):
				for ep in season.get("episodes", []):
					if ep.get("id") == chan_id:
						return ep
	except Exception as e:
		log(f"[UTILS FETCH] Error in fetch_by_chanid: {e}", xbmc.LOGERROR)
	return None


def _get_feed():
	"""Retrieve and cache the full feed."""
	now = time.time()
	if _feed_cache["data"] and (now - _feed_cache["timestamp"]) < CACHE_TTL:
		return _feed_cache["data"]

	try:
		response = s.get(LN_URL, headers = HEADERS)
		data = json.loads(response.text)

		_feed_cache["data"] = data
		_feed_cache["timestamp"] = now
		log("[UTILS FETCH][_get_feed] Feed refreshed from network", xbmc.LOGINFO)
		return data

	except Exception as e:
		log(f"[UTILS FETCH][_get_feed] Error fetching feed: {e}", xbmc.LOGERROR)
		return _feed_cache["data"]


def fetch_epg(url=None, ttl=None):
	"""
	Fetch EPG JSON with caching.
	TTL comes from update_interval setting (minutes).
	"""
	if ttl is None:
		ttl = CACHE_TTL
	if not url:
		log("[UTILS FETCH] No EPG URL provided to fetch_epg(); returning empty data.", xbmc.LOGWARNING)
		return {}

	cache_file = _cache_path("epg")
	now = time.time()

	# Try cache
	if xbmcvfs.exists(cache_file):
		try:
			with xbmcvfs.File(cache_file) as f:
				raw = f.read()
			obj = json.loads(raw)
			if now - obj.get("timestamp", 0) < ttl:
				log("[UTILS FETCH] Loaded EPG from cache", xbmc.LOGINFO)
				return obj.get("data", {})
		except Exception as e:
			log(f"[UTILS FETCH] Failed to read cache: {e}", xbmc.LOGWARNING)

	# Fetch fresh
	try:
		log(f"[UTILS FETCH] Fetching EPG from {url[:150]}", xbmc.LOGDEBUG)
		response = s.get(url, headers = HEADERS)
		log('[UTILS FETCH] FETCHING FROM: ' + str(url),xbmc.LOGDEBUG)
		log('[UTILS FETCH] RESPONSE CODE: ' + str(response.status_code),xbmc.LOGDEBUG)
		log('[UTILS FETCH] RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGDEBUG)
		data = json.loads(response.text)
		with xbmcvfs.File(cache_file, "w") as f:
			f.write(json.dumps({"timestamp": now, "data": data}))
		log("[UTILS FETCH][fetch_epg] Fetched and cached fresh EPG", xbmc.LOGINFO)
		return data
	except Exception as e:
		log(f"[UTILS FETCH] Error fetching EPG: {e}", xbmc.LOGERROR)
		return {}



def clear_cache():
	log(f"[CLEAR_CACHE] CACHE_DIR={CACHE_DIR}, exists={xbmcvfs.exists(CACHE_DIR)}, contents={os.listdir(CACHE_DIR) if os.path.exists(CACHE_DIR) else 'N/A'}")
	log(f"[CLEAR_CACHE] THUMBS_DIR={THUMBS_DIR}, exists={xbmcvfs.exists(THUMBS_DIR)}, contents={os.listdir(THUMBS_DIR) if os.path.exists(THUMBS_DIR) else 'N/A'}")

	"""Clear cached EPG JSON and channel logos manually."""
	try:
		# Delete JSON cache
		if os.path.exists(CACHE_DIR):
			log(f"[CLEAR_CACHE] EPG cache files: {os.listdir(CACHE_DIR)}")
			for f in os.listdir(CACHE_DIR):
				path = os.path.join(CACHE_DIR, f)
				if os.path.isfile(path):
					xbmcvfs.delete(path)

		# Delete thumbnails recursively
		if os.path.exists(THUMBS_DIR):
			log(f"[CLEAR_CACHE] Deleting thumbnails in {THUMBS_DIR}")
			shutil.rmtree(THUMBS_DIR, ignore_errors=True)
			# Re-create empty thumbs folder
			xbmcvfs.mkdirs(THUMBS_DIR)

		xbmcgui.Dialog().notification(
			"CW Live EPG",
			"Cache cleared",
			xbmcgui.NOTIFICATION_INFO,
			3000,
			sound=False
		)
		log("[CLEAR_CACHE] Manual cache clear completed", xbmc.LOGINFO)

	except Exception as e:
		log(f"[CLEAR_CACHE] Error clearing cache: {e}", xbmc.LOGERROR)


def clear_cache_and_refresh_thumbs():
	try:
		log("[CACHE] Starting clear and thumbnail download")

		# --- Step 1: Clear cached epg.json ---
		epg_file = os.path.join(CACHE_DIR, "epg.json")
		if os.path.exists(epg_file):
			xbmcvfs.delete(epg_file)
			log("[CACHE] epg.json deleted")

		# --- Step 2: Clear thumbs directory ---
		if os.path.exists(THUMBS_DIR):
			shutil.rmtree(THUMBS_DIR, ignore_errors=True)
		xbmcvfs.mkdirs(THUMBS_DIR)
		log("[CACHE] Thumbs directory cleared")

		# --- Step 3: Download thumbs and display progress bar ---

		try:
			feed = _get_feed()
			shows = feed.get("shows", {}) if isinstance(feed, dict) else {}

			all_eps = []
			for show in shows.values():
				img_url = show.get("img_logo") or show.get("img_thumbh") or ""
				if not img_url:
					continue
				for season in show.get("seasons", []):
					for ep in season.get("episodes", []):
						ep_id = ep.get("id")
						if ep_id:
							all_eps.append((ep_id, img_url))

			total = len(all_eps)
			if not total:
				log("[UTILS_FETCH] No episodes found in feed", xbmc.LOGWARNING)
				return

			dlg = xbmcgui.DialogProgress()
			dlg.create("CW Live EPG", "Downloading channel logos...")

			for i, (ep_id, img_url) in enumerate(all_eps, 1):
				if dlg.iscanceled():
					break

				local_file = os.path.join(THUMBS_DIR, f"{ep_id}.png")
				if not xbmcvfs.exists(local_file):
					try:
						with urllib.request.urlopen(img_url) as resp, open(local_file, "wb") as out:
							out.write(resp.read())
					except Exception as e:
						log(f"[UTILS_FETCH] Failed to download {img_url}: {e}", xbmc.LOGWARNING)

				# Update every 10 logos to reduce lag
				if i % 10 == 0 or i == total:
					pct = int((i / total) * 100)
					dlg.update(pct, f"Downloaded {i}/{total} logos")

			dlg.close()
			xbmcgui.Dialog().notification("CW Live EPG", "Cache refresh complete", xbmcgui.NOTIFICATION_INFO, 3000, sound=False)
			log(f"[UTILS_FETCH] Cached {total} channel logos", xbmc.LOGINFO)

		except Exception as e:
			log(f"[UTILS_FETCH] Error during first-run setup: {e}", xbmc.LOGERROR)


	except Exception as e:
		log(f"[CACHE] Error: {e}")
		try:
			dlg.close()
		except:
			pass
