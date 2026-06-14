import os
import json
import xbmc
import xbmcvfs
import xbmcaddon

ADDON = xbmcaddon.Addon()

OLD_KEYS = {"name", "logo"}
NEW_KEYS = {"slug", "name", "logo", "url", "addon_id"}


def check_favorites_format(addon_id):
	"""
	Checks whether favorites.json exists and determines
	whether entries use the old or new favorites schema.
	"""

	favorites_path = os.path.join(
		xbmcvfs.translatePath("special://userdata/addon_data/{}/".format(addon_id)),
		"favorites.json"
	)

	if not xbmcvfs.exists(favorites_path):
		xbmc.log(
			"[{}] favorites.json not found".format(addon_id),
			xbmc.LOGINFO
		)
		return "missing"

	try:
		with open(favorites_path, "r", encoding="utf-8") as f:
			data = json.load(f)

		if not isinstance(data, dict):
			xbmc.log(
				"[{}] favorites.json is not a valid dictionary".format(addon_id),
				xbmc.LOGWARNING
			)
			return "invalid"

		old_count = 0
		new_count = 0
		unknown_count = 0

		for channel_id, item in data.items():

			if not isinstance(item, dict):
				unknown_count += 1
				continue

			keys = set(item.keys())

			if NEW_KEYS.issubset(keys):
				new_count += 1

			elif OLD_KEYS.issubset(keys):
				old_count += 1

			else:
				unknown_count += 1

		xbmc.log(
			"[{}] Favorites format check -> "
			"new: {}, old: {}, unknown: {}".format(
				addon_id,
				new_count,
				old_count,
				unknown_count
			),
			xbmc.LOGINFO
		)

		if old_count > 0:
			ADDON.setSetting("old_favorites", "True")
			xbmc.log(
				"[{}] favorites.json contains OLD format entries".format(addon_id),
				xbmc.LOGWARNING
			)
			return "old"

		if new_count > 0 and old_count == 0:
			ADDON.setSetting("old_favorites", "False")
			xbmc.log(
				"[{}] favorites.json is using NEW format".format(addon_id),
				xbmc.LOGINFO
			)
			return "new"

		return "unknown"

	except Exception as e:
		xbmc.log(
			"[{}] Error checking favorites format: {}".format(addon_id, e),
			xbmc.LOGERROR
		)
		return "error"
		

def migrate_favorites(favorites, channels):

    updated = False

    for channel_id, item in favorites.items():

        if is_old_format(item):

            channel = channels.get(channel_id)

            if not channel:
                continue

            favorites[channel_id] = {
                "slug": channel.get("slug", ""),
                "name": channel.get("name", ""),
                "logo": channel.get("logo", ""),
                "url": channel.get("url", ""),
                "addon_id": ADDON_ID
            }

            updated = True

    if updated:
        save_favorites(favorites)
