# resources/lib/write_videos.py

import json
import xbmc
import xbmcvfs
import xbmcaddon
import time

from resources.lib.logger import *

ADDON_ID = xbmcaddon.Addon().getAddonInfo('id')
PROFILE_PATH = "special://userdata/addon_data/metalchris.video.nasaplus/"
VIDEOS_FILE = PROFILE_PATH +  ADDON_ID + ".json"


def write_video_list(videos_data,topic):
	"""
	videos_data format:
	{
		"title": {"description": "...", "url": "..."},
		...
	}
	"""
	
	now = time.time()
	merged_dict = {}
	
	try:
		real_path = xbmcvfs.translatePath(PROFILE_PATH)

		if not xbmcvfs.exists(real_path):
			xbmcvfs.mkdirs(real_path)
			
		if xbmcvfs.exists(VIDEOS_FILE):
			with xbmcvfs.File(VIDEOS_FILE, 'r') as f:
				data = json.load(f)
			merged_dict = {**merged_dict, **data['videos'], **videos_data}

		else:
			merged_dict = {**merged_dict, **videos_data}
			with xbmcvfs.File(VIDEOS_FILE, 'w') as f:
				f.write(json.dumps({"timestamp": now, "videos": merged_dict}, indent=2))   

		#file_path = xbmcvfs.translatePath(VIDEOS_FILE)

		with xbmcvfs.File(VIDEOS_FILE, 'w') as f:
			f.write(json.dumps({"timestamp": now, "videos": merged_dict}, indent=2))   

		log(f"[WRITE VIDEOS] [{topic}] {len(videos_data)} videos", xbmc.LOGINFO)

	except Exception as e:
		log(f"[WRITE VIDEOS] [{topic}] Failed to write videos: {e}", xbmc.LOGERROR)
