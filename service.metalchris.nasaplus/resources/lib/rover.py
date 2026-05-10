import os
import shutil
import xbmc
import xbmcvfs
import json
import time

from resources.lib.logger import log
from resources.lib.notifications import notify

OLD_ADDON_ID = "service.metalchris.nasaplus.audio"

ADDONS_PATH = xbmcvfs.translatePath("special://home/addons/")
USERDATA_PATH = xbmcvfs.translatePath("special://profile/addon_data/")


def remove_old_service():

	old_addon_path = os.path.join(ADDONS_PATH, OLD_ADDON_ID)
	old_userdata_path = os.path.join(USERDATA_PATH, OLD_ADDON_ID)

	if not os.path.exists(old_addon_path):
		log(f"Old add-on {OLD_ADDON_ID} not found", xbmc.LOGDEBUG)
		return

	try:
		notify(
			"NASA+ Service Upgrade",
			f"Removing old service: {OLD_ADDON_ID}"
		)

		log(f"Old NASA+ Audio Service detected: {OLD_ADDON_ID}", xbmc.LOGINFO)

		# 1. Disable in Kodi registry (fixes UI "still enabled")
		_disable_addon(OLD_ADDON_ID)

		# 2. Stop if running
		xbmc.executebuiltin(f"StopScript({OLD_ADDON_ID})")

		# 3. Give Kodi time to apply state change
		time.sleep(0.5)

		# 4. Remove files
		shutil.rmtree(old_addon_path, ignore_errors=True)
		shutil.rmtree(old_userdata_path, ignore_errors=True)

		log(f"Old NASA+ Audio Service removed: {OLD_ADDON_ID}", xbmc.LOGINFO)

	except Exception as e:
		log(f"Failed removing old add-on {OLD_ADDON_ID}: {e}", xbmc.LOGERROR)


def _disable_addon(addon_id):
	xbmc.executeJSONRPC(json.dumps({
		"jsonrpc": "2.0",
		"method": "Addons.SetAddonEnabled",
		"params": {
			"addonid": addon_id,
			"enabled": False
		},
		"id": 1
	}))
