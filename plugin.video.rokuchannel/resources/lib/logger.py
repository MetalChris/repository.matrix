import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")

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
    message = f"[{ADDON_NAME}] [{level_name}] {msg}"

    if level == xbmc.LOGERROR:
        xbmc.log(message, xbmc.LOGERROR)
        return

    if debug_enabled:
        # force visibility by logging as WARNING
        xbmc.log(message, xbmc.LOGWARNING)
    else:
        xbmc.log(message, level)



#  log(f"[VIDEO]: found menu: title='{title}' href='{href}'") ONLY SHOWS WHEN ADD-ON DEBUG ENABLED
#  xbmc.log(f"[ADD-ON STARTED]", xbmc.LOGINFO) ALWAYS SHOWS
