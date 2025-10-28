import xbmc
import xbmcgui
from resources.lib.logger import log
import xbmcaddon

ADDON = xbmcaddon.Addon()

def safe_play(ep, epg_window=None):
    """
    Attempt playback using the user’s preferred method (ISA or HLS).
    Falls back automatically if ISA fails.
    """
    use_ISA = ADDON.getSettingBool("use_ISA")
    title = ep.get("episode_title") or ep.get("title") or "Unknown"

    try:
        if use_ISA:
            from resources.lib.playback_ISA import play_episode
        else:
            from resources.lib.playback_HLS import play_episode

        play_episode(ep, epg_window)

    except Exception as e:
        log(f"[PLAYBACK] Error using {'ISA' if use_ISA else 'HLS'}: {e}", xbmc.LOGERROR)
        if use_ISA:
            xbmcgui.Dialog().notification(
                "DistroTV EPG",
                "ISA playback failed — retrying without InputStream Adaptive",
                xbmcgui.NOTIFICATION_WARNING,
                3000,
                sound=False
            )
            try:
                from resources.lib.playback_HLS import play_episode
                play_episode(ep, epg_window)
            except Exception as e2:
                log(f"[PLAYBACK] Fallback HLS also failed: {e2}", xbmc.LOGERROR)
                xbmcgui.Dialog().notification(
                    "DistroTV EPG",
                    "Playback failed",
                    xbmcgui.NOTIFICATION_ERROR,
                    3000,
                    sound=False
                )
