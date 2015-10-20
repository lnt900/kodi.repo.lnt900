# -*- coding: utf-8 -*-
import xbmc,sys,xbmcaddon,xbmcgui
import urlparse, binascii
import SimpleHTTPServer
import SocketServer
import urllib2, urllib
import re, json, hashlib, string
import xml.etree.ElementTree as xmltree
import resources.pyaes as pythonaes
from random import randint

xmiocookie = False
sctvhash = False

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
def encryptAES(st, key, iv):
	aes = pythonaes.AESModeOfOperationCBC(key, iv = iv)
	le = len(st)/16
	thua = len(st)%16
	if thua != 0:
		le += 1
		thieu = 16-thua
		st += ' '*thieu
	encrypted = ''
	for x in range(0,le):
		en = st[x*16:x*16+16]
		encrypted += binascii.hexlify(aes.encrypt(en))
	return encrypted
def xmiologin(user,pw):
	pwhash = hashlib.md5(pw).hexdigest()
	devid = str(xbmcaddon.Addon().getSetting('xmio_deviceid'))
	if devid == 'none':
		devid = json.loads(geturl("http://125.212.227.230:7001/billing/authen?action=create_device&os=android&type=stb&sign=7182a5a7d7"))['data']['device_id']
		xbmcaddon.Addon().setSetting("xmio_deviceid", devid)
	sign = hashlib.md5("%s%s%s$387F$*G$&#@FHBEJHDBKC@(T$#$&TCBDF" %(user,pwhash,devid)).hexdigest()[:10]
	res = geturl("http://125.212.227.230:7001/billing/authen?action=login&username=%s&password=%s&sign=%s&device_id=%s" %(user,pwhash,sign,devid))
	if 'token' in res:
		login = json.loads(res)
		xmiotoken = login['data']['token']
		xmiocookie = {'Authorization': "Bearer %s" %xmiotoken}
		cookie = geturl("http://125.212.227.230:7001/live/index",cookies=xmiocookie,getcookies=True)
		ck = {'Cookie' : cookie}
		xmiocookie.update(ck)
		return xmiocookie
	else:
		xbmc.executebuiltin((u'XBMC.Notification(%s,%s,%s)'%('VNIPTV','[COLOR red]Lỗi Xmio! Kiểm tra user/password trong addon setting[/COLOR]',4000)).encode("utf-8"))
		return False
def sctvlogin(email):
	ranst = hex(randint(65536,15728600)).lstrip('0x').upper()
	ranmac = '%s:%s:%s' %(ranst[0:2],ranst[2:4],ranst[4:6])
	aid = 'ff27125408%s' %str(hex(randint(65536,15728640)).lstrip('0x'))
	c = {'Content-Type': 'text/xml'}
	res = geturl('https://vtspub.sctv.vn:8444/adphone/WSV_SctvOnline_Sec_Mobile.asmx','<v:Envelope xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns:d="http://www.w3.org/2001/XMLSchema" xmlns:c="http://schemas.xmlsoap.org/soap/encoding/" xmlns:v="http://schemas.xmlsoap.org/soap/envelope/"><v:Header /><v:Body><USP_GetGenPIN xmlns="http://vtspub.sctv.vn/" id="o0" c:root="1"><arg0 i:type="d:string">%s</arg0><arg1 i:type="d:string"></arg1><arg2 i:type="d:string">%s</arg2><arg3 i:type="d:string">B4:52:00:%s</arg3><arg4 i:type="d:string">3580900%s</arg4><arg5 i:type="d:string">0</arg5><arg98 i:type="d:string">ScolMBV3</arg98><arg99 i:type="d:string">QazCDE#@!</arg99></USP_GetGenPIN></v:Body></v:Envelope>' %(email,aid,ranmac,str(randint(20000000,90000000))),ecoding_param=False,cookies=c,customct=True)
	try:
		xml = xmltree.fromstring(res)
		sctvkeys = {'id': xml[0][0][0][0].text,'pin':xml[0][0][0][1].text,'iv':xml[0][0][0][2].text}
		#sys.stdout.write("VNIPTV: sctv login - %s/%s/%s/%s/%s" %(email,aid,sctvkeys['pin'], sctvkeys['iv'],sctvkeys['id']))
		sctvhash = encryptAES('%s-0-%s-1-22' %(email,aid), sctvkeys['pin'], sctvkeys['iv'])
		sctvhash += '-%s' %sctvkeys['id']
		return sctvhash
	except:
		xbmc.executebuiltin((u'XBMC.Notification(%s,%s,%s)'%('VNIPTV','[COLOR red]Lỗi SCTV! Login không thành công[/COLOR]',4000)).encode("utf-8"))
		return False
def getFPT(id):
	vtvcab = ['bibi','bongdatvhd','thethaotvhd','bongdatvsd','thethaotvsd','giaitritv','styletv','yeah1tv','kenh17','haytv','o2tv','investtv','infotv','echanel','phimviet','ddramas']
	isvtvcab = False
	if id in vtvcab:
		isvtvcab = id
		id = 'htv9-hd'
	data={"id": id, "type": "newchannel", "quality": "4",	"mobile": "web"}
	cookie = {'Referer' : "http://fptplay.net/livetv", "X-Requested-With" : "XMLHttpRquest"}
	info = json.loads(geturl('http://fptplay.net/show/getlinklivetv',data,cookies=cookie))
	if info['stream']:
		stream = info['stream']
		if isvtvcab:
			ret = info['stream'].replace('htv9hd',isvtvcab).replace('livek/','livev/')
			if isvtvcab.endswith('hd'):ret = ret.replace('_hls.smil','_2000.stream')
			stream = ret
		rs = geturl(stream)
		rt = "blank.mp4"
		ln = rs.splitlines()
		i = 0
		while (i < len(ln)):
			if 'chunklist' in ln[i]:rt = re.sub('playlist.+',ln[i],stream)
			i += 1
		return rt
	else: return "blank.mp4"
def getHTV(channel):
	link = "http://www.htvonline.com.vn/livetv/%s.html" %channel
	htmlStr = geturl(link)
	p = re.compile("data\-source=\"([^\"]*)\"")
	m = p.search(htmlStr)
	if (m):
		return urllib.unquote(m.group(1)).decode('utf8')
	else: return "blank.mp4"

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

	def do_HEAD(self):
		if '/htv?' in self.path or '/fpt?' in self.path or '/xmio?' in self.path or '/sctv?' in self.path or '/vtvgo?' in self.path:self.do_GET()
		else:self.dummy(200,'VNIPTV Service')

	def do_GET(self):
		if self.path == '/':self.dummy(200,'VNIPTV Service')
		else:
			parsed_params = urlparse.urlparse(self.path)
			global sctvhash
			global xmiocookie
			if parsed_params.path == '/fpt':
				reslink = getFPT(parsed_params.query)
				self.redirect(reslink)
			elif parsed_params.path == '/htv':
				reslink = getHTV(parsed_params.query)
				self.redirect(reslink)
			elif parsed_params.path == '/xmio':
				xmio_user = str(xbmcaddon.Addon().getSetting('xmiouser'))
				xmio_pw = str(xbmcaddon.Addon().getSetting('xmiopw'))
				quality = str(xbmcaddon.Addon().getSetting('xmio_hd')) == 'HD'
				chid = parsed_params.query
				if not xmiocookie:xmiocookie = xmiologin(xmio_user,xmio_pw)
				reslink = "blank.mp4"
				if xmiocookie:
					xvar = "http://125.212.227.230:7001/live/index?action=get_stream&channel_id=%s&device_Type=stb" % chid
					index = geturl(xvar,cookies=xmiocookie)
					if not "url" in index or not 'data' in index:
						xmiocookie = xmiologin(xmio_user,xmio_pw)
						if xmiocookie:index = geturl(xvar,cookies=xmiocookie)
					if "url" in index and 'data' in index:
						lnk = json.loads(index)['data']['url']
						lnk = re.sub('\$_p2.+\$','$',lnk)
						lnk = re.sub('\$_p4.+\$','$',lnk)
						if quality:
							lnk = re.sub('\$_p3.+/','$_p5!3000000!0!1280!720/',lnk)
							lnk = re.sub('\$_p3.+\$','$',lnk)
						else:
							lnk = re.sub('\$_p5.+/','/',lnk)
							lnk = lnk.replace('$/','/')
						reslink = lnk
					else: reslink = "blank.mp4"
				else:reslink = "blank.mp4"
				self.redirect(reslink)
			elif parsed_params.path == '/sctv':
				sctv_user = str(xbmcaddon.Addon().getSetting('sctvuser'))
				sctv_port = str(xbmcaddon.Addon().getSetting('sctv_port'))
				if not sctvhash:sctvhash = sctvlogin(sctv_user)
				reslink = "blank.mp4"
				if sctvhash:
					sv = 'mslive2'
					channel = ''
					if '/' in parsed_params.query:
						clink = parsed_params.query.split('/')
						sv = clink[0]
						channel = clink[1]
					else:channel = parsed_params.query
					url = 'http://112.197.2.135:%s/%s/%s/playlist.m3u8?us=%s'
					index = geturl(url%(sctv_port,sv,channel,sctvhash))
					if not index or 'chunklist' not in index:
						sctvhash = sctvlogin(sctv_user)
						if sctvhash:index = geturl(url%(sctv_port,sv,channel,sctvhash))
					if index and 'chunklist' in index:
						for xx in index.splitlines():
							if 'chunklist' in xx and 'm3u' in xx:
								reslink = 'http://112.197.2.135:%s/%s/%s/%s' %(sctv_port,sv,channel,xx)
								break
					else:reslink = 'blank.mp4'
				else:
					sys.stdout.write("VNIPTV: can't get sctv hash !")
					reslink = 'cantgetsctvhash.mp4'
				self.redirect(reslink)
			elif parsed_params.path == '/logoutxmio':
				xmio_user = str(xbmcaddon.Addon().getSetting('xmiouser'))
				xmio_pw = str(xbmcaddon.Addon().getSetting('xmiopw'))
				try:
					if not xmiocookie:xmiocookie = xmiologin(xmio_user,xmio_pw)
					devid = str(xbmcaddon.Addon().getSetting('xmio_deviceid'))
					index = geturl('http://125.212.227.230:7001/billing/account?device_id=%s&action=logout' %devid,cookies=xmiocookie)
					self.dummy(200,'VNIPTV: Logged out Xmio')
				except:pass
			else:self.dummy(404,'VNIPTV 404: Not Found')
	
	def dummy(self,head,text):
		self.send_response(int(head))
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write(text)
		self.wfile.close()
	
	def redirect(self, link):
		self.send_response(301)
		self.send_header('Content-type','text/html')
		self.send_header('Location', link)
		self.end_headers()
if __name__ == '__main__':
	
	PORT = 9991
	handler = MyRequestHandler
	httpd = SocketServer.TCPServer(("", PORT), handler)
	sys.stdout.write("Server started at Port %d" % PORT)
	httpd.serve_forever()