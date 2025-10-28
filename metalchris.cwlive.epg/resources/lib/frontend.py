import os
import re
import xbmc
import xbmcgui
import xbmcvfs
import xml.etree.ElementTree as ET

class EPGFrontend:
    def __init__(self, addon):
        self.addon = addon
        self.merge_path = xbmcvfs.translatePath("special://profile/addon_data/plugin.program.iptv.merge/")
        self.playlist_file = os.path.join(self.merge_path, "playlist.m3u8")
        self.epg_file = os.path.join(self.merge_path, "epg.xml")

    def run(self):
        if not os.path.exists(self.playlist_file):
            xbmcgui.Dialog().notification("Frontend EPG", "playlist.m3u8 not found!", xbmcgui.NOTIFICATION_ERROR)
            return
        if not os.path.exists(self.epg_file):
            xbmcgui.Dialog().notification("Frontend EPG", "epg.xml not found!", xbmcgui.NOTIFICATION_ERROR)
            return

        channels = self.parse_playlist()
        guide = self.parse_epg()

        list_items = []
        for ch in channels:
            title = ch.get("name")
            logo = ch.get("logo")
            slug = ch.get("url")

            now_show = guide.get(title, "No EPG data")
            li = xbmcgui.ListItem(label=f"{title}  •  {now_show}")
            if logo:
                li.setArt({'thumb': logo, 'icon': logo})
            li.setProperty("slug", slug)
            list_items.append(li)

        dialog = xbmcgui.Dialog()
        idx = dialog.select("Select Channel", list_items)
        if idx >= 0:
            slug = list_items[idx].getProperty("slug")
            self.play_channel(slug)

    def parse_playlist(self):
        """Parse IPTV Merge M3U playlist"""
        channels = []
        with open(self.playlist_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        name, logo, url = None, None, None
        for line in lines:
            if line.startswith("#EXTINF"):
                match_name = re.search(r',(.+)', line)
                match_logo = re.search(r'tvg-logo="([^"]+)"', line)
                name = match_name.group(1).strip() if match_name else "Unknown"
                logo = match_logo.group(1) if match_logo else ""
            elif line.startswith("plugin://"):
                url = line.strip()
                if name and url:
                    channels.append({"name": name, "logo": logo, "url": url})
        return channels

    def parse_epg(self):
        """Parse XMLTV EPG"""
        guide = {}
        try:
            tree = ET.parse(self.epg_file)
            root = tree.getroot()
            for prog in root.findall("programme"):
                channel = prog.get("channel")
                title = prog.find("title").text if prog.find("title") is not None else "Unknown"
                if channel not in guide:
                    guide[channel] = title
        except Exception as e:
            xbmc.log(f"[Frontend EPG] EPG parse error: {e}", xbmc.LOGERROR)
        return guide

    def play_channel(self, slug):
        xbmc.executebuiltin(f"RunPlugin({slug})")
