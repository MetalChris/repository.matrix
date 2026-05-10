import xbmcgui
import os

from resources.lib.logger import *

ADDON      = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
MEDIA_PATH = os.path.join(ADDON_PATH, "resources", "media")

ICON   = os.path.join(MEDIA_PATH, "icon.png")

def notify(title, message, time_ms=3000):

    xbmcgui.Dialog().notification(
        title,
        message,
        ICON,
        time_ms
    )
