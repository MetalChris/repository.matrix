# resources/lib/write_channels.py

import json
import xbmc
import xbmcvfs

SHARED_PATH = "special://userdata/addon_data/metalchris.shared/"
REFRESH_FILE = SHARED_PATH + "refresh.json"


def write_refresh_channels(channel_data):
    """
    channel_data format:
    {
        "709": {"name": "...", "logo": "..."},
        ...
    }
    """
    try:
        real_path = xbmcvfs.translatePath(SHARED_PATH)

        if not xbmcvfs.exists(real_path):
            xbmcvfs.mkdirs(real_path)

        file_path = xbmcvfs.translatePath(REFRESH_FILE)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(channel_data, f, indent=2)

        xbmc.log(f"[REFRESH] Wrote {len(channel_data)} channels to refresh.json", xbmc.LOGINFO)

    except Exception as e:
        xbmc.log(f"[REFRESH] Failed to write refresh.json: {e}", xbmc.LOGERROR)
