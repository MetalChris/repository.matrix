import xbmc
import requests

SESSION = requests.Session()

def pre_play_xumo(url, variant_fallback_fn=None):
    """
    Test Xumo stream URL before playback.
    If primary fails, attempt variant resolution via callback.
    """

    xbmc.log(f"[XUMO EPG] [PREPLAY] Testing primary URL: {url}", xbmc.LOGINFO)

    # -----------------------------
    # Step 1: test primary URL
    # -----------------------------
    try:
        r = SESSION.get(
            url,
            allow_redirects=True,
            timeout=5,
            stream=True,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://play.xumo.com/"
            }
        )

        status = r.status_code
        final_url = r.url
        r.close()

        xbmc.log(f"[XUMO EPG] [PREPLAY] Primary response: {status}", xbmc.LOGDEBUG)

        if status == 200:
            xbmc.log(f"[XUMO EPG] ✅ Primary playable: {final_url}", xbmc.LOGINFO)
            return final_url

    except Exception as e:
        xbmc.log(f"[XUMO EPG] ⚠️ Primary request error: {e}", xbmc.LOGWARNING)

    xbmc.log("[XUMO EPG] ❌ Primary failed, attempting variant fallback", xbmc.LOGWARNING)

    # -----------------------------
    # Step 2: variant fallback
    # -----------------------------
    if variant_fallback_fn:
        try:
            variant_url = variant_fallback_fn(url)

            if variant_url:
                xbmc.log(f"[XUMO EPG] [PREPLAY] Testing variant: {variant_url}", xbmc.LOGINFO)

                r = SESSION.get(
                    variant_url,
                    allow_redirects=True,
                    timeout=5,
                    stream=True,
                    headers={
                        "User-Agent": "Mozilla/5.0",
                        "Referer": "https://play.xumo.com/"
                    }
                )

                status = r.status_code
                final_url = r.url
                r.close()

                xbmc.log(f"[XUMO EPG] [PREPLAY] Variant response: {status}", xbmc.LOGDEBUG)

                if status == 200:
                    xbmc.log(f"[XUMO EPG] ✅ Variant playable: {final_url}", xbmc.LOGINFO)
                    return final_url

        except Exception as e:
            xbmc.log(f"[XUMO EPG] ⚠️ Variant fallback error: {e}", xbmc.LOGERROR)

    # -----------------------------
    # Step 3: fallback to original
    # -----------------------------
    xbmc.log("[XUMO EPG] ❗ Falling back to original URL (last resort)", xbmc.LOGWARNING)
    return url


import re
import xbmc

def pick_highest_variant(url):
    r = requests.get(url, allow_redirects=True, timeout=5)
    lines = r.text.splitlines()

    variants = []
    current_info = None

    for line in lines:
        line = line.strip()

        # Capture metadata line
        if line.startswith("#EXT-X-STREAM-INF"):
            current_info = line
            continue

        # Capture variant URL
        if line and ".m3u8" in line and not line.startswith("#"):
            if current_info:
                resolution = None
                bandwidth = 0

                # Extract resolution
                res_match = re.search(r"RESOLUTION=(\d+)x(\d+)", current_info)
                if res_match:
                    width = int(res_match.group(1))
                    height = int(res_match.group(2))
                    resolution = width * height

                # Extract bandwidth (fallback metric)
                bw_match = re.search(r"BANDWIDTH=(\d+)", current_info)
                if bw_match:
                    bandwidth = int(bw_match.group(1))

                variants.append({
                    "url": line,
                    "resolution": resolution or 0,
                    "bandwidth": bandwidth
                })

            current_info = None

    if not variants:
        xbmc.log("[XUMO] No variants found, returning original", xbmc.LOGWARNING)
        return url

    # Pick highest resolution, fallback to bandwidth if needed
    best = sorted(
        variants,
        key=lambda x: (x["resolution"], x["bandwidth"]),
        reverse=True
    )[0]

    xbmc.log(f"[XUMO] Selected variant: {best['url']}", xbmc.LOGINFO)

    return best["url"]
