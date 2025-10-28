import xbmc
import xbmcaddon
import xbmcvfs
import os

from resources.lib.logger import *

ADDON      = xbmcaddon.Addon()
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo("path"))
EPG_MODE = ADDON.getSetting("epg_mode")  # "Panel" or "Fullscreen"

def get_skin_name():
    """
    Return the current Kodi skin directory.
    Falls back to 'skin.estuary' if detection fails.
    """
    try:
        return xbmc.getSkinDir()
    except Exception:
        return "skin.estuary"


def get_epg_skin_file():
    """
    Resolve the path to the EPG XML file based on current skin.
    Falls back to Estuary if missing.
    Returns (xml_file, theme).
    """
    current_skin = get_skin_name()
    log(f"[SKIN UTILS] Kodi skin ID: {current_skin}", xbmc.LOGINFO)

    skin_map = {
        "skin.estuary": "Estuary",
        "skin.confluence": "Confluence"
    }

    if current_skin not in skin_map:
        log(f"[SKIN UTILS] WARNING: Skin '{current_skin}' not mapped, falling back to Estuary", xbmc.LOGWARNING)

    theme = skin_map.get(current_skin, "Estuary")

    skin_path = os.path.join(ADDON_PATH, "resources", "skins", theme, "720p")
    XML_FILE = "panel.xml" if EPG_MODE == '0' else "full-screen.xml"
    log(f"[SKIN_UTILS] EPG_MODE: {EPG_MODE}", xbmc.LOGDEBUG)
    log(f"[SKIN_UTILS] XML_FILE: {XML_FILE}", xbmc.LOGDEBUG)
    full_xml_path = os.path.join(skin_path, XML_FILE)

    if not os.path.exists(full_xml_path):
        log(f"[SKIN UTILS] XML not found at {full_xml_path}, falling back to Estuary", xbmc.LOGWARNING)
        theme = "Estuary"
        skin_path = os.path.join(ADDON_PATH, "resources", "skins", theme, "720p")
        full_xml_path = os.path.join(skin_path, XML_FILE)

    if not os.path.exists(full_xml_path):
        log(f"[SKIN UTILS] ERROR: XML file still not found at {full_xml_path}", xbmc.LOGERROR)
        return None, None

    log(f"[SKIN UTILS] Using theme folder: {theme}", xbmc.LOGDEBUG)
    log(f"[SKIN UTILS] Loading XML: {full_xml_path}", xbmc.LOGINFO)

    return XML_FILE, theme
