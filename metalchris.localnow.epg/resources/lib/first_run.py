import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import os
import urllib.request

from resources.lib.utils_fetch import get_channel_thumbs, _get_feed, THUMBS_DIR
from resources.lib.logger import log
from resources.lib.uas import ua

log(f"[FIRST RUN] User-Agent: {(ua)}", xbmc.LOGINFO)

ADDON = xbmcaddon.Addon()
ADDON_ID = "metalchris.localnow.epg"
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
SETTING_ID = "first_run"
PROFILE_PATH = xbmcvfs.translatePath(f"special://profile/addon_data/{ADDON_ID}/")
EPG_JSON = os.path.join(PROFILE_PATH, "cache", "epg.json")

def run_first_run():
	"""
	Run first-run setup: download all channel logos with progress bar.
	Only runs once — controlled by hidden setting.
	"""
	if not ADDON.getSettingBool(SETTING_ID):
		return

	if os.path.exists(EPG_JSON):
		log(f"[FIRST RUN] Cached epg.json exists", xbmc.LOGINFO)
		return

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

	all_eps = []
	try:
		feed = _get_feed()
		channels = feed.get("channels", [])
		log(f"[FIRST RUN] Feed length {len(feed)}", xbmc.LOGINFO)# If channels is a dict, convert to list of values
		if isinstance(channels, dict):
			channels = channels.values()

		for channel in channels:
			chan_id = channel.get("channel_number", "") if isinstance(channel, dict) else ""
			img_url = channel.get("wallpaper") if isinstance(channel, dict) else ""
			if not img_url:
				continue
			all_eps.append((chan_id, img_url))

		total = len(all_eps)
		log(f"[FIRST RUN] Found {total} channels", xbmc.LOGINFO)

		if not total:
			log("[FIRST RUN] No episodes found in feed", xbmc.LOGWARNING)
			return

		dlg = xbmcgui.DialogProgress()
		dlg.create("LocalNow EPG", "Downloading channel logos...")

		for i, (chan_id, img_url) in enumerate(all_eps, 1):
			if dlg.iscanceled():
				break

			local_file = os.path.join(THUMBS_DIR, f"{chan_id}.png")
			if not xbmcvfs.exists(local_file):
				try:
					req = urllib.request.Request(img_url, headers={"User-Agent": ua})
					with urllib.request.urlopen(req) as resp, open(local_file, "wb") as out:
						out.write(resp.read())
				except Exception as e:
					log(f"[FIRST RUN] Failed to download {img_url}: {e}", xbmc.LOGWARNING)

			# Update every 10 logos to reduce lag
			if i % 10 == 0 or i == total:
				pct = int((i / total) * 100)
				dlg.update(pct, f"Downloaded {i}/{total} logos")

		dlg.close()
		ADDON.setSettingBool(SETTING_ID, False)
		xbmcgui.Dialog().notification("LocalNow EPG", "First run setup complete", xbmcgui.NOTIFICATION_INFO, 3000, sound=False)
		log(f"[FIRST RUN] Cached {total} channel logos", xbmc.LOGINFO)

	except Exception as e:
		log(f"[FIRST RUN] Error during first-run setup: {e}", xbmc.LOGERROR)
