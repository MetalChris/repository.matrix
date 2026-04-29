import xbmc
import time
import calendar

from resources.lib.logger import *

def convert_to_local(utc_str):
	try:
		utc_tuple = time.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
		utc_epoch = calendar.timegm(utc_tuple)
		local_tuple = time.localtime(utc_epoch)

		time_format = xbmc.getRegion("time").replace(":%S", "")
		return time.strftime(time_format, local_tuple)
	except Exception as e:
		log(f"[TCLTV+ EPG] Time conversion failed for {utc_str}: {e}", xbmc.LOGERROR)
		return "N/A"


def format_epg_time(ts, context_info=""):
	if not ts:
		log(f"[EPG] ❌ format_epg_time received empty timestamp for {context_info}", xbmc.LOGWARNING)
		return ""  # safely return empty string
	try:
		# Parse UTC ISO timestamp
		t = time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
		# Convert to local time
		local_time = time.localtime(calendar.timegm(t))

		# Get user time format from Kodi settings
		time_format = xbmc.getRegion('time')  # returns something like '%H:%M' or '%I:%M %p'
		time_format = time_format.replace(":%S", "")  # remove seconds if present

		# Format according to user preference
		return time.strftime(time_format, local_time)
	except Exception as e:
		log(f"[TCLTV+ EPG] Time conversion failed for {ts}: {e}", xbmc.LOGERROR)
		return ""


def has_program_ended(end_ts):
	# Parse UTC timestamp (end time)
	t = time.strptime(end_ts, "%Y-%m-%dT%H:%M:%SZ")
	end_utc = calendar.timegm(t)  # convert to epoch seconds (UTC)

	# Get current UTC time as epoch seconds
	now_utc = calendar.timegm(time.gmtime())

	# Compare
	return now_utc > end_utc


def get_program_status(start_ts, end_ts):
	now_utc = calendar.timegm(time.gmtime())
	start_utc = calendar.timegm(time.strptime(start_ts, "%Y-%m-%dT%H:%M:%SZ"))
	end_utc = calendar.timegm(time.strptime(end_ts, "%Y-%m-%dT%H:%M:%SZ"))

	if now_utc < start_utc:
		return "upcoming"
	elif now_utc < end_utc:
		return "live"
	else:
		return "ended"


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
		struct = time.strptime(ts.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
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
