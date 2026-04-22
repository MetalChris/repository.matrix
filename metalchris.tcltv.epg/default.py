import os
import json
import time
import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
from datetime import datetime
from itertools import islice
import time
import sys
from urllib.parse import parse_qs

from resources.lib.utils_fetch import *
from resources.lib.uas import *
from resources.lib.build_items import build_items
from resources.lib.get_items import *
from resources.lib.skin_utils import *
from resources.lib.monitor import *
from resources.lib.context_menu import *
from resources.lib.refresh import *
from resources.lib.actions import *
from resources.lib.logger import *
from resources.lib.first_run import run_first_run
from resources.lib.monitor import PlayerMonitor

ADDON = xbmcaddon.Addon()
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
MEDIA_PATH = os.path.join(ADDON_PATH, "resources", "media")
USERDATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
THUMBS_PATH = os.path.join(USERDATA_PATH, "thumbs")
ICON   = os.path.join(MEDIA_PATH, "icon.png")
SORT_ALPHA = ADDON.getSettingBool("sort_alpha")
GENRE_FILTER_PROP = "tcltv_epg_genre_filter"
#EPG_JSON = os.path.join(ADDON_PATH, "epg.json")  # cached JSON in addon root
EPG_JSON = os.path.join(USERDATA_PATH,"cache/epg.json")

XML_FILE = "script-panel-demo.xml"
SKIN = "default"
RESOLUTION = "1080i"
XML_PATH = os.path.join(ADDON_PATH, "resources", "skins", SKIN, RESOLUTION, XML_FILE)
#FEED_URL = "https://tv.jsrdn.com/tv_v5/getfeed.php?type=live"

apiUrl = 'https://gateway-prod.ideonow.com/api/metadata/v1/epg/programlist'
plugin = "TCLTV+ EPG"

local_string = xbmcaddon.Addon(id='metalchris.tcltv.epg').getLocalizedString

log(f"Loaded addon id={ADDON_ID}, version={ADDON_VERSION}", xbmc.LOGINFO)


today = time.strftime("%Y-%m-%d")

log('TODAY: ' + str(today),xbmc.LOGINFO)
log('NOW: ' + str(round(time.time())),xbmc.LOGINFO)
log('UTC Offset: ' + str(-time.timezone),xbmc.LOGINFO)

offset = -time.timezone
NOW = (round(time.time()) - offset)
log('NOW_OFFSET: ' + str(NOW),xbmc.LOGINFO)
log(('LG CHANNELS EPG 2025.10.01'),xbmc.LOGINFO)

HEADERS = {
	'user-agent': ua,
	'x-device-country': 'US',
	'x-device-language': 'en',
}


class EPGPanel(xbmcgui.WindowXML):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.listitems = kwargs.get("listitems", [])
		self.title = kwargs.get("title", "TCLTV+ EPG")

	def onInit(self):
		log("Window initialized", xbmc.LOGINFO)
		try:
			ctrl = self.getControl(9000)
			ctrl.reset()
			ctrl.addItems(self.listitems)
			log(f"Added {len(self.listitems)} items to list", xbmc.LOGINFO)

			# Unified title from build_items
			heading_ctrl = self.getControl(1)
			if heading_ctrl:
				heading_ctrl.setLabel(self.title)

			if not hasattr(self, "player_monitor") or not self.player_monitor:
				self.player_monitor = PlayerMonitor(self)

		except Exception as e:
			log(f"Error adding listitems: {e}", xbmc.LOGERROR)

	def onAction(self, action):
		handle_action(self, action)

	def show_context_menu(self):
		try:
			list_control = self.getControl(9000)
			pos = list_control.getSelectedPosition()
			if pos is None or pos < 0:
				return

			li = list_control.getListItem(pos)
			handle_context_menu(self, li)

		except Exception as e:
			log(f"Error showing context menu: {e}", xbmc.LOGERROR)

	def refresh_list(self, *args, **kwargs):
		refresh_epg_list(self)



def run():
	xbmcgui.Dialog().notification(
		"TCLTV+ EPG",
		"Building EPG...",
		ICON,
		3000,
		sound=False
	)
	addon.setSettingBool("favorites_mode", False)
	# Clear cached EPG and thumbs
	if addon.getSettingBool("clear_cache_on_next_start"):
		# optional confirmation (useful if user changed setting remotely)
		confirm = xbmcgui.Dialog().yesno(
			"TCLTV+ EPG",
			"Clear EPG cache and thumbnails now?",
			yeslabel="Clear",
			nolabel="Cancel"
		)
		if confirm:
			log("[SETTINGS] Clearing EPG cache and thumbnails (requested from settings)")
			clear_cache_and_refresh_thumbs()
			xbmcgui.Dialog().notification(
				"TCLTV+ EPG",
				"EPG cache and thumbnails cleared",
				ICON,
				3000,
				sound=False
			)
		else:
			log("[SETTINGS] Clear cache request cancelled by user")

		# reset the setting so it doesn't run again
		addon.setSetting("clear_cache_on_next_start", "false")


	data = {}
	data = fetch_epg(apiUrl)

	thumbs_map = get_channel_thumbs()
	category_map  = build_category_map()

	win = xbmcgui.Window(10025)
	if addon.getSettingBool("remember_genre"):
		last_genre = addon.getSetting("last_genre")
		if last_genre:
			win.setProperty("tcltv_epg_genre_filter", last_genre)
		else:
			win.clearProperty(GENRE_FILTER_PROP)
	else:
		win.clearProperty(GENRE_FILTER_PROP)
		
	xbmc.log(f"[DEFAULT] data type = {type(data)}", xbmc.LOGERROR)
	xbmc.log(f"[DEFAULT] data preview = {str(data)[:300]}", xbmc.LOGERROR)

	#listitems, kept, title = build_items(data, thumbs_map, desc_map, category_map, win, fav_ids=None)
	listitems, kept, title = build_items(data, thumbs_map, category_map, win, fav_ids=None)

	# Resolve which XML to load for EPG skin
	from resources.lib.skin_utils import get_epg_skin_file
	xml_file, theme = get_epg_skin_file()
	if not xml_file or not theme:
		xbmcgui.Dialog().notification("TCLTV+ EPG", "EPG skin XML missing", xbmcgui.NOTIFICATION_ERROR, 5000, sound=False)
		return

	w = EPGPanel(xml_file, ADDON_PATH, theme, "720p")
	w.listitems = listitems
	w.title = title
	#w = EPGPanel(xml_file, ADDON_PATH, theme, "720p", listitems=listitems, title=title)
	w.doModal()
	del w

		#return epg_list


if __name__ == "__main__":
	#if xbmcvfs.exists(XML_PATH):
		#run()
		#w = EPGPanel(XML_FILE, ADDON_PATH, SKIN, RESOLUTION)
		#w.doModal()
		#del w
	#else:
		#xbmcgui.Dialog().ok("EPG Panel", "Custom XML not found.")
	# Check if user pressed "Clear cache" in settings
	#if ADDON.getSetting("clear_cache") == "true":
		#from resources.lib.utils_fetch import clear_cache
		#clear_cache()
		# Reset setting so it doesn’t trigger again
		#ADDON.setSetting("clear_cache", "false")
	run_first_run()
	run()
