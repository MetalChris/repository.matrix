import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup

from concurrent.futures import ThreadPoolExecutor, as_completed

from resources.lib.logger import *
from resources.lib.caching import fmt_time, fmt_ttl, compute_hash, _cache_key, _cache_ensure_loaded, _cache_flush, cache_get, cache_set, cache_set_many, cache_get_with_meta, normalize_html, CACHE_TTL_PAGES, CACHE_TTL_DESCRIPTIONS, clear_cache, notify_meta_progress, close_meta_progress

def get_url(**kwargs):
	"""Build plugin URL with query params."""
	return sys.argv[0] + '?' + urllib.parse.urlencode(kwargs)

def fetch_page(url):
	log("[TEST] fetch_page called", xbmc.LOGDEBUG)
	"""Fetch and parse HTML page with caching."""
	cache_key = _cache_key("page", url)
	
	cached_html, meta, expired = cache_get_with_meta(cache_key)

	# ✅ Fresh cache → no request
	if cached_html and not expired:
		log(f"[{ADDON_NAME}] [CACHE NOT EXPIRED]: {url}", xbmc.LOGDEBUG)
		return BeautifulSoup(cached_html, "html.parser")

	# 🔄 Expired → validate via hash
	if cached_html and expired:
		try:
			log(f"[{ADDON_NAME}] [CACHE EXPIRED]: {url}", xbmc.LOGDEBUG)
			log(f"[{ADDON_NAME}] [VALIDATING]: {url}", xbmc.LOGDEBUG)
			resp = requests.get(url, timeout=(3, 10))
			resp.raise_for_status()
			new_html = resp.text

			new_hash = hashlib.sha1(normalize_html(new_html).encode()).hexdigest()
			old_hash = meta.get('hash')

			if new_hash == old_hash:
				# ✅ unchanged → extend TTL only
				cache_set(cache_key, cached_html, CACHE_TTL_PAGES)
				log(f"[{ADDON_NAME}] Hash VALID for: {url}", xbmc.LOGDEBUG)
				return BeautifulSoup(cached_html, "html.parser")

			# 🔄 changed → update cache
			cache_set(cache_key, new_html, CACHE_TTL_PAGES)
			log(f"[{ADDON_NAME}] Hash INVALID for: {url}", xbmc.LOGDEBUG)
			return BeautifulSoup(new_html, "html.parser")

		except Exception:
			# 🚨 network fail → serve stale
			return BeautifulSoup(cached_html, "html.parser")

	# 🚀 No cache → normal fetch
	log(f"[{ADDON_NAME}] [NO CACHE FETCHING]: {url}", xbmc.LOGDEBUG)
	resp = requests.get(url, timeout=(3, 10))
	resp.raise_for_status()
	html = resp.text

	cache_set(cache_key, html, CACHE_TTL_PAGES)

	return BeautifulSoup(html, "html.parser")


def fetch_series_full_description(url, session=None):
	try:
		requester = session or requests
		resp = requester.get(url, timeout=(2, 4))
		resp.raise_for_status()

		soup = BeautifulSoup(resp.text, "html.parser")

		# Try full description first
		container = soup.select_one("div.usa-prose.banner--info-text.margin-bottom-2 p")
		if container:
			text = container.get_text(strip=True)
			if text:
				return text

		# Fallback to meta
		meta = soup.find("meta", attrs={"property": "og:description"}) \
			or soup.find("meta", attrs={"name": "description"})

		if meta:
			content = meta.attrs.get("content", "")
			if isinstance(content, str):
				return content.strip()

		return ""

	except Exception as e:
		log(f"[SERIES] Description fetch failed for '{url}': {e}")
		return ""


def fetch_series_descriptions(urls):
	"""Fetch series descriptions with cache-first and fast parallel fallback."""
	results = {}
	unique_urls = [u for u in dict.fromkeys(urls) if u]
	if not unique_urls:
		return results

	missing_urls = []
	for url in unique_urls:
		key = _cache_key("desc", url)
		cached, meta, expired = cache_get_with_meta(key)

		if cached and not expired:
			log(f"[DESC CACHE HIT] {url}", xbmc.LOGDEBUG)
			results[url] = cached
		else:
			log(
				f"[DESC CACHE MISS] {url} expired={expired} has_meta={meta is not None}",
				xbmc.LOGDEBUG
			)
			missing_urls.append(url)

	if not missing_urls:
		return results

	total_missing = len(missing_urls)
	log(f"[{ADDON_NAME}] [MISSING URLS]: {total_missing}", xbmc.LOGINFO)
	completed = 0
	update_step = max(1, total_missing // 30)
	notify_meta_progress("Series", 0, total_missing)

	session = requests.Session()
	max_workers = min(10, max(4, len(missing_urls) // 2))
	fresh_entries = {}
	try:
		with ThreadPoolExecutor(max_workers=max_workers) as executor:
			future_map = {
				executor.submit(fetch_series_full_description, url, session): url
				for url in missing_urls
			}
			for future in as_completed(future_map):
				url = future_map[future]
				try:
					description = future.result() or ""
				except Exception:
					description = ""
				results[url] = description
				fresh_entries[_cache_key("desc", url)] = description
				completed += 1
				if completed == total_missing or completed % update_step == 0:
					notify_meta_progress("Series", completed, total_missing)
	
	finally:
		session.close()
		close_meta_progress("Series")

	if fresh_entries:
		cache_set_many(fresh_entries, CACHE_TTL_DESCRIPTIONS)

	return results


def fetch_video_page_description(url, session=None):
	"""Fetch full video description, fallback to meta."""
	try:
		requester = session or requests
		resp = requester.get(url, timeout=(2, 4))
		resp.raise_for_status()

		soup = BeautifulSoup(resp.text, "html.parser")

		# --- Try full description first ---
		p = soup.select_one("div.entry-content.usa-prose p")
		if p:
			text = p.get_text(strip=True)
			if text:
				return text

		# --- Fallback to meta ---
		meta = soup.find("meta", attrs={"name": "description"}) \
			or soup.find("meta", attrs={"property": "og:description"})

		if meta:
			content = meta.attrs.get("content", "")
			if isinstance(content, str):
				return content.strip()

		return ""

	except Exception as e:
		log(f"[VIDEO] Description fetch failed for '{url}': {e}")
		return ""


def fetch_video_descriptions(urls):
	"""Fetch video descriptions with cache-first and fast parallel fallback."""
	results = {}
	unique_urls = [u for u in dict.fromkeys(urls) if u]
	if not unique_urls:
		return results

	missing_urls = []
	for url in unique_urls:
		key = _cache_key("vdesc", url)
		cached, meta, expired = cache_get_with_meta(key)

		if cached and not expired:
			log(f"[DESC CACHE HIT] {url}", xbmc.LOGDEBUG)
			results[url] = cached
		else:
			log(
				f"[DESC CACHE MISS] {url} expired={expired} has_meta={meta is not None}",
				xbmc.LOGDEBUG
			)
			missing_urls.append(url)

	if not missing_urls:
		return results

	total_missing = len(missing_urls)
	log(f"[{ADDON_NAME}] [MISSING URLS]: {total_missing}", xbmc.LOGINFO)
	completed = 0
	update_step = max(1, total_missing // 30)
	notify_meta_progress("Videos", 0, total_missing)

	session = requests.Session()
	max_workers = min(10, max(4, len(missing_urls) // 2))
	fresh_entries = {}
	try:
		with ThreadPoolExecutor(max_workers=max_workers) as executor:
			future_map = {
				executor.submit(fetch_video_page_description, url, session): url
				for url in missing_urls
			}
			for future in as_completed(future_map):
				video_url = future_map[future]
				try:
					description = future.result() or ""
				except Exception:
					description = ""
				results[video_url] = description
				fresh_entries[_cache_key("vdesc", video_url)] = description
				completed += 1
				if completed == total_missing or completed % update_step == 0:
					notify_meta_progress("Videos", completed, total_missing)
	
	finally:
		session.close()
		close_meta_progress("Videos")

	if fresh_entries:
		cache_set_many(fresh_entries, CACHE_TTL_DESCRIPTIONS)

	return results
