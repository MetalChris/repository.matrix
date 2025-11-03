import xbmc
import xbmcgui

from resources.lib.uas import ua
from resources.lib.logger import log

def log_and_notify(message, title="Playback Error"):
    xbmc.log(f"[PLAYBACK] {message}", xbmc.LOGERROR)
    xbmcgui.Dialog().notification(title, message, xbmcgui.NOTIFICATION_ERROR, 5000, sound=False)


def play_episode_isa(title, url, image, epg_window=None):
    try:
        if not url:
            xbmcgui.Dialog().notification("LocalNow EPG", "No stream URL", xbmcgui.NOTIFICATION_ERROR, 3000, sound=False)
            return

        li = xbmcgui.ListItem(label=title)
        li.setArt({'icon': image, 'thumb': image})
        li.setInfo("video", {"title": title})
        li.setProperty("IsPlayable", "true")

        # InputStream properties
        try:
            li.setProperty("inputstream", "inputstream.adaptive")
            li.setProperty("inputstream.adaptive.manifest_type", "hls")
            li.setProperty('inputstream.adaptive.stream_headers', f"User-Agent={ua}")
            li.setProperty('inputstream.adaptive.manifest_headers', f"User-Agent={ua}")

            # --- LocalNow DRM handling for Mysterious Worlds ---
            if "Mysterious Worlds" in title or "localnow" in url.lower():
                license_url = (
                    "https://keyserver.cloudport.amagi.tv/MysteriousWorlds_LocalNow.key"
                    "|Referer=https%3A%2F%2Flocalnow.com%2F&User-Agent=Mozilla%2F5.0"
                )
                li.setProperty("inputstream.adaptive.license_type", "com.widevine.alpha")
                li.setProperty("inputstream.adaptive.license_key", license_url)

        except Exception as e:
            log(f"[PLAYBACK] Failed setting InputStream properties: {e}")

        xbmc.log(f"[PLAYBACK] Playing: {title} ({url[:120]})", xbmc.LOGINFO)
        try:
            xbmc.Player().play(item=url, listitem=li)
        except Exception as e:
            short_url = url.split('?')[0]  # keep only base URL
            log_and_notify(f"Failed to play {short_url}: {e}")

    except Exception as e:
        xbmc.log(f"[PLAYBACK] play_episode_isa failed: {e}", xbmc.LOGERROR)
