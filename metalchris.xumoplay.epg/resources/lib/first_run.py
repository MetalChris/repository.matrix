import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import os
import urllib.request

from resources.lib.utils_fetch import fetch_epg, fetch_channel_descriptions, get_channel_thumbs, _get_feed, THUMBS_DIR
from resources.lib.logger import log
from resources.lib.uas import ua
from resources.lib.get_items import fetch_all_programs

log(f"[FIRST RUN] User-Agent: {(ua)}", xbmc.LOGINFO)

ADDON = xbmcaddon.Addon()
ADDON_ID = "metalchris.xumoplay.epg"
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
SETTING_ID = "first_run"
PROFILE_PATH = xbmcvfs.translatePath(f"special://profile/addon_data/{ADDON_ID}/")
EPG_JSON = os.path.join(PROFILE_PATH, "cache", "epg.json")
apiUrl = 'https://valencia-app-mds.xumo.com/v2/'
FEED_URL = apiUrl + 'proxy/channels/list/10006.json'

def run_first_run():
	"""
	Run first-run setup: download all channel logos with progress bar.
	Only runs once — controlled by hidden setting.
	"""
	if not ADDON.getSettingBool(SETTING_ID):
		return

	""" Fallback for testing purposes
	if os.path.exists(EPG_JSON):
		log(f"[FIRST RUN] Cached epg.json exists", xbmc.LOGINFO)
		return
	"""

		# Path to message text file
	msg_path = os.path.join(ADDON.getAddonInfo("path"), "resources", "first_run_message.txt")

	# Default fallback message
	message = (
		"This is your first time running the add-on.\n\n"
		"It will now download data and images for caching.\n"
		"This may take a minute."
	)

	# Read message from file if available
	if os.path.exists(msg_path):
		try:
			with open(msg_path, "r", encoding="utf-8") as f:
				message = f.read().strip()
		except Exception as e:
			log(f"[FIRST RUN] Failed to read message file: {e}", xbmc.LOGWARNING)

	xbmcgui.Dialog().textviewer(ADDON_NAME + " - First Run Setup", message)


	try:
		""" get epg.json --> fetch_epg(FEED_URL) in default.py
		    create epg.json before anything else """
		data = {}
		data = fetch_epg(FEED_URL)

		""" get desc_map_programs_logo.json --> fetch_channel_descriptions(data) in utils_fetch.py
	        this file is needed to get channel thumbs """
		desc_map = fetch_channel_descriptions(data)

		"""get channel thumbs --> get_channel_thumbs(data) in utils_fetch.py
	        download and convert all channel thumbs - uses desc_map_programs_logo.json
	        should run from first_run.py and then only if thumbs are missing """
		thumbs_map = get_channel_thumbs(data)

		""" get program information --> fetch_all_programs(data) in get_items.py
	        creates map_all_programs.json used in build_items()"""
		program_map = fetch_all_programs(data)


		try:
		    log(f"[FIRST RUN] Attempting to set {SETTING_ID} = False", xbmc.LOGINFO)
		    ADDON.setSettingBool(SETTING_ID, False)
		    new_val = ADDON.getSettingBool(SETTING_ID)
		    log(f"[FIRST RUN] After set, {SETTING_ID} = {new_val}", xbmc.LOGINFO)
		except Exception as e:
		    log(f"[FIRST RUN] Error setting {SETTING_ID}: {e}", xbmc.LOGERROR)

		xbmcgui.Dialog().notification("XumoPlay EPG", "First run setup complete", xbmcgui.NOTIFICATION_INFO, 3000, sound=False)

	except Exception as e:
		log(f"[FIRST RUN] Error during first-run setup: {e}", xbmc.LOGERROR)
