import xbmc
import xbmcgui
import time
from resources.lib.logger import log


class PlayerMonitor(xbmc.Player):
    """
    Custom player monitor that listens for playback stop/end events
    while the EPG window remains open.
    Restores the window title and channel focus when playback finishes.
    """

    def __init__(self, epg_window):
        super().__init__()
        self.epg_window = epg_window
        log("[LG Channels EPG] [MONITOR] PlayerMonitor initialized and listening for playback events", xbmc.LOGINFO)

    def onPlayBackStopped(self):
        log("[LG Channels EPG] [MONITOR] Playback stopped — restoring EPG title and focus", xbmc.LOGINFO)
        self.restore_epg_state()

    def onPlayBackEnded(self):
        log("[LG Channels EPG] [MONITOR] Playback ended — restoring EPG title and focus", xbmc.LOGINFO)
        self.restore_epg_state()

    def restore_epg_state(self):
        """
        Restores the EPG window title and reselects the previously focused channel.
        Uses channel slug first, falling back to saved index if necessary.
        """
        if not self.epg_window:
            log("[LG Channels EPG] [MONITOR] No EPG window reference — cannot restore state", xbmc.LOGERROR)
            return

        try:
            # --- Retrieve saved title ---
            prop_title = (
                self.epg_window.getProperty("EPG_TITLE")
                or xbmc.getInfoLabel("Window.Property(EPG_TITLE)")
                or xbmc.getInfoLabel("System.Property(EPG_TITLE)")
                or "CW Live EPG"
            )

            # Reapply to both window and global props so it's retained for next time
            self.epg_window.setProperty("EPG_TITLE", prop_title)
            xbmc.executebuiltin(f'SetProperty(EPG_TITLE, {prop_title}, home)')

            heading_ctrl = self.epg_window.getControl(1)
            if heading_ctrl:
                heading_ctrl.setLabel(prop_title)
                log(f"[LG Channels EPG] [MONITOR] Restored EPG title: {prop_title}", xbmc.LOGDEBUG)
            else:
                log("[LG Channels EPG] [MONITOR] Heading control not found — could not restore title", xbmc.LOGWARNING)

            # --- Restore focus by slug ---
            last_slug = self.epg_window.getProperty("LAST_SELECTED_SLUG")
            restored = False
            ctrl = self.epg_window.getControl(9000)
            if ctrl and last_slug:
                restored = self._restore_focus_by_slug(ctrl, last_slug)

            # --- Fallback: restore by saved index ---
            if not restored:
                last_index = self.epg_window.getProperty("LAST_SELECTED_INDEX")
                if last_index is not None:
                    try:
                        index = int(last_index)
                        if 0 <= index < ctrl.size():
                            ctrl.selectItem(index)
                            log(f"[LG Channels EPG] [MONITOR] Focus restored to index {index} (fallback)", xbmc.LOGDEBUG)
                            restored = True
                    except Exception as e:
                        log(f"[LG Channels EPG] [MONITOR] Failed to restore focus by index: {e}", xbmc.LOGERROR)

            if not restored:
                log("[LG Channels EPG] [MONITOR] Could not restore focus — no matching slug or valid index", xbmc.LOGWARNING)

            # Final verification log
            heading_label = heading_ctrl.getLabel() if heading_ctrl else "N/A"
            log(f"[LG Channels EPG] [MONITOR] Verified/reapplied EPG title: {heading_label}", xbmc.LOGDEBUG)

        except Exception as e:
            log(f"[LG Channels EPG] [MONITOR] Error restoring EPG state: {e}", xbmc.LOGERROR)


    def _restore_focus_by_slug(self, ctrl, slug):
        """
        Selects the list item in 'ctrl' that has property SLUG == slug.
        Returns True if successful, False otherwise.
        """
        try:
            for i in range(ctrl.size()):
                item = ctrl.getListItem(i)
                if item and item.getProperty("channel_slug") == slug:
                    ctrl.selectItem(i)
                    log(f"[LG Channels EPG] [MONITOR] Focus restored to slug '{slug}' at index {i}", xbmc.LOGDEBUG)
                    return True
        except Exception as e:
            log(f"[LG Channels EPG] [MONITOR] _restore_focus_by_slug failed: {e}", xbmc.LOGERROR)
        return False
