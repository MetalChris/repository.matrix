import sys
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import os
import requests
import re
import json
import html
from urllib.parse import quote_plus
from urllib.parse import unquote_plus
from resources.lib.logger import log

ADDON      = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
MEDIA_PATH = os.path.join(ADDON_PATH, "resources", "media")

ICON   = os.path.join(MEDIA_PATH, "icon.png")
FANART = os.path.join(MEDIA_PATH, "fanart.jpg")

HANDLE = int(sys.argv[1])

SHOWS_URL = "https://play.history.com/shows"

#xbmc.log("HISTORY ADDON STARTED", xbmc.LOGERROR)

try:
	debug_enabled = ADDON.getSettingBool("debug")
except Exception:
	debug_enabled = False

status = "ENABLED" if debug_enabled else "DISABLED"
xbmc.log(f"[{ADDON_NAME} v{ADDON_VERSION}] [ADD-ON STARTED] [DEBUG: {status}]", level=xbmc.LOGINFO)

def list_shows():
	log("list_shows CALLED", xbmc.LOGINFO)

	try:
		response = requests.get(
			SHOWS_URL,
			headers={"User-Agent": "Mozilla/5.0"},
			timeout=10
		)

		log(f"REQUEST URL: {SHOWS_URL}", xbmc.LOGINFO)
		log(f"STATUS CODE: {response.status_code}", xbmc.LOGINFO)
		log(f"FINAL URL (after redirects): {response.url}", xbmc.LOGINFO)

		html = response.text

		match = re.search(
			r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
			html,
			re.DOTALL
		)

		if not match:
			log("NO JSON FOUND", xbmc.LOGERROR)
			return

		data = json.loads(match.group(1))

		apollo = data.get("props", {}).get("apolloState", {})
		# 🔍 DEBUG: inspect all Series nodes BEFORE selection
		for node in apollo.values():
			if isinstance(node, dict) and node.get("__typename") == "Series":
				log(
					f"HISTORY SERIES CANDIDATE: id={node.get('id')} canonical={node.get('canonical')} unlocked={len(node.get('unlockedEpisodes', [])) if node.get('unlockedEpisodes') else 0}",
					xbmc.LOGDEBUG
				)

		log(f"apollo keys: {len(apollo)}", xbmc.LOGINFO)

		shows = []

		for key, item in apollo.items():

			if not isinstance(item, dict):
				continue

			if item.get("__typename") != "Series":
				continue

			if item.get("isBehindWall", True):
				continue

			# --- ADD THIS BLOCK ---
			episode_count = item.get("displayMetadata", {}).get("episodeCount")

			try:
				episode_count = int(episode_count)
			except (TypeError, ValueError):
				episode_count = 0

			if episode_count == 0:
				log(f"SKIPPING SHOW (no episodes): {item.get('title')}", xbmc.LOGINFO)
				continue
			# --- END BLOCK ---				

			title = (item.get("title"))
			slug = item.get("canonical")
			slug = slug.replace("/shows/", "").strip("/")
			slug = f"{slug}/unlocked"
			image = item.get("images", {}).get("sizes", {}).get("primary16x9", "")
			box = item.get("images", {}).get("sizes", {}).get("primary2x3", "")


			if not title:
				continue

			# fallback safety
			if not slug:
				slug = ""

			base = sys.argv[0]
			url = f"{base}?action=episodes&slug={slug}"
			#xbmc.log(f"HISTORY URL: {url}", xbmc.LOGERROR)	

			li = xbmcgui.ListItem(label=title)

			li.setArt({
				"thumb": box,
				"icon": box,
				"fanart": image
			})

			xbmcplugin.addDirectoryItem(
				HANDLE,
				url,
				li,
				True  # <-- IMPORTANT: folder now
			)
		xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
		xbmcplugin.endOfDirectory(HANDLE)

	except Exception as e:
		log(f"ERROR: {e}", xbmc.LOGERROR)
		li = xbmcgui.ListItem(label="ERROR")
		xbmcplugin.addDirectoryItem(HANDLE, "", li, False)
		xbmcplugin.endOfDirectory(HANDLE)
		
		
def list_episodes(slug):
	log(f"EPISODES CALLED FOR: {slug}", xbmc.LOGINFO)

	try:
		url = f"https://play.history.com/shows/{slug}"

		response = requests.get(
			url,
			headers={"User-Agent": "Mozilla/5.0"},
			timeout=10
		)

		log(f"STATUS CODE: {response.status_code}", xbmc.LOGINFO)

		match = re.search(
			r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
			response.text,
			re.DOTALL
		)

		if not match:
			log("EPISODES: NO JSON FOUND", xbmc.LOGERROR)
			return

		data = json.loads(match.group(1))
		apollo = data.get("props", {}).get("apolloState", {})

		# ---------------- CLEAN EPISODE SOURCE ----------------
		series_obj = next(
			(
				v for v in apollo.values()
				if isinstance(v, dict)
				and v.get("__typename") == "Series"
				and v.get("unlockedEpisodes")
			),
			None
		)

		if not series_obj:
			log("EPISODES: SERIES NOT FOUND", xbmc.LOGERROR)
			return

		unlocked_refs = series_obj.get("unlockedEpisodes", [])
		log(f"UNLOCKED EPISODES: {len(unlocked_refs)}", xbmc.LOGINFO)

		# ---------------- BUILD EPISODES ----------------
		episodes = []

		for ref in unlocked_refs:
			ref_id = ref.get("__ref")
			if not ref_id:
				continue

			ep = apollo.get(ref_id)
			if not ep:
				continue

			title = html.unescape(ep.get("title") or ep.get("name") or "Untitled")
			canonical = ep.get("canonical", "")

			video_id = None
			video_ref = ep.get("primaryVideo", {}).get("__ref")
			if video_ref:
				video_obj = apollo.get(video_ref, {})
				video_id = video_obj.get("id")

			episodes.append({
				"title": title,
				"description": html.unescape(ep.get("description", "")),
				"season": ep.get("tvSeasonNumber", ""),
				"episode": ep.get("tvSeasonEpisodeNumber", ""),
				"canonical": canonical,
				"video_id": video_id,
				"image": ep.get("images", {}).get("sizes", {}).get("video16x9", "")
			})

		# ---------------- RENDER ----------------
		for ep in episodes:
			label = ep["title"]

			if ep["season"] and ep["episode"]:
				label = f"S{ep['season']:02}E{ep['episode']:02} - {label}"

			li = xbmcgui.ListItem(label=label)
			li.setProperty("IsPlayable", "true")

			li.setInfo("video", {
				"title": ep["title"],
				"plot": ep["description"],
				"season": ep["season"],
				"episode": ep["episode"],
			})

			li.setArt({
				"thumb": ep["image"],
				"icon": ep["image"],
				"fanart": ep["image"]
			})

			url = (
				f"{sys.argv[0]}"
				f"?action=play"
				f"&video_id={ep['video_id']}"
				f"&canonical={quote_plus(ep['canonical'])}"
			)

			xbmcplugin.addDirectoryItem(HANDLE, url, li, False)

		xbmcplugin.setContent(HANDLE, "episodes")
		xbmcplugin.endOfDirectory(HANDLE)

	except Exception as e:
		log(f"EPISODES ERROR: {e}", xbmc.LOGERROR)
		
		
def get_stream_from_dai(content_source_id, video_id):
	import requests

	url = f"https://dai.google.com/ondemand/hls/content/{content_source_id}/vid/{video_id}/streams"

	headers = {
		"User-Agent": "Mozilla/5.0",
		"Accept": "application/json"
	}

	r = requests.post(url, headers=headers, timeout=10)
	log(f"DAI RESPONSE: HTTP {r.status_code}", xbmc.LOGINFO)

	if not r.ok:
		log(f"DAI ERROR: HTTP {r.status_code}", xbmc.LOGERROR)

		xbmcgui.Dialog().notification(
			f"{r.status_code} {r.reason}",
			"This episode is not available",
			ICON,
			4000,
			False
		)
		return None
		
	data = r.json()

	stream_url = data.get("stream_manifest")

	#xbmc.log(f"DAI STREAM URL: {stream_url}", xbmc.LOGINFO)

	return stream_url
	
	
def play_episode(video_id, canonical):
	log(f"PLAY CALLED: video_id={video_id} canonical={canonical}", xbmc.LOGINFO)

	try:
		episode_url = f"https://play.history.com{canonical}"

		html = requests.get(
			episode_url,
			headers={"User-Agent": "Mozilla/5.0"},
			timeout=10
		).text

		soup_match = re.search(
			r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
			html,
			re.DOTALL
		)

		if not soup_match:
			log("PLAY: NO NEXT DATA SCRIPT FOUND", xbmc.LOGERROR)
			return

		raw_json = soup_match.group(1).strip()

		log(f"PLAY RAW JSON START: {raw_json[:200]}", xbmc.LOGDEBUG)

		try:
			next_data = json.loads(raw_json)
		except Exception as e:
			log(f"PLAY JSON PARSE ERROR: {e}", xbmc.LOGERROR)
			return

		apollo = next_data.get("props", {}).get("apolloState", {})

		content_source_id = (
			apollo
			.get("ROOT_QUERY", {})
			.get("config", {})
			.get("vendor", {})
			.get("dfp", {})
			.get("contentSourceID")
		)

		log(f"PLAY content_source_id: {content_source_id}", xbmc.LOGINFO)

		if not content_source_id or not video_id:
			log("PLAY: MISSING IDS", xbmc.LOGERROR)
			return

		# video_id sometimes comes in as list
		if isinstance(video_id, list):
			video_id = video_id[0]

		stream_url = get_stream_from_dai(content_source_id, video_id)

		if not stream_url:
			log("PLAY: NO STREAM URL (likely non-DAI episode)", xbmc.LOGERROR)
			return

		log(f"PLAY STREAM: {stream_url}", xbmc.LOGINFO)

		li = xbmcgui.ListItem(path=stream_url)

		li.setProperty("inputstream", "inputstream.adaptive")
		li.setProperty("inputstream.adaptive.manifest_type", "hls")
		li.setMimeType("application/vnd.apple.mpegurl")
		li.setContentLookup(False)

		xbmcplugin.setResolvedUrl(HANDLE, True, li)
		return

	except Exception as e:
		log(f"PLAY ERROR: {e}", xbmc.LOGERROR)
		
		
from urllib.parse import parse_qs

def router():
	params = parse_qs(sys.argv[2][1:] if len(sys.argv) > 2 else "")

	action = params.get("action", [None])[0]
	slug = params.get("slug", [None])[0]

	log(f"ROUTER action={action} slug={slug}", xbmc.LOGINFO)

	if action == "episodes" and slug:
		list_episodes(slug)
	elif action == "play":
		video_id = params.get("video_id", [""])[0]
		canonical = unquote_plus(params.get("canonical", [""])[0])
		play_episode(video_id, canonical)		
	else:
		list_shows()


router()
