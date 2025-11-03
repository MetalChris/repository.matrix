import xbmc
import xbmcgui

from resources.lib.uas import ua
from resources.lib.logger import log
from resources.lib.playback_utils import *

def play_episode_hls(title, url, image, epg_window=None):
    """
    Play a video stream directly without using InputStream Adaptive.
    """
    try:
        #title = ep.get("episode_title") or ep.get("title") or "Unknown"
        #desc  = ep.get("episode_description") or ep.get("description") or ""
        #url   = ep.get("content", {}).get("url")# + f"&User-Agent={ua}"
        #image = ep.get("img_thumbh")

        if not url:
            xbmcgui.Dialog().notification(
                "LocalNow EPG",
                "No stream URL",
                xbmcgui.NOTIFICATION_ERROR,
                3000,
                sound=False
            )
            return

        play_url = pre_play(url)

        # Create ListItem
        li = xbmcgui.ListItem(label=title)
        if image:
            li.setArt({'icon': image, 'thumb': image})
        li.setInfo("video", {"title": title})
        #li.setInfo("video", {"title": title, "plot": desc})
        li.setProperty("IsPlayable", "true")

        # Close the EPG window if one was passed
        #if epg_window:
            #try:
                #epg_window.close()
            #except Exception:
                #pass

        xbmc.log(f"[PLAYBACK] Playing directly: {title} ({url})", xbmc.LOGINFO)
        xbmc.Player().play(item=play_url, listitem=li)

    except Exception as e:
        xbmc.log(f"[PLAYBACK] play_episode failed: {e}", xbmc.LOGERROR)
