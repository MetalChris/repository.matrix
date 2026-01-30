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
#import inputstreamhelper

from resources.lib.utils_fetch import *
from resources.lib.uas import *
from resources.lib.build_items import *
from resources.lib.get_items import *
from resources.lib.skin_utils import *
from resources.lib.monitor import *
from resources.lib.context_menu import *
from resources.lib.refresh import *
from resources.lib.actions import *
from resources.lib.logger import *
from resources.lib.first_run import run_first_run


ADDON = xbmcaddon.Addon()
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
USERDATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
THUMBS_PATH = os.path.join(USERDATA_PATH, "thumbs")
SORT_ALPHA = ADDON.getSettingBool("sort_alpha")
GENRE_FILTER_PROP = "xumoplay_epg_genre_filter"
EPG_JSON = os.path.join(USERDATA_PATH,"cache/epg.json")
SKIN = "default"
RESOLUTION = "1080i"

apiUrl = 'https://valencia-app-mds.xumo.com/v2/'
devUrl = 'https://play-dev.xumo.com/_next/data/-tJ2heLKohd5CJOzD6cKF/'
baseUrl = 'https://play.xumo.com/'
FEED_URL = apiUrl + 'proxy/channels/list/10006.json'
plugin = "Xumo Play"
local_string = xbmcaddon.Addon(id='metalchris.xumoplay.epg').getLocalizedString
USERDATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
PRE_EPG = os.path.join(USERDATA_PATH,"cache/desc_map_programs_logo.json")
ICON = 'special://home/addons/metalchris.xumoplay.epg/resources/media/icon.png'


class EPGPanel(xbmcgui.WindowXML):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.listitems = kwargs.get("listitems", [])
		self.title = kwargs.get("title") or xbmc.getInfoLabel("Window.Property(EPG_TITLE)") or "XumoPlay EPG"
		self.player_monitor = None  # <--- define it here

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
				current_title = self.getProperty("EPG_TITLE") or self.title
				self.setProperty("EPG_TITLE", current_title)
				heading_ctrl.setLabel(current_title)

		except Exception as e:
			log(f"Error adding listitems: {e}", xbmc.LOGERROR)

		last_genre = addon.getSetting("last_genre")
		if last_genre:
			self.setProperty(GENRE_FILTER_PROP, last_genre)
			log(f"[XumoPlay EPG] [INFO] GENRE_FILTER_PROP set to: {last_genre}", xbmc.LOGINFO)


		if not self.player_monitor:
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
		heading = "XumoPlay EPG",
		message = "Building EPG...",
		icon = ICON,
		time = 3000,
		sound=False
	)
	# Clear cached EPG and thumbs
	if addon.getSettingBool("clear_cache_on_next_start"):
		# optional confirmation (useful if user changed setting remotely)
		confirm = xbmcgui.Dialog().yesno(
			"XumoPlay EPG",
			"Clear EPG cache and thumbnails now?",
			yeslabel="Clear",
			nolabel="Cancel"
		)
		if confirm:
			log("[SETTINGS] Clearing EPG cache and thumbnails (requested from settings)")
			clear_cache_and_refresh_thumbs()
			xbmcgui.Dialog().notification(
				heading = "XumoPlay EPG",
				message = "EPG cache and thumbnails cleared",
				icon = ICON,
				time = 3000,
				sound=False
			)
		else:
			log("[SETTINGS] Clear cache request cancelled by user")

		# reset the setting so it doesn't run again
		addon.setSetting("clear_cache_on_next_start", "false")


	#episode_ids = fetch_all_episode_ids()
	data = {}
	data = fetch_epg(FEED_URL)

	program_map = fetch_all_programs(data)
	desc_map   = fetch_channel_descriptions(data)
	thumbs_map = get_channel_thumbs(data)
	genre_map  = build_genre_map(data)

	win = xbmcgui.Window(10025)
	if addon.getSettingBool("remember_genre"):
		last_genre = addon.getSetting("last_genre")
		if last_genre:
			win.setProperty("xumoplay_epg_genre_filter", last_genre)
		else:
			win.clearProperty(GENRE_FILTER_PROP)
	else:
		win.clearProperty(GENRE_FILTER_PROP)

	#listitems, kept, title = build_items(data, thumbs_map, desc_map, genre_map, win, fav_ids=None)
	listitems, kept, title = build_items(data, thumbs_map, desc_map, program_map, genre_map, win, fav_ids=None)

	# Resolve which XML to load for EPG skin
	from resources.lib.skin_utils import get_epg_skin_file
	XML_FILE, theme = get_epg_skin_file()
	if not XML_FILE or not theme:
		xbmcgui.Dialog().notification(heading = "XumoPlay EPG", message = "EPG skin XML missing", icon = ICON, time = 5000, sound=False)
		return



	w = EPGPanel(XML_FILE, ADDON_PATH, theme, "720p")
	w.listitems = listitems
	w.title = title
	#w = EPGPanel(xml_file, ADDON_PATH, theme, "720p", listitems=listitems, title=title)
	w.doModal()
	del w

		#return epg_list


if __name__ == "__main__":
	log(f"[DEFAULT] Loaded ADDON ID: {ADDON_ID.upper()}, Version: {ADDON_VERSION.upper()}", xbmc.LOGINFO)
	run_first_run()
	run()
