import xbmc
import xbmcvfs
import xbmcaddon
import json
import shutil
import urllib.parse, urllib.error, urllib.request, urllib.error
import requests
from requests import Request, Session
import datetime
import http.cookiejar
from http.cookiejar import LWPCookieJar
import re

from logger import *
from check_cache_ttl import *
from roku_meta import *

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))

CookieJar = http.cookiejar.LWPCookieJar(os.path.join(addon_path_profile, 'cookies.lwp'))

s = requests.Session()
s.cookies = CookieJar

Live = 'https://therokuchannel.roku.com/api/v2/homescreen/pages/w.DzWLgJdPr1hPM0J89axBs1lBP4jwQzcdedlray1BhAP79Q3q6wTQA4Bx8RMxUYM2Ll2RWGcRDDgRN149tWYwVJAq6oSZjlGydblvFVb0ymJQw5sxmDy6Yj53HeVp9aVwG4f1Qbxd79wg/rendered?limit=99'
apiUrl = 'https://therokuchannel.roku.com/api/v2/homescreen/v2/home'

def find_channel(sid):
	data = get_live_api()
	for collection in data.get('collections', []):
		for view in collection.get('view', []):
			content = view.get('content', {})
			meta = content.get('meta', {})

			if meta.get('sid') == sid:
				log(f"FIND_CHANNEL CONTENT LENGTH: {len(content)}", xbmc.LOGDEBUG)
				#infoText = get_meta(view)
				#log(f"INFOTEXT: {infoText}", xbmc.LOGINFO)
				
				infoText = get_saved_epg(view)
				log(f"FIND_CHANNEL INFOTEXT: {infoText}", xbmc.LOGDEBUG)
				return infoText

	return None


def find_movie(url):
	if os.path.exists(addon_path_profile + 'saved.json'):
		with open(addon_path_profile + 'saved.json', "r") as f:
			saved = json.load(f)
	else:
		saved = []
	response = s.get(url)
	log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGDEBUG)
	log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGDEBUG)
	data = json.loads(response.text)
	with open(addon_path_profile + 'saved.json', "w") as f:
		json.dump(data, f, indent=4)
	genres = []
	for count, item in enumerate(data['genres']):
		genres.append(item.title())
	#log('GENRES: ' + str(genres),xbmc.LOGDEBUG)
	log('DESCRIPTION LENGTH: ' + str(len(data['descriptions'])),xbmc.LOGDEBUG)
	if len(data['descriptions']) >= 1:
		descriptions = []
		for count, item in enumerate(data['descriptions']):
			descriptions.append(item)
		#log('DESCRIPTION: ' + str(descriptions),xbmc.LOGDEBUG)
		desc = descriptions[-1]
		description = data['descriptions'][desc]['text']
	else:
		description = data['description']
	duration = data.get('runTimeSeconds',0) 
	#log('DURATION: ' + str(duration),xbmc.LOGDEBUG)
	if 'runTimeSeconds' in data:
		duration = data['runTimeSeconds']
	else:
		duration = 0
	rating = data['parentalRatings'][0]['code']
	runtime = str(datetime.timedelta(seconds=duration))
	info = '(' + str(genres)[1:-1].replace("'","") + ') ' + str(description) + '\n\nRated: ' + rating + ' Duration: ' + str(runtime)
	#log('DESCRIPTION: ' + str(description),xbmc.LOGDEBUG)
	if data['type'] == 'series':
		episodes = len(data['episodes'])
		log('EPISODES: ' + str(episodes),xbmc.LOGDEBUG)
		info = '(' + str(genres)[1:-1].replace("'","") + ') ' + str(description) + '\n\nRated: ' + rating + '\n\n' + str(episodes) + ' Episodes'

	return info
	
	
def get_live_api():
	if is_cache_stale(addon_path_profile + 'live.json') != False:
		log(f"Downloading from API... {Live}",xbmc.LOGINFO)
		with urllib.request.urlopen(Live) as response, open(os.path.join(addon_path_profile, 'live.json'), 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
	with open(os.path.join(addon_path_profile, 'live.json'), 'rb') as f:
		data = json.load(f)
		
	return data
	
	
def get_movie():
	if is_cache_stale(addon_path_profile + 'api.json') != False:
		log(f"Downloading from API... {apiUrl}",xbmc.LOGINFO)
		with urllib.request.urlopen(Live) as response, open(os.path.join(addon_path_profile, 'api.json'), 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
	with open(os.path.join(addon_path_profile, 'api.json'), 'rb') as f:
		data = json.load(f)
		
	return data
