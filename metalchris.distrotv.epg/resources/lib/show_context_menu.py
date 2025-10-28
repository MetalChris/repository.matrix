def show_context_menu(self):
    list_control = self.getControl(9000)
    pos = list_control.getSelectedPosition()
    if pos < 0:
        return

    li = list_control.getListItem(pos)

    options = ["Show Now", "Show Next", "Search by Genre..."]
    # Only offer clear if filter is active
    if xbmcgui.Window(10025).getProperty(GENRE_FILTER_PROP):
        options.append("Clear Genre Filter")

    choice = xbmcgui.Dialog().select("Options", options)
    if choice == -1:
        return

    if options[choice] == "Show Now":
        description = li.getProperty("desc") or "No description available."
        xbmcgui.Dialog().textviewer(f"{li.getLabel()} - Now", description)

    elif options[choice] == "Show Next":
        description = li.getProperty("desc2") or "No description available."
        xbmcgui.Dialog().textviewer(f"{li.getLabel()} - Next", description)

    elif options[choice] == "Search by Genre...":
        query = xbmcgui.Dialog().input("Search genre")
        if query:
            xbmcgui.Window(10025).setProperty(GENRE_FILTER_PROP, query.lower())
        else:
            xbmcgui.Window(10025).clearProperty(GENRE_FILTER_PROP)
        xbmc.executebuiltin("Container.Refresh")

    elif options[choice] == "Clear Genre Filter":
        xbmcgui.Window(10025).clearProperty(GENRE_FILTER_PROP)
        xbmc.executebuiltin("Container.Refresh")
