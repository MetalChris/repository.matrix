import sys
import urllib.parse
import xbmcplugin
import xbmcgui
import xbmcvfs
import requests
import time

from resources.lib.logger import *
from resources.lib.uas import *
from resources.lib.playback_utils import *
from resources.lib.favorites import *
from resources.lib.file_migrate import *

ADDON      = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
FAVORITES_FILE = xbmcvfs.translatePath(
	"special://profile/addon_data/metalchris.stirr.video/favorites.json"
)
EPG_FILE = xbmcvfs.translatePath(
	"special://profile/addon_data/metalchris.stirr.epg/favorites.json"
)
BASE_URL = sys.argv[0]
HANDLE = int(sys.argv[1])

copy_userdata_files()

def build_url(query):
	return BASE_URL + '?' + urllib.parse.urlencode(query)
	
	
def get_url(url):
	try:
		r = requests.get(url, headers=headers, timeout=10)
		r.raise_for_status()

		data = r.json()
		return data
	
	except Exception as e:
		log(f"REQUEST ERROR: {e}", xbmc.LOGERROR)


def main_menu():
	try:
		debug_enabled = ADDON.getSettingBool("debug")
	except Exception:
		debug_enabled = False

	status = "ENABLED" if debug_enabled else "DISABLED"
	log(f"[{ADDON_NAME} v{ADDON_VERSION}] [ADD-ON STARTED] [DEBUG: {status}]", level=xbmc.LOGINFO)
	
	items = [
		("Live", {"action": "live"}),
		("Movies", {"action": "movies"}),
		("TV Shows", {"action": "tv"}),
	]

	#if xbmcvfs.exists(FAVORITES_FILE):
	items.insert(0, ("Favorites", {"action": "favorites"}))

	for label, query in items:
		li = xbmcgui.ListItem(label)
		xbmcplugin.addDirectoryItem(
			handle=HANDLE,
			url=build_url(query),
			listitem=li,
			isFolder=True
		)

	xbmcplugin.endOfDirectory(HANDLE)


DEFAULTIMAGE = 'special://home/addons/metalchris.stirr.video/resources/media/icon.png'
LIVE_URL = "https://stirr.com/api/videos/list/?categories=all_categories&content_type=4&no_limit=true"
MOVIES_URL = "https://stirr.com/api/videos/categories/?type=is_video"
SHOWS_URL = "https://stirr.com/api/series/categories/?type=is_series"
CAT_URL = "https://stirr.com/api/videos/list/?categories=" # + cat_id + "&content_type=1"
SERIES_URL = "https://stirr.com/api/series/list/?categories=" #  + str(cat_id)
SEASONS_URL = "https://stirr.com/api/season/list/" #  + str(cat_id)
EPG_FILE = xbmcvfs.translatePath(
	"special://profile/addon_data/metalchris.stirr.epg/cache/epg.json"
)

def make_cache(data):
	epg_dir = os.path.dirname(EPG_FILE)
	if not xbmcvfs.exists(epg_dir):
		xbmcvfs.mkdirs(epg_dir)
	
	now = time.time()
	with xbmcvfs.File(EPG_FILE, "w") as f:
		f.write(json.dumps({"timestamp": now, "data": data}))
	log("[make_cache] Fetched and cached fresh EPG", xbmc.LOGINFO)
		
	

headers = {
	"User-Agent": get_ua(),
	"Accept": "application/json",
	"Referer": "https://stirr.com/live"
}


def get_live_channels():
	try:
		log(f"Fetching live channel list", xbmc.LOGINFO)
		log(f"HEADERS: {headers}", xbmc.LOGDEBUG)

		data = get_url(LIVE_URL)
		make_cache(data)

		log(f"STIRR ROOT KEYS: {list(data.keys())}", xbmc.LOGDEBUG)

		# ✅ Correct structure handling
		raw = data.get("videos", {}).get("category_videos", [])
		channels = []

		for group in raw:
			if isinstance(group, list):
				channels.extend(group)

		log(f"Retrieved {len(channels)} channels", xbmc.LOGINFO)

		return channels

	except Exception as e:
		log(f"STIRR ERROR: {e}", xbmc.LOGERROR)
		return []


def list_live():
	channels = get_live_channels()

	if not channels:
		xbmcgui.Dialog().notification("STIRR", "No channels found")
		xbmcplugin.endOfDirectory(HANDLE)
		return

	for ch in channels:

		if not isinstance(ch, dict):
			continue

		title = ch.get("title") or ch.get("name") or "No Title"

		thumbs = ch.get("thumbs", {})
		thumb = thumbs.get("416x260") or thumbs.get("original") or DEFAULTIMAGE

		video_id = ch.get("videoid")
		desc = ch.get("description")

		li = xbmcgui.ListItem(label=title)
		
		li.setInfo("video",{
			"plot": desc
			})

		li.setArt({
			"thumb": thumb,
			"icon": thumb,
			"poster": thumb,
			"fanart": thumb
		})
		
		li.addContextMenuItems([
			('Add to STIRR Favorites',f"RunPlugin({build_url({'action': 'add_favorite','videoid': video_id,'name': title,'logo': thumbs.get('168x105')})})"	)])

		# pass ONLY identifier forward
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
	xbmcplugin.setContent(HANDLE, 'episodes')
	
	
def get_cats(url):

	try:
		log(f"Fetching movie categories", xbmc.LOGINFO)
		log(f"HEADERS: {headers}", xbmc.LOGDEBUG)

		data = get_url(url)
	
		log(f"STIRR ROOT KEYS: {list(data.keys())}", xbmc.LOGDEBUG)

		cats = []
		
		cats = [{"id": cat["category_id"], "name": cat["category_name"], "desc": cat["category_desc"]} for cat in data["categories"]]

		log(f"Retrieved {len(cats)} categories", xbmc.LOGINFO)

		return cats
		
	except Exception as e:
		log(f"STIRR ERROR: {e}", xbmc.LOGERROR)
		return []
	

def movies():
	cats = get_cats(MOVIES_URL)
	
	if not cats:
		xbmcgui.Dialog().notification("STIRR", "No categories found")
		xbmcplugin.endOfDirectory(HANDLE)
		return

	for cat in cats:

		if not isinstance(cat, dict):
			continue

		title = cat.get("title") or cat.get("name") or "No Title"

		thumbs = cat.get("thumbs", {})
		thumb = thumbs.get("416x260") or thumbs.get("original") or DEFAULTIMAGE

		cat_id = cat.get("id")
		desc = cat.get("desc")

		li = xbmcgui.ListItem(label=title)
		
		li.setInfo("video",{
			"plot": desc
			})

		li.setArt({
			"thumb": thumb,
			"icon": thumb,
			"poster": thumb
		})

		# pass ONLY identifier forward
		url = build_url({
			"action": "cat",
			"cat_id": cat_id
		})

		xbmcplugin.addDirectoryItem(
			handle=HANDLE,
			url=url,
			listitem=li,
			isFolder=True
		)
		
		xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(HANDLE)
	xbmcplugin.setContent(HANDLE, 'episodes')
	
	
def tv():
	cats = get_cats(SHOWS_URL)
	
	if not cats:
		xbmcgui.Dialog().notification("STIRR", "No categories found")
		xbmcplugin.endOfDirectory(HANDLE)
		return

	for cat in cats:

		if not isinstance(cat, dict):
			continue

		title = cat.get("title") or cat.get("name") or "No Title"

		thumbs = cat.get("thumbs", {})
		thumb = thumbs.get("416x260") or thumbs.get("original") or DEFAULTIMAGE

		cat_id = cat.get("id")
		desc = cat.get("desc")

		li = xbmcgui.ListItem(label=title)
		
		li.setInfo("video",{
			"plot": desc
			})

		li.setArt({
			"thumb": thumb,
			"icon": thumb,
			"poster": thumb
		})

		# pass ONLY identifier forward
		url = build_url({
			"action": "shows",
			"cat_id": cat_id
		})

		xbmcplugin.addDirectoryItem(
			handle=HANDLE,
			url=url,
			listitem=li,
			isFolder=True
		)
		
		xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(HANDLE)
	xbmcplugin.setContent(HANDLE, 'episodes')
	
	
def get_seasons(cat_id):
	log(f"STIRR TV CAT_ID: {cat_id}", xbmc.LOGDEBUG)
	url = SEASONS_URL + str(cat_id)

	try:
		log(f"Resolving seasons {cat_id}", xbmc.LOGINFO)

		data = get_url(url)

		log(f"STIRR ROOT KEYS: {list(data.keys())}", xbmc.LOGDEBUG)
		seasons = []
		
		seasons = [{"season_id": v["season_id"]}
          for v in data["data"]["seasons"]]

		log(f"Retrieved {len(seasons)} seasons", xbmc.LOGINFO)
		return seasons
				
	except Exception as e:
		log(f"STIRR ERROR: {e}", xbmc.LOGERROR)
	
	
def shows(cat_id):
	log(f"STIRR TV CAT_ID: {cat_id}", xbmc.LOGDEBUG)
	url = SERIES_URL + str(cat_id)

	try:
		log(f"Resolving category {cat_id}", xbmc.LOGINFO)

		data = get_url(url)

		log(f"STIRR ROOT KEYS: {list(data.keys())}", xbmc.LOGDEBUG)
		series = []
		
		series = [{"title": v["series_name"], "description": v["series_description"], "thumbs": v["thumbs"], "series_id": v["series_id"], "season_id": v["first_season_id"], "posters": v["portrait_thumbs"]}
          for videos in data["series"]["category_series"].values()
          for v in videos]

		log(f"Retrieved {len(series)} series", xbmc.LOGINFO)


		for show in series:

			title = show.get("title") or show.get("name") or "No Title"

			thumbs = show.get("thumbs", {})
			thumb = thumbs.get("416x260") or thumbs.get("original") or DEFAULTIMAGE

			series_id = show.get("series_id")
			season_id = show.get("season_id")
			desc = show.get("description")

			li = xbmcgui.ListItem(label=title)
			
			li.setInfo("video",{
				"plot": desc,
				})

			li.setArt({
				"thumb": thumb,
				"icon": thumb,
				"poster": thumb,
				"fanart": thumb
			})

			# pass ONLY identifier forward
			url = build_url({
				"action": "episodes",
				"series_id": series_id,
				"season_id": season_id
			})

			xbmcplugin.addDirectoryItem(
				handle=HANDLE,
				url=url,
				listitem=li,
				isFolder=True
			)
			
			xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
		xbmcplugin.endOfDirectory(HANDLE)
		xbmcplugin.setContent(HANDLE, 'episodes')
		
	except Exception as e:
		log(f"STIRR ERROR: {e}", xbmc.LOGERROR)
		
		
def episodes(series_id, season_id):
	seasons = get_seasons(series_id)
	log(f"STIRR SEASONS: {seasons}", xbmc.LOGDEBUG)
	log(f"STIRR SERIES_ID: {series_id}", xbmc.LOGDEBUG)
	log(f"STIRR SEASON_ID: {season_id}", xbmc.LOGDEBUG)
	url = "https://stirr.com/api/season/data?series_id=" + str(series_id) + "&season_id=" + str(season_id)
	log(f"URL: {url}", xbmc.LOGINFO)
	
	for season_id in seasons:
		url = "https://stirr.com/api/season/data?series_id=" + str(series_id) + "&season_id=" + str(season_id["season_id"])
		log(f"URL: {url}", xbmc.LOGINFO)
		
		try:
			log(f"Resolving category {series_id}", xbmc.LOGINFO)

			data = get_url(url)

			log(f"STIRR ROOT KEYS: {list(data.keys())}", xbmc.LOGDEBUG)
			episodes = []
			
			episodes = [{"title": v["title"], "description": v["description"], "thumbs": v["thumbs"], "gif": v["gif"], "duration": v["duration_in_seconds"], "videoid": v["videoid"]}
			  for v in data["data"]]

			log(f"Retrieved {len(episodes)} episodes", xbmc.LOGINFO)


			for episode in episodes:

				title = episode.get("title") or episode.get("name") or "No Title"

				thumbs = episode.get("thumbs", {})
				thumb = thumbs.get("416x260") or thumbs.get("original") or DEFAULTIMAGE

				videoid = episode.get("videoid")
				desc = episode.get("description")
				duration = episode.get("duration")
				#url = episode.get("gif").replace('preview.webp','playlist.m3u8')

				li = xbmcgui.ListItem(label=title)
				
				li.setInfo("video",{
					"plot": desc,
					"duration": duration
					})

				li.setArt({
					"thumb": thumb,
					"icon": thumb,
					"poster": thumb,
					"fanart": thumb
				})

				# pass ONLY identifier forward
				url = build_url({
					"action": "play",
					"videoid": videoid
				})


				li.setProperty("IsPlayable", "true")

				xbmcplugin.addDirectoryItem(
					handle=HANDLE,
					url=url,
					listitem=li,
					isFolder=False
				)
			
		except Exception as e:
			log(f"STIRR ERROR: {e}", xbmc.LOGERROR)
				
	xbmcplugin.addSortMethod(HANDLE, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(HANDLE)
	xbmcplugin.setContent(HANDLE, 'episodes')
		

def cat(cat_id):
	log(f"STIRR CAT_ID: {cat_id}", xbmc.LOGDEBUG)
	url = CAT_URL + str(cat_id) + "&content_type=1"

	try:
		log(f"Resolving category {cat_id}", xbmc.LOGINFO)

		data = get_url(url)

		log(f"STIRR ROOT KEYS: {list(data.keys())}", xbmc.LOGDEBUG)
		movies = []
		
		movies = [{"title": v["title"], "description": v["description"], "thumbs": v["thumbs"], "gif": v["gif"], "videoid": v["videoid"], "duration": v["duration_in_seconds"]}
          for videos in data["videos"]["category_videos"].values()
          for v in videos]

		log(f"Retrieved {len(movies)} movies", xbmc.LOGINFO)

		for movie in movies:

			title = movie.get("title") or movie.get("name") or "No Title"

			thumbs = movie.get("thumbs", {})
			thumb = thumbs.get("416x260") or thumbs.get("original") or DEFAULTIMAGE

			video_id = movie.get("videoid")
			desc = movie.get("description")
			duration = movie.get("duration")

			li = xbmcgui.ListItem(label=title)
			
			li.setInfo("video",{
				"plot": desc,
				"duration": duration
				})

			li.setArt({
				"thumb": thumb,
				"icon": thumb,
				"poster": thumb,
				"fanart": thumb
			})

			# pass ONLY identifier forward
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
		xbmcplugin.setContent(HANDLE, 'episodes')
		
	except Exception as e:
		log(f"STIRR ERROR: {e}", xbmc.LOGERROR)
	

def resolve_stream(video_id):
	url = f"https://stirr.com/api/v2/videos/{video_id}/playable"

	try:
		log(f"Resolving stream for {video_id}", xbmc.LOGINFO)

		data = get_url(url)

		# 🎯 Extract stream
		stream = (
			data.get("data", [{}])[0]
				.get("media", [{}])[0]
		)

		log(f"STIRR STREAM: {stream}", xbmc.LOGINFO)

		return stream

	except Exception as e:
		log(f"STIRR RESOLVE ERROR: {e}", xbmc.LOGERROR)
		return None


def play_channel(video_id):
	addon_info = "stirr." + str(video_id)
	url = f"https://stirr.com/api/v2/videos/{video_id}/playable"

	try:
		log(f"Resolving stream for {video_id}", xbmc.LOGINFO)

		r = requests.post(url, headers=headers, timeout=10)
		r.raise_for_status()

		data = r.json()

		stream = (
			data.get("data", [{}])[0]
				.get("media", [{}])[0]
		)

		#debug_ssl(stream)
		stream_url = fetch_playable(video_id)

		# 🎯 InputStream Adaptive setup
		li = xbmcgui.ListItem(path=stream_url)		
		li.setInfo("video", {"plot": addon_info})

		li.setProperty("inputstream", "inputstream.adaptive")
		li.setProperty("inputstream.adaptive.manifest_type", "hls")
		#li.setProperty("inputstream.adaptive.manifest_upd_params", "full")
		# Optional but helpful for SSAI streams
		li.setProperty("inputstream.adaptive.stream_headers",
					   "User-Agent={}".format(get_ua()))

		li.setMimeType("application/vnd.apple.mpegurl")
		li.setContentLookup(False)

		xbmcplugin.setResolvedUrl(
			handle=HANDLE,
			succeeded=True,
			listitem=li
		)

		log(f"Playing stream -> {stream}", xbmc.LOGINFO)

	except Exception as e:
		log(f"PLAY ERROR: {e}", xbmc.LOGERROR)
		log(f"422 RESPONSE: {r.text}", xbmc.LOGWARNING)

		xbmcplugin.setResolvedUrl(
			handle=HANDLE,
			succeeded=False,
			listitem=xbmcgui.ListItem()
		)


def debug_ssl(stream_url):
	import requests
	r = requests.get(stream_url, verify=False)
	log(f"STREAM STATUS CODE: {r.status_code}",xbmc.LOGINFO)


def router(paramstring):
	params = dict(urllib.parse.parse_qsl(paramstring))

	action = params.get("action")

	if action == "live":
		list_live()
	elif action == "movies":
		movies()
	elif action == "cat":
		cat(params.get("cat_id"))
	elif action == "tv":
		tv()
	elif action == "favorites":
		favorites()
	elif action == "shows":
		shows(params.get("cat_id"))
	elif action == "episodes":
		episodes(params.get("series_id"),params.get("season_id"))
	elif action == "play":
		play_channel(params.get("videoid"))
	elif action == "add_favorite":
		channel = {
			"videoid": params.get("videoid"),
			"title": params.get("name"),
			"thumbs": {
				"168x105": params.get("logo")
			}
		}
		add_favorite(channel)
	elif action == "remove_favorite":
		remove_favorite(params.get("videoid"))
	else:
		main_menu()


if __name__ == "__main__":
	router(sys.argv[2][1:])
