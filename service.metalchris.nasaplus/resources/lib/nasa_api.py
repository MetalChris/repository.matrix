import re
import json
import html
import urllib.request
import xbmc

from resources.lib.logger import *
from resources.lib.notifications import *

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

		log(f"Live Response: {data}", xbmc.LOGDEBUG)

		# Handles both possible formats safely
		return data not in (False, None, "false", "False", 0)

	except Exception as e:
		log(f"Live Check Error: {e}", xbmc.LOGERROR)
		return False


def fetch_schedule_html():

	try:
		req = urllib.request.Request(
			SCHEDULE_URL,
			headers={"User-Agent": "Mozilla/5.0"}
		)

		with urllib.request.urlopen(req, timeout=10) as response:
			html_data = response.read().decode("utf-8")

			log(f"Schedule HTML length: {len(html_data)}", xbmc.LOGDEBUG)

			return html_data

	except Exception as e:
		log(f"Schedule fetch error: {e}", xbmc.LOGERROR)
		return ""


def parse_events(html_data):

	events = []

	pattern = r'<div\s+.*?grid-col-12 tablet:grid-col-7 desktop:grid-col-9.*?>(.*?)</figure>'

	matches = re.findall(pattern, html_data, re.DOTALL)
	if not matches:
		log("No Scheduled Events Found", xbmc.LOGINFO)
		return events

	log(f"MATCHES: {len(matches)}", xbmc.LOGDEBUG)

	for m in matches:

		t = re.findall(r'/">(.+?)</a>', m)
		u = re.findall(r'href="(.+?)"', m)
		s = re.findall(r'timestamp=(.+?)>', m)

		if not (t and u and s):
			continue

		title = html.unescape(t[0].strip())
		url = u[0].strip()

		try:
			start = int(s[0].strip())
		except:
			continue

		log(f"Match Title: {title}", xbmc.LOGDEBUG)
		log(f"Match URL: {url}", xbmc.LOGDEBUG)
		log(f"Match Start Time: {start}", xbmc.LOGDEBUG)

		events.append({
			"title": title,
			"url": url,
			"start": start
		})

	log(f"EVENTS: {events}", xbmc.LOGDEBUG)

	return events
	
	
def get_schedule():

	html_data = fetch_schedule_html()

	if not html_data:
		return []

	events = parse_events(html_data)

	log(f"Schedule events found: {len(events)}", xbmc.LOGINFO)

	return events
