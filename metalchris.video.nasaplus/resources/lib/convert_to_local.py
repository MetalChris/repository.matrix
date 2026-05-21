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
        #fmt = "%b %d %Y %H:%M" if use_24hr else "%b %d %Y %I:%M %p"
        fmt = "%x %H:%M" if use_24hr else "%x %I:%M %p"
        formatted = time.strftime(fmt, local_time)

        # Remove leading zero in 12-hour mode
        if not use_24hr:
            formatted = formatted.lstrip("0")

        return formatted

    except Exception as e:
        xbmc.log(f"[EPG] ❌ Failed to format Unix timestamp '{unix_ts}' for {context_info} ({e})", xbmc.LOGWARNING)
        return ""


def fmt_time(ts):
	try:
		return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
	except:
		return "N/A"
		
		
def fmt_ttl(seconds):
    if seconds < 3600:
        return f"{seconds // 60} minutes"

    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"

    days = seconds // 86400
    return f"{days} day{'s' if days != 1 else ''}"


def parse_duration(duration_str):
    """
    Convert duration strings (HH:MM:SS or MM:SS) into seconds.
    Safe to reuse across add-ons.
    """
    if not duration_str:
        return 0

    parts = duration_str.strip().split(":")
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return 0

    if len(parts) == 3:
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    else:
        return 0

    return hours * 3600 + minutes * 60 + seconds
