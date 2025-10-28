import xbmc
import xbmcgui
import xbmcaddon

def run_merge_and_reopen():
    log("[MERGE] Running IPTV Merge externally", xbmc.LOGINFO)
    xbmcgui.Dialog().notification("EPG", "Updating sources via IPTV Merge...", xbmcgui.NOTIFICATION_INFO, 2000)

    # Run the merge add-on (this opens its GUI)
    xbmc.executebuiltin('RunAddon(plugin.program.iptv.merge)')

    # Wait until the user closes IPTV Merge before relaunching your EPG
    xbmc.Monitor().waitForAbort(5)  # optional short delay
    xbmc.executebuiltin('RunScript(special://home/addons/metalchris.frontend.epg/default.py)')
