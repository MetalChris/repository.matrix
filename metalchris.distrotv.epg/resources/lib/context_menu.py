import xbmc
import xbmcgui
import xbmcaddon

import json, os, xbmcvfs

from resources.lib.logger import *
from resources.lib.utils_fetch import *
from resources.lib.favorites import add_favorite, has_favorites, list_favorites, fetch_favorites, remove_favorite, _save_favorites
from resources.lib.refresh_addon_settings import *

GENRE_FILTER_PROP = "distro_epg_genre_filter"
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

		if win.getProperty(GENRE_FILTER_PROP):
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
			xbmcgui.Dialog().textviewer(f"{channel} – {title}", description)

		elif sel == "Show Next program info":
			channel = listitem.getProperty("channel") or "No description available."
			title = listitem.getProperty("Label5") or "No description available."
			description = listitem.getProperty("Label4") or "No description available."
			xbmcgui.Dialog().textviewer(f"{channel} – {title}", description)

		elif sel == "Add channel to Favorites":
			chan_id = listitem.getProperty("channel_id")
			chan_name = listitem.getProperty("channel")
			logo = listitem.getProperty("thumb")  # optional
			if add_favorite(chan_id, chan_name, logo):
				xbmcgui.Dialog().notification(
					"DistroTV EPG",
					f"{chan_name} added to Favorites",
					xbmcgui.NOTIFICATION_INFO,
					3000,
					sound=False
				)
			else:
				xbmcgui.Dialog().notification(
					"DistroTV EPG",
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
			epg_window.setProperty("EPG_TITLE", f"DistroTV - Favorites")
			log(f"[CONTEXT MENU] Applying favorites filter: {fav_channels}")

			xbmcgui.Dialog().notification(
				"DistroTV EPG",
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

			epg_window.setProperty("EPG_TITLE", "DistroTV EPG")
			log("[CONTEXT MENU] Exiting favorites view")
			epg_window.refresh_list()

		elif sel == "Remove channel from Favorites":
			chan_id = listitem.getProperty("channel_id")
			chan_name = listitem.getProperty("channel")

			removed = remove_favorite(chan_id)  # now includes confirmation dialog
			if removed:
				xbmcgui.Dialog().notification(
					"DistroTV EPG",
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
			confirm = dlg.yesno("DistroTV EPG", "Are you sure you want to delete all favorites?")
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

			epg_window.setProperty("EPG_TITLE", "DistroTV EPG")
			epg_window.refresh_list()

			xbmcgui.Dialog().notification(
				"DistroTV EPG",
				"All favorites have been cleared",
				xbmcgui.NOTIFICATION_INFO,
				3000,
				sound=False
			)

		elif sel == "Search by Genre...":
			try:
				from resources.lib.utils_fetch import build_genre_map
				genre_map = build_genre_map()  # feed fetched internally

				if not genre_map:
					xbmcgui.Dialog().notification(
						"My EPG Add-on",
						"No genres available. Try refreshing EPG.",
						xbmcgui.NOTIFICATION_INFO,
						3000,
						sound=False
					)
					return

				# --- Split multiple genres into individual entries ---
				genres = set()
				for g in genre_map.values():
					if g:
						# Split on comma, strip spaces, add each individually
						for genre in str(g).split(","):
							genre = genre.strip()
							if genre:
								genres.add(genre)

				genres = sorted(list(genres))
				if not genres:
					xbmcgui.Dialog().notification(
						"My EPG Add-on",
						"No genres available in EPG.",
						xbmcgui.NOTIFICATION_INFO,
						3000,
						sound=False
					)
					return

				# Optional: add “Show All Channels” at top
				genres.insert(0, "Show All Channels")

				# --- Show dropdown ---
				selected_index = xbmcgui.Dialog().select("Select a Genre", genres)
				if selected_index == -1:
					return  # user canceled

				selected_genre = genres[selected_index]

				if selected_genre == "Show All Channels":
					win.clearProperty(GENRE_FILTER_PROP)
					if addon.getSettingBool("remember_genre"):
						addon.setSetting("last_genre", "")
					xbmcgui.Dialog().notification(
						"My EPG Add-on",
						"Genre filter cleared",
						xbmcgui.NOTIFICATION_INFO,
						2000,
						sound=False
					)
				else:
					win.setProperty(GENRE_FILTER_PROP, selected_genre.lower())
					if addon.getSettingBool("remember_genre"):
						addon.setSetting("last_genre", selected_genre.lower())
					xbmcgui.Dialog().notification(
						"My EPG Add-on",
						f"Genre filter set: {selected_genre}",
						xbmcgui.NOTIFICATION_INFO,
						2000,
						sound=False
					)

				log(f"[CONTEXT MENU] Genre selected: {selected_genre}", xbmc.LOGINFO)
				epg_window.refresh_list()

			except Exception as e:
				log(f"[CONTEXT MENU] Error loading genres: {e}", xbmc.LOGERROR)
				xbmcgui.Dialog().notification(
					"My EPG Add-on",
					"Error loading genres.",
					xbmcgui.NOTIFICATION_ERROR,
					3000,
					sound=False
				)



		elif sel == "Clear Genre Filter":
			win.clearProperty(GENRE_FILTER_PROP)
			if addon.getSettingBool("remember_genre"):
				addon.setSetting("last_genre", "")
			xbmcgui.Dialog().notification(
				"DistroTV EPG",
				"Genre filter cleared",
				xbmcgui.NOTIFICATION_INFO,
				2000,
				sound=False
			)
			epg_window.refresh_list()

		elif sel == "Clear EPG cache and thumbs":
			log("[CONTEXT_MENU] User selected Clear EPG Cache")
			clear_cache()
			xbmcgui.Dialog().notification(
				"DistroTV EPG",
				"EPG cache and logos cleared",
				xbmcgui.NOTIFICATION_INFO,
				3000,
				sound=False
			)
			epg_window.refresh_list()

	except Exception as e:
		log(f"[CONTEXT MENU] Error in context menu: {e}", xbmc.LOGERROR)
