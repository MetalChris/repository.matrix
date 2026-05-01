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
        xbmc.log(f"[DistroTV EPG] Time conversion failed for {utc_str}: {e}", xbmc.LOGERROR)
        return "N/A"


def format_duration(seconds):
	if not seconds:
		return ""

	minutes_total = seconds // 60
	hours = minutes_total // 60
	minutes = minutes_total % 60

	if hours > 0 and minutes > 0:
		return f"{hours} Hour{'s' if hours > 1 else ''} {minutes} Minutes"
	elif hours > 0:
		return f"{hours} Hour{'s' if hours > 1 else ''}"
	else:
		return f"{minutes_total} Minutes"


def iso_to_unix(ts):
	if not ts:
		return None
	try:
		struct = time.strptime(ts, "%Y-%m-%d %H:%M:%S")
		return calendar.timegm(struct)
	except Exception:
		return None
		
		
def time_remaining_text(end_ts):
	if not end_ts:
		return ""

	now = int(time.time())
	remaining = end_ts - now

	# Already ended or invalid
	if remaining < 60:
		return "Ending now"
	if remaining <= 0:
		return "Ended"

	duration_text = format_duration(remaining)

	if duration_text:
		return f"Ends in {duration_text}"

	return ""
