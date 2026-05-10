import os
import json
import xbmc
import xbmcvfs

from resources.lib.logger import *

ADDON_DATA = xbmcvfs.translatePath(
    "special://profile/addon_data/service.metalchris.nasaplus/"
)

CACHE_FILE = os.path.join(ADDON_DATA, "cache.json")


def load_cache():

    if not xbmcvfs.exists(CACHE_FILE):
        log("Cache file does not exist", xbmc.LOGINFO)
        return {}

    try:
        with xbmcvfs.File(CACHE_FILE) as f:
            data = f.read()

        cache = json.loads(data)

        log("Cache loaded successfully", xbmc.LOGINFO)

        return cache

    except Exception as e:

        log(f"Cache load failed: {e}", xbmc.LOGERROR)

        return {}
        

def save_cache(cache_data):

    try:

        if not xbmcvfs.exists(ADDON_DATA):
            xbmcvfs.mkdirs(ADDON_DATA)

        data = json.dumps(cache_data)

        f = xbmcvfs.File(CACHE_FILE, "w")
        f.write(data)
        f.close()

        log("Cache saved successfully", xbmc.LOGINFO)

    except Exception as e:

        log(f"Cache save failed: {e}", xbmc.LOGERROR)
