import xbmc
import xbmcaddon
from resources.lib.logger import *

ADDON = xbmcaddon.Addon()

# Global settings, persistent across restarts
#use_inputstream = ADDON.getSettingBool("use_isa")
remember_genre = ADDON.getSettingBool("remember_genre")
language_filter = ADDON.getSetting("filter_language")
#start_in_favorites = ADDON.getSettingBool("start_in_favorites")
sort_alpha = ADDON.getSettingBool("sort_alpha")


def refresh_addon_settings(epg_window=None):
    """
    Reload add-on settings from settings.xml and update EPG panel if provided.
    Call this after addon.openSettings().
    """
    global use_inputstream, remember_genre, language_filter, start_in_favorites, sort_alpha

    # Re-read all settings
    use_inputstream = ADDON.getSettingBool("use_isa")
    remember_genre = ADDON.getSettingBool("remember_genre")
    language_filter = ADDON.getSetting("filter_language")
    start_in_favorites = ADDON.getSettingBool("start_in_favorites")
    sort_alpha = ADDON.getSettingBool("sort_alpha")

    log(
        f"[REFRESH] Settings reloaded: use_isa={use_inputstream}, sort_alpha={sort_alpha}",
        xbmc.LOGDEBUG,
    )

    if epg_window:
        try:
            # Update the panel's copy of settings
            epg_window.use_inputstream = use_inputstream
            epg_window.remember_genre = remember_genre
            epg_window.language_filter = language_filter
            epg_window.start_in_favorites = start_in_favorites
            epg_window.sort_alpha = sort_alpha

            # Trigger live list refresh
            epg_window.refresh_list()
            log("[REFRESH] EPG panel refreshed after settings change.", xbmc.LOGDEBUG)

        except Exception as e:
            log(f"[REFRESH] Failed to refresh EPG panel: {e}", xbmc.LOGERROR)
