import time
import xbmc

from resources.lib.logger import *
from resources.lib.nasa_api import is_live, get_schedule
from resources.lib.notifications import notify
from resources.lib.cache import save_cache

class PollingManager:

	def __init__(self, service):
		self.service = service


	def check_live(self):
		live = is_live()

		if live and not self.service.was_live:
			if self.service.notify_live_events:
				notify("NASA+", "LIVE Event Streaming Now")

			self.service.was_live = live
		
	def check_schedule(self):
		events = get_schedule()
		current_urls = set(event["url"] for event in events)
		new_urls = current_urls - self.service.known_event_urls
		new_events = [
			event for event in events
			if event["url"] in new_urls
		]

		for event in new_events:

			title = event.get("title", "New NASA+ Event")

			log(f"New Event Detected: {title}", xbmc.LOGINFO)

			if self.service.notify_schedule_events:
				notify(
					"NASA+",
					f"New Event: {title}"
				)

		log(f"New URLs: {new_urls}", xbmc.LOGDEBUG)
		log(f"Current URLs: {current_urls}", xbmc.LOGDEBUG)
		
		if current_urls != self.service.known_event_urls:
			self.service.known_event_urls = current_urls

			save_cache({
				"known_event_urls": list(self.service.known_event_urls)
			})
			log("Cache updated", xbmc.LOGDEBUG)
			
		self.service.cached_events = events


	def get_next_event_start(self):

		if not hasattr(self, "cached_events"):
			return None

		now = time.time()

		future_events = [
			e for e in self.service.cached_events
			if e.get("start") and e["start"] > now
		]

		if not future_events:
			log("No future events found", xbmc.LOGDEBUG)
			return None

		next_event_start = min(e["start"] for e in future_events)
		time_until_event = next_event_start - now

		if self.service.known.service.known_logged_next_event != next_event_start:
			log(f"Next event start: {next_event_start}", xbmc.LOGDEBUG)
			self.service.known_logged_next_event = next_event_start

		# optional: reduce spam further by bucketing time
		bucket = int(time_until_event // 300)  # 5-minute buckets

		if self.service.known_logged_delta_bucket != bucket:
			log(f"Time until event: {time_until_event}", xbmc.LOGDEBUG)
			self.service.known_logged_delta_bucket = bucket

		return next_event_start


	def get_live_interval(self):

		now = time.time()
		next_event = self.get_next_event_start()

		# Default slow polling
		interval = 300  # 5 minutes

		if not next_event:
			return interval

		time_until_event = next_event - now

		# Event happening soon (within 30 min)
		if time_until_event <= 1800:
			return 60  # 1 minute

		# Event within 2 hours
		if time_until_event <= 7200:
			return 120  # 2 minutes

		return interval
