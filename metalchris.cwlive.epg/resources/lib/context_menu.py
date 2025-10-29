import xbmc
import xbmcgui
import xbmcaddon

import json, os, xbmcvfs

from resources.lib.logger import *
from resources.lib.utils_fetch import *
from resources.lib.favorites import add_favorite, has_favorites, list_favorites, fetch_favorites, remove_favorite, _save_favorites
from resources.lib.refresh_addon_settings import *

GENRE_FILTER_PROP = "cwlive_epg_genre_filter"
addon = xbmcaddon.Addon()

def handle_context_menu(epg_window, listitem):
	log("[CONTEXT_MENU] handle_context_menu called")

	try:
		win = xbmcgui.Window(10025)
		in_favorites = bool(epg_window.getProperty("FAVORITES_FILTER"))

		# --- Base options ---
		options = [
			"Show Now program info",
			"Show Next program info"
		]

		# Only show genre search if NOT in favorites
		if not in_favorites:
			options.append("Search by Genre...")

		if epg_window.getProperty(GENRE_FILTER_PROP) and not in_favorites:
			options.append("Clear Genre Filter")

		# Dynamically add favorites-related options
		if has_favorites():
			if in_favorites:
				options.append("Exit Favorites")
				options.append("Remove channel from Favorites")
				options.append("Clear All Favorites")  # new option
			else:
				options.append("View Favorites")


		# --- Add channel to favorites only if not already viewing favorites ---
		if listitem.getProperty("channel_id") and not in_favorites:
			options.append("Add channel to Favorites")

		# --- Show menu ---
		choice = xbmcgui.Dialog().select("Options", options)
		if choice == -1:
			return

		sel = options[choice]

		# --- Handlers ---
		if sel == "Show Now program info":
			channel = listitem.getProperty("channel") or "No description available."
			title = listitem.getProperty("Label") or "No description available."
			description = listitem.getProperty("Label2") or "No description available."
			times = listitem.getProperty("nowtimes") or "No description available."
			xbmcgui.Dialog().textviewer(f"{channel} – {title}", f"{description}\n\n{times}")

		elif sel == "Show Next program info":
			channel = listitem.getProperty("channel") or "No description available."
			title = listitem.getProperty("Label5") or "No description available."
			description = listitem.getProperty("Label4") or "No description available."
			times = listitem.getProperty("nexttimes") or "No description available."
			xbmcgui.Dialog().textviewer(f"{channel} – {title}", f"{description}\n\n{times}")

		elif sel == "Add channel to Favorites":
			chan_id = listitem.getProperty("channel_id")
			chan_name = listitem.getProperty("channel")
			logo = listitem.getProperty("thumb")  # optional
			if add_favorite(chan_id, chan_name, logo):
				xbmcgui.Dialog().notification(
					"CW Live EPG",
					f"{chan_name} added to Favorites",
					xbmcgui.NOTIFICATION_INFO,
					3000,
					sound=False
				)
			else:
				xbmcgui.Dialog().notification(
					"CW Live EPG",
					f"{chan_name} already in Favorites",
					xbmcgui.NOTIFICATION_INFO,
					3000,
					sound=False
				)

		elif sel == "View Favorites":
			# Save current genre filter
			current_genre = win.getProperty(GENRE_FILTER_PROP)
			if current_genre:
				win.setProperty("PREV_GENRE_FILTER", current_genre)

			# Clear genre filter and load favorites
			win.clearProperty(GENRE_FILTER_PROP)
			favs = list_favorites()
			fav_channels = list(favs.keys())
			epg_window.setProperty("FAVORITES_FILTER", ",".join(fav_channels))
			epg_window.setProperty("EPG_TITLE", f"CW Live - Favorites")
			log(f"[CONTEXT MENU] Applying favorites filter: {fav_channels}")

			xbmcgui.Dialog().notification(
				"CW Live EPG",
				"Genre filter cleared for Favorites view",
				xbmcgui.NOTIFICATION_INFO,
				2000,
				sound=False
			)
			epg_window.refresh_list()

		elif sel == "Exit Favorites":
			# Clear favorites filter
			epg_window.clearProperty("FAVORITES_FILTER")

			# Restore previous genre filter if exists
			prev_genre = win.getProperty("PREV_GENRE_FILTER")
			if prev_genre:
				win.setProperty(GENRE_FILTER_PROP, prev_genre)
				if addon.getSettingBool("remember_genre"):
					addon.setSetting("last_genre", prev_genre)
				win.clearProperty("PREV_GENRE_FILTER")

			# Set proper title before refresh
			epg_window.setProperty("EPG_TITLE", "CW Live EPG")
			log("[CONTEXT MENU] Exiting favorites view")

			# Refresh and update heading
			epg_window.refresh_list()

		elif sel == "Remove channel from Favorites":
			chan_id = listitem.getProperty("channel_id")
			chan_name = listitem.getProperty("channel")

			removed = remove_favorite(chan_id)  # now includes confirmation dialog
			if removed:
				xbmcgui.Dialog().notification(
					"CW Live EPG",
					f"{chan_name} removed from Favorites",
					xbmcgui.NOTIFICATION_INFO,
					3000,
					sound=False
				)

				# Refresh favorites filter
				favs = list_favorites()
				fav_channels = list(favs.keys())
				if fav_channels:
					epg_window.setProperty("FAVORITES_FILTER", ",".join(fav_channels))
				else:
					epg_window.clearProperty("FAVORITES_FILTER")  # no favorites left

				epg_window.refresh_list()  # refresh the EPG so removed channel disappears

			# Do nothing if user cancelled — no notification needed

		elif sel == "Clear All Favorites":
			dlg = xbmcgui.Dialog()
			confirm = dlg.yesno("CW Live EPG", "Are you sure you want to delete all favorites?")
			if not confirm:
				return  # user cancelled

			# --- Store current genre filter before clearing ---
			prev_genre = win.getProperty(GENRE_FILTER_PROP)
			if prev_genre:
				win.setProperty("PREV_GENRE_FILTER", prev_genre)

			# Clear favorites storage
			_save_favorites({})

			# Clear favorites filter
			epg_window.clearProperty("FAVORITES_FILTER")

			# Restore previous genre if it exists
			prev_genre = win.getProperty("PREV_GENRE_FILTER")
			if prev_genre:
				win.setProperty(GENRE_FILTER_PROP, prev_genre)
				if addon.getSettingBool("remember_genre"):
					addon.setSetting("last_genre", prev_genre)
				win.clearProperty("PREV_GENRE_FILTER")

			epg_window.setProperty("EPG_TITLE", "CW Live EPG")
			epg_window.refresh_list()

			xbmcgui.Dialog().notification(
				"CW Live EPG",
				"All favorites have been cleared",
				xbmcgui.NOTIFICATION_INFO,
				3000,
				sound=False
			)

		elif sel == "Search by Genre...":
			try:
				profile = addon.getAddonInfo("profile")
				epg_path = os.path.join(profile, "cache", "epg.json")
				os_path = xbmcvfs.translatePath(epg_path)

				if not xbmcvfs.exists(os_path):
					xbmcgui.Dialog().notification(
						"CW Live EPG",
						"EPG cache not found. Refresh EPG first.",
						xbmcgui.NOTIFICATION_ERROR,
						3000,
						sound=False
					)
					return

				with open(os_path, "r", encoding="utf-8") as fh:
					cached = json.load(fh)

				# --- Load channels safely ---
				channels = cached.get("channels") or cached.get("data", {}).get("channels", []) or []
				if not channels:
					xbmcgui.Dialog().notification(
						"CW Live EPG",
						"Invalid EPG format: no channel data.",
						xbmcgui.NOTIFICATION_ERROR,
						3000,
						sound=False
					)
					log(f"[CONTEXT MENU] Invalid EPG format keys: {list(cached.keys())}", xbmc.LOGWARNING)
					return

				# --- Build a genre map from channels ---
				genre_map = {}
				for ch in channels:
					genre_field = (ch.get("genre") or "").strip()
					if not genre_field:
						continue

					# Split multi-genre strings like "Drama, Comedy"
					for g in [g.strip() for g in genre_field.split(",") if g.strip()]:
						genre_map.setdefault(g, set()).add(ch.get("slug") or ch.get("title") or ch.get("guid"))

				genres = sorted(genre_map.keys())
				if not genres:
					xbmcgui.Dialog().notification(
						"CW Live EPG",
						"No genres available in EPG.",
						xbmcgui.NOTIFICATION_INFO,
						3000,
						sound=False
					)
					return

				genres.insert(0, "Show All Channels")

				# --- User selection ---
				selected_index = xbmcgui.Dialog().select("Select a Genre", genres)
				if selected_index == -1:
					return  # user canceled

				selected_genre = genres[selected_index]
				win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

				if selected_genre == "Show All Channels":
					win.clearProperty(GENRE_FILTER_PROP)
					epg_window.setProperty("FILTER_GENRE", "")
					#if addon.getSettingBool("remember_genre"):
					addon.setSetting("last_genre", "")
					xbmcgui.Dialog().notification(
						"CW Live EPG",
						"Genre filter cleared",
						xbmcgui.NOTIFICATION_INFO,
						2000,
						sound=False
					)
				else:
					win.setProperty(GENRE_FILTER_PROP, selected_genre.lower())
					epg_window.setProperty("FILTER_GENRE", selected_genre.lower())
					if addon.getSettingBool("remember_genre"):
						addon.setSetting("last_genre", selected_genre.lower())
					xbmcgui.Dialog().notification(
						"CW Live EPG",
						f"Genre filter set: {selected_genre}",
						xbmcgui.NOTIFICATION_INFO,
						2000,
						sound=False
					)

				log(f"[CONTEXT MENU] Genre selected: {selected_genre}", xbmc.LOGDEBUG)
				epg_window.refresh_list()

			except Exception as e:
				log(f"[CONTEXT MENU] Error loading genres: {e}", xbmc.LOGERROR)
				xbmcgui.Dialog().notification(
					"CW Live EPG",
					"Error loading genres.",
					xbmcgui.NOTIFICATION_ERROR,
					3000,
					sound=False
				)

		elif sel == "Clear Genre Filter":
			epg_window.clearProperty(GENRE_FILTER_PROP)
			#if addon.getSettingBool("remember_genre"):
			addon.setSetting("last_genre", "")
			xbmcgui.Dialog().notification(
				"CW Live EPG",
				"Genre filter cleared",
				xbmcgui.NOTIFICATION_INFO,
				2000,
				sound=False
			)
			epg_window.setProperty("FILTER_GENRE", "")
			epg_window.refresh_list()

		elif sel == "Clear EPG cache and thumbs":
			log("[CONTEXT_MENU] User selected Clear EPG Cache")
			clear_cache()
			xbmcgui.Dialog().notification(
				"CW Live EPG",
				"EPG cache and logos cleared",
				xbmcgui.NOTIFICATION_INFO,
				3000,
				sound=False
			)
			epg_window.refresh_list()

	except Exception as e:
		log(f"[CONTEXT MENU] Error in context menu: {e}", xbmc.LOGERROR)
