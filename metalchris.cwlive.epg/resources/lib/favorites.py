import json
import os
import xbmc
import xbmcaddon
import xbmcvfs
import time
from resources.lib.logger import log
from resources.lib.utils_fetch import *
from resources.lib.refresh import *

ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_DATA = xbmcvfs.translatePath(ADDON.getAddonInfo("profile"))
FAV_FILE = os.path.join(ADDON_DATA, "favorites.json")
# Local cache paths
ADDON_ID = "metalchris.cwlive.epg"
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

log(f"[FAVORITES] Using cache TTL: {CACHE_TTL // 60} minutes", xbmc.LOGDEBUG)

def _cache_path(name):
    return os.path.join(CACHE_DIR, name + ".json")


def fetch_favorites(fav_ids, epg_window):
    try:
        log(f"[DEBUG] refresh_epg_list called with FAVORITES_FILTER={epg_window.getProperty('FAVORITES_FILTER')}")

        # --- Load EPG data ---
        fav_filter = epg_window.getProperty("FAVORITES_FILTER")
        fav_ids = [s.strip() for s in fav_filter.split(",") if s.strip()] if fav_filter else None

        data = {}
        if fav_ids:
            # Load cached epg.json
            import xbmcaddon, os, json, xbmcvfs
            profile = xbmcaddon.Addon().getAddonInfo("profile")
            epg_path = os.path.join(profile, "cache", "epg.json")
            os_path = xbmcvfs.translatePath(epg_path)
            if xbmcvfs.exists(epg_path):
                log(f"[FAVORITES] epg_path exists", xbmc.LOGERROR)
                try:
                    with open(os_path, "r", encoding="utf-8") as fh:
                        cached = json.load(fh)
                        # Handle both old and new formats
                    if "channels" in cached and isinstance(cached["channels"], list):
                        # New format: channels is a list
                        epg_channels = cached["channels"]
                    elif "data" in cached and "channels" in cached["data"]:
                        # Old format: channels inside data
                        epg_channels = cached["data"]["channels"]
                    else:
                        epg_channels = []
                    # Build a lookup dict by channel_number (as string)
                    epg_dict = {str(ch.get("channel_number")): ch for ch in epg_channels if isinstance(ch, dict)}
                    #epg_dict = cached.get("data", {}).get("channels", [])
                    # Normalize fav_ids to strings
                    fav_ids = [str(cid) for cid in fav_ids]
                    # Filter only favorites that exist in EPG
                    data["channels"] = [epg_dict[cid] for cid in fav_ids if cid in epg_dict]

                    #data["channels"] = {cid: epg_dict[cid] for cid in fav_ids if cid in epg_dict}
                    kept = len(data['channels'])
                    log(f"[FAVORITES] Loaded {len(data['channels'])} favorite channels", xbmc.LOGDEBUG)

                    return(data)

                except Exception as e:
                    log(f"[FAVORITES] Failed reading cached epg.json: {e}", xbmc.LOGERROR)

        log(f"[FAVORITES] EPG list refreshed ({kept} channels)", xbmc.LOGDEBUG)

    except Exception as e:
        log(f"[FAVORITES] Error refreshing list: {e}", xbmc.LOGERROR)


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
        log(f"[FAVORITES] Saved {len(favs)} favorites", xbmc.LOGDEBUG)
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
            log(f"[FAVORITES] Channel '{chan_name}' ({chan_id}) already in favorites", xbmc.LOGDEBUG)
            return False

        # Add new channel
        favorites[chan_id] = {
            "name": chan_name,
            "logo": os.path.join(ADDON_DATA, "thumbs", f"{chan_id}.png")
        }

        # Save updated file
        with xbmcvfs.File(FAV_FILE, "w") as f:
            f.write(json.dumps(favorites, indent=2))

        log(f"[FAVORITES] Added channel '{chan_name}' ({chan_id}) to favorites", xbmc.LOGDEBUG)
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
    confirm = dlg.yesno("CW Live EPG", f"Are you sure you wish to remove {chan_name} from Favorites?")
    if not confirm:
        return False  # user cancelled

    # --- Remove from favorites ---
    del favs[chan_id]
    _save_favorites(favs)
    log(f"[FAVORITES] Removed {chan_id} ({chan_name}) from favorites", xbmc.LOGDEBUG)
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
