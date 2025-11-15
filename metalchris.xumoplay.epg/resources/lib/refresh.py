import xbmc
import os, json, xbmcaddon, xbmcvfs
from resources.lib.logger import log
from resources.lib.utils_fetch import fetch_all_episode_ids, fetch_epg, get_channel_thumbs, fetch_channel_descriptions, build_genre_map
from resources.lib.build_items import build_items
from resources.lib.refresh_addon_settings import sort_alpha
from resources.lib.get_items import *

USERDATA_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
EPG_JSON = os.path.join(USERDATA_PATH,"cache/epg.json")

def refresh_epg_list(epg_window):
    try:
        log(f"[DEBUG] refresh_epg_list called with FAVORITES_FILTER={epg_window.getProperty('FAVORITES_FILTER')}")

        # --- Save currently selected index ---
        try:
            selected_idx = epg_window.getControl(9000).getSelectedItemPosition()
        except Exception:
            selected_idx = 0

        fav_filter = epg_window.getProperty("FAVORITES_FILTER")
        fav_ids = [s.strip() for s in fav_filter.split(",") if s.strip()] if fav_filter else None

        data = {}
        profile = xbmcaddon.Addon().getAddonInfo("profile")
        epg_path = os.path.join(profile, "cache", "epg.json")

        # --- Load EPG from disk only if not cached in memory ---
        if not hasattr(epg_window, "all_epg_channels"):
            os_path = xbmcvfs.translatePath(epg_path)
            if xbmcvfs.exists(os_path):
                try:
                    with open(os_path, "r", encoding="utf-8") as fh:
                        cached = json.load(fh)
                        all_channels = cached.get("data", {}).get("channel", {}).get("item", [])
                        for ch in all_channels:
                            if "channel" not in ch:
                                ch["channel"] = str(ch.get("number", ""))
                        epg_window.all_epg_channels = all_channels
                        log(f"[REFRESH] Loaded {len(all_channels)} channels from disk", xbmc.LOGINFO)
                except Exception as e:
                    log(f"[REFRESH] Failed reading EPG file: {e}", xbmc.LOGERROR)
                    epg_window.all_epg_channels = []
            else:
                log(f"[REFRESH] EPG file does not exist: {os_path}", xbmc.LOGERROR)
                epg_window.all_epg_channels = []

        # --- Filter channels ---
        if fav_ids:
            # Favorites view
            fav_channels = [ch for ch in epg_window.all_epg_channels if str(ch.get("number")) in fav_ids]
            data["categories"] = [{"categoryName": "Favorites", "channels": fav_channels}]
            data["channel"] = {"item": fav_channels}
            log(f"[REFRESH] Loaded {len(fav_channels)} favorite channels", xbmc.LOGINFO)
            fav_numbers = [str(ch.get("number")) for ch in fav_channels]
            log(f"[DEBUG] Favorite channel numbers: {fav_numbers}", xbmc.LOGDEBUG)
        else:
            # Normal view
            data["categories"] = [{"categoryName": "All Channels", "channels": epg_window.all_epg_channels}]
            data["channel"] = {"item": epg_window.all_epg_channels}
            log(f"[REFRESH] Loaded {len(epg_window.all_epg_channels)} channels for normal view", xbmc.LOGINFO)
            normal_numbers = [str(ch.get("number")) for ch in epg_window.all_epg_channels[:10]]
            log(f"[DEBUG] First 10 normal channel numbers: {normal_numbers}", xbmc.LOGDEBUG)

        # --- Auxiliary data ---
        thumbs_map = get_channel_thumbs(data)
        desc_map = fetch_channel_descriptions(data)
        genre_map = build_genre_map(data)
        program_map = fetch_all_programs(data)

        # --- Preserve filters before rebuild ---
        filter_lang = epg_window.getProperty("FILTER_LANGUAGE")
        filter_genre = epg_window.getProperty("FILTER_GENRE")
        log(f"[REFRESH] Active filters before build: lang={filter_lang}, genre={filter_genre}", xbmc.LOGDEBUG)

        # --- Build Kodi list items ---
        new_items, kept, title = build_items(
            data, thumbs_map, desc_map, program_map, genre_map, epg_window, fav_ids=fav_ids
        )

        # --- Restore filters after rebuild ---
        if filter_lang:
            epg_window.setProperty("FILTER_LANGUAGE", filter_lang)
        if filter_genre:
            epg_window.setProperty("FILTER_GENRE", filter_genre)

        # --- Update Kodi control and restore selection ---
        ctrl = epg_window.getControl(9000)
        ctrl.reset()
        ctrl.addItems(new_items)
        epg_window.listitems = new_items

        try:
            if 0 <= selected_idx < len(new_items):
                ctrl.selectItem(selected_idx)
        except Exception:
            pass

        # --- Update heading ---
        heading_ctrl = epg_window.getControl(1)
        if heading_ctrl:
            heading_ctrl.setLabel(title)

        log(f"[REFRESH] EPG list refreshed ({kept} channels)", xbmc.LOGINFO)

    except Exception as e:
        log(f"[REFRESH] Error refreshing list: {e}", xbmc.LOGERROR)
