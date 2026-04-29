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
        log(f"[XumoPlay EPG] Time conversion failed for {utc_str}: {e}", xbmc.LOGERROR)
        return "N/A"

def format_unix_time_kodi(unix_ts, context_info=""):
    """
    Convert a Unix timestamp to local HH:MM string based on Kodi's 12/24-hour setting.
    Safe version: handles missing or invalid timestamps gracefully.

    Parameters:
    - unix_ts: int, float, or str (Unix timestamp in seconds)
    - context_info: str, optional context for logging

    Returns:
    - str: formatted time, or '' if invalid
    """
    try:
        if unix_ts is None or unix_ts == "":
            xbmc.log(f"[EPG] ⚠️ Empty Unix timestamp for {context_info}", xbmc.LOGWARNING)
            return ""

        # Ensure numeric type
        ts = float(unix_ts)

        # Convert Unix timestamp → local time struct
        local_time = time.localtime(ts)

        # Detect Kodi time format
        time_format = xbmc.getRegion('time')  # e.g., "%H:%M:%S" or "%I:%M:%S %p"
        use_24hr = "%H" in time_format

        # Format HH:MM only
        fmt = "%H:%M" if use_24hr else "%I:%M %p"
        formatted = time.strftime(fmt, local_time)

        # Remove leading zero in 12-hour mode
        if not use_24hr:
            formatted = formatted.lstrip("0")

        return formatted

    except Exception as e:
        xbmc.log(f"[EPG] ❌ Failed to format Unix timestamp '{unix_ts}' for {context_info} ({e})", xbmc.LOGWARNING)
        return ""


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
