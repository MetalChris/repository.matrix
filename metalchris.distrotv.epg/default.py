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
from resources.lib.build_items import *
#from resources.lib.playback import *
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
USERDATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
THUMBS_PATH = os.path.join(USERDATA_PATH, "thumbs")
SORT_ALPHA = ADDON.getSettingBool("sort_alpha")
GENRE_FILTER_PROP = "distro_epg_genre_filter"
#EPG_JSON = os.path.join(ADDON_PATH, "epg.json")  # cached JSON in addon root
EPG_JSON = os.path.join(USERDATA_PATH,"cache/epg.json")

XML_FILE = "script-panel-demo.xml"
SKIN = "default"
RESOLUTION = "1080i"
XML_PATH = os.path.join(ADDON_PATH, "resources", "skins", SKIN, RESOLUTION, XML_FILE)
FEED_URL = "https://tv.jsrdn.com/tv_v5/getfeed.php?type=live"


log(f"Loaded addon id={ADDON_ID}, version={ADDON_VERSION}", xbmc.LOGINFO)



class EPGPanel(xbmcgui.WindowXML):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.listitems = kwargs.get("listitems", [])
		self.title = kwargs.get("title", "DistroTV EPG")

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

		except Exception as e:
			log(f"Error adding listitems: {e}", xbmc.LOGERROR)

		if not hasattr(self, "player_monitor") or not self.player_monitor:
			self.player_monitor = PlayerMonitor(self)


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
		"DistroTV EPG",
		"Building EPG...",
		xbmcgui.NOTIFICATION_INFO,
		3000,
		sound=False
	)
	# Clear cached EPG and thumbs
	if addon.getSettingBool("clear_cache_on_next_start"):
		# optional confirmation (useful if user changed setting remotely)
		confirm = xbmcgui.Dialog().yesno(
			"DistroTV EPG",
			"Clear EPG cache and thumbnails now?",
			yeslabel="Clear",
			nolabel="Cancel"
		)
		if confirm:
			log("[SETTINGS] Clearing EPG cache and thumbnails (requested from settings)")
			clear_cache_and_refresh_thumbs()
			xbmcgui.Dialog().notification(
				"DistroTV EPG",
				"EPG cache and thumbnails cleared",
				xbmcgui.NOTIFICATION_INFO,
				3000,
				sound=False
			)
		else:
			log("[SETTINGS] Clear cache request cancelled by user")

		# reset the setting so it doesn't run again
		addon.setSetting("clear_cache_on_next_start", "false")


	episode_ids = fetch_all_episode_ids()
	data = {}
	if episode_ids:
		epg_url = "https://tv.jsrdn.com/epg/query.php?range=now,2h&id=" + ",".join(map(str, episode_ids))
		log(f"Built EPG URL with {len(episode_ids)} IDs", xbmc.LOGDEBUG)
		#log(f"EPG URL: {epg_url}", xbmc.LOGDEBUG)
		data = fetch_epg(epg_url)
	else:
		log("No episode IDs found, not fetching remote EPG", xbmc.LOGWARNING)

	thumbs_map = get_channel_thumbs()
	desc_map   = fetch_channel_descriptions()
	genre_map  = build_genre_map()

	win = xbmcgui.Window(10025)
	if addon.getSettingBool("remember_genre"):
		last_genre = addon.getSetting("last_genre")
		if last_genre:
			win.setProperty("distro_epg_genre_filter", last_genre)
		else:
			win.clearProperty(GENRE_FILTER_PROP)
	else:
		win.clearProperty(GENRE_FILTER_PROP)


	listitems, kept, title = build_items(data, thumbs_map, desc_map, genre_map, win, fav_ids=None)

	# Resolve which XML to load for EPG skin
	from resources.lib.skin_utils import get_epg_skin_file
	xml_file, theme = get_epg_skin_file()
	if not xml_file or not theme:
		xbmcgui.Dialog().notification("DistroTV EPG", "EPG skin XML missing", xbmcgui.NOTIFICATION_ERROR, 5000, sound=False)
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
