import xbmc
import xbmcgui
import xbmcaddon

import json, os, xbmcvfs

from resources.lib.logger import *
from resources.lib.utils_fetch import *
from resources.lib.favorites import add_favorite, has_favorites, list_favorites, fetch_favorites, remove_favorite, _save_favorites
from resources.lib.refresh_addon_settings import *
from resources.lib.program_info import *

GENRE_FILTER_PROP = "tcltv_epg_genre_filter"
addon = xbmcaddon.Addon()
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
MEDIA_PATH = os.path.join(ADDON_PATH, "resources", "media")
ICON   = os.path.join(MEDIA_PATH, "icon.png")

def handle_context_menu(epg_window, listitem):
	log("[CONTEXT_MENU] handle_context_menu called")

	try:
		win = xbmcgui.Window(10025)
		in_favorites = bool(epg_window.getProperty("FAVORITES_FILTER"))

		# --- Base options ---
		options = [
			"Show Program Info",
			"Show Channel Description"
		]

		# Only show genre search if NOT in favorites
		if not in_favorites:
			options.append("Search by Category...")

		if win.getProperty(GENRE_FILTER_PROP):
			options.append("Clear Category Filter")

		# Dynamically add favorites-related options
		in_favorites = addon.getSettingBool("favorites_mode")
		if has_favorites():
			if in_favorites:
				options.append("Reload Favorites")
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
		if sel == "Show Program Info":
			channel = listitem.getProperty("channel") or "No description available."
			now_id = listitem.getProperty("now_id")
			next_id = listitem.getProperty("next_id")
			show_program_info(channel,now_id,next_id)
			#xbmcgui.Dialog().textviewer(f"{channel}", f"{now_id} – {next_id}\n\n{now_id}\n\n\n\n{next_id} – {now_id}\n\n{url}")
			return

		elif sel == "Show Channel Description":
			channel = listitem.getProperty("channel") or "No description available."
			#title = listitem.getProperty("Label5") or "No description available."
			description = listitem.getProperty("chan_desc") or "No description available."
			xbmcgui.Dialog().ok(f"{channel}", description)

		elif sel == "Add channel to Favorites":
			chan_id = listitem.getProperty("channel_id")
			chan_name = listitem.getProperty("channel")
			logo = listitem.getProperty("thumb")  # optional
			if add_favorite(chan_id, chan_name, logo):
				xbmcgui.Dialog().notification(
					"TCLTV+ EPG",
					f"{chan_name} added to Favorites",
					ICON,
					3000,
					sound=False
				)
			else:
				xbmcgui.Dialog().notification(
					"TCLTV+ EPG",
					f"{chan_name} already in Favorites",
					ICON,
					3000,
					sound=False
				)

		elif sel == "View Favorites" or sel == "Reload Favorites":
			# Save current genre filter
			current_genre = win.getProperty(GENRE_FILTER_PROP)
			if current_genre:
				win.setProperty("PREV_GENRE_FILTER", current_genre)

			# Clear Category Filter and load favorites
			addon.setSettingBool("favorites_mode", True)
			win.clearProperty(GENRE_FILTER_PROP)
			favs = list_favorites()
			fav_channels = list(favs.keys())
			epg_window.setProperty("FAVORITES_FILTER", ",".join(fav_channels))
			epg_window.setProperty("EPG_TITLE", f"TCLTV+ - Favorites")
			log(f"[CONTEXT MENU] Applying favorites filter: {fav_channels}")

			xbmcgui.Dialog().notification(
				"TCLTV+ EPG",
				"Genre filter cleared for Favorites view",
				ICON,
				2000,
				sound=False
			)
			epg_window.refresh_list()

		elif sel == "Exit Favorites":
			# Clear favorites filter
			addon.setSettingBool("favorites_mode", False)
			epg_window.clearProperty("FAVORITES_FILTER")

			# Restore previous genre filter if exists
			prev_genre = win.getProperty("PREV_GENRE_FILTER")
			if prev_genre:
				win.setProperty(GENRE_FILTER_PROP, prev_genre)
				if addon.getSettingBool("remember_genre"):
					addon.setSetting("last_genre", prev_genre)
				win.clearProperty("PREV_GENRE_FILTER")

			epg_window.setProperty("EPG_TITLE", "TCLTV+ EPG")
			log("[CONTEXT MENU] Exiting favorites view")
			epg_window.refresh_list()

		elif sel == "Remove channel from Favorites":
			chan_id = listitem.getProperty("channel_id")
			chan_name = listitem.getProperty("channel")

			removed = remove_favorite(chan_id)  # now includes confirmation dialog
			if removed:
				xbmcgui.Dialog().notification(
					"TCLTV+ EPG",
					f"{chan_name} removed from Favorites",
					ICON,
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
			confirm = dlg.yesno("TCLTV+ EPG", "Are you sure you want to delete all favorites?")
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

			epg_window.setProperty("EPG_TITLE", "TCLTV+ EPG")
			epg_window.refresh_list()

			xbmcgui.Dialog().notification(
				"TCLTV+ EPG",
				"All favorites have been cleared",
				ICON,
				3000,
				sound=False
			)

		elif sel == "Search by Category...":
			try:
				category_map = build_category_map()
				if not category_map:
					xbmcgui.Dialog().notification(
						"TCLTV+ EPG",
						"No genres found in EPG.",
						ICON,
						3000,
						sound=False
					)
					return

				genres = sorted(list(category_map.keys()))
				genres.insert(0, "Show All Channels")

				selected_index = xbmcgui.Dialog().select("Select a Genre", genres)
				if selected_index == -1:
					return  # user canceled

				selected_genre = genres[selected_index]

				if selected_genre == "Show All Channels":
					win.clearProperty(GENRE_FILTER_PROP)
					if addon.getSettingBool("remember_genre"):
						addon.setSetting("last_genre", "")
					xbmcgui.Dialog().notification(
						"TCLTV+ EPG",
						"Genre filter cleared",
						ICON,
						2000,
						sound=False
					)
				else:
					# Optionally, get all channel numbers for this genre:
					channels_for_genre = category_map.get(selected_genre, [])
					win.setProperty(GENRE_FILTER_PROP, selected_genre.lower())
					if addon.getSettingBool("remember_genre"):
						addon.setSetting("last_genre", selected_genre.lower())
					xbmcgui.Dialog().notification(
						"TCLTV+ EPG",
						f"Genre filter set: {selected_genre}",
						ICON,
						2000,
						sound=False
					)

				log(f"[CONTEXT MENU] Genre selected: {selected_genre}", xbmc.LOGINFO)
				epg_window.refresh_list()

			except Exception as e:
				log(f"[CONTEXT MENU] Error loading genres: {e}", xbmc.LOGERROR)
				xbmcgui.Dialog().notification(
					"TCLTV+ EPG",
					"Error loading genres.",
					ICON,
					3000,
					sound=False
		)



		elif sel == "Clear Category Filter":
			win.clearProperty(GENRE_FILTER_PROP)
			if addon.getSettingBool("remember_genre"):
				addon.setSetting("last_genre", "")
			xbmcgui.Dialog().notification(
				"TCLTV+ EPG",
				"Genre filter cleared",
				ICON,
				2000,
				sound=False
			)
			epg_window.refresh_list()

		elif sel == "Clear EPG cache and thumbs":
			log("[CONTEXT_MENU] User selected Clear EPG Cache")
			clear_cache()
			xbmcgui.Dialog().notification(
				"TCLTV+ EPG",
				"EPG cache and logos cleared",
				ICON,
				3000,
				sound=False
			)
			epg_window.refresh_list()
			
		xbmc.log("[STATE] context window id = %s" % id(epg_window), xbmc.LOGINFO)

	except Exception as e:
		log(f"[CONTEXT MENU] Error in context menu: {e}", xbmc.LOGERROR)
