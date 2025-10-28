import xbmc
from resources.lib.logger import log
from resources.lib.utils_fetch import fetch_all_episode_ids, fetch_epg, get_channel_thumbs, fetch_channel_descriptions, build_genre_map
from resources.lib.build_items import build_items
from resources.lib.refresh_addon_settings import sort_alpha

def refresh_epg_list(epg_window):
    try:
        log(f"[DEBUG] refresh_epg_list called with FAVORITES_FILTER={epg_window.getProperty('FAVORITES_FILTER')}")

        # --- Load EPG data ---
        fav_filter = epg_window.getProperty("FAVORITES_FILTER")
        fav_ids = [s.strip() for s in fav_filter.split(",") if s.strip()] if fav_filter else None

        data = {}
        if fav_ids:
            # Load cached epg.json
            import xbmcaddon, os, json, xbmcvfs
            profile = xbmcaddon.Addon().getAddonInfo("profile")
            epg_path = os.path.join(profile, "cache", "epg.json")
            os_path = xbmcvfs.translatePath(epg_path)
            if xbmcvfs.exists(epg_path):
                try:
                    with open(os_path, "r", encoding="utf-8") as fh:
                        cached = json.load(fh)
                    epg_dict = cached.get("data", {}).get("epg", {})
                    data["epg"] = {cid: epg_dict[cid] for cid in fav_ids if cid in epg_dict}
                    log(f"[REFRESH] Loaded {len(data['epg'])} favorite channels", xbmc.LOGINFO)
                except Exception as e:
                    log(f"[REFRESH] Failed reading cached epg.json: {e}", xbmc.LOGERROR)
        else:
            # Normal fetch
            episode_ids = fetch_all_episode_ids()
            if episode_ids:
                epg_url = "https://tv.jsrdn.com/epg/query.php?range=now,2h&id=" + ",".join(map(str, episode_ids))
                data = fetch_epg(epg_url)

        # --- Auxiliary data ---
        thumbs_map = get_channel_thumbs()
        desc_map = fetch_channel_descriptions()
        genre_map = build_genre_map()

        # --- Preserve filters before rebuild ---
        filter_lang = epg_window.getProperty("FILTER_LANGUAGE")
        filter_genre = epg_window.getProperty("FILTER_GENRE")

        log(f"[REFRESH] Active filters before build: lang={filter_lang}, genre={filter_genre}", xbmc.LOGDEBUG)



        # --- Build Kodi list items ---
        new_items, kept, title = build_items(data, thumbs_map, desc_map, genre_map, epg_window, fav_ids=fav_ids)

                # --- Restore filters after rebuild ---
        if filter_lang:
            epg_window.setProperty("FILTER_LANGUAGE", filter_lang)
        if filter_genre:
            epg_window.setProperty("FILTER_GENRE", filter_genre)



        # --- Update Kodi control ---
        ctrl = epg_window.getControl(9000)
        ctrl.reset()
        ctrl.addItems(new_items)
        epg_window.listitems = new_items

        # --- Update heading ---
        heading_ctrl = epg_window.getControl(1)
        if heading_ctrl:
            heading_ctrl.setLabel(title)

        log(f"[REFRESH] EPG list refreshed ({kept} channels)", xbmc.LOGINFO)

    except Exception as e:
        log(f"[REFRESH] Error refreshing list: {e}", xbmc.LOGERROR)
