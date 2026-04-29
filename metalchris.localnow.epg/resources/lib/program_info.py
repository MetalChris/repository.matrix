import xbmc
import xbmcgui
import xbmcaddon
import requests
import urllib.request
import json

from resources.lib.logger import *
from resources.lib.convert_to_local import format_duration

HEADERS = {
	"User-Agent": "Mozilla/5.0 (Linux; Android 15; T702D Build/AP3A.240905.015.A2; wv)",
	"Accept": "application/json",
	"Referer": "https://tcltv.plus/"
}

def show_program_info(channel_name,now_id,next_id,now_end,next_time):
	url = 'https://gateway-prod.ideonow.com/api/metadata/v1/epg/program/detail?ids=' + next_id + '&ids=' + now_id
	log(f"[PROGRAM INFO] URL: {url}", xbmc.LOGINFO)

	try:
		req = urllib.request.Request(url, headers=HEADERS)
		with urllib.request.urlopen(req, timeout=10) as resp:
			data = json.loads(resp.read())
			log(f"[PROGRAM INFO] JSON LENGTH: {len(data)}", xbmc.LOGDEBUG)
		# Extract descriptions (structure may vary slightly)
		programs = data if isinstance(data, list) else data.get("data", [])
		
		program_lookup = {
			prog.get("id"): prog
			for prog in programs
			if isinstance(prog, dict)
		}
		
		ordered_ids = [now_id, next_id]

		ordered_programs = [
			program_lookup.get(pid)
			for pid in ordered_ids
			if pid in program_lookup
		]

		text_lines = []

		for i, prog in enumerate(ordered_programs):
			desc = prog.get("desc", "No description available")
			rating = prog.get("rating", "")
			year = prog.get("release_year", "")
			
			series = prog.get("series") or {}
			title = series.get("name") or prog.get("title", "Unknown")
			season = series.get("season")
			episode = series.get("episode")
			
			duration_text = format_duration(prog.get("length"))

			extra = []
			if season and episode:
				extra.append(f"S{season} E{episode}")
			if rating:
				extra.append(rating)
			if year:
				extra.append(str(year))
			if duration_text:
				extra.append(duration_text)

			meta_line = " • ".join(extra)

			# Add prefix based on position
			prefix = "Now: " if i == 0 else "Next: "

			
			block = f"[B][I]{prefix}[/I] {title}[/B]"				

			if meta_line:
				block += f"\n[I]{meta_line}[/I]"

			if i < 1:
				block+= f"\n{desc}\n• [I]{now_end}[/I]"
			else:
				block += f"\n{desc}\n• [I]{next_time}[/I]"


			text_lines.append(block)
			#text_lines.append(f"[B]{prefix}{title}[/B]\n{desc}")
			
		xbmcgui.Dialog().textviewer(channel_name, "\n\n".join(text_lines))

	except Exception as e:
		log(f"[PROGRAM INFO] Failed to fetch: {e}", xbmc.LOGERROR)
		xbmcgui.Dialog().notification("TCLTV+ EPG", "Failed to load program info", sound=False)
