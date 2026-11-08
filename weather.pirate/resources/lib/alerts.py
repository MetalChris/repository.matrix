import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import hashlib
import json
import os

from resources.lib.convert_to_local import *
ADDON = xbmcaddon.Addon()
ALERT_FILE = xbmcvfs.translatePath(
	os.path.join(ADDON.getAddonInfo('profile'), 'last_alerts.json')
)
SOUND_FILE = os.path.join(ADDON.getAddonInfo('path'), 'resources', 'sounds', 'alert.ogg')

def alert_key(alert):
	"""Stable key: title + issue time. Re-issued alerts get a new time."""
	return '%s|%d' % (alert['title'], alert['time'])
	

def load_shown_keys():
	try:
		with open(ALERT_FILE, 'r') as f:
			return set(json.load(f))
	except (IOError, ValueError):
		return set()
		

def save_shown_keys(keys):
	alert_dir = os.path.dirname(ALERT_FILE)
	if not os.path.isdir(alert_dir):
		os.makedirs(alert_dir)
	with open(ALERT_FILE, 'w') as f:
		json.dump(list(keys), f)
		

def check_and_display_alerts(alerts):
	maybe_reset_alerts()
	show_notification = ADDON.getSetting('alert_notification')

	shown = load_shown_keys()
	current_keys = set(alert_key(a) for a in alerts)

	new_alerts = [a for a in alerts if alert_key(a) not in shown]

	if new_alerts:
		play_alert_sound()
		lines = []
		for a in new_alerts:
			regions = ', '.join(a.get('regions', []))
			lines.append('[%s] %s\n%s\n\nRegions: %s\n' % (
				a['severity'], a['title'], a['description'], regions))
				
		title = f"{a.get('severity')} - {a.get('title')}"
		if show_notification == '0':
			xbmcgui.Dialog().textviewer(title, a.get('description'))
		if show_notification == '1':
			xbmcgui.Dialog().notification(title, f"Expires: {format_unix_time_kodi(a.get('expires'))}", xbmcgui.NOTIFICATION_WARNING, 10000)

		shown.update(current_keys)
		save_shown_keys(shown)   


def play_alert_sound():
	play_sound = ADDON.getSetting('alert_sound') == 'true'
	if not play_sound:
		return
	if xbmc.Player().isPlaying():
		return  # User is watching/listening — they'll see the textviewer
	path = os.path.join(ADDON.getAddonInfo('path'), 'resources', 'sounds', SOUND_FILE)
	if os.path.exists(path):
		xbmc.executebuiltin('PlayMedia("%s")' % path)


def maybe_reset_alerts():
	if ADDON.getSetting('reset_alerts') == 'true':
		try:
			os.remove(ALERT_FILE)
		except (IOError, OSError):
			pass  # File already gone, no problem
		ADDON.setSetting('reset_alerts', 'false')   
