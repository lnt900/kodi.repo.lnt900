# -*- coding: utf-8 -*-
import urllib2, urllib, re, os, json, string,xbmc, math
from crypt import *

__version__ = 3
def geturl(url,param=False,ecoding_param=False,agent=False,cookies=False,getcookies=False,customct=False):
	headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1'}
	if agent:headers = agent
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

def regsearch(pattern,string,group=1,flags=0):
	try:s=re.search(pattern,string,flags).group(group)
	except:s=''
	return s
	
def getPM(url,content=''):
	rt = ''
	if content != '':a = content
	else:a=geturl(url)
	xurl=regsearch('src="([^"]*?episodeinfo[^"]+?)"',a).replace('javascript','json')
	b=geturl(xurl)
	try:j=json.loads(b)
	except:j={}
	links=j.get('medias',[])
	big = 0
	encrypted_string = ''
	for res in links:
		if res.get('resolution',0) > big:
			big = res['resolution']
			encrypted_string = res['url']
	if encrypted_string.startswith('http'):link = encrypted_string
	else:link=gibberishAES(encrypted_string,'PhimMoi.Net@%s'%j.get('episodeId'))
	if not link.startswith('http'):rt = ''
	else:
		rt = {'link': link, 'sub': ''};
	return rt

def get_moviePM(url):
	url = '%sxem-phim.html'%url
	a = geturl(url)
	if a.count('data-part=') > 1:
		b = re.findall('data-part="([^"]+?)"[^>]+?data-language="([^"]+?)"[^>]+?href="([^"]+?)">',a);
		#return b[0][0];
		link = ''
		for links in b:
			if int(links[0]) == 0 and (links[1] == 'subtitle' or links[1] == 'dubbing'):link = getPM('http://www.phimmoi.net/%s'%links[2])
			if link != '' and link['link'].startswith('http'):break
			#return links[2]
		if link != '':return link
		else: return '%s.m3u'%url.replace('http://','')
	else:return getPM('',a)
	
def getHdviet(url):
	attr = url.split("/")
	a = json.loads(geturl("http://api-v2.hdviet.com/movie/play?movieid=%s&ep=%s"%(attr[1],attr[2])))
	if int(a["e"]) == 0:
		movie = a["r"]
		m3ulink = movie['LinkPlay'].replace("playlist.m3u8","playlist_h.m3u8")
		rs = geturl(m3ulink)
		ln = rs.splitlines()
		maxres = 0
		url = ''
		for line in ln:
			if line.endswith('playlist.m3u8'):
				res = int(regsearch('_([\d]+?)/playlist.m3u8',line))
				if res > maxres:
					maxres = res
					url = line
		if url != '':
			subtitle_url = ''
			try:
				subtitle_url = movie['Subtitle']['VIE']['Source']
				if subtitle_url == '':
					subtitle_url = movie['SubtitleExt']['VIE']['Source']
				if subtitle_url == '':
					subtitle_url = movie['SubtitleExtSe']['VIE']['Source']
			except: pass
			m3ulink = m3ulink.replace('playlist_h.m3u8',url)
			kVer = int(xbmc.__date__[-4:])
			if kVer < 2017:m3ulink = m3ulink.replace('http://','HDVIETM3ULINK/')
			rt = {'link': m3ulink, 'sub': subtitle_url}
			return rt;
		else:return ''
	else:return ''

def getVSHD(url):
	paths = url.split("/")
	htmlfile = paths[len(paths)-1]
	htmlfile = htmlfile[0:-5]
	movid = regsearch('-([\d]+?)/%s\.html'%htmlfile,url)
	epid = regsearch('-([\d]+?)\.html',url)
	a = geturl('http://www.vietsubhd.com/ajaxload','NextEpisode=1&EpisodeID=%s&filmID=%s'%(epid,movid))
	if a.find('{') > -1 and a.find('}') >-1 and a.find('link:') > -1:
		a = a[a.find('{'):a.find('}')+1].replace('link','"link"').replace('autostart','"autostart"').replace('subtitle','"subtitle"')
		j1 = json.loads(a)
		j = json.loads(geturl('http://www.vietsubhd.com/gkphp/plugins/gkpluginsphp.php','link=%s'%j1['link']))
		links = []
		if j.get('link'): links = j['link']
		elif j.get('list'):
			for lk in j['list']:
				for link in lk['link']:
					links.append(link)
		rt = ''
		biggest = 0
		for url in links:
			try:
				label = int(url['label'].replace('p',''))
				if label > biggest:
					biggest = label
					rt = url['link']
			except:pass
		if rt != '':return {'link': rt, 'sub': j1['subtitle']}
		else:return ''
	else: return ''

def get_movieVSHD(url):
	url = '%sxem-phim.html'%url
	#movieid = regsearch('-([\d]+?)/xem-phim\.html',url)
	a = geturl(url)
	a = a[a.find('<div class="block servers">'):a.find('<div class="block comment">')]
	b = re.findall('<a href="([^"]+?)"',a);
	rt = ''
	for link in b:
		epid = regsearch('-([\d]+?)\.html',link)
		#rt = getVSHD(epid,movieid)
		rt = getVSHD(link)
		if rt !='' and rt['link'].startswith('http'):break
	return rt
			
def base_convert(number, fromBase, toBase):
	try:
		# Convert number to base 10
		base10 = int(number, fromBase)
	except ValueError:
		raise
	if toBase < 2 or toBase > 36:
		raise NotImplementedError
	output_value = ''
	digits = "0123456789abcdefghijklmnopqrstuvwxyz"
	sign = ''
	if base10 == 0:
		return '0'
	elif base10 < 0:
		sign = '-'
		base10 = -base10

	# Convert to base toBase    
	s = ''
	while base10 != 0:
		r = base10 % toBase
		r = int(r)
		s = digits[r] + s
		base10 //= toBase
		
	output_value = sign + s
	return output_value
	
def genRE(c,a):
	if c < a:s1 = ''
	else:s1 = genRE(int(c/a),a)
	c = c%a;
	if c > 35:s2 = chr(c+29)
	else:s2 = base_convert(str(c),10,36);
	return s1+s2;

def getHDO(url):
	url = url.replace('://hdonline.vn/','://m.hdonline.vn/')
	#url = url.replace('://www.hdonline.vn/','://m.hdonline.vn/')
	useragent = {'User-Agent':'Mozilla/5.0 (Linux; Android 7.0; E6683 Build/32.3.A.0.376) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'}
	a=geturl(url,False,False,useragent)
	var = regsearch('return p}\((.+)\.split',a)
	vars = eval('['+var+']')
	b = vars[3].split('|')
	x = vars[0]
	c = int(vars[2])
	while c > -1:
		c -= 1
		if len(b) >= c and b[c] != '':x = re.sub(r'\b%s\b'%genRE(c,int(vars[1])),b[c],x)
		
	jstring = regsearch('setup\(([^\)]+?)\)',x)
	js = json.loads(jstring)
	if js.get('playlist') and len(js['playlist'])>0:
		subtitle = ''
		link = ''
		sources = js['playlist'][0]['sources']
		subs = js['playlist'][0]['tracks']
		if len(subs)>0:
			for sub in subs:
				if sub.get('language') and sub['language'] == 'vi':
					subtitle = sub['file']
					break
		if len(sources)>1:
			biggest = 0
			for url in sources:
				if url['type'] == 'hls':
					if url['label'].startswith('P.'):
						link = url['file']
						break
					else:link = sources[0]['file']
				else:
					try:
						label = int(url['label'].replace('p',''))
						if label > biggest:
							biggest = label
							link = url['file']
					except:pass
		elif len(sources)==1:link = sources[0]['file']
		if link != '':
			if link.endswith('.m3u8'):link = link.replace('http://','HDVIETM3ULINK/')
			return {'link': link, 'sub': subtitle}
		else: return ''
	else:return ''
	
def getMovie(url):
	if url.startswith('http://www.phimmoi.net'):return get_moviePM(url)
	elif url.startswith('hdviet.com'):return getHdviet(url)
	elif url.startswith('http://www.vietsubhd.com'):return get_movieVSHD(url)
	elif url.find('hdonline.vn/')>-1:return getHDO(url)

def getTV(url):
	if url.startswith('http://www.phimmoi.net'):return getPM(url)
	elif url.startswith('hdviet.com'):return getHdviet(url)
	elif url.startswith('http://www.vietsubhd.com'):return getVSHD(url)
	elif url.find('hdonline.vn/')>-1:return getHDO(url)
