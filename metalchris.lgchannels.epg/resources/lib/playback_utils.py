import xbmc
import requests

def pre_play(url):
    """
    Test the LG Channels stream URL before playback.
    Tries the full URL, truncated-at-first-& variant, and base URL,
    following redirects and using GET (not HEAD) since some servers
    return 404 to HEAD requests.
    """
    xbmc.log(f"[LG Channels EPG] [PLAYBACK_UTILS] Starting pre-play checks for: {url}", xbmc.LOGINFO)

    test_urls = [url]

    # Build truncated variants
    if '?' in url:
        base, params = url.split('?', 1)
        if '&' in params:
            first_param = params.split('&', 1)[0]
            truncated_amp = f"{base}?{first_param}"
            test_urls.append(truncated_amp)
            xbmc.log(f"[LG Channels EPG] [PLAYBACK_UTILS] Added variant (truncated at first '&'): {truncated_amp}", xbmc.LOGDEBUG)
        truncated_q = base
        test_urls.append(truncated_q)
        xbmc.log(f"[LG Channels EPG] [PLAYBACK_UTILS] Added variant (truncated at '?'): {truncated_q}", xbmc.LOGDEBUG)

    # Test each version
    for test_url in test_urls:
        try:
            xbmc.log(f"[LG Channels EPG] [PLAYBACK_UTILS] Testing URL: {test_url}", xbmc.LOGDEBUG)

            # Use GET but don't download data
            response = requests.get(test_url, allow_redirects=True, timeout=5, stream=True)
            final_url = response.url
            status = response.status_code
            response.close()

            xbmc.log(f"[LG Channels EPG] [PLAYBACK_UTILS] Response: {status} (final: {final_url})", xbmc.LOGDEBUG)

            if status in (200, 301, 302):
                xbmc.log(f"[LG Channels EPG] [PLAYBACK_UTILS] ✅ Playable URL found: {final_url}", xbmc.LOGINFO)
                return final_url

            elif status in (22, 400, 404):
                xbmc.log(f"[LG Channels EPG] [PLAYBACK_UTILS] ❌ Invalid response ({status}), trying next variant...", xbmc.LOGWARNING)
                continue

            else:
                xbmc.log(f"[LG Channels EPG] [PLAYBACK_UTILS] ⚠️ Unexpected response {status}, continuing...", xbmc.LOGWARNING)

        except requests.RequestException as e:
            xbmc.log(f"[LG Channels EPG] [PLAYBACK_UTILS] ⚠️ Exception testing {test_url}: {e}", xbmc.LOGERROR)
            continue

    xbmc.log(f"[LG Channels EPG] [PLAYBACK_UTILS] ❗ All attempts failed, falling back to original URL: {url}", xbmc.LOGWARNING)
    return url
