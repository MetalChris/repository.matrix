import xbmc
import xbmcgui
import xbmcvfs
import urllib.request
import json
import time
import os
from xbmcaddon import Addon
import shutil

from resources.lib.logger import *

ADDON = Addon("metalchris.distrotv.epg")
FEED_URL = "https://tv.jsrdn.com/tv_v5/getfeed.php?type=live"

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
ADDON_ID = "metalchris.distrotv.epg"
PROFILE_PATH = xbmcvfs.translatePath(f"special://profile/addon_data/{ADDON_ID}/")
CACHE_DIR = os.path.join(PROFILE_PATH, "cache")
THUMBS_DIR = os.path.join(PROFILE_PATH, "thumbs")

for path in [CACHE_DIR, THUMBS_DIR]:
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdirs(path)


def _cache_path(name):
    return os.path.join(CACHE_DIR, name + ".json")


def build_genre_map(feed=None):
    genre_map = {}
    try:
        if feed is None:
            feed = _get_feed()
        if not feed:
            log("[UTILS FETCH] build_genre_map: no feed available", xbmc.LOGWARNING)
            return genre_map

        shows = feed.get("shows", {})
        for show_id, show in shows.items():
            genre = show.get("genre", "") or ""
            for season in show.get("seasons", []):
                for ep in season.get("episodes", []):
                    ep_id = ep.get("id")
                    if ep_id is None:
                        continue
                    try:
                        genre_map[int(ep_id)] = genre
                    except Exception:
                        continue

        log(f"[UTILS FETCH] Built genre_map with {len(genre_map)} entries", xbmc.LOGDEBUG)
    except Exception as e:
        log(f"[UTILS FETCH] Error building genre_map: {e}", xbmc.LOGERROR)

    return genre_map


def fetch_channel_descriptions(feed=None):
    desc_map = {}
    try:
        if feed is None:
            feed = _get_feed()
        if not feed:
            log("[UTILS FETCH] fetch_channel_descriptions: no feed available", xbmc.LOGWARNING)
            return desc_map

        shows = feed.get("shows", {})
        for show_id, show in shows.items():
            for season in show.get("seasons", []):
                for ep in season.get("episodes", []):
                    chan_id = ep.get("id")
                    chan_desc = ep.get("description")
                    if chan_id and chan_desc:
                        desc_map[int(chan_id)] = chan_desc
        log(f"[UTILS FETCH] Built channel description map with {len(desc_map)} entries", xbmc.LOGDEBUG)
    except Exception as e:
        log(f"[UTILS FETCH] Error fetching channel descriptions: {e}", xbmc.LOGERROR)
    return desc_map


def get_channel_thumbs():
    """
    Cache channel logos locally and return a chan_id → local_path map.
    Prefers img_logo, falls back to img_thumbh.
    Automatically cleans up stale logo files.
    """
    thumbs = {}
    try:
        feed = _get_feed()
        if not feed:
            log("[UTILS FETCH] No feed data available for thumbs", xbmc.LOGERROR)
            return thumbs

        shows = feed.get("shows") if isinstance(feed, dict) else None
        if not shows:
            log("[UTILS FETCH] Feed has no 'shows' section", xbmc.LOGERROR)
            return thumbs

        valid_ids = set()

        for show_id, show in shows.items():
            img_url = show.get("img_logo") or show.get("img_thumbh") or ""
            if not img_url:
                continue

            for season in show.get("seasons", []):
                for ep in season.get("episodes", []):
                    ep_id = ep.get("id")
                    if not ep_id:
                        continue

                    valid_ids.add(str(ep_id))
                    local_file = os.path.join(THUMBS_DIR, f"{ep_id}.png")

                    if not xbmcvfs.exists(local_file):
                        try:
                            with urllib.request.urlopen(img_url) as resp, open(local_file, "wb") as out:
                                out.write(resp.read())
                            #log(f"[UTILS FETCH] Cached logo for chan_id={ep_id}", xbmc.LOGDEBUG)
                        except Exception as e:
                            log(f"[UTILS FETCH] Failed to cache logo {img_url}: {e}", xbmc.LOGWARNING)
                            local_file = img_url  # fallback to URL
                    thumbs[ep_id] = local_file

        # Cleanup stale logo files
        try:
            for f in os.listdir(THUMBS_DIR):
                if f.endswith(".png"):
                    chan_id = f.replace(".png", "")
                    if chan_id not in valid_ids:
                        stale_file = os.path.join(THUMBS_DIR, f)
                        xbmcvfs.delete(stale_file)
                        log(f"[UTILS FETCH] Removed stale cached logo: {stale_file}", xbmc.LOGDEBUG)
        except Exception as e:
            log(f"[UTILS FETCH] Failed cleaning thumbs dir: {e}", xbmc.LOGWARNING)

        log(f"[UTILS FETCH] Collected {len(thumbs)} channel thumbnails", xbmc.LOGDEBUG)
    except Exception as e:
        log(f"[UTILS FETCH] Error building thumbs map: {e}", xbmc.LOGERROR)

    return thumbs


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
        with urllib.request.urlopen(FEED_URL, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)

        _feed_cache["data"] = data
        _feed_cache["timestamp"] = now
        log("[UTILS FETCH] Feed refreshed from network", xbmc.LOGINFO)
        return data

    except Exception as e:
        log(f"[UTILS FETCH] Error fetching feed: {e}", xbmc.LOGERROR)
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
        with urllib.request.urlopen(url, timeout=20) as response:
            data = json.load(response)
        with xbmcvfs.File(cache_file, "w") as f:
            f.write(json.dumps({"timestamp": now, "data": data}))
        log("[UTILS FETCH] Fetched and cached fresh EPG", xbmc.LOGINFO)
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
            "DistroTV EPG",
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
            dlg.create("DistroTV EPG", "Downloading channel logos...")

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
            xbmcgui.Dialog().notification("DistroTV EPG", "Cache refresh complete", xbmcgui.NOTIFICATION_INFO, 3000, sound=False)
            log(f"[UTILS_FETCH] Cached {total} channel logos", xbmc.LOGINFO)

        except Exception as e:
            log(f"[UTILS_FETCH] Error during first-run setup: {e}", xbmc.LOGERROR)


    except Exception as e:
        log(f"[CACHE] Error: {e}")
        try:
            dlg.close()
        except:
            pass
