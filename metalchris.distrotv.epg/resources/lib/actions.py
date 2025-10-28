import xbmc
import xbmcgui
import xbmcaddon
from resources.lib.utils_fetch import fetch_by_chanid
from resources.lib.playback_hls import play_episode_hls
from resources.lib.playback_isa import play_episode_isa
from resources.lib.logger import *

ADDON = xbmcaddon.Addon()

def handle_action(epg_window, action):
    """
    Handle actions (back, context menu, enter/play) for the EPG window.
    """
    action_id = action.getId()

    # Close on back/escape
    if action_id in (9, 10, 92, 216):
        epg_window.close()
        return

    # Context menu
    if action_id == xbmcgui.ACTION_CONTEXT_MENU:
        epg_window.show_context_menu()
        return

    # OK / Enter -> playback
    if action_id in (7, 100):
        try:
            ctrl = epg_window.getControl(9000)
            if ctrl is None:
                xbmc.log("[ACTIONS] getControl(9000) returned None", xbmc.LOGERROR)
                return

            pos = ctrl.getSelectedPosition()
            if pos is None or pos < 0:
                xbmc.log("[ACTIONS] No list item selected", xbmc.LOGWARNING)
                return

            li = ctrl.getListItem(pos)
            if li is None:
                xbmc.log(f"[ACTIONS] getListItem returned None for pos {pos}", xbmc.LOGWARNING)
                return

            chan_id = li.getProperty("channel_id") or li.getProperty("chan_id") or li.getProperty("episode_id")
            if not chan_id:
                xbmc.log("[ACTIONS] ListItem missing chan_id property", xbmc.LOGWARNING)
                xbmcgui.Dialog().notification("DistroTV EPG", "Channel ID missing", xbmcgui.NOTIFICATION_INFO, 3000, sound=False)
                return

            try:
                chan_id_int = int(chan_id)
            except Exception:
                xbmc.log(f"[ACTIONS] chan_id not an integer: {chan_id!r}", xbmc.LOGERROR)
                xbmcgui.Dialog().notification("DistroTV EPG", "Bad channel id", xbmcgui.NOTIFICATION_ERROR, 3000, sound=False)
                return

            ep = fetch_by_chanid(chan_id_int)
            if ep:
                title = ep.get("episode_title") or ep.get("title") or "Unknown"
                url   = ep.get("content", {}).get("url")

                if url:
                    use_isa = ADDON.getSettingBool("use_isa")
                    xbmc.log(f"[ACTIONS] Playing {title} from {url}", xbmc.LOGINFO)
                    if use_isa:
                        play_episode_isa(ep, epg_window)
                    else:
                        play_episode_hls(ep, epg_window)


                    log(f"[ACTIONS] Playback Using {'InputStream Adaptive' if use_isa else 'native HLS (FFmpeg)'}", xbmc.LOGINFO)

                else:
                    xbmc.log(f"[ACTIONS] No content URL in episode {title}", xbmc.LOGWARNING)
                    xbmcgui.Dialog().notification("DistroTV EPG", "No stream URL", xbmcgui.NOTIFICATION_ERROR, 3000, sound=False)
            else:
                xbmc.log(f"[ACTIONS] No episode match for chan_id={chan_id_int}", xbmc.LOGINFO)
                xbmcgui.Dialog().notification("DistroTV EPG", "No match found", xbmcgui.NOTIFICATION_INFO, 3000, sound=False)

        except Exception as exc:
            xbmc.log(f"[ACTIONS] Error handling OK action: {exc}", xbmc.LOGERROR)
