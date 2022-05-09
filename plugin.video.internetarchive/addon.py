#!/usr/bin/python
#
#
# Constructed by MetalChris
# Released under GPL(v2) or Later

# 11.25.2021

from six.moves import urllib_parse, urllib_request, urllib_error, http_client
from kodi_six import xbmc, xbmcplugin, xbmcaddon, xbmcgui, xbmcvfs
import re
import os
import random
import sys
from bs4 import BeautifulSoup
import json
import requests
import socket
if sys.version_info >= (3, 4, 0):
    import html
    _html_parser = html
    PY2 = False
    translatePath = xbmcvfs.translatePath
else:
    from six.moves import html_parser
    _html_parser = html_parser.HTMLParser()
    PY2 = True
    translatePath = xbmc.translatePath


settings = xbmcaddon.Addon(id="plugin.video.internetarchive")
artbase = 'special://home/addons/plugin.video.internetarchive/resources/media/'
selfAddon = xbmcaddon.Addon(id='plugin.video.internetarchive')
_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
translation = selfAddon.getLocalizedString
local_string = xbmcaddon.Addon(id='plugin.video.internetarchive').getLocalizedString
dsort = settings.getSetting(id="dsort")
ssort = settings.getSetting(id="ssort")
download = settings.getSetting(id="download")
usexbmc = selfAddon.getSetting('watchinxbmc')
settings = xbmcaddon.Addon(id="plugin.video.internetarchive")
addon = xbmcaddon.Addon(id="plugin.video.internetarchive")
addonname = addon.getAddonInfo('name')
baseurl = 'https://archive.org/'
movieurl = 'https://archive.org/details/movies'
__resource__ = translatePath(os.path.join(_addon_path, 'resources', 'lib'))  # .encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

from uas import *

log_notice = settings.getSetting(id="log_notice")
if log_notice != 'false':
    log_level = xbmc.LOGNOTICE if PY2 else xbmc.LOGINFO
else:
    log_level = xbmc.LOGDEBUG
xbmc.log('LOG_NOTICE: ' + str(log_notice), level=log_level)
xbmc.log('DSORT: ' + str(dsort), level=log_level)

plugin = "Internet Archive [Video]"

defaultimage = 'special://home/addons/plugin.video.internetarchive/resources/media/icon.png'
defaultfanart = 'special://home/addons/plugin.video.internetarchive/resources/media/fanart.jpg'
defaulticon = 'special://home/addons/plugin.video.internetarchive/resources/media/icon.png'

addon_handle = int(sys.argv[1])
# int(sys.argv[1])
confluence_views = [551, 500, 501, 502, 503, 504, 508, 515]
# xbmc.executebuiltin("Container.SetViewMode("+str(confluence_views[4])+")")

# ##### Sort Stuff #####
# https://archive.org/details/Film_Noir?sort=-addeddate&page=2
# ?sort=-addeddate 1
# ?sort=titleSorter 2

if dsort == '0':
    sort_value = '?sort=-week'
if dsort == '1':
    sort_value = '?sort=-addeddate'
if dsort == '2':
    sort_value = '?sort=titleSorter'


# 60
def ia_categories(url):
    try:
        # data = urllib_request.urlopen(movieurl).read()
        data = get_html(url)
    except urllib_error.HTTPError as e:
        xbmc.log('Error Type= ' + str(type(e)), level=log_level)  # not catch
        xbmc.log('Error Args= ' + str(e.args), level=log_level)
        line1 = 'The addon ' + str(e.args).partition("'")[-1].rpartition("'")[0] + '.'
        # dialog = xbmcgui.Dialog()
        xbmcgui.Dialog().ok(addonname, line1 + ' Please Try Again')
        return
    except urllib_error.URLError as e:
        xbmc.log('Error Type= ' + str(type(e)), level=log_level)
        xbmc.log('Error Args= ' + str(e.args), level=log_level)
        line1 = 'The addon ' + str(e.args).partition("'")[-1].rpartition("'")[0] + '.'
        # dialog = xbmcgui.Dialog()
        xbmcgui.Dialog().ok(addonname, line1 + ' Please Try Again')
        return
    add_directory2('*Search', baseurl, 65, defaultfanart, defaulticon, plot='')
    soup = BeautifulSoup(data, 'html.parser')
    for item in soup.find_all('div', {'class': 'collection-title C C2'}):
        mode = 62
        for link in item.find_all('a'):
            l = link.get('href')  # noqa
            # xbmc.log('LINK: ' + str(link),level=log_level)
            title = link.get('title')
            # title = re.sub(r"[\n\t\s]*", "", title)
            # xbmc.log('Title= ' + str(title),level=log_level)
            if title == 'TV NSA Clip Library':
                mode = 64
                url = l + '&page=1'
            if title == 'Occupy Wall Street':
                url = l + '&page=1'
            else:
                url = l
            if len(url) < 5:
                continue
            if str(url)[0] == '/':
                url = 'https://archive.org' + url
            if title not in link:
                title = link.text
                if len(title) < 1:
                    continue
                link = str(link)
                # title = re.compile('>(.+?)</a>').findall(link)[0]
                # xbmc.log('TITLE: ' + str(title),level=log_level)
                if 'img' in title:
                    continue
                if '</span> ' in title:
                    title = re.compile('</span> (.+?)</').findall(link)[0]
                if 'Understanding' in title:
                    add_directory2(title, 'https://archive.org/details/911', 70, artbase + 'fanart.jpg', artbase + 'icon.png', plot='')
                    continue
                if ('All Video' in title) or ('Just' in title):
                    # Find a better way #
                    title = (title.split(" ", 1))[-1]
                    #
                    mode = 61
                if title == 'TV News':
                    mode = 62
                    url = 'https://archive.org/details/tvnews'
                elif 'Collections' in title:
                    mode = 61

            # ##### Add the sort method here #####

            url = url + sort_value + '&page=1'  # +default+
            title = title.strip()
            xbmc.log('TITLE: {0}  - MODE: {1}'.format(title, mode), level=log_level)
            # xbmc.log('IA URL= ' + str(url), level=log_level)
            add_directory2(title, url, mode, artbase + 'fanart.jpg', artbase + 'icon.png', plot='')
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    # xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

    r = re.search(r'<a\s*href="([^"]+)[^.]+class="page-next"', data)
    if r:
        url = baseurl[:-1] + r.group(1)
        xbmc.log('IA Next Page URL= ' + str(url), level=log_level)
        add_directory2('*Next Page', url, 60, defaultfanart, defaulticon, plot='')

    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# >>> striphtml('<a href="foo.com" class="bar">I Want This <b>text!</b></a>')
# 'I Want This text!'
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


# 61
def ia_sub_cat(url):
    url = url.split("?")[0]
    # xbmc.log('ia sub cat url= ' + str(url),level=log_level)
    data = urllib_request.urlopen(url).read()
    soup = BeautifulSoup(data, 'html.parser')
    for item in soup.find_all(attrs={'class': 'collection-title'}):
        for link in item.find_all('a'):
            l = link.get('href')  # noqa
            url = 'http://archive.org' + l + '&page=1'  # '?&sort='+default+
            if len(url) < 25:
                continue
            link = str(link)
            title = re.sub(r'\s+', ' ', link)
            title = re.compile('<div>(.+)</div>').findall(title)[0]
            title = title.replace('&amp;', '&')
            if 'Television Archive' in title:
                mode = 61
            if 'Movies' in title:
                mode = 61
            if 'Feature' in title:
                mode = 61
            else:
                mode = 62

            add_directory2(title, url, mode, artbase + 'fanart.jpg', artbase + 'icon.png', plot='')
    # xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# 62
def ia_sub2_video(url):
    page = (url)[-1]
    # page = re.search(r'(\d+)\D+$', url).group(1)
    xbmc.log('PAGE: ' + str(page), level=log_level)
    thisurl = url.split("?")[0]
    xbmc.log('thisurl= ' + str(thisurl), level=log_level)
    req = urllib_request.Request(url)
    try:
        data = urllib_request.urlopen(req, timeout=10)
    except urllib_error.HTTPError as e:
        xbmc.log('Error Type= ' + str(type(e)), level=log_level)  # not catch
        xbmc.log('Error Args= ' + str(e.args), level=log_level)
        xbmc.log('Error Code0= ' + str(e.code), level=log_level)
        line1 = str(e.code)  # .partition("'")[-1].rpartition("'")[0]
        # dialog = xbmcgui.Dialog()
        xbmcgui.Dialog().ok(addonname, line1 + ' Please Try Again')
        return
    except urllib_error.URLError as e:
        xbmc.log('Error Type= ' + str(type(e)), level=log_level)
        xbmc.log('Error Args= ' + str(e.args), level=log_level)
        line1 = str(e.args)  # .partition("'")[-1].rpartition("'")[0]
        # dialog = xbmcgui.Dialog()
        xbmcgui.Dialog().ok(addonname, line1 + ' Please Try Again')
        return
    # hidden = BeautifulSoup(data,'html.parser').find_all('div', 'details-ia')
    # xbmc.log('HIDDEN: ' + str(hidden)),level=log_level)
    # xbmc.log('HIDDEN: ' + str(len(hidden))),level=log_level)
    try:
        soup = BeautifulSoup(data, 'html.parser')
    except Exception as e:
        xbmc.log('Error Type= ' + str(type(e)), level=log_level)  # not catch
        xbmc.log('Error Args= ' + str(e.args), level=log_level)
        line1 = 'Time Out'  # str(e.args).partition("'")[-1].rpartition("'")[0]
        # dialog = xbmcgui.Dialog()
        xbmcgui.Dialog().ok(addonname, line1 + ' Please Try Again')
        return
    # if soup.find('div',{'class':'details-ia'}):
        # xbmc.log('MATCH'),level=log_level)
    for item in soup.find_all(attrs={"class": "item-ia"}):  # ('div',{'class':'item-ttl'}):
        if item.find('div', {'class': 'item-ttl'}):
            # xbmc.log('MATCH'),level=log_level)
            # for item in items.find('div',{'class':'C234'})[0]:
            for link in item.find_all('a'):
                purl = 'https://archive.org' + link.get('href')
                title = link.get('title')
                if title is None:
                    continue
                title = title.encode('utf-8') if PY2 else title
                image = 'https://archive.org' + link.find('img')['source']
                # plot = plots.find('div',{'class':'C234'})
            try:
                add_directory3(title, purl, 67, defaultfanart, image, plot='')
            except KeyError:
                continue
    page = int(page) + 1
    # thisurl = thisurl.rpartition('&')[0]
    url = thisurl + sort_value + '&page=' + str(page)  # '?&sort='+default+'&page=' + str(page)
    xbmc.log('IA Next Page URL= ' + str(url), level=log_level)
    add_directory2('Next Page', url, 62, artbase + 'fanart.jpg', artbase + 'icon.png', plot='')
    # xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# 67
def get_links(name, url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser').find_all(attrs={"class": "js-play8-playlist"})
    xbmc.log('SOUP: ' + str(len(soup)), level=log_level)
    if len(soup) < 1:
        pass
    else:
        jsob = re.compile("value='(.+?)'").findall(str(soup))[0]
        xbmc.log('JSOB: ' + str(len(jsob)), level=log_level)
        data = json.loads(jsob)
        total = len(data)
        xbmc.log('JSOB LEN: ' + str((total)), level=log_level)
        if total > 1:
            get_files(total, data)
            sys.exit()
        elif total == 1:
            jd = json.loads(get_html(url.replace('/details/', '/metadata/')))
            sources = [i for i in jd.get('files') if 'height' in i.keys() and '.jpg' not in i.get('name')]
            if len(sources) > 1:
                sources.sort(key=lambda item: (int(item.get('height')), item.get('source'), int(item.get('size'))), reverse=True)
                srcs = ['{0} ({1} {2}p) {3}'.format(
                    i.get('name').split('.')[-1],
                    i.get('source'),
                    i.get('height'),
                    get_printable_size(int(i.get('size')))
                ) for i in sources]
                ret = xbmcgui.Dialog().select('Choose Source', srcs)
                if ret == -1:
                    return False
            else:
                ret = 0
            surl = 'https://{0}{1}/{2}'.format(
                random.choice(jd.get('workable_servers')),
                jd.get('dir'),
                urllib_parse.quote(sources[ret].get('name').encode('utf-8') if PY2 else sources[ret].get('name'))
            )
            play(name, surl)
    match = re.compile('<meta property="og:video" content="(.+?)"').findall(html)
    xbmc.log('MATCH: ' + str(match), level=log_level)
    if str(match) == '[]':
        xbmc.log('NOTHING TO PLAY', level=log_level)
        xbmcgui.Dialog().notification('IA [Video]', 'No Playable File on Archive.org', xbmcgui.NOTIFICATION_INFO, 5000)
        sys.exit()
    plot = str(re.compile('<meta property="og:description" content="(.+?)"').findall(html))[2:-2]
    plot = plot.replace('\\xc2\\xa0', ' ').replace('\\xe2\\x80\\x99', '\'').replace('\\xe2\\x80\\x98', '')
    # image = str(re.compile('<meta property="og:image" content="(.+?)"/>').findall(html))[2:-2]
    # infoLabels = {'title':name, 'plot':plot}
    clipstream = re.compile('TV.clipstream_clips  = (.+?);').findall(html)
    xbmc.log('CLIPSTREAM: ' + str(len(clipstream)), level=log_level)
    if str(clipstream) == '[]':
        url = str(match)[2:-2]
        play(name, url)
    else:
        xbmc.log('CLIPSTREAM: ' + str(len(clipstream)), level=log_level)
        xbmc.log('URL: ' + str(url), level=log_level)
        ia_clipstream(url)


def get_printable_size(byte_size):
    BASE_SIZE = 1024.00
    MEASURE = ["B", "KB", "MB", "GB", "TB", "PB"]

    def _fix_size(size, size_index):
        if not size:
            return "0"
        elif size_index == 0:
            return str(size)
        else:
            return "{:.2f}".format(size)

    current_size = byte_size
    size_index = 0

    while current_size >= BASE_SIZE and len(MEASURE) != size_index:
        current_size = current_size / BASE_SIZE
        size_index = size_index + 1

    size = _fix_size(current_size, size_index)
    measure = MEASURE[size_index]
    return size + measure


def get_files(total, data):
    # for i in range(total):
    for i in data:
        title = i.get('title').replace("\u0027", "'")
        if i.get('image'):
            image = 'https://archive.org' + i.get('image')
        else:
            image = defaultimage
        url = 'https://archive.org' + i['sources'][0]['file']
        xbmc.log('STREAM: {0}, URL: {1}'.format(title, url), level=log_level)
        add_directory3(title, url, 999, defaultfanart, image, plot='')
    xbmcplugin.endOfDirectory(addon_handle)


# 63
def ia_clipstream(url):
    xbmc.log('CLIPSTREAM URL:' + str(url), level=log_level)
    html = get_html(url)
    clipstream = re.compile('TV.clipstream_clips  = (.+?);').findall(html)
    xbmc.log('CLIPSTREAM: ' + str(len(clipstream)), level=log_level)
    data = str(clipstream)[3:-3]
    data = data.replace('"', '')
    data = data.split(',')
    xbmc.log('DATA: ' + str(len(data)), level=log_level)
    for item in data:
        title = item
        url = (item.split('\\?'))[0]
        add_directory3(title, url, 999, defaultfanart, defaultimage, plot='')
    xbmcplugin.endOfDirectory(addon_handle)


# 80
def downloader(url):
    xbmc.log('DOWNLOAD', level=log_level)
    path = addon.getSetting('download')
    if path == "":
        xbmc.executebuiltin("XBMC.Notification(%s,%s,10000,%s)"
                            % (translation(30000), translation(30010), defaulticon))
        addon.openSettings()
        path = addon.getSetting('download')
    if path == "":
        return
    html = get_html(url)
    xbmc.log('Download URL: ' + str(url), level=log_level)
    match = re.compile('<meta property="og:video" content="(.+?)">').findall(str(html))
    xbmc.log('MATCH: ' + str(match), level=log_level)
    xbmc.log('MATCH[0]: ' + str(match[0]), level=log_level)
    # url = resolve_http_redirect(match[0])
    url = match[0].replace(' ', '%20')
    xbmc.log('FINAL URL: ' + str(url), level=log_level)
    file_name = url.split('/')[-1].replace('%20', ' ')
    dlsn = settings.getSetting(id="status")
    bsize = settings.getSetting(id="bsize")
    # xbmc.log('bfr Size= ' + str(bsize),level=log_level)
    ret = xbmcgui.Dialog().yesno("Internet Archive [Video]", 'Download Selected File? ' + str(file_name))
    if ret is False:
        return ia_sub2_video
    else:
        xbmcgui.Dialog().notification('IA [Video]', 'Getting Download URL.', xbmcgui.NOTIFICATION_INFO, 5000, False)
        response = urllib_request.urlopen(url)
        headers = response.getheader('Content-Length')
        xbmc.log('HEADERS: ' + str(headers), level=log_level)
        file_size = float(response.getheader('Content-Length'))
        xbmc.log('FILE_SIZE: ' + str(file_size), level=log_level)
        xbmcgui.Dialog().notification('IA [Video]', 'Download Started.', xbmcgui.NOTIFICATION_INFO, 3000, False)
        xbmc.log('Download Started', level=log_level)
    xbmc.log('URL: ' + str(url), level=log_level)
    xbmc.log('Filename: ' + str(file_name), level=log_level)
    xbmc.log('Download Location: ' + str(download), level=log_level)
    file_size = float(response.headers['Content-Length'])
    xbmc.log('FILE_SIZE: ' + str(file_size), level=log_level)
    with open(path + file_name, 'wb') as f:
        # response = urllib_request.urlretrieve(url)
        response = requests.get(url, stream=True)
        # total = int(response.headers.get('Content-Length'))
        # total = file_size
        MB = round(float(file_size / (1024 * 1024)), 2)
        xbmc.log('TOTAL: ' + str(MB), level=log_level)
        if file_size is None:
            f.write(response.content)
        else:
            downloaded = 0
            file_size = int(file_size)
            for data in response.iter_content(chunk_size=max(int(file_size / 1000), 1024 * 1024)):
                downloaded += len(data)
                f.write(data)
                done = int(100 * downloaded / file_size)
                # xbmc.log('DONE: ' + str(done), level=log_level)
                if dlsn != 'false':
                    xbmcgui.Dialog().notification('IA [Video] Download in Progress', str(done) + '% of ' + str(MB) + ' MB', xbmcgui.NOTIFICATION_INFO, 10000, False)
                    # xbmcgui.Dialog().notification('IA [Video] Download in Progress', str(done) + '% of ' + str(float(total/1000) / 1024*1024) + ' MB', xbmcgui.NOTIFICATION_INFO, 10000, False)
                else:
                    break
    xbmcgui.Dialog().notification('IA [Video]', 'Download Completed.', xbmcgui.NOTIFICATION_INFO, 5000, False)
    xbmc.log('Download Completed', level=log_level)


def sanitize(data):
    output = ''
    for i in data:
        for current in i:
            if ((current >= '\x20') and (current <= '\xD7FF')) or ((current >= '\xE000') and (current <= '\xFFFD')) or ((current >= '\x10000') and (current <= '\x10FFFF')):
                output = output + current
    return output


# 73
def ia_911_streams(url):
    html = get_html(url)
    images = re.compile('src="(.+?)"/>').findall(html)
    i = 0
    for image in images:
        if i % 2 == 0:
            seconds = ':00'
        else:
            seconds = ':30'
        urlkey = image.rsplit('/', 1)[-1].rpartition("_")[0]
        network = str(urlkey[:3])
        start = str(image.rpartition("_")[-1])[2:-4]
        end = str(int(start) + 30)
        url = 'https://ia802203.us.archive.org/28/items/' + urlkey + '/' + urlkey + '.mp4?start=' + start + '&end=' + end + '&ignore=x.mp4'
        image = 'https:' + str(image)
        title = network + ' - ' + re.compile('title="(.+?)"').findall(html)[i].replace('am', seconds + 'am').replace('pm', seconds + 'pm')
        i = i + 1
        li = xbmcgui.ListItem(title)
        li.setArt({
            'thumb': image,
            'icon': image,
            'fanart': artbase + 'fanart.jpg'
        })
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, totalItems=15)
    # xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# 70
def ia_u911(url):
    html = get_html(url)
    days = re.compile('<span class="day">(.+?)</span><br />\\n    <a href="(.+?)">(.+?)</a>').findall(html)
    for day, url, date in days[1:]:
        title = day + ', ' + date
        url = 'https://archive.org' + str(url)
        add_directory2(title, url, 71, artbase + 'fanart.jpg', artbase + 'icon.png', plot='')
    u911 = re.compile('<td class="c1">(.+?)</tr>').findall(html)
    i = 0
    for title in u911:
        title = striphtml(title)
        title = "[" + "m ] ".join(title.split("m", 1))
        url = re.compile('"file":"(.+?)"').findall(html)[i]
        url = 'https://archive.org' + url.replace('\\', '')
        i = i + 1
        li = xbmcgui.ListItem(title)
        li.setArt({
            'thumb': artbase + 'ia.jpg',
            'icon': artbase + 'ia.jpg',
            'fanart': artbase + 'fanart.jpg'
        })
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, totalItems=15)
    # xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# 71
def ia_u911_day(url):
    html = get_html(url)
    # datecode = url.rsplit('/', 1)[-1]
    soup = BeautifulSoup(html, 'html.parser')
    nets = soup.find_all(attrs={'id': 'gridL'})
    location = re.compile('<i>(.+?)</i>').findall(str(nets))
    i = 0
    networks = re.compile('url\\((.+?)\\)').findall(html)
    for network in networks:
        title = network.partition("_")[-1].rpartition(".jpg")[0] + ' - ' + str(location[i])
        image = 'https://archive.org' + str(network)

        i = i + 1
        add_directory2(title, url, 72, artbase + 'fanart.jpg', image, plot='')
    # xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# 72
def ia_u911_day_net(name, url):
    html = get_html(url)
    datecode = url.rsplit('/', 1)[-1]
    divid = name.split('-', 1)[0].strip() + '_' + datecode
    # xbmc.log('divid= ' + str(divid),level=log_level)
    soup = BeautifulSoup(html, 'html.parser')
    for ndiv in soup.find_all(attrs={'id': divid}):
        for link in ndiv.find_all('a'):
            l = link.get('href')  # noqa
            url = 'https://archive.org' + l + '&hi1=0&raw=1'
            title = link.get('title')
            add_directory2(title, url, 73, artbase + 'fanart.jpg', artbase + 'fanart.jpg', plot='')
    # xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)


# 64
def ia_nsa(url):
    data = get_html(url)
    page = (url)[-1]
    # page = re.search(r'(\d+)\D+$', url).group(1)
    xbmc.log('PAGE: ' + str(page), level=log_level)
    match = re.compile('<video src="(.+?)"').findall(data)
    for link in match:
        url = 'https://archive.org' + link
        title = url
        li = xbmcgui.ListItem(title)
        li.setArt({
            'thumb': artbase + 'ia.jpg',
            'icon': artbase + 'ia.jpg',
            'fanart': artbase + 'fanart.jpg'
        })
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, totalItems=70)
    page = str(int(page) + 1)
    url = 'https://archive.org/details/nsa?page=' + page
    xbmc.log('IA NSA Next Page URL= ' + str(url), level=log_level)
    add_directory2('Next Page', url, 64, artbase + 'fanart.jpg', artbase + 'icon.png', plot='')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


# 65
def ia_search():
    keyb = xbmc.Keyboard('', 'Search')
    keyb.doModal()
    if (keyb.isConfirmed()):
        search = urllib_parse.quote_plus(keyb.getText())
        xbmc.log('SEARCH: ' + search, level=log_level)
        # https://archive.org/search.php?query=%28commodore%29%20AND%20mediatype%3A%28movies%29
        url = 'https://archive.org/search.php?query=' + search + '%20AND%20mediatype%3Amovies'  # + sort_value[1:] #+ '&page=1' #+ '?sort=-addeddate'
        # url = 'https://archive.org/search.php?query=' + search + '&and[]=mediatype%3A%22movies%22&page=1'
        xbmc.log('SEARCH_URL: ' + url, level=log_level)
        ia_search_video(url)
    else:
        ia_categories()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


# 66
def ia_search_video(url):
    # page = re.search(r'(\d+)\D+$', url).group(1)
    # xbmc.log('PAGE: ' + str(page),level=log_level)
    # xbmc.log('PAGE: ' + str(page),level=log_level)
    thisurl = url.split("?")[0]
    xbmc.log('THISURL: ' + str(thisurl), level=log_level)
    # try: data = urllib_request.urlopen(url).read()

    data = get_html(url)
    soup = BeautifulSoup(data, 'html.parser')
    # xbmc.log('SOUP= ' + str(soup),level=log_level)
    for item in soup.find_all(attrs={'class': 'item-ttl'}):
        # for link in item.find_all('a'):
        l = item.find('a')['href']  # noqa
        purl = 'https://archive.org' + l
        title = (item.find('a')['title'])
        if len(title) < 1:
            continue
        image = 'https://archive.org' + item.find('img')['source']
        try:
            add_directory3(title, purl, 67, defaultfanart, image, plot='')
        except KeyError:
            continue

    r = re.search(r'<a\s*href="([^"]+)[^.]+class="page-next"', data)
    if r:
        url = baseurl[:-1] + r.group(1)
        xbmc.log('IA Next Page URL= ' + str(url), level=log_level)
        add_directory2('Next Page', url, 66, artbase + 'fanart.jpg', artbase + 'icon.png', plot='')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def play(name, url):
    url = url.replace(' ', '%20')
    xbmc.log(url, level=log_level)
    listitem = xbmcgui.ListItem(name)
    xbmc.Player().play(url, listitem)
    sys.exit()
    xbmcplugin.endOfDirectory(addon_handle)


def plot_info(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    descript = soup.find('div', {'id': 'descript'})
    plot = striphtml(str(descript))
    # plot = str(re.compile('<meta property="og:description" content="(.+?)"').findall(html))[2:-2]
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Plot Info', plot)
    # xbmcgui.Dialog().ok('Plot Info', plot)


def add_directory3(name, url, mode, fanart, thumbnail, plot):
    u = sys.argv[0] + "?url=" + urllib_parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib_parse.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setInfo(type="Video", infoLabels={"Title": name,
                                          "plot": plot})
    if not fanart:
        fanart = ''
    liz.setArt({
        'thumb': thumbnail,
        'icon': "DefaultFolder.png",
        'fanart': fanart
    })
    # commands = []
    # commands.append ----- THIS WORKS! -----
    liz.addContextMenuItems([('Download File', 'RunPlugin(%s?mode=80&url=%s)' % (sys.argv[0], url)), ('Description', 'RunPlugin(%s?mode=81&url=%s)' % (sys.argv[0], url))])
    # liz.addContextMenuItems([('Plot Info', 'XBMC.RunPlugin(%s?mode=81&url=%s)' % (sys.argv[0], url))])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True, totalItems=70)
    return ok


def add_directory2(name, url, mode, fanart, thumbnail, plot):
    u = sys.argv[0] + "?url=" + urllib_parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib_parse.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setInfo(type="Video", infoLabels={"Title": name,
                                          "plot": plot})
    if not fanart:
        fanart = ''
    liz.setArt({
        'thumb': thumbnail,
        'icon': "DefaultFolder.png",
        'fanart': fanart
    })
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True, totalItems=70)
    return ok


def add_directory(name, url, mode, fanart, thumbnail, plot):
    u = sys.argv[0] + "?url=" + urllib_parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib_parse.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setInfo(type="Video", infoLabels={"Title": name,
                                          "plot": plot})
    if not fanart:
        fanart = ''
    liz.setArt({
        'thumb': thumbnail,
        'icon': "DefaultFolder.png",
        'fanart': fanart
    })
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False, totalItems=70)
    return ok


def get_html(url):
    req = urllib_request.Request(url)
    req.add_header('User-Agent', ua)
    xbmc.log('USER AGENT: ' + str(ua), level=log_level)

    try:
        response = urllib_request.urlopen(req, timeout=30)
        html = response.read()
        response.close()
    except urllib_error.HTTPError:
        response = False
        html = False
    except socket.timeout as e:
        xbmc.log('*** SOCKET TIMEOUT ***' + str(e.args), level=log_level)
        xbmcgui.Dialog().ok('Internet Archive [Video]', 'Socket Timeout: ' + str(e.args) + '\n\nCaused by slow response from Archive.org')
        sys.exit()
    except urllib_error.URLError as e:
        xbmc.log('*** CONNECTION ERROR ***', level=log_level)
        xbmcgui.Dialog().ok('Internet Archive [Video]', 'Connection Error: ' + str(e.args) + '\n\nCheck your connection')
        sys.exit()
    return html.decode('utf-8')


def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param


def resolve_http_redirect(url, depth=0):
    if depth > 10:
        raise Exception("Redirected " + depth + " times, giving up.")
    o = urllib_parse.urlparse(url, allow_fragments=True)
    conn = http_client.HTTPConnection(o.netloc)
    path = o.path
    if o.query:
        path += '?' + o.query
    conn.request("HEAD", path)
    res = conn.getresponse()
    headers = dict(res.getheaders())
    xbmc.log('HEADERS: ' + str(headers), level=log_level)
    if headers.get('Location', '') != url:
        return resolve_http_redirect(headers['Location'], depth + 1)
    else:
        return url


def unescape(s):
    p = _html_parser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()


params = get_params()
url = None
name = None
mode = None
cookie = None

try:
    url = urllib_parse.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib_parse.unquote_plus(params["name"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass

xbmc.log("Mode: " + str(mode), level=log_level)
xbmc.log("URL: " + str(url), level=log_level)
xbmc.log("Name: " + str(name), level=log_level)

if mode is None or url is None or len(url) < 1:
    xbmc.log("Generate Main Menu", level=log_level)
    ia_categories(movieurl)
elif mode == 1:
    xbmc.log("Indexing Videos", level=log_level)
    index(url)
elif mode == 4:
    xbmc.log("Play Video", level=log_level)
elif mode == 6:
    xbmc.log("Get Episodes", level=log_level)
    get_episodes(url)
elif mode == 60:
    xbmc.log("Get IA Video Categories", level=log_level)
    # ia_video(url)
    ia_categories(url)
elif mode == 61:
    xbmc.log("Get IA Video Sub Categories", level=log_level)
    ia_sub_cat(url)
elif mode == 62:
    xbmc.log("Get IA Video Sub2 Categories", level=log_level)
    ia_sub2_video(url)
elif mode == 63:
    xbmc.log("Get IA Clipstream", level=log_level)
    ia_clipstream(url)
elif mode == 64:
    xbmc.log("Get IA NSA", level=log_level)
    ia_nsa(url)
elif mode == 65:
    xbmc.log("IA Search", level=log_level)
    ia_search()
elif mode == 66:
    xbmc.log("IA Search Video", level=log_level)
    ia_search_video(url)
elif mode == 67:
    xbmc.log("IA Get Links", level=log_level)
    get_links(name, url)
elif mode == 70:
    xbmc.log("IA Understanding 9/11", level=log_level)
    ia_u911(url)
elif mode == 71:
    xbmc.log("IA 9/11 Day", level=log_level)
    ia_u911_day(url)
elif mode == 72:
    xbmc.log("IA 9/11 Day Net", level=log_level)
    ia_u911_day_net(name, url)
elif mode == 73:
    xbmc.log("IA 911 Streams", level=log_level)
    ia_911_streams(url)
elif mode == 80:
    xbmc.log("IA Download File", level=log_level)
    downloader(url)
elif mode == 81:
    xbmc.log("IA Plot Info", level=log_level)
    plot_info(url)
elif mode == 999:
    xbmc.log("IA Play URL", level=log_level)
    play(name, url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
