import xbmc
import json
import time

from logger import *
from convert_to_local import *

def get_meta(data):
	rating = 'Unrated'
	nrating = 'Unrated'
	nseason = ''
	nepisode = ''

	schedule = data.get('features', {}).get('linearSchedule', [])

	log(f"GET_META SCHED LENGTH: {len(schedule)}", xbmc.LOGDEBUG)

	if not schedule:
		return '', ''

	now_timestamp = int(time.time())

	now = {}
	next_program = {}

	for index, program in enumerate(schedule):
		if program.get('start', 0) <= now_timestamp < program.get('end', 0):
			now = program
			next_program = schedule[index + 1] if index + 1 < len(schedule) else {}
			break

	if not now:
		now = schedule[0]

	content = now.get('content', {})
	meta = content.get('meta', {})
	mediaType = meta.get('mediaType', '')

	#log(f"GET_META mediaType: {mediaType}", xbmc.LOGDEBUG)

	ratings = content.get('parentalRatings', [])
	if ratings:
		rating = ratings[0].get('code', 'Unrated')

	if mediaType == 'episode':
		season = content.get('seasonNumber', '')
		episode = content.get('episodeNumber', '')

		onNowText = f"S{season} E{episode} • {rating}"

	else:
		onNowText = rating

	# Next program
	next_content = next_program.get('content', {})

	next_ratings = next_content.get('parentalRatings', [])
	if next_ratings:
		nrating = next_ratings[0].get('code', 'Unrated')

	if mediaType == 'episode':
		nseason = next_content.get('seasonNumber', '')
		nepisode = next_content.get('episodeNumber', '')

		if nseason and nepisode:
			onNextText = f"S{nseason} E{nepisode} • {nrating}"
		else:
			onNextText = nrating
	else:
		onNextText = nrating

	return onNowText, onNextText
	

def get_saved_epg(data):
	rating = 'Unrated'
	nrating = 'Unrated'
	nseason = ''
	nepisode = ''

	schedule = data.get('features', {}).get('linearSchedule', [])
	content = data.get('content', {})
	chan_title = data.get('content', {}).get('title')
	log(f"GET_SAVED_EPG Chan Title: {chan_title}", xbmc.LOGDEBUG)

	log(f"GET_SAVED_EPG SCHED LENGTH: {len(schedule)}", xbmc.LOGDEBUG)

	if not schedule:
		return '', ''

	now_timestamp = int(time.time())

	now = {}
	next_program = {}

	for index, program in enumerate(schedule):
		if program.get('start', 0) <= now_timestamp < program.get('end', 0):
			now = program
			next_program = schedule[index + 1] if index + 1 < len(schedule) else {}
			break

	if not now:
		now = schedule[0]

	#next_program = {}

	content = now.get('content', {})
	meta = content.get('meta', {})
	mediaType = meta.get('mediaType', '')

	show_title = content.get('series',{}).get('title')

	
	now_title = now.get('content', {}).get('title', '')
	
	if now_title and show_title.lower() not in chan_title.lower():
		now_title = f"{show_title}: {now_title}"
	
	now_start = now.get('start', 0)
	now_end = now.get('end', 0)
	remaining = time_remaining_text(now_end)

	ratings = content.get('parentalRatings', [])
	if ratings:
		rating = ratings[0].get('code', 'Unrated')

	if mediaType == 'episode':
		season = content.get('seasonNumber', '')
		episode = content.get('episodeNumber', '')

		onNowText = f" [B]{now_title}[/B]\nS{season} E{episode} • {rating}  {remaining}"

	else:
		onNowText = rating

	# Next program
	next_content = next_program.get('content', {})
	
	next_title = next_program.get('content', {}).get('title', '')
	
	if next_title and show_title.lower() not in chan_title.lower():
		next_title = f"{show_title}: {next_title}"
		
	next_start = format_unix_time_kodi(next_program.get('start', 0))
	next_end = format_unix_time_kodi(next_program.get('end', 0))

	next_ratings = next_content.get('parentalRatings', [])
	if next_ratings:
		nrating = next_ratings[0].get('code', 'Unrated')

	if mediaType == 'episode':
		nseason = next_content.get('seasonNumber', '')
		nepisode = next_content.get('episodeNumber', '')

		if nseason and nepisode:
			onNextText = f"Next: [B]{next_title}[/B]\nS{nseason} E{nepisode} • {nrating}  ({next_start} - {next_end})"
		else:
			onNextText = nrating
	else:
		onNextText = nrating

	return onNowText, onNextText
