import json
import os
import xbmc
import xbmcaddon
import xbmcvfs
import time
from resources.lib.logger import log
from resources.lib.utils_fetch import *
from resources.lib.build_items import *
from resources.lib.refresh import *

ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_DATA = xbmcvfs.translatePath(ADDON.getAddonInfo("profile"))
FAV_FILE = os.path.join(ADDON_DATA, "favorites.json")
# Local cache paths
ADDON_ID = "metalchris.distrotv.epg"
PROFILE_PATH = xbmcvfs.translatePath(f"special://profile/addon_data/{ADDON_ID}/")
CACHE_DIR = os.path.join(PROFILE_PATH, "cache")
THUMBS_DIR = os.path.join(PROFILE_PATH, "thumbs")

for path in [CACHE_DIR, THUMBS_DIR]:
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdirs(path)

# Read TTL from settings (slider returns string → cast to int)
try:
    CACHE_TTL = int(ADDON.getSetting("cache_ttl")) * 60
except Exception:
    CACHE_TTL = 900  # fallback 15 min

log(f"[FAVORITES] Using cache TTL: {CACHE_TTL // 60} minutes", xbmc.LOGINFO)

def _cache_path(name):
    return os.path.join(CACHE_DIR, name + ".json")


def fetch_favorites(url, ttl=None):
    """
    Fetch EPG JSON with caching.
    TTL comes from update_interval setting (minutes).
    """
    if ttl is None:
        ttl = CACHE_TTL
    if not url:
        log("[FAVORITES] No EPG URL provided to fetch_epg(); returning empty data.", xbmc.LOGWARNING)
    #return {}

    cache_file = _cache_path("fav_epg")
    now = time.time()

    # Fetch fresh
    try:
        log(f"[FAVORITES] Fetching EPG from {url[:150]}", xbmc.LOGINFO)
        with urllib.request.urlopen(url, timeout=20) as response:
            data = json.load(response)
        with xbmcvfs.File(cache_file, "w") as f:
            f.write(json.dumps({"timestamp": now, "data": data}))
        log("[FAVORITES] Fetched and cached fresh EPG", xbmc.LOGINFO)
        #return data
    except Exception as e:
        log(f"[FAVORITES] Error fetching EPG: {e}", xbmc.LOGERROR)
    #return {}
    log(f"[FAVORITES] Passing to build_items", xbmc.LOGINFO)

    thumbs_map = get_channel_thumbs()
    desc_map   = fetch_channel_descriptions()
    genre_map  = build_genre_map()

    win = xbmcgui.Window(10025)
    if ADDON.getSettingBool("remember_genre"):
        last_genre = ADDON.getSetting("last_genre")
        if last_genre:
            win.setProperty("distro_epg_genre_filter", last_genre)


    listitems, kept, title = build_items(data, thumbs_map, desc_map, genre_map)


def _load_favorites():
    """Load favorites dict from file (or return empty)."""
    try:
        if not xbmcvfs.exists(FAV_FILE):
            return {}
        with xbmcvfs.File(FAV_FILE) as f:
            data = f.read()
            if not data:
                return {}
            return json.loads(data)
    except Exception as e:
        log(f"[FAVORITES] Failed to load favorites: {e}", xbmc.LOGERROR)
        return {}

def _save_favorites(favs):
    """Save dict to file."""
    try:
        with xbmcvfs.File(FAV_FILE, "w") as f:
            f.write(json.dumps(favs, indent=2))
        log(f"[FAVORITES] Saved {len(favs)} favorites", xbmc.LOGINFO)
    except Exception as e:
        log(f"[FAVORITES] Failed to save favorites: {e}", xbmc.LOGERROR)

def add_favorite(chan_id, chan_name, logo_path):
    """
    Add a channel to favorites.json if not already present.
    """
    try:
        # Make sure the directory exists
        if not xbmcvfs.exists(ADDON_DATA):
            xbmcvfs.mkdirs(ADDON_DATA)

        # Load existing favorites
        favorites = {}
        if xbmcvfs.exists(FAV_FILE):
            try:
                with xbmcvfs.File(FAV_FILE, "r") as f:
                    raw = f.read()
                    if raw:
                        favorites = json.loads(raw)
            except Exception as e:
                log(f"[FAVORITES] Failed to load favorites.json: {e}", xbmc.LOGWARNING)
                favorites = {}

        # Avoid duplicates
        if chan_id in favorites:
            log(f"[FAVORITES] Channel '{chan_name}' ({chan_id}) already in favorites", xbmc.LOGINFO)
            return False

        # Add new channel
        favorites[chan_id] = {
            "name": chan_name,
            "logo": os.path.join(ADDON_DATA, "thumbs", f"{chan_id}.png")
        }

        # Save updated file
        with xbmcvfs.File(FAV_FILE, "w") as f:
            f.write(json.dumps(favorites, indent=2))

        log(f"[FAVORITES] Added channel '{chan_name}' ({chan_id}) to favorites", xbmc.LOGINFO)
        return True

    except Exception as e:
        log(f"[FAVORITES] Error adding favorite: {e}", xbmc.LOGERROR)
        return False


def remove_favorite(chan_id):
    """Remove channel from favorites with confirmation dialog."""
    favs = _load_favorites()
    if chan_id not in favs:
        return False

    chan_name = favs[chan_id].get("name") or "Unknown Channel"

    # --- Confirmation dialog ---
    dlg = xbmcgui.Dialog()
    confirm = dlg.yesno("DistroTV EPG", f"Are you sure you wish to remove {chan_name} from Favorites?")
    if not confirm:
        return False  # user cancelled

    # --- Remove from favorites ---
    del favs[chan_id]
    _save_favorites(favs)
    log(f"[FAVORITES] Removed {chan_id} ({chan_name}) from favorites", xbmc.LOGINFO)
    return True

def list_favorites():
    """Return dict of all favorites."""
    return _load_favorites()

def has_favorites():
    """Check if favorites file exists and has entries."""
    favs = _load_favorites()
    return bool(favs)

def get_favorite_ids():
    fav_file = os.path.join(ADDON_DATA, "favorites.json")
    if not xbmcvfs.exists(fav_file):
        return []
    try:
        with open(fav_file, "r") as f:
            data = json.load(f)
        return list(data.keys())
    except Exception as e:
        log(f"[FAVORITES] Error loading favorites: {e}", xbmc.LOGERROR)
        return []
