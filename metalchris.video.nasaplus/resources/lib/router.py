# -------------------
# Router
# -------------------

from resources.lib.caching import _cache_flush

def router(params):
	action = params.get("action")
	url = params.get("url")
	try:
		if action is None:
			from default import get_main_menu
		elif action == "live":
			live_menu(url)
		elif action == "topics":
			topics_menu(url)
		elif action == "series":
			series_menu(url)
		elif action == "videos":
			video_menu(url)
		elif action == "play":
			play_video(url)
		elif action == "stream":
			stream_video(url,title,image)
		if action == "clear_cache":
			if xbmcgui.Dialog().yesno("NASA+", "Clear cached data?"):
				clear_cache()
		else:
			get_main_menu()
	finally:
		_cache_flush()
