import xbmc
import xbmcgui
from resources.lib.logger import log
import xbmcaddon

from resources.lib.playback_isa import play_episode_isa
from resources.lib.logger import *

ADDON = xbmcaddon.Addon()

def safe_playback(title, stream, image, captions, epg_window):
    try:
        # Attempt to close the EPG window
        #if epg_window:
            #epg_window.close()

        # Start playback
        play_episode_isa(title, stream, image, captions, epg_window=None)

    except Exception as e:
        log(f"[SAFE_PLAYBACK] Playback failed: {e}", xbmc.LOGERROR)
        # If something went wrong, reopen the EPG window
        #try:
            #if epg_window:
                #epg_window.open()
        #except Exception as e2:
            #log(f"[SAFE_PLAYBACK] Failed to reopen EPG window: {e2}", xbmc.LOGERROR)
