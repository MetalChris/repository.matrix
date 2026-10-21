import re
import json
import html
import urllib.request
import xbmc

SCHEDULE_URL = "https://plus.nasa.gov/scheduled-events/"

LIVE_URL = "https://plus.nasa.gov/wp-json/nasaplus/v1/live"


def is_live():

	try:
		req = urllib.request.Request(
			LIVE_URL,
			headers={"User-Agent": "Mozilla/5.0"}
		)

		with urllib.request.urlopen(req, timeout=10) as response:
			data = json.loads(response.read().decode("utf-8"))

		xbmc.log(f"NASA+ Live Response: {data}", xbmc.LOGINFO)

		# Handles both possible formats safely
		return data not in (False, None, "false", "False", 0)

	except Exception as e:
		xbmc.log(f"NASA+ Live Check Error: {e}", xbmc.LOGERROR)
		return False


def fetch_schedule_html():

	try:
		req = urllib.request.Request(
			SCHEDULE_URL,
			headers={"User-Agent": "Mozilla/5.0"}
		)

		with urllib.request.urlopen(req, timeout=10) as response:
			html_data = response.read().decode("utf-8")

			xbmc.log(f"NASA+ schedule HTML length: {len(html_data)}", xbmc.LOGINFO)

			return html_data

	except Exception as e:
		xbmc.log(f"NASA+ schedule fetch error: {e}", xbmc.LOGERROR)
		return ""
		
		
import re
import html
import xbmc

import re
import html
import xbmc

def parse_events(html_data):

	events = []
	
	pattern = r'<div\s+.*?grid-col-12 tablet:grid-col-7 desktop:grid-col-9.*?>(.*?)</figure>'

	# Find all start times first (anchor point)
	starts = list(re.findall('timestamp=(.+?)>', html_data))

	xbmc.log(f"NASA+ DEBUG start-time matches: {len(starts)}", xbmc.LOGINFO)
	#xbmc.log(f"NASA+ RAW SNIPPET:\n{html_data[:2000]}", xbmc.LOGINFO)

	matches = re.findall(pattern, html_data, re.DOTALL)

	xbmc.log(f"NASA+ DEBUG MATCHES: {len(matches)}", xbmc.LOGINFO)
	#xbmc.log(f"NASA+ DEBUG context sample: {matches}", xbmc.LOGINFO)

	for count, m in enumerate(matches):
		#title = m.find('a')['class,{nasatv-video-title}']
		t = re.findall('/">(.+?)</a>', m)
		u = re.findall('href="(.+?)"', m)
		s = re.findall('timestamp=(.+?)>', m)
		if t:
			title = t[0]
			url = u[0]
			start = s[0]
			xbmc.log(f"NASA+ DEBUG Match Title: {title}", xbmc.LOGINFO)
			xbmc.log(f"NASA+ DEBUG Match URL: {url}", xbmc.LOGINFO)
			xbmc.log(f"NASA+ DEBUG Match Start Time: {start}", xbmc.LOGINFO)
		
		if title:
			events.append({
				"title": html.unescape(title.strip()),
				"url": url,
				"start": int(start.strip())
			})
		#count += 1
	xbmc.log(f"NASA+ DEBUG EVENTS: {events}", xbmc.LOGINFO)
	return events
	
	
def get_schedule():

	html_data = fetch_schedule_html()

	if not html_data:
		return []

	events = parse_events(html_data)

	xbmc.log(f"NASA+ schedule events found: {len(events)}", xbmc.LOGINFO)

	return events
