import xbmcgui
import xbmcaddon

ADDON = xbmcaddon.Addon()

class EPGOverlay(xbmcgui.WindowXMLDialog):
    pass

def show_overlay():
    overlay = EPGOverlay(
        "MyEPGOverlay.xml",
        ADDON.getAddonInfo("path"),
        "Confluence",
        "720p"
    )
    overlay.doModal()
