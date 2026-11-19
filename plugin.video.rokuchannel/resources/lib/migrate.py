import ast
import json
import os
import re
import xbmcvfs
from urllib.parse import unquote

from logger import *

def create_favorites():
	favorites_path = xbmcvfs.translatePath(
		'special://profile/addon_data/plugin.video.rokuchannel'
	)
	migrate_path = xbmcvfs.translatePath(
		'special://profile/addon_data/plugin.video.rokuchannel'
	)

	favorites = {}

	for filename in os.listdir(favorites_path):
		if not filename.endswith('-livefeed.txt'):
			continue
		log(f"[MIGRATE]Favorite: {filename}",xbmc.LOGDEBUG)

		filepath = os.path.join(favorites_path, filename)

		with open(filepath, 'r') as f:
			data = ast.literal_eval(f.read())

		playback_url, content_type, logo_url = data
		
		log(f"[MIGRATE]LOGO URL: {logo_url}", xbmc.LOGDEBUG)

		#match = re.search(r'/id/([^/]+)/', logo_url)
		match = re.search(r'.*%2F(.*)$', playback_url)
		log(f"[MIGRATE]REGEX MATCH: {match.group(1) if match else 'NONE'}", xbmc.LOGDEBUG)
		if not match:
			continue

		sid = match.group(1)

		name = unquote(
			filename.rsplit('-livefeed.txt', 1)[0].replace('+', ' ')
		)

		favorites[sid] = {
			'slug': sid,
			'name': name,
			'logo': logo_url,
			'url': playback_url,
			'addon_id': 'plugin.video.rokuchannel'
		}

	favorites_file = os.path.join(favorites_path, 'favorites.json')

	with open(favorites_file, 'w') as f:
		json.dump(favorites, f, indent=4)
		
	log(f"[MIGRATE]Favorites Migration Complete",xbmc.LOGDEBUG)
