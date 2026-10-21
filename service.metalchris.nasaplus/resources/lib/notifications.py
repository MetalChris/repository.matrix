import xbmcgui
import os
import urllib.parse
import xbmc

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
		time_ms,
		sound=False
	)
	
	log(f"[NOTIFICATION]: {message}")
	
	
def notify_live_event(title, message, url, event_title, image):
	if xbmcgui.Dialog().yesno(title, message):
		log(f"Play URL: {url}", xbmc.LOGINFO)
		plugin_url = (
			"plugin://metalchris.video.nasaplus/"
			f"?action=stream&url={urllib.parse.quote(url, safe='')}&title={urllib.parse.quote(event_title, safe='')}&image={urllib.parse.quote(image, safe='')}"
		)

		log(f"Playing: {plugin_url}", xbmc.LOGINFO)
		xbmc.executebuiltin(f"PlayMedia({plugin_url})")
