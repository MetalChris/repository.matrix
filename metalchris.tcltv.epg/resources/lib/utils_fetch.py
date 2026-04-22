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

s = requests.Session()

from resources.lib.logger import *
from resources.lib.uas import *

ADDON = Addon("metalchris.tcltv.epg")
FEED_URL = 'https://gateway-prod.ideonow.com/api/metadata/v1/epg/programlist'

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
ADDON_ID = "metalchris.tcltv.epg"
PROFILE_PATH = xbmcvfs.translatePath(f"special://profile/addon_data/{ADDON_ID}/")
CACHE_DIR = os.path.join(PROFILE_PATH, "cache")
THUMBS_DIR = os.path.join(PROFILE_PATH, "thumbs")
EPG_JSON = os.path.join(PROFILE_PATH, "cache", "epg.json")

for path in [CACHE_DIR, THUMBS_DIR]:
	if not xbmcvfs.exists(path):
		xbmcvfs.mkdirs(path)

HEADERS = {
	"User-Agent": "Mozilla/5.0 (Linux; Android 15; T702D Build/AP3A.240905.015.A2; wv)",
	"Accept": "application/json",
	"Referer": "https://tcltv.plus/"
}

def _cache_path(name):
	return os.path.join(CACHE_DIR, name + ".json")


def build_category_map():
	"""
	Build a mapping of category -> list of channel IDs from the cached TCL EPG.
	"""
	category_map = {}

	try:
		if not xbmcvfs.exists(EPG_JSON):
			log("[UTILS_FETCH][build_category_map] EPG JSON not found", xbmc.LOGWARNING)
			return category_map

		with open(EPG_JSON, "r", encoding="utf-8") as f:
			epg_data = json.load(f)

		# --- Normalize structure ---
		if isinstance(epg_data, str):
			epg_data = json.loads(epg_data)

		if isinstance(epg_data, dict):
			epg_data = epg_data.get("data") or epg_data.get("categories") or []

		if not isinstance(epg_data, list):
			log("[UTILS_FETCH][build_category_map] Unexpected JSON structure", xbmc.LOGERROR)
			return category_map

		# --- Build map ---
		for category in epg_data:
			if not isinstance(category, dict):
				continue

			cat_name = category.get("category")
			if not cat_name:
				continue

			for ch in category.get("channels", []):
				if not isinstance(ch, dict):
					continue

				channel_id = str(ch.get("id"))
				if channel_id:
					category_map.setdefault(cat_name, set()).add(channel_id)

		# Convert sets → lists (keep compatibility with rest of addon)
		category_map = {k: list(v) for k, v in category_map.items()}

		log(f"[UTILS_FETCH][build_category_map] Built category map with {len(category_map)} categories", xbmc.LOGDEBUG)

	except Exception as e:
		log(f"[UTILS_FETCH][build_category_map] Error building category map: {e}", xbmc.LOGERROR)

	return category_map


def fetch_channel_descriptions(data):
	desc_map = {}
	try:
		channels = data.get("channels", [])
		log(f"Channels type: {type(channels)}", xbmc.LOGDEBUG)
		# If channels is a dict, convert to list of values
		if isinstance(channels, dict):
			channels = channels.values()

		for channel in channels:
			chan_desc = channel.get("description", "") if isinstance(channel, dict) else ""
			chan_id = channel.get("channelNumber", "") if isinstance(channel, dict) else ""
			try:
				desc_map[int(chan_id)] = chan_desc
			except Exception:
				continue

		log(f"[UTILS FETCH] Built desc_map with {len(desc_map)} entries", xbmc.LOGDEBUG)
	except Exception as e:
		log(f"[UTILS FETCH] Error building desc_map: {e}", xbmc.LOGERROR)

	return desc_map


def get_channel_thumbs():
    try:
        addon = xbmcaddon.Addon()
        profile_path = xbmcvfs.translatePath(addon.getAddonInfo("profile"))
        cache_file = os.path.join(profile_path, "cache", "epg.json")
        thumbs_dir = os.path.join(profile_path, "thumbs")

        if not xbmcvfs.exists(thumbs_dir):
            xbmcvfs.mkdirs(thumbs_dir)

        with open(cache_file, "r", encoding="utf-8") as f:
            epg_data = json.load(f)

        # --- FIX 1: TCL/LG safe data extraction ---
        data = epg_data.get("data", [])
        if isinstance(data, dict):
            categories = data.get("categories", [])
        else:
            categories = data

        if not categories:
            log("[UTILS_FETCH][get_channel_thumbs] No categories found", xbmc.LOGERROR)
            return

        all_eps = []

        # --- FIX 2: proper iteration ---
        for category in categories:
            if not isinstance(category, dict):
                continue

            for channel in category.get("channels", []):
                if not isinstance(channel, dict):
                    continue

                raw_id = channel.get("channelNumber") or channel.get("id")
                chan_id = str(raw_id) if raw_id not in (None, "", "None") else ""

                raw_img = (
                    channel.get("channelLogoUrl") or
					channel.get("poster_h_small") or             # TCL (small 16x9)
					channel.get("logo_color") or             # TCL (small box)
                    channel.get("image") or ""
                )

                # FIX 3: safe URL handling
                if raw_img.startswith("http"):
                    img_url = raw_img
                elif raw_img:
                    img_url = "https://tcl-channel-cdn.ideonow.com" + raw_img
                else:
                    img_url = ""

                if chan_id and img_url:
                    all_eps.append((chan_id, img_url))

        total = len(all_eps)
        if total == 0:
            log("[UTILS_FETCH][get_channel_thumbs] No valid channels found", xbmc.LOGWARNING)
            return

        dlg = xbmcgui.DialogProgress()
        dlg.create("TCLTV+ EPG", f"Downloading {total} channel logos...")

        for i, (num, logo_url) in enumerate(all_eps, start=1):
            if dlg.iscanceled():
                break

            local_path = os.path.join(thumbs_dir, f"{num}.png")

            if xbmcvfs.exists(local_path):
                continue

            try:
                req = urllib.request.Request(logo_url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()

                with xbmcvfs.File(local_path, "wb") as f:
                    f.write(data)

            except Exception as e:
                log(f"[UTILS_FETCH] Failed {logo_url}: {e}", xbmc.LOGWARNING)

            if i % 10 == 0 or i == total:
                pct = int((i / total) * 100)
                dlg.update(pct, f"Downloaded {i}/{total}")

        dlg.close()

    except Exception as e:
        log(f"[UTILS_FETCH][get_channel_thumbs] Unexpected error: {e}", xbmc.LOGERROR)

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
		#req = urllib.request.Request(FEED_URL, headers=HEADERS)
		#with urllib.request.urlopen(req, timeout=15) as resp:
		resp = s.get(FEED_URL, headers = HEADERS)
		#raw = resp.read().decode("utf-8")
		data = json.loads(resp.text)

		_feed_cache["data"] = data
		_feed_cache["timestamp"] = now
		log("[UTILS FETCH][_get_feed] Feed refreshed from network", xbmc.LOGDEBUG)
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
				log("[UTILS FETCH][fetch_epg] Loaded EPG from cache", xbmc.LOGINFO)
				return obj.get("data", {})
		except Exception as e:
			log(f"[UTILS FETCH][fetch_epg] Failed to read cache: {e}", xbmc.LOGWARNING)

	# Fetch fresh
	try:
		log(f"[UTILS FETCH][fetch_epg] Fetching EPG from {url[:150]}", xbmc.LOGINFO)
		response = s.get(url, headers = HEADERS)
		#response = s.get(TylerUrl, headers = {'User-Agent': ua})
		log('[UTILS FETCH][fetch_epg] FETCHING FROM: ' + str(url),xbmc.LOGDEBUG)
		log('[UTILS FETCH][fetch_epg] RESPONSE CODE: ' + str(response.status_code),xbmc.LOGDEBUG)
		log('[UTILS FETCH][fetch_epg] RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGDEBUG)
		data = json.loads(response.text)
		with xbmcvfs.File(cache_file, "w") as f:
			f.write(json.dumps({"timestamp": now, "data": data}))
		log("[UTILS FETCH][fetch_epg] Fetched and cached fresh EPG", xbmc.LOGINFO)
		return data
	except Exception as e:
		log(f"[UTILS FETCH][fetch_epg] Error fetching EPG: {e}", xbmc.LOGERROR)
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
			"TCLTV+ EPG",
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
			dlg.create("TCLTV+ EPG", "Downloading channel logos...")

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
			xbmcgui.Dialog().notification("TCLTV+ EPG", "Cache refresh complete", xbmcgui.NOTIFICATION_INFO, 3000, sound=False)
			log(f"[UTILS_FETCH] Cached {total} channel logos", xbmc.LOGINFO)

		except Exception as e:
			log(f"[UTILS_FETCH] Error during first-run setup: {e}", xbmc.LOGERROR)


	except Exception as e:
		log(f"[CACHE] Error: {e}")
		try:
			dlg.close()
		except:
			pass
