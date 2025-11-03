import xbmc
import xbmcgui

class PlayerMonitor(xbmc.Player):
    def __init__(self, epg_class):
        super().__init__()
        self.epg_class = epg_class   # reference to your EPGWindow class
        self.selection = 0

    def set_selection(self, index):
        self.selection = index

    def play(self, url, listitem):
        """Play media and let monitor track stop events."""
        super().play(url, listitem)

    def onPlayBackStopped(self):
        self._reopen_epg()

    def onPlayBackEnded(self):
        self._reopen_epg()

    def _reopen_epg(self):
        try:
            win = self.epg_class("script-epg.xml", xbmcaddon.Addon().getAddonInfo("path"))
            win.doModal()
            # restore selection if possible
            ctrl = win.getControl(9000)
            if ctrl and self.selection >= 0:
                try:
                    ctrl.selectItem(self.selection)
                except Exception:
                    xbmc.log("[DistroTV EPG] Failed to restore selection", xbmc.LOGWARNING)
        except Exception as e:
            xbmc.log(f"[DistroTV EPG] Error reopening EPG: {e}", xbmc.LOGERROR)
