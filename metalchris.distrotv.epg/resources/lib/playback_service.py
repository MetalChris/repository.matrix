import xbmc
import xbmcgui

from resources.lib.uas import *

#UA = "your-user-agent-here"

def play(url, title=""):
    if not url:
        xbmcgui.Dialog().notification(
            "DistroTV",
            "Missing stream URL",
            xbmcgui.NOTIFICATION_ERROR
        )
        return

    li = xbmcgui.ListItem(label=title, path=url)

    # InputStream Adaptive setup
    li.setProperty("inputstream", "inputstream.adaptive")
    li.setProperty("inputstream.adaptive.manifest_type", "hls")

    # UA only (keep it simple for now)
    li.setProperty(
        "inputstream.adaptive.stream_headers",
        f"User-Agent={ua}"
    )
    li.setProperty(
        "inputstream.adaptive.manifest_headers",
        f"User-Agent={ua}"
    )

    li.setMimeType("application/vnd.apple.mpegurl")
    li.setContentLookup(False)

    xbmc.log("PLAYBACK SERVICE: starting stream", xbmc.LOGINFO)

    xbmc.Player().play(url, li)
