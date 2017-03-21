# -*- coding: utf-8 -*-
import urllib2, urllib, re, os, json, string
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import glob, time, codecs, sys, zipfile
import sqlite3
import mediaget
from crypt import *
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup , Tag, NavigableString

datapath=xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode("utf-8")
my_addon = xbmcaddon.Addon()
scanwrite = False
lastpaths = ['','','','','']
lastjson = {}

def geturl(url,param=False,ecoding_param=True,cookies=False,getcookies=False,customct=False):
	headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1'}
	if cookies:headers.update(cookies)
	try:
		if param:
			if not customct:
				ct={'Content-Type': 'application/x-www-form-urlencoded'}
				headers.update(ct)
			if ecoding_param: param = urllib.urlencode(param)
			req = urllib2.Request(url,param,headers=headers)
		else:
			req = urllib2.Request(url,headers=headers)
		f = urllib2.urlopen(req)
		if getcookies: body= str(f.info().getheader('Set-Cookie'))
		else: body=f.read()
		return body
	except:
		return False
try:server = geturl('http://pastebin.com/raw/gT6bzUfA')
except:server = 'http://movtv.gxdesign.net/'
if server == False:server = 'http://movtv.gxdesign.net/'

def regsearch(pattern,string,group=1,flags=0):
	try:s=re.search(pattern,string,flags).group(group)
	except:s=''
	return s
	
def getfile(folder,file):
	if folder == '':
		path = datapath
		file_url = '%s%s' %(server,file)
	else:
		path = os.path.join(datapath,folder)
		file_url = '%s%s/%s' %(server,folder,file)
	path = os.path.join(path,file)
	f = urllib2.urlopen(file_url)
	with open(path, "wb") as code:
		code.write(f.read())

def openfile(folder,file,read=True):
	if folder == '':fpath = datapath
	else:fpath = os.path.join(datapath,folder)
	fpath = os.path.join(fpath,file)
	try:
		if read:
			with codecs.open(fpath, 'r', encoding='utf-8') as myfile:
				f=myfile.read()
		else:f = codecs.open(fpath,'r', encoding='utf-8')
	except:
		getfile(folder,file)
		if read:
			with codecs.open(fpath, 'r', encoding='utf-8') as myfile:
				f=myfile.read()
		else:f = open(fpath,'r')
	return f

def checkupdate(path,scan,write=True):
	if scan:
		global scanwrite
		if write and scanwrite:
			paths = path.split('/')
			if paths[0] == 'tv':
				list = open(os.path.join(datapath,'files','%s.txt' %paths[1]),'r').read()
				utime = int(regsearch('^'+re.escape(paths[2])+'\|(\d+?)$',list,1,re.M))
				listupdate = ''
				try:
					listupdate = open(os.path.join(datapath,'files','stat_%s.txt' %paths[1]),'r').read() 
				except:pass
				if re.search('^'+re.escape(paths[2])+'\|',listupdate,re.M) != None:
					ltime = regsearch('^'+re.escape(paths[2])+'\|(\d+?)$',listupdate,1,re.M)
				else:ltime = '0000000000'
				if utime > int(ltime):
					if listupdate == '' or re.search('^'+re.escape(paths[2])+'\|',listupdate,re.M) == None:
						towrite = '%s%s|%s\n'%(listupdate,paths[2],str(utime))
					else:
						namestring = regsearch('^('+re.escape(paths[2])+'\|\d+?)$',listupdate,1,re.M)
						new_namestr = namestring.replace(ltime,str(utime))
						towrite = re.sub('^'+re.escape(namestring)+'$',new_namestr,listupdate,flags=re.M)
					with open(os.path.join(datapath,'files','stat_%s.txt' %paths[1]), "w") as code:code.write(towrite)
				scanwrite = False
			#if paths[0] == 'movie':
				#my_addon.setSetting('sync%s'%paths[1], str(int(time.time())))
				#scanwrite = False
		elif not write:
			paths = path.split('/')
			if paths[0] == 'tv':
				list = open(os.path.join(datapath,'files','%s.txt' %paths[1]),'r').read()
				utime = int(regsearch('^'+re.escape(paths[2])+'\|(\d+?)$',list,1,re.M))
				listupdate = ''
				try:
					listupdate = open(os.path.join(datapath,'files','stat_%s.txt' %paths[1]),'r').read() 
				except:pass
				if re.search('^'+re.escape(paths[2])+'\|',listupdate,re.M) != None:
					ltime = regsearch('^'+re.escape(paths[2])+'\|(\d+?)$',listupdate,1,re.M)
				else:ltime = '0000000000'
				if utime > int(ltime):
					scanwrite = True
					return True
				else:return False
	else:return True

def addlibpath(c,path,istv=False,tvNoUpdate=1):
	if c == None:
		db_path = xbmc.translatePath('special://database')
		db_files = glob.glob('%s/MyVideos*.db'%db_path)
		dbfile = db_files[0]
		if len(db_files) > 1:
			lastversion = 0
			for v in db_files:
				version = int(regsearch('MyVideos([\d]+?)\.db',v))
				if version > lastversion:
					lastversion = version
					dbfile = v
		conn = sqlite3.connect(dbfile)
		cs = conn.cursor()
	else:
		cs = c
	cs.execute("select idPath from path where strPath = '%s'"%path)
	f = cs.fetchall()
	if istv:
		if len(f)>0:
			data = ('tvshows','metadata.local',1,0,tvNoUpdate,path)
			cs.execute("update path set strContent=?,strScraper=?,scanRecursive=?,useFolderNames=?,noUpdate=? where strPath=?",data)
		else:
			data = (path,'tvshows','metadata.local',1,0,tvNoUpdate)
			cs.execute("insert into path(strPath,strContent,strScraper,scanRecursive,useFolderNames,noUpdate) values(?,?,?,?,?,?)",data)
	else:
		if len(f)>0:
			data = ('movies','metadata.local',1,0,path)
			cs.execute("update path set strContent=?,strScraper=?,scanRecursive=?,useFolderNames=? where strPath=?",data)
		else:
			data = (path,'movies','metadata.local',1,0)
			cs.execute("insert into path(strPath,strContent,strScraper,scanRecursive,useFolderNames) values(?,?,?,?,?)",data)
	if c == None:
		conn.commit()
		conn.close()

def echofolder(path,scan):
	paths = path.split('/')
	html = '<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 3.2 Final//EN\">\n<html> <head>\n  <title>Index of /%s</title>\n </head>\n<body>\n<h1>Index of /%s</h1>\n<pre><hr>' %(path,path)
	if paths[0] == 'movie':
		if len(paths) == 1:
			files = json.load(open(os.path.join(datapath,'files.txt'),'r'))
			for f in files['list']:
				f= f.strip()
				html += '<a href="%s/">%s/</a>\n' %(f,f)
		elif len(paths) == 2:
			movfile = os.path.join(datapath,'files','%s.txt' %paths[1])
			#if scan:
				#lastsync = 0 if my_addon.getSetting('sync%s'%paths[1]) == '' else int(my_addon.getSetting('sync%s'%paths[1]))
				#lastmod = int(os.path.getmtime(movfile))
			#if not scan or lastmod > lastsync:
			for f in open(movfile,'r'):
				filename = f.strip().split('|')
				html += '<a href="%s.mkv">%s.mkv</a>\n' %(filename[0],filename[0])
				html += '<a href="%s.nfo">%s.nfo</a>\n' %(filename[0],filename[0])
				#if scan and lastmod > lastsync:
					#global scanwrite
					#scanwrite = True
	elif paths[0] == 'tv':
		if len(paths) == 1:
			files = json.load(open(os.path.join(datapath,'files.txt'),'r'))
			for f in files['tvlist']:
				f= f.strip()
				html += '<a href="%s/">%s/</a>\n' %(f,f)
		elif len(paths) == 2:
			for f in open(os.path.join(datapath,'files','%s.txt' %paths[1]),'r'):
				filename = f.strip().split('|')
				html += '<a href="%s/">%s/</a>\n' %(filename[0],filename[0])
		elif len(paths) == 3:
			showing = checkupdate(path,scan,False)
			#if xbmc.getCondVisibility('Library.IsScanningVideo') != False:
			if showing:
				listseasons = glob.glob('%s/%s.s*' %(os.path.join(datapath,'tvjson'),paths[2]))
				if len(listseasons) == 0:
					sslist = json.loads(geturl('%snewslist.php?f=%s&t=%d'%(server,paths[2],0)))
					if len(sslist) > 0:
						for jfile in sslist:getfile('tvjson',jfile)
						listseasons = glob.glob('%s/%s.s*' %(os.path.join(datapath,'tvjson'),paths[2]))
				for f in listseasons:
					season = 'Season %s' % f[f.find('tvjson')+len(paths[2])+9:-5]
					html += '<a href="%s/">%s/</a>\n' %(urllib.quote(season),season)
			html += '<a href="tvshow.nfo">tvshow.nfo</a>\n'
		elif len(paths) == 4:
			season = urllib.unquote(paths[3]).replace('Season ','')
			jsonpath = os.path.join(datapath,'tvjson')
			jsonpath = os.path.join(jsonpath,'%s.s%s.json' %(paths[2],season))
			#html += jsonpath + '\n'
			try:file = open(jsonpath,'r')
			except:
				getfile('tvjson','%s.s%s.json' %(paths[2],season))
				file = open(jsonpath,'r')
			data = json.load(open(jsonpath,'r'))
			included = []
			for eps in data['episodes']:
				if not int(eps['ep']) in included:
					included.append(int(eps['ep']))
					f = 's%se%s' %(season,str(eps['ep']))
					html += '<a href="%s.mkv">%s.mkv</a>\n' %(f,f)
					html += '<a href="%s.nfo">%s.nfo</a>\n' %(f,f)
					#html += '<a href="%s.srt">%s.srt</a>\n' %(f,f)
	html += '<hr></pre>\n</body></html>'
	return html

def echonfo(path):
	paths = path.split('/')
	if paths[0] == 'movie':
		return openfile('static',paths[len(paths)-1]).encode('utf-8')
	if paths[0] == 'tv':
		if paths[len(paths)-1].endswith('tvshow.nfo'):
			f = openfile('tvnfo','%s.nfo'%paths[2]).encode('utf-8')
			f += str(openfile('tvposter','%s.txt'%paths[2]))
			f += '</tvshow>'
			return f
		else:
			global lastpaths,lastjson
			season = urllib.unquote(paths[3]).replace('Season ','')
			epinfo = paths[len(paths)-1][paths[len(paths)-1].find('e')+1:-4]
			if paths[2] == lastpaths[2] and paths[3] == lastpaths[3]:data = lastjson
			else:
				f = openfile('tvjson','%s.s%s.json' %(paths[2],season),False)
				data = json.load(f)
				lastjson = data
			xmlinfo = re.sub(u'<title>[^<]+?<',u'<title>Tập %s<'%epinfo,data['metanfo']).encode('utf-8')
			xmlinfo = xmlinfo.replace('<episode>1','<episode>%s'%epinfo)
			return xmlinfo
	lastpaths = paths

def mkvdirect(path):
	autopick = my_addon.getSetting('autopickserver') == 'true'
	reload(mediaget)
	paths = path.split('/')
	if paths[0] == 'movie':
		filename = paths[len(paths)-1][0:-4]
		if path.endswith('.strm'):filename = paths[len(paths)-1][0:-5]
		#if scan:links = json.load(openfile('movielinks','%s.json'%filename,False))
		links = json.loads(geturl("%smovielinks/%s.json"%(server,filename)))
		link = ''
		nguon = []
		for u in links:
			if autopick:
				link = mediaget.getMovie(u)
				if link != '':break
			else:
				src = u.replace('http://','').replace('www.','').split('.')
				nguon.append(src[0])
		if not autopick:
			if len(nguon)>1:
				ret = xbmcgui.Dialog().select(u'Chọn nguồn phim', nguon)
				if ret>-1:link = mediaget.getMovie(links[ret])
			else:link = mediaget.getMovie(links[0])
		return link
	if paths[0] == 'tv':
		season = urllib.unquote(paths[3]).replace('Season ','')
		epinfo = paths[len(paths)-1][paths[len(paths)-1].find('e')+1:-4]
		f = openfile('tvjson','%s.s%s.json' %(paths[2],season),False)
		data = json.load(f)
		link = ''
		backuplink = ''
		nguon = []
		medialinks = []
		for epi in data['episodes']:
			if autopick:
				if int(epi['ep']) == int(epinfo):
					if epi['sub'] == 'VietSub' or epi['sub'] == 'dubbing':
						link = mediaget.getTV(epi['link'])
					else:backuplink = epi['link']
				if link != '' and link['link'].startswith('http'):break
			else:
				if int(epi['ep']) == int(epinfo):
					medialinks.append(epi['link'])
					srcs = epi['link'].replace('http://','').replace('www.','').split('.')
					src = '%s - %s'%(srcs[0],epi['sub'])
					nguon.append(src)
		if autopick:
			if link == '' and backuplink != '':link = mediaget.getTV(backuplink)
		else:
			if len(nguon)>1:
				ret = xbmcgui.Dialog().select(u'Chọn nguồn phim', nguon)
				if ret>-1:link = mediaget.getTV(medialinks[ret])
			else:link = mediaget.getTV(medialinks[0])
		return link

def mp4direct(path):
	reload(mediaget)
	url = 'http://%s' %path[path.find('www.phimmoi.net'):-4]
	return mediaget.getPM(url);

def echom3u(path):
	paths = path.split('/')
	if path.find('www.phimmoi.net') > 0:
		url = 'http://%s' %path[path.find('www.phimmoi.net'):-4]
		a = geturl(url)
		if a.count('data-part=') > 1:
			b = re.findall('data-part="([^"]+?)"[^>]+?data-language="([^"]+?)"[^>]+?href="([^"]+?)">',a);
			m3ucontent = '#EXTM3U\n'
			curpart = 1
			for link in b:
				if int(link[0]) == curpart and (link[1] == 'subtitle' or link[1] == 'dubbing'):
					mplink = link[2].split('/')
					m3ucontent += '#EXTINF:-1,\n'
					m3ucontent += '%s.mp4\n'%mplink[len(mplink)-1]
					curpart += 1
			m3ucontent += '\n'
			return m3ucontent
	if path.find('HDVIETM3ULINK/') > 0:
		urlx = path[path.find('HDVIETM3ULINK/'):]
		url = urlx.replace('HDVIETM3ULINK/','http://')
		ux = url.split('/')
		#ux = urlx.split('/')
		prefix = url.replace(ux[len(ux)-1],'')
		#prefix = urlx.replace(ux[len(ux)-1],'')
		a = geturl(url)
		ln = a.splitlines()
		rt = []
		for line in ln:
			if line.endswith('.ts'):
				line = "%s%s" %(prefix,line)
			rt.append(line)
		return '\n'.join(rt)
		#return a;

def echosrt(path):
	return path

def echots(path):
	if path.find('HDVIETM3ULINK/') > 0:
		url = path[path.find('HDVIETM3ULINK/'):]
		url = url.replace('HDVIETM3ULINK/','http://')
		return geturl(url)
	else:return ''

def file_not_exist(folder,file):
	if folder == '':fpath = datapath
	else:fpath = os.path.join(datapath,folder)
	fpath = os.path.join(fpath,file)
	if os.path.isfile(fpath):return False;
	else: return True

def addVideoSources():
	source_path = os.path.join(xbmc.translatePath('special://profile/'), 'sources.xml')
	try:
		file = open(source_path, 'r')
		content=file.read()
		file.close()
	except:
		#dialog.ok("Error","Could not read from sources.xml, does it really exist?")
		#file = open(source_path, 'w')
		content = "<sources>\n"
		content += "    <programs>"
		content += "        <default pathversion=\"1\"></default>"
		content += "    </programs>"
		content += "    <video>"
		content += "        <default pathversion=\"1\"></default>"
		content += "    </video>"
		content += "    <music>"
		content += "        <default pathversion=\"1\"></default>"
		content += "    </music>"
		content += "    <pictures>"
		content += "        <default pathversion=\"1\"></default>"
		content += "    </pictures>"
		content += "    <files>"
		content += "        <default pathversion=\"1\"></default>"
		content += "    </files>"
		content += "</sources>"
		#file.close()
	
	soup = BeautifulSoup(content)  
	video = soup.find("video")      
	
	if len(soup.findAll(text="MoviesLib")) < 1:
		movie_source_tag = Tag(soup, "source")
		movie_name_tag = Tag(soup, "name")
		movie_name_tag.insert(0, "MoviesLib")
		movie_path_tag = Tag(soup, "path")
		movie_path_tag['pathversion'] = 1
		movie_path_tag.insert(0, "http://127.0.0.1:5735/movie/")
		movie_allowsharing_tag = Tag(soup, "allowsharing")
		movie_allowsharing_tag.insert(0, "true")
		movie_source_tag.insert(0, movie_name_tag)
		movie_source_tag.insert(1, movie_path_tag)
		movie_source_tag.insert(2, movie_allowsharing_tag)
		video.insert(2, movie_source_tag)
	
	if len(soup.findAll(text="TvShowsLib")) < 1: 
		tvshow_source_tag = Tag(soup, "source")
		tvshow_name_tag = Tag(soup, "name")
		tvshow_name_tag.insert(0, "TvShowsLib")
		tvshow_path_tag = Tag(soup, "path")
		tvshow_path_tag['pathversion'] = 1
		tvshow_path_tag.insert(0, "http://127.0.0.1:5735/tv/")
		tvshow_allowsharing_tag = Tag(soup, "allowsharing")
		tvshow_allowsharing_tag.insert(0, "true")
		tvshow_source_tag.insert(0, tvshow_name_tag)
		tvshow_source_tag.insert(1, tvshow_path_tag)
		tvshow_source_tag.insert(2, tvshow_allowsharing_tag)
		video.insert(2, tvshow_source_tag)
	
	file = open(source_path, 'w')
	file.write(str(soup))
	file.close()

def updatedata():
	try:
		if xbmc.getCondVisibility('Library.IsScanningVideo'):xbmc.sleep(1000)
	except:pass
	firstrun = False
	tvnoupdate = 1
	if int(my_addon.getSetting('firstrun')) == 1:
		firstrun = True
		my_addon.setSetting('lastsync', '1')
	getfile('','files.txt')
	files = json.load(open(os.path.join(datapath,'files.txt'),'r'))
	if firstrun:
		#xbmc.executebuiltin((u'XBMC.Notification(%s,%s,%s)'%('MovieTV Lib',u'Đang khởi tạo dữ liệu, vui lòng đợi ...',10000)).encode("utf-8"))
		dialog  = xbmcgui.DialogProgressBG()
		dialog.create(u'Đang khởi tạo dữ liệu, vui lòng đợi ...')
		dialog.update(10,u'Đang khởi tạo dữ liệu, vui lòng đợi',u'Đang tải dữ liệu...')
		getfile('','data.zip')
		dialog.update(50,u'Đang khởi tạo dữ liệu, vui lòng đợi',u'Đang giải nén...')
		zip_ref = zipfile.ZipFile(os.path.join(datapath,'data.zip'), 'r')
		zip_ref.extractall(datapath)
		zip_ref.close()
		dialog.update(90,u'Đang khởi tạo dữ liệu, vui lòng đợi',u'Đang hoàn tất dữ liệu...')
		os.remove(os.path.join(datapath,'data.zip'))
		movlinkfolder = os.path.join(datapath,'movielinks')
		if not os.path.exists(movlinkfolder):os.makedirs(movlinkfolder)
		my_addon.setSetting('lastsync', str(geturl('%sziptime.txt'%server)))
		my_addon.setSetting('firstrun', '0')
		addVideoSources()
		#xbmc.executebuiltin((u'XBMC.Notification(%s,%s,%s)'%('MovieTV Lib',u'Khởi tạo dữ liệu hoàn tất',3000)).encode("utf-8"))
		dialog.close()
		db_path = xbmc.translatePath('special://database')
		db_files = glob.glob('%s/MyVideos*.db'%db_path)
		dbfile = db_files[0]
		if len(db_files) > 1:
			lastversion = 0
			for v in db_files:
				version = int(regsearch('MyVideos([\d]+?)\.db',v))
				if version > lastversion:
					lastversion = version
					dbfile = v
		conn = sqlite3.connect(dbfile)
		c = conn.cursor()
		for pp in files['list']:addlibpath(c,'http://127.0.0.1:5735/movie/%s/'%pp)
		scantvnow = xbmcgui.Dialog().yesno('MovieTV Lib', 'Quét tất cả phim bộ vào thư viện sẽ rất lâu','Bạn có muốn tự động thêm tất cả phim bộ vào thư viện?', 'Chọn Không để thêm các phim bộ vào sau',nolabel='Không',yeslabel='Có')
		if scantvnow:tvnoupdate = 0
		else:tvnoupdate = 1
		for px in files['tvlist']:addlibpath(c,'http://127.0.0.1:5735/tv/%s/'%px,True,tvnoupdate)
		conn.commit()
		conn.close()
	try:
		addon_path = os.path.join(xbmc.translatePath('special://home'),'addons','service.onlinelibrary')
		if int(files['mediaget_version']) > mediaget.__version__:
			file_url = '%s/mediaget.py'%server
			path = os.path.join(addon_path,'mediaget.py')
			f = urllib2.urlopen(file_url)
			with open(path, "wb") as code:
				code.write(f.read())
	except:pass
	lastsync = int(my_addon.getSetting('lastsync'))
	#getfile('','%s.txt'%files['current_updating'])
	for g in files['list']:
		if file_not_exist('files','%s.txt'%g):
			addlibpath(None,'http://127.0.0.1:5735/movie/%s/'%g)
		getfile('files','%s.txt'%g)
	for f in files['tvlist']:
		if file_not_exist('files','%s.txt'%f):
			addlibpath(None,'http://127.0.0.1:5735/tv/%s/'%f,True,tvnoupdate)
		getfile('files','%s.txt'%f)
		for c in open(os.path.join(datapath,'files','%s.txt'%f),'r'):
			d = c.strip().split('|')
			try:
				if file_not_exist('tvnfo','%s.nfo'%d[0]):getfile('tvnfo','%s.nfo'%d[0])
			except:print d[0]
			if int(d[1]) > lastsync:
				fileexist = False;
				#jsonn = json.loads(geturl('%snewslist.php?f=%s&t=%d'%(server,d[0],int(d[1])-60)))
				for jfile in json.loads(geturl('%snewslist.php?f=%s&t=%d'%(server,d[0],int(d[1])-60))):
					if fileexist == False:fileexist = file_not_exist('tvjson',jfile)
					getfile('tvjson',jfile)
				if fileexist:getfile('tvposter','%s.txt'%d[0])
	my_addon.setSetting('lastsync', str(int(time.time())))
	if not xbmc.getCondVisibility('Library.IsScanningVideo') and not xbmc.Player().isPlaying():xbmc.executebuiltin('UpdateLibrary(video)')