import xbmc
import os
import time
import json
import xbmcvfs
from resources.lib.logger import log

ttl_minutes = 80

def is_cache_stale(path):
	"""
	Check if a cache file is older than ttl_minutes.
	Returns True if missing or expired.
	"""
	try:
		if not xbmcvfs.exists(path):
			log(f"[CACHE] {os.path.basename(path)} missing", xbmc.LOGINFO)
			return True

		stat = xbmcvfs.Stat(path)
		mod_time = stat.st_mtime()
		age_minutes = int((time.time() - mod_time) / 60)
		log(f"[CACHE] file age: {age_minutes}", xbmc.LOGINFO)	
		

		if age_minutes > int(ttl_minutes):
			log(f"[CACHE] {os.path.basename(path)} expired ({int(age_minutes)} min old)", xbmc.LOGINFO)
			return True

		return False

	except Exception as e:
		log(f"[CACHE] Error checking cache age for {path}: {e}", xbmc.LOGERROR)
		return True
