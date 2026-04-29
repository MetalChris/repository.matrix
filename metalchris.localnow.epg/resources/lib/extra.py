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

		
def extra_meta(season,episode,duration):
	#log(f"[PROGRAM INFO] S,E,D: {season,episode,duration}", xbmc.LOGDEBUG)	
	try:
		text_lines = []
		block = []

		extra = []
		if season and episode:
			if season == '0':
				pass
			elif season and episode != 'None':
				extra.append(f"S{season} E{episode}")
		if duration:
			duration_text = format_duration(int(duration))
			extra.append(duration_text)

		meta_line = " • ".join(extra)			

		if meta_line:
			block += f"[I]{meta_line}[/I]"

		text_lines.append(block)
		
		#log(f"[PROGRAM INFO] META: {meta_line}", xbmc.LOGDEBUG)
		
		return meta_line
		#text_lines.append(f"[B]{prefix}{title}[/B]\n{desc}")
			
		#xbmcgui.Dialog().textviewer(channel, "\n\n".join(text_lines))

	except Exception as e:
		log(f"[PROGRAM INFO] Failed to fetch: {e}", xbmc.LOGERROR)
		xbmcgui.Dialog().notification("TCLTV+ EPG", "Failed to load program info", sound=False)
