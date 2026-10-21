import xbmc
import xbmcaddon
import xbmcvfs
import json
import time

ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
ADDON_ID = ADDON.getAddonInfo('id')
PROFILE_PATH = xbmcvfs.translatePath(f"special://profile/addon_data/{ADDON_ID}/")

error_file = PROFILE_PATH + "error_file.json"

# Internal guard so we only log startup once per session

def log(msg, level=xbmc.LOGDEBUG):
    """
    Add-on scoped logging.
    - ERROR always logs
    - DEBUG/INFO show only if add-on debug is enabled
    """

    try:
        debug_enabled = ADDON.getSettingBool("debug_logging")
    except Exception:
        debug_enabled = False

    level_map = {
        xbmc.LOGDEBUG: "DEBUG",
        xbmc.LOGINFO: "INFO",
        xbmc.LOGWARNING: "WARNING",
        xbmc.LOGERROR: "ERROR",
    }
    level_name = level_map.get(level, "LOG")

    # Prefix with name, version, and level
    message = f"[{ADDON_NAME}]{msg}"

    if level == xbmc.LOGERROR:
        xbmc.log(message, xbmc.LOGERROR)
        return

    if debug_enabled:
        # force visibility by logging as WARNING
        xbmc.log(message, xbmc.LOGWARNING)
    else:
        xbmc.log(message, level)



#  log(f"[VIDEO]: found menu: title='{title}' href='{href}'") ONLY SHOWS WHEN ADD-ON DEBUG ENABLED
#  xbmc.log(f"NASA+ [ADD-ON STARTED]", xbmc.LOGINFO) ALWAYS SHOWS
		

def log_error(e, channel_slug, ADDON_ID):
	#log(f"[LOG_ERROR] {e}, {channel_slug}, {ADDON_ID}", xbmc.LOGINFO)
	
	try:
		now = int(time.time())
		
		# 1. Prepare the new line as bytes
		new_entry = {"timestamp": now, "error": str(e), "addon_id": ADDON_ID, "slug": channel_slug}
		new_line = json.dumps(new_entry) + "\n"
		buffer = bytearray(new_line, 'utf-8')

		# 2. Read existing content (if any) as bytes
		existing_data = bytearray()
		if xbmcvfs.exists(error_file):
			with xbmcvfs.File(error_file, 'rb') as f:
				existing_data = f.readBytes()

		# 3. Write everything back in binary mode ("wb")
		# This effectively appends by writing (old + new)
		with xbmcvfs.File(error_file, 'wb') as f:
			f.write(existing_data + buffer)
			
	except Exception as e:
		log(f"[LOG_ERROR] ERROR: {e}", xbmc.LOGERROR)
