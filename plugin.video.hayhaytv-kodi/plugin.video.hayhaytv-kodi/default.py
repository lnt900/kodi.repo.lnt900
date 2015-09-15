# -*- coding: utf-8 -*-
import urllib, urllib2, json, re, urlparse, sys, time, os, hashlib
import xbmc, xbmcgui, xbmcaddon, xbmcplugin

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

my_addon = xbmcaddon.Addon()
npp = str(my_addon.getSetting('npp'))
hi_res_thumb = my_addon.getSetting('hiresthumb') == 'true'
reload(sys);

header_web = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1'}
header_api = {'User-Agent' : 'Apache-HttpClient/UNAVAILABLE (java 1.4)',
			'Authorization': 'Basic YXBpaGF5OmFzb2tzYXBySkRMSVVSbzJ1MDF1cndqcQ==',
			'Content-Type' : 'application/x-www-form-urlencoded'}

def make_request(url, params=None, headers=None):
	if headers is None:
		headers = header_web
	try:
		if params is not None:
			#params = urllib.urlencode(params)
			req = urllib2.Request(url,params,headers)
		else:req = urllib2.Request(url,headers=headers)
		f = urllib2.urlopen(req)
		body=f.read()
		f.close()
		return body
	except:
		pass
def login():
	username = my_addon.getSetting('username')
	password = my_addon.getSetting('password')
	if len(username) < 5 or len(password) < 1:
		my_addon.setSetting("token", "none")
		xbmc.executebuiltin((u'XBMC.Notification(%s,%s,%s)'%('HayhayTV','[COLOR red]Chưa nhập email/password[/COLOR]',3000)).encode("utf-8"))
		return "fail"
	h = hashlib.md5()
	h.update(password)
	passwordhash = h.hexdigest()
	result = make_request('http://services.hayhaytv.vn/user/login', 'request={"data":[{"email":"%s","password":"%s"}]}&device=androidbox&secure_token=1.0' %(username,password), header_api)
	if "token_app" in result:
		res = json.loads(result)["data"]
		my_addon.setSetting("token", res["token_app"])
		my_addon.setSetting("user_id", res["user_id"])
		xbmc.executebuiltin((u'XBMC.Notification(%s,%s,%s)'%('HayhayTV','[COLOR green]Logged in ![/COLOR]',2000)).encode("utf-8"))
		return res["token_app"];
	else:
		#xbmcgui.Dialog().ok("hayhaytv", result)
		my_addon.setSetting("token", "none")
		my_addon.setSetting("user_id", "none")
		xbmc.executebuiltin((u'XBMC.Notification(%s,%s,%s)'%('HayhayTV','[COLOR red]Log in Failed ![/COLOR]',2000)).encode("utf-8"))
		return "fail"
def logout():
	my_addon.setSetting("token", "none")
	my_addon.setSetting("user_id", "none")
	xbmc.executebuiltin((u'XBMC.Notification(%s,%s,%s)'%('HayhayTV','[COLOR red]Logged out ![/COLOR]',2000)).encode("utf-8"))
def make_rq_string(input):
	st = "request=%s&device=androidbox&secure_token=1.0" % str(input)
	return st
def main_menu_api():
	a = {"startIndex":"0","pageCount": npp}
	b = {"tag_id":"263","startIndex":"0","pageCount": npp}
	addDir('Tìm Kiếm', {'mode':'search'}, '', '')
	addDir('Phim Lẻ', {'mode':'sub_menu_api', 'type': '1'}, '', '')
	addDir('Phim Bộ', {'mode':'sub_menu_api', 'type': '2'}, '', '')
	addDir('Phim lẻ mới', {'mode':'movies_from_api', 'cat':'hot/newest_single_movies', 'request': json.dumps(a)}, '', '')
	addDir('Phim bộ mới', {'mode':'movies_from_api', 'cat':'hot/newest_bundle_movies', 'request': json.dumps(a)}, '', '')
	addDir('Phim chiếu rạp', {'mode':'movies_from_api', 'cat':'hot/cinema_movies', 'request': json.dumps(a)}, '', '')
	addDir('Phim Full HD', {'mode':'movies_from_api', 'cat':'movie/movie_tags', 'request': json.dumps(b)}, '', '')
	addDir('Phim xem nhiều', {'mode':'movies_from_api', 'cat':'hot/hot_movies', 'request':'{"startIndex":"0","pageCount":"-1"}'}, '', '')
	addDir('Đăng xuất tài khoản', {'mode':'logout'}, '', '')

def sub_menu_api(movie_type):
	if movie_type == "1":
		c = 'category'
		d = 'category_id'
	elif movie_type == "2":
		c = 'countries'
		d = 'country_id'
	cats = json.loads(make_request('http://services.hayhaytv.vn/%s&device=androidbox&secure_token=1.0' % c, '', header_api))["data"]
	for cat in cats:
		e = {"startIndex":"0","pageCount":npp,"order_id":"1","country_id":"-1","category_id":"-1","type_film":movie_type}
		e[d] = cat['id']
		addDir(cat['name'], {'mode':'movies_from_api', 'cat':'search/filter', 'request': json.dumps(e)}, '', '')
		
def search():
	query = ''
	try:
		keyboard = xbmc.Keyboard('', '')
		keyboard.doModal()
		if (keyboard.isConfirmed()):
			query = keyboard.getText()
	except:
		pass

	if query != '':
		j = {"key": query,"startIndex":"0","pageCount": npp}
		movies_from_api('search', json.dumps(j))

def get_movie_info(movie_id):
	j = {"movie_id": str(movie_id)}
	result = json.loads(make_request('http://services.hayhaytv.vn/movie/movie_detail', make_rq_string(json.dumps(j)), header_api))
	return result['data']

def movies_from_api(mcat,mrequest):
	request = make_rq_string(mrequest)
	rjson = json.loads(mrequest)
	result = make_request('http://services.hayhaytv.vn/%s' % mcat, request, header_api)
	#xbmcgui.Dialog().ok("hayhaytv", result)
	res = json.loads(result)
	movies = res['data']
	try:total = int(res['total'])
	except:total = False
	
	for movie in movies:
		fanart = movie['banner_image']
		thumbnail = movie['image']
		if hi_res_thumb:thumbnail = thumbnail.replace('/crop/','/')
		name = movie['name'] + ' - ' + movie['extension']
		extinfo = {"year" : movie['year'], "rating" : movie['imdb'], "genre" : movie['category']}
		ismovie = True
		try:
			if movie['last_episode'] != '' or '- season ' in movie['name'].lower():ismovie = False
		except:ismovie = True
		if ismovie: 
			addMovie(name, {'mode':'play', 'movie_id' : movie['id'], 'ep' : '1', 'subtitle':'none'}, thumbnail, movie['intro_text'], fanart, extinfo)
		else:
			addDir(name, {'mode':'movie_detail', 'movie_id' : movie['id']}, thumbnail, movie['intro_text'], fanart, extinfo)
	if total and rjson['startIndex']:
		nextstartindex = int(rjson['startIndex'])+int(npp)
		if nextstartindex < total:
			rjson['startIndex'] = nextstartindex
			addDir('Trang Sau', {'mode':'movies_from_api','cat': mcat, 'request': json.dumps(rjson)}, '', '')
def movie_detail(movie_id):
	movie_info = get_movie_info(movie_id)
	ismovie = False
	try:
		if movie_info['list_episode']:ismovie = False
	except:ismovie = True
	thumbnail = movie_info['image']
	if hi_res_thumb:thumbnail = thumbnail.replace('/crop/','/')
	pd = 'donthave'
	if ismovie:
		# single ep
		try:
			if movie_info['vn_subtitle'] != '':pd = str(movie_info['vn_subtitle'])
		except: pd = 'donthave'
		addMovie('%s - %s' % (movie_info['name'], movie_info['extension']), {'mode':'play', 'movie_id' : movie_info['id'], 'ep' : '2', 'subtitle': pd}, thumbnail, movie_info['intro_text'], movie_info['banner_image'])
	else:
		for eps_info in movie_info['list_episode']:
			try:
				if eps_info['vn_subtitle'] != '':pd = str(eps_info['vn_subtitle'])
			except: pd = 'donthave'
			addMovie(u'[COLOR green][B]%s.[/B][/COLOR] %s - %s' % (eps_info['name'], movie_info['name'], movie_info['extension']), {'mode':'play', 'movie_id' : eps_info['id'], 'ep' : '2', 'subtitle': pd}, thumbnail, movie_info['intro_text'], movie_info['banner_image'])

def play(movie_id, ep = 1,subtitle = False):
	token = my_addon.getSetting('token')
	if token == 'none': token = login()
	if token == 'fail': return
	user_id = my_addon.getSetting('user_id')
	if int(ep) == 2:c = 'getlink/movie_episode'
	else:c = 'getlink/movie'
	j1 = {"user_id":user_id,"token":token}
	check = json.loads(make_request('http://services.hayhaytv.vn/user/check_valid_token' , make_rq_string(json.dumps(j1)), header_api))['data']
	if int(check['user_status']) == 0: token = login()
	j = {"show_id": movie_id, "movie_id": movie_id,"user_id": user_id,"token": token}
	movie = json.loads(make_request('http://services.hayhaytv.vn/%s' % c, make_rq_string(json.dumps(j)), header_api))['data']
	if movie:
		if subtitle == 'none':
			movie_info = get_movie_info(movie_id)
			try:
				if movie_info['vn_subtitle'] != '':subtitle = str(movie_info['vn_subtitle'])
			except: subtitle = 'donthave'

		try:links = movie['link_play']
		except:return
		linkplay = False
		for link in links:
			if '1080' in link['resolution']:
				linkplay = link['mp3u8_link']
				break
			elif '720' in link['resolution']: linkplay = link['mp3u8_link']
		if not linkplay:
			try:linkplay = links[0]['mp3u8_link']
			except:return
		if linkplay:
			set_resolved_url(linkplay, subtitle)

def set_resolved_url(stream_url, subtitle_url):
	h1 = '|User-Agent=' + urllib.quote_plus('HayhayTV/2.0.1 CFNetwork/711.2.23 Darwin/14.0.0')
	h2 = '&Accept=' + urllib.quote_plus('*/*')
	h3 = '&Accept-Language=' + urllib.quote_plus('en-us')
	h4 = '&Connection=' + urllib.quote_plus('Keep-Alive')
	h5 = '&Accept-Encoding=' + urllib.quote_plus('gzip, deflate')
	xbmcplugin.setResolvedUrl(addon_handle, succeeded=True, listitem=xbmcgui.ListItem(label = '', path = stream_url + h1 + h2 + h3 + h5))
	player = xbmc.Player()
	if subtitle_url != 'donthave':
		subtitlePath = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')).decode("utf-8")
		subfile = xbmc.translatePath(os.path.join(subtitlePath, "temp.sub"))
		try:
			if os.path.exists(subfile):
				os.remove(subfile)
			f = urllib2.urlopen(subtitle_url)
			with open(subfile, "wb") as code:
				code.write(f.read())
			xbmc.sleep(3000)
			xbmc.Player().setSubtitles(subfile)
		except:
			pass
	
	for _ in xrange(30):
		if player.isPlaying():
			break
		time.sleep(1)
	else:
		raise Exception('No video playing. Aborted after 30 seconds.')

def build_url(query):
	return base_url + '?' + urllib.urlencode(query)


def addDir(name,query,iconimage, plot, fanart = False, extendinfo = False):
	addItem(name, query, iconimage, plot, True, fanart, extendinfo)
	
def addMovie(name,query,iconimage, plot, fanart = False, extendinfo = False):
	addItem(name, query, iconimage, plot, False, fanart, extendinfo)
	
def addItem(name,query,iconimage, plot, isFolder, fanart = False, extendinfo = False):
	u=build_url(query)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	if fanart:liz.setProperty('Fanart_Image',fanart)
	mediainfo = {"Title": name, "Plot" : plot}
	if extendinfo:mediainfo.update(extendinfo)
	liz.setInfo( type="Video", infoLabels=mediainfo)
	if not isFolder:
		liz.setProperty('IsPlayable', 'true')
	ok=xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liz,isFolder=isFolder)
	return ok

mode = args.get('mode', None)

if mode is None:
	main_menu_api()
elif mode[0] == 'sub_menu_api':
	type = args.get('type', None)
	sub_menu_api(type[0])
elif mode[0] == 'movies_from_api':
	cat = args.get('cat', None)
	request = args.get('request', None)
	movies_from_api(cat[0], request[0])
elif mode[0] == 'movie_detail':
	movie_detail(args.get('movie_id', None)[0])
elif mode[0] == 'play':
	play(args.get('movie_id', None)[0], args.get('ep', None)[0], args.get('subtitle', None)[0])
elif mode[0] == 'search':
	search()
elif mode[0] == 'logout':
	logout()
xbmcplugin.endOfDirectory(int(sys.argv[1]))