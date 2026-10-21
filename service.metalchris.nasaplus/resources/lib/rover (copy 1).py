import xbmc
import xbmcaddon
import xbmcgui
import json

OLD_ADDON_ID = "service.metalchris.nasaplus.audio"  # Replace with actual ID

def disable_and_uninstall_old_addon():
	# Check if old add-on is installed
	try:
		old_addon = xbmcaddon.Addon(OLD_ADDON_ID)
		dialog = xbmcgui.Dialog()
		if dialog.yesno("Update Available", f"Old service '{OLD_ADDON_ID}' detected. Uninstall it?"):
			# Disable the old add-on via JSON-RPC
			xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "id": 1, "params": {"addonid": "%s", "enabled": false}}' % OLD_ADDON_ID)
			xbmc.sleep(1000)  # Wait for disable to take effect
			# Uninstall the old add-on
			xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.RemoveAddon", "id": 1, "params": {"addonid": "%s"}}' % OLD_ADDON_ID)
			xbmc.log(f"Old add-on {OLD_ADDON_ID} disabled and uninstalled.", level=xbmc.LOGINFO)
	except Exception as e:
		xbmc.log(f"Old add-on {OLD_ADDON_ID} not found or already removed: {e}", level=xbmc.LOGDEBUG)

# Call this function when your new add-on starts
if __name__ == "__main__":
	disable_and_uninstall_old_addon()
	# Proceed with your new service   
