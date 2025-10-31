import urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, xbmcvfs, re, os
import json
import time
from time import strftime, localtime
import requests

from resources.lib.logger import *
from resources.lib.uas import *
from resources.lib.playback_hls import play_episode_hls
from resources.lib.playback_isa import play_episode_isa

#addon_handle = int(sys.argv[1])
#xbmcplugin.setContent(addon_handle, 'video')

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
addon_path_profile = xbmcvfs.translatePath(_addon.getAddonInfo('profile'))
selfAddon = xbmcaddon.Addon(id='metalchris.lgchannels.epg')
translation = selfAddon.getLocalizedString
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
settings = xbmcaddon.Addon(id="metalchris.lgchannels.epg")
apiUrl = 'https://api.lgchannels.com/api/v1.0/schedulelist'
plugin = "LG Channels EPG"
local_string = xbmcaddon.Addon(id='metalchris.lgchannels.epg').getLocalizedString
defaultimage = 'special://home/addons/metalchris.lgchannels.epg/resources/media/icon.png'
#defaultfanart = 'special://home/addons/plugin.video.localnow/resources/media/fanart.jpg'

__resource__   = xbmcvfs.translatePath( os.path.join( _addon_path, 'resources', 'lib' ))#.encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

s = requests.Session()

headers = {
    'user-agent': ua,
    'x-device-country': 'US',
    'x-device-language': 'en',
}

def ensure_content_length(
	url, *args, method='GET', session=None, max_size=2**20,  # 1Mb
	**kwargs
):
	kwargs['stream'] = True
	session = session or requests.Session()
	r = session.request(method, url, *args, **kwargs)
	if 'Content-Length' not in r.headers:
		# stream content into a temporary file so we can get the real size
		spool = tempfile.SpooledTemporaryFile(max_size)
		shutil.copyfileobj(r.raw, spool)
		r.headers['Content-Length'] = str(spool.tell())
		log('RESP: ' + str(r.headers),xbmc.LOGDEBUG)
		spool.seek(0)
		# replace the original socket with our temporary file
		r.raw._fp.close()
		r.raw._fp = spool
		log('RESP: ' + str(r.text),xbmc.LOGDEBUG)
	return r


def getTargetIds(jsonData):
	log(('Check for key'),xbmc.LOGINFO)
	data = json.loads(jsonData)
	log('JSONDATA: ' + str(data),xbmc.LOGDEBUG)
	if 'ssaiStreamUrl' not in data:
		#raise ValueError("No target in given data")
		log(('Key does not exist.'),xbmc.LOGDEBUG)
		return jsonData


def ends(endDateTime):
	NOW = time.time()
	#log('ENDS: ' + str(endDateTime),xbmc.LOGINFO)
	p='%Y-%m-%dT%H:%M:%SZ'
	epoch = int(time.mktime(time.strptime(endDateTime,p)))
	#log('EPOCH: ' + str(epoch),xbmc.LOGINFO)
	epochDif = (int((int(epoch) - int(NOW)))) - int(time.timezone) + 3600
	#log(('EPOCH_DIF: ' + str(epochDif)),xbmc.LOGINFO)
	if epochDif < 0:
		epochDif = epochDif + 7200
	remaining = str(datetime.timedelta(seconds=epochDif))
	#log(('REMAINING: ' + str(remaining)),xbmc.LOGINFO)
	return remaining


def get_api(apiUrl):
	response = s.get(apiUrl, headers = headers)
	response = ensure_content_length(apiUrl, headers=headers)
	log('RESPONSE CODE: ' + str(response.status_code),xbmc.LOGINFO)
	log('RESPONSE LENGTH: ' + str(len(response.text)),xbmc.LOGDEBUG)
	#log('RESPONSE: ' + str(response.text),xbmc.LOGINFO)
	data = json.loads(response.text)
	return(data)
