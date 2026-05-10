import xbmc
import xbmcaddon

from resources.lib.logger import *

ADDON = xbmcaddon.Addon(id="service.metalchris.nasaplus")

class AudioTrackSelector(xbmc.Player):
	def __init__(self):
		super().__init__()
		self.monitor = xbmc.Monitor()

	def onAVStarted(self):
		
		if not ADDON.getSettingBool("auto_audio_select"):
			return
		log("AudioTrackSelector: Playback started", xbmc.LOGINFO)

		try:
			# Primary check: plugin URL
			filename = self.getPlayingFile()
			is_nasa = filename.startswith("plugin://metalchris.video.nasaplus")

			# Fallback: ListItem property
			if not is_nasa:
				li = self.getPlayingItem()
				if li:
					prop = li.getProperty('metalchris.nasaplus')
					if prop == 'true':
						log("AudioTrackSelector: Detected NASA+ via property", xbmc.LOGINFO)
						is_nasa = True

			# Single exit gate (important)
			if not is_nasa:
				log("AudioTrackSelector: Skipping (not NASA+)", xbmc.LOGINFO)
				return

			audio_streams = []

			for _ in range(5):
				audio_streams = self.getAvailableAudioStreams()
				if audio_streams:
					break
				xbmc.sleep(100)

			if len(audio_streams) > 1:
				try:
					stream_index = int(1)
					self.setAudioStream(stream_index)
					log("AudioTrackSelector: Switched to audio stream index 1", xbmc.LOGINFO)
				except Exception as e:
					log(f"AudioTrackSelector: failed to set audio stream: {e}", xbmc.LOGERROR)

		except Exception as e:
			log(f"AudioTrackSelector error: {e}", xbmc.LOGERROR)
