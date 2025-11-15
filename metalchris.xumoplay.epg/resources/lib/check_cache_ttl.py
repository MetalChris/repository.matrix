import xbmc
import os
import time
import json
import xbmcvfs
from resources.lib.logger import log

def is_cache_stale(path, ttl_minutes):
    """
    Check if a cache file is older than ttl_minutes.
    Returns True if missing or expired.
    """
    try:
        if not xbmcvfs.exists(path):
            log(f"[CACHE] {os.path.basename(path)} missing", xbmc.LOGINFO)
            return True

        stat = xbmcvfs.Stat(path)
        # Use modification time (ctime unreliable on some OSes)
        mod_time = stat.st_mtime()
        age_minutes = (time.time() - mod_time) / 60

        if age_minutes > ttl_minutes:
            log(f"[CACHE] {os.path.basename(path)} expired ({int(age_minutes)} min old)", xbmc.LOGINFO)
            return True

        return False

    except Exception as e:
        log(f"[CACHE] Error checking cache age for {path}: {e}", xbmc.LOGERROR)
        return True
