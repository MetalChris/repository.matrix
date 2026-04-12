import xbmc

class AudioTrackSelector(xbmc.Player):
	def __init__(self):
		super().__init__()
		self.monitor = xbmc.Monitor()

	def onAVStarted(self):
		xbmc.log("AudioTrackSelector: Playback started", xbmc.LOGINFO)

		try:
			# ✅ Primary check: plugin URL
			filename = self.getPlayingFile()

			is_nasa = filename.startswith("plugin://metalchris.video.nasaplus")

			# ✅ Fallback: ListItem property
			if not is_nasa:
				li = self.getPlayingItem()
				if li:
					prop = li.getProperty('metalchris.nasaplus')
					if prop == 'true':
						xbmc.log("AudioTrackSelector: Detected NASA+ via property", xbmc.LOGINFO)
						is_nasa = True

			if not is_nasa:
				xbmc.log("AudioTrackSelector: Skipping (not NASA+)", xbmc.LOGINFO)
				return

			xbmc.sleep(500)

			audio_streams = self.getAvailableAudioStreams()

			if len(audio_streams) > 1:
				#current = self.getAudioStream()
				#if current != 1:
				self.setAudioStream(1)
				xbmc.log("AudioTrackSelector: Switched to audio stream index 1", xbmc.LOGINFO)

		except Exception as e:
			xbmc.log(f"AudioTrackSelector error: {e}", xbmc.LOGERROR)


if __name__ == "__main__":
	player = AudioTrackSelector()

	while not player.monitor.abortRequested():
		xbmc.sleep(1000)
