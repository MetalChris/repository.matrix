import xbmc
import xbmcaddon
import time

from resources.lib.logger import *
from resources.lib.nasa_api import is_live
from resources.lib.notifications import notify
from resources.lib.nasa_api import get_schedule
from resources.lib.audio_selector import AudioTrackSelector
from resources.lib.cache import load_cache, save_cache
from resources.lib.polling import PollingManager
from resources.lib.rover import remove_old_service

ADDON = xbmcaddon.Addon(id="service.metalchris.nasaplus")

class MonitorService:

	def __init__(self):
		remove_old_service()
		self.monitor = xbmc.Monitor()
		self.check_live_events = ADDON.getSettingBool("check_live_events")
		self.notify_live_events = ADDON.getSettingBool("notify_live_events")
		self.notify_schedule_events = ADDON.getSettingBool("notify_schedule_events")
		self.polling = PollingManager(self)
		self.was_live = False
		self.known_events = []
		
		cache = load_cache()
		
		self.known_event_urls = set(
			cache.get("known_event_urls", [])
		)

		log(f"Cache Contents: {cache}", xbmc.LOGDEBUG)
		
		self.last_schedule_check = 0
		self.last_live_check = 0

		self.schedule_interval = ADDON.getSettingInt("schedule_interval") * 3600 # 6 hour default
		self.live_idle_interval = ADDON.getSettingInt("live_idle_interval") * 60 # 5 minute default
		self.live_active_interval = ADDON.getSettingInt("live_active_interval") # 60 second default
		
		self.auto_audio_select = ADDON.getSettingBool("auto_audio_select")
		self.audio_selector = AudioTrackSelector()
		
		self.last_logged_next_event = None
		self.last_logged_delta_bucket = None

	def run(self):

		log("Monitor Service Started", xbmc.LOGINFO)
		notify("NASA+", "Monitor Service Started")

		while not self.monitor.abortRequested():

			now = time.time()

			if self.check_live_events:
				# Always check live, but throttled
				if now - self.last_live_check >= self.polling.get_live_interval():
					self.polling.check_live()
					self.last_live_check = now

			# Schedule check (slow cadence)
			if now - self.last_schedule_check >= self.schedule_interval:
				self.polling.check_schedule()
				self.last_schedule_check = now

			# small sleep to prevent CPU spin
			self.monitor.waitForAbort(5)


		log("Monitor Service Stopped", xbmc.LOGINFO)

