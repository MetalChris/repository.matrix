import xbmc
import time
import calendar

def convert_to_local(utc_str):
    try:
        utc_tuple = time.strptime(utc_str, "%Y-%m-%d %H:%M:%S")
        utc_epoch = calendar.timegm(utc_tuple)
        local_tuple = time.localtime(utc_epoch)

        time_format = xbmc.getRegion("time").replace(":%S", "")
        return time.strftime(time_format, local_tuple)
    except Exception as e:
        xbmc.log(f"[LocalNow EPG] Time conversion failed for {utc_str}: {e}", xbmc.LOGERROR)
        return "N/A"
