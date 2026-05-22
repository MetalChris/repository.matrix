import xbmcgui
import xbmcaddon
import xbmcvfs
import os
import sys
import json
import threading
import hashlib
import time
import requests

from resources.lib.convert_to_local import *
from resources.lib.logger import *

ADDON      = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
MEDIA_PATH = os.path.join(ADDON_PATH, "resources", "media")

ICON   = os.path.join(MEDIA_PATH, "icon.png")
FANART = os.path.join(MEDIA_PATH, "fanart.jpg")

BASE_URL = "https://plus.nasa.gov"
HANDLE = int(sys.argv[1])

# Cache TTLs (time-to-live in seconds)
PAGE_CACHE_TTLS = [
    3600,
    3600 * 6,
    3600 * 12,
    3600 * 24,
    3600 * 24 * 7
]

DESC_CACHE_TTLS = [
    3600 * 24,
    3600 * 24 * 7,
    3600 * 24 * 30,
    3600 * 24 * 90,
    3600 * 24 * 365,
    999999999
]

def get_setting_index(setting_id, default=0):
    try:
        value = ADDON.getSetting(setting_id)
        return int(value) if value != "" else default
    except Exception:
        return default

CACHE_TTL_PAGES = PAGE_CACHE_TTLS[
    get_setting_index("page_cache_ttl")
]

CACHE_TTL_DESCRIPTIONS = DESC_CACHE_TTLS[
    get_setting_index("desc_cache_ttl")
]

# Cache setup
PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
CACHE_DIR = os.path.join(PROFILE_PATH, 'cache')
if not xbmcvfs.exists(CACHE_DIR):
	xbmcvfs.mkdirs(CACHE_DIR)
CACHE_FILE = os.path.join(CACHE_DIR, 'nasa_plus_cache.json')

#CACHE_TTL_PAGES = 3600 * 6            # 6 hours for HTML pages
#CACHE_TTL_DESCRIPTIONS = 999999999 # 31.7 years #3600 * 24 * 7   # 7 days for series descriptions
#CACHE_TTL_DESCRIPTIONS = 60 * 2	# 2 minutes for testing

# In-memory cache state for this addon run
CACHE_LOCK = threading.Lock()
CACHE_DATA = {}
CACHE_LOADED = False
CACHE_DIRTY = False

	
    
log(f"[{ADDON_NAME}] PAGE CACHE: {fmt_ttl(CACHE_TTL_PAGES)}", xbmc.LOGINFO)
log(f"[{ADDON_NAME}] DESC CACHE: {fmt_ttl(CACHE_TTL_DESCRIPTIONS)}", xbmc.LOGINFO)
#log(f"[{ADDON_NAME} v{ADDON_VERSION}] [ADD-ON RUNNING]", xbmc.LOGINFO)

# -------------------
# Helpers
# -------------------
		
		
def normalize_html(html):
	return " ".join(html.split())


def compute_hash(value, normalize=False):
	if not isinstance(value, str):
		return None
	if normalize:
		value = normalize_html(value)
	return hashlib.sha1(value.encode()).hexdigest()


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
			'created': time.time(),
			'value': value,
			'expires': time.time() + ttl,
			'hash': hashlib.sha1(normalize_html(value).encode()).hexdigest() if isinstance(value, str) else None
		}
		CACHE_DIRTY = True


def cache_set_many(entries, ttl):
	log(f"[CACHE WRITE] {len(entries)} entries (ttl={ttl})", xbmc.LOGDEBUG)
	"""Store many cache entries in one lock/write cycle."""
	global CACHE_DIRTY
	now = time.time()
	with CACHE_LOCK:
		_cache_ensure_loaded()
		for key, value in entries.items():
			CACHE_DATA[key] = {
				'created': time.time(),
				'value': value,
				'expires': time.time() + ttl,
				'hash': hashlib.sha1(normalize_html(value).encode()).hexdigest() if isinstance(value, str) else None
			}
		CACHE_DIRTY = True
		
		
def cache_get_with_meta(key):
	with CACHE_LOCK:
		_cache_ensure_loaded()

		entry = CACHE_DATA.get(key)

		if not entry:
			log("[TEST] NO ENTRY", xbmc.LOGDEBUG)
			return None, None, True

		expired = entry.get('expires', 0) <= time.time()

		log(
			f"[CACHE] key={key[:20]}... expired={expired}",
			xbmc.LOGDEBUG
		)

		created = entry.get('created')
		expires = entry.get('expires')
		expired = entry.get('expires', 0) <= time.time()

		age = int(time.time() - created) if created else None

		log(
			f"[CACHE] key={key[:20]}... "
			f"created={fmt_time(created)} "
			f"expires={fmt_time(expires)} "
			f"age={age}s "
			f"expired={expired} "
			f"has_hash={'hash' in entry}",
			xbmc.LOGDEBUG
		)

		return entry.get('value'), entry, expired

		return entry.get('value'), entry, expired


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


def clear_cache():
	try:
		if xbmcvfs.exists(CACHE_FILE):
			xbmcvfs.delete(CACHE_FILE)

		# Optional: wipe entire cache directory instead
		# if xbmcvfs.exists(CACHE_DIR):
		#     shutil.rmtree(CACHE_DIR)
		#     xbmcvfs.mkdirs(CACHE_DIR)

		xbmcgui.Dialog().notification(
			"NASA+",
			"Cache cleared",
			ICON,
			3000
		)

	except Exception as e:
		log(f"[CACHE] Clear failed: {e}")
		xbmcgui.Dialog().notification(
			"NASA+ ERROR",
			"Failed to clear cache",
			ICON,
			3000
		)
