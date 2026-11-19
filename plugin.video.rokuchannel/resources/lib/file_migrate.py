import os
import shutil
import xbmcvfs

from logger import *


src_dir = xbmcvfs.translatePath(
	"special://profile/addon_data/plugin.video.rokuchannel")
dst_dir = xbmcvfs.translatePath(
	"special://profile/addon_data/metalchris.rokuchannel.epg")
	
addon_src = xbmcvfs.translatePath(
	"special://home/addons/plugin.video.rokuchannel/resources/media")
addon_dst = xbmcvfs.translatePath(
	"special://home/addons/metalchris.rokuchannel.epg/resources/media")	

def copy_userdata_files():
	"""Copy all files from src_dir to dst_dir, creating dst_dir if needed."""
	if not os.path.isdir(dst_dir):
		os.makedirs(dst_dir, exist_ok=True)
	for fname in os.listdir(src_dir):
		src = os.path.join(src_dir, fname)
		if os.path.isfile(src):
			shutil.copy2(src, dst_dir)
			
	log(f"UserData File Migration Complete",xbmc.LOGINFO)
	

def copy_addon_files():
	"""Copy all files from src_dir to dst_dir, creating dst_dir if needed."""
	if not os.path.isdir(addon_dst):
		os.makedirs(addon_dst, exist_ok=True)
	for fname in os.listdir(addon_src):
		src = os.path.join(addon_src, fname)
		if os.path.isfile(src):
			shutil.copy2(src, addon_dst)
			
	log(f"Addon File Migration Complete",xbmc.LOGINFO)

