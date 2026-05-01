import xbmc
import xbmcgui
import xbmcaddon
import requests
import urllib.request
import json
import re

from resources.lib.logger import *
from resources.lib.convert_to_local import format_duration
from resources.lib.get_items import *

		
def extra_meta(rating,duration):
	#log(f"[PROGRAM INFO] S,E,D: {season,episode,duration}", xbmc.LOGDEBUG)	
	try:
		extra = []
		if rating:
			extra.append(rating)
		else:
			rating = 'Not Rated'
			extra.append(rating)
		if duration:
			duration_text = format_duration(int(duration))
			extra.append(duration_text)

		meta_line = " • ".join(extra)
		
		return meta_line

	except Exception as e:
		log(f"[PROGRAM INFO] Failed to fetch: {e}", xbmc.LOGERROR)
		xbmcgui.Dialog().notification("TCLTV+ EPG", "Failed to load program info", sound=False)
