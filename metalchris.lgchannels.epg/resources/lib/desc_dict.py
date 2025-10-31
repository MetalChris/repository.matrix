
desc_dict = {}

try:
    if not xbmcvfs.exists(EPG_JSON):
        xbmc.log("[UTILS_FETCH][fetch_channel_descriptions] EPG JSON not found", xbmc.LOGWARNING)
        return desc_dict

    with open(EPG_JSON, "r", encoding="utf-8") as f:
        epg_data = json.load(f)

    categories = epg_data.get("data", {}).get("categories", [])
    if not categories:
        xbmc.log("[UTILS_FETCH][fetch_channel_descriptions] No categories found in EPG", xbmc.LOGERROR)
        return desc_dict

    for category in categories:
        for ch in category.get("channels", []):
            if not isinstance(ch, dict):
                continue
            channel_number = str(ch.get("channelNumber"))
            genre = ch.get("channelGenreName")
            if channel_number and genre:
                desc_dict.setdefault(genre, []).append(channel_number)

    xbmc.log(f"[UTILS_FETCH][fetch_channel_descriptions] Built desc map with {len(desc_dict)} genres", xbmc.LOGINFO)

except Exception as e:
    xbmc.log(f"[UTILS_FETCH][fetch_channel_descriptions] Error building desc map: {e}", xbmc.LOGERROR)

return desc_dict
