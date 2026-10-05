import os
import shutil
import xbmcvfs

from resources.lib.logger import *


src_dir = xbmcvfs.translatePath(
	"special://profile/addon_data/metalchris.stirr.video")
dst_dir = xbmcvfs.translatePath(
	"special://profile/addon_data/metalchris.stirr.epg")

def copy_userdata_files():
	"""Copy all files from src_dir to dst_dir, creating dst_dir if needed."""
	if not os.path.isdir(dst_dir):
		os.makedirs(dst_dir, exist_ok=True)
	for fname in os.listdir(src_dir):
		src = os.path.join(src_dir, fname)
		if os.path.isfile(src):
			shutil.copy2(src, dst_dir)
			
	log(f"UserData File Migration Complete",xbmc.LOGINFO)
