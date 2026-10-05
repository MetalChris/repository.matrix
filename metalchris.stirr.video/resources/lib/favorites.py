import json
import sys
import os
#import urllib.parse
import xbmc
import xbmcvfs
import xbmcgui
import xbmcplugin
import traceback

from .logger import log

BASE_URL = sys.argv[0]
HANDLE = int(sys.argv[1])
DEFAULTIMAGE = 'special://home/addons/metalchris.stirr.video/resources/media/icon.png'
ICON = 'special://home/addons/metalchris.stirr.video/resources/media/icon.png'
FAVORITES_FILE = xbmcvfs.translatePath(
	"special://profile/addon_data/metalchris.stirr.video/favorites.json"
)
EPG_FILE = xbmcvfs.translatePath(
	"special://profile/addon_data/metalchris.stirr.epg/favorites.json"
)

from default import build_url

def add_favorite(channel):
	log(f"CHANNEL: {channel}", xbmc.LOGINFO)
	
	try:
		video_id = str(channel.get("videoid"))

		favorites = {}
		
		favorites_dir = os.path.dirname(FAVORITES_FILE)
		epg_dir = os.path.dirname(EPG_FILE)

		if not xbmcvfs.exists(favorites_dir):
			xbmcvfs.mkdirs(favorites_dir)
		if not xbmcvfs.exists(epg_dir):
			xbmcvfs.mkdirs(epg_dir)

		if xbmcvfs.exists(FAVORITES_FILE):
			with xbmcvfs.File(FAVORITES_FILE, "r") as f:
				favorites = json.load(f)

		if video_id in favorites:
			log(f"Already a favorite: {channel.get('title')}", xbmc.LOGINFO)
			xbmcgui.Dialog().notification(
				heading = "STIRR",
				message = f"{channel.get('title')} already in Favorites",
				icon = ICON,
				time = 3000,
				sound=False
			)
			return

		thumbs = channel.get("thumbs", {})
		logo = thumbs.get("168x105")

		favorites[video_id] = {
			"slug": video_id,
			"name": channel.get("title") or channel.get("name") or "No Title",
			"logo": logo,
			"url": video_id,
			"addon_id": "metalchris.stirr.video"
		}

		with xbmcvfs.File(FAVORITES_FILE, "w") as f:
			json.dump(favorites, f, indent=2)
		with xbmcvfs.File(EPG_FILE, "w") as f:
			json.dump(favorites, f, indent=2)

		log(f"Added favorite: {channel.get('title')}", xbmc.LOGINFO)
		xbmcgui.Dialog().notification(
			heading = "STIRR",
			message = f"{channel.get('title')} added to Favorites",
			icon = ICON,
			time = 3000,
			sound=False
		)

	except Exception as e:
		log(f"Failed to save favorite: {e}", xbmc.LOGERROR)


def load_favorites():
	try:
		if not xbmcvfs.exists(FAVORITES_FILE):
			return []

		with xbmcvfs.File(FAVORITES_FILE, "r") as f:
			return json.load(f)

	except Exception:
		log(f"Failed to load favorites: {traceback.format_exc()}", xbmc.LOGERROR)
		return []


def favorites():
	
	favorites = load_favorites()

	if not favorites:
		xbmcgui.Dialog().notification(
			heading="STIRR",
			message="No Favorites",
			icon=ICON,
			time=3000,
			sound=False
		)
		xbmcplugin.endOfDirectory(HANDLE)
		return
    
	channels = list(load_favorites().values())
	log(f"FAVORITES: {channels}", xbmc.LOGDEBUG)

	if not channels:
		xbmcgui.Dialog().notification("STIRR", "No favorites found", sound=False)
		xbmcplugin.endOfDirectory(HANDLE)
		return

	for ch in channels:
		if not isinstance(ch, dict):
			continue

		title = ch.get("name") or "No Title"
		thumb = (ch.get("logo") or "").replace("168x105", "416x260") or DEFAULTIMAGE
		video_id = ch.get("slug")

		li = xbmcgui.ListItem(label=title)

		li.setArt({
			"thumb": thumb,
			"icon": thumb,
			"poster": thumb,
			"fanart": thumb
		})
		
		li.addContextMenuItems([
			('Remove STIRR Favorite',f"RunPlugin({build_url({'action': 'remove_favorite','videoid': video_id})})"
			)
		])

		url = build_url({
			"action": "play",
			"videoid": video_id
		})

		li.setProperty("IsPlayable", "true")

		xbmcplugin.addDirectoryItem(
			handle=HANDLE,
			url=url,
			listitem=li,
			isFolder=False
		)

	xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(HANDLE)
	xbmcplugin.setContent(HANDLE, "episodes")


def remove_favorite(video_id):
	if not video_id:
		return

	if not xbmcgui.Dialog().yesno(
		"STIRR Favorites",
		"Remove this channel from your favorites?"
	):
		return

	favorites = load_favorites()

	if video_id not in favorites:
		return

	del favorites[video_id]

	try:
		with xbmcvfs.File(FAVORITES_FILE, "w") as f:
			json.dump(favorites, f, indent=4)
		with xbmcvfs.File(EPG_FILE, "w") as f:
			json.dump(favorites, f, indent=4)

		xbmcgui.Dialog().notification(
			"STIRR Favorites",
			"Favorite removed",
			icon = ICON,
			sound=False
		)
		
		xbmc.executebuiltin("Container.Refresh")

	except Exception:
		log(f"Failed to save favorites: {traceback.format_exc()}", xbmc.LOGERROR)
