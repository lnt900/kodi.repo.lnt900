# -*- coding: utf-8 -*-
import urlparse, binascii
import SimpleHTTPServer
import SocketServer,threading
import urllib2, urllib, os
import xbmc, xbmcgui, xbmcaddon, xbmcplugin, sys
import re, json, hashlib, string
from functions import *

scanning = False
subtitle = ''
class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	
	def do_HEAD(self):
		if self.path.endswith('.jpg') or self.path.endswith('.png') or self.path.endswith('.nomedia') or self.path.endswith('.tbn') or self.path.endswith('.bdmv') or self.path.endswith('VIDEO_TS.IFO') or self.path.endswith('.actors'):self.dummy(404,'')
		elif self.path.endswith('.mkv'):
			global scanning
			if scanning:checkupdate(self.path[1:],scanning)
			self.dummy(200,'')
		else:self.dummy(200,'')
		#scanning = xbmc.getCondVisibility('Library.IsScanningVideo')

	def do_GET(self):
		global scanning
		global subtitle
		if self.path == '/':self.dummy(200,'Movies,TV Api Service')
		else:
			if self.path.endswith('.mkv'):
				play = mkvdirect(self.path[1:])
				if play != '':
					subtitle = play['sub']
					self.redirect(play['link'])
					#self.dummy(200,play['link'])
				else:self.dummy(404,'')
			elif self.path.endswith('.mp4'):
				play = mp4direct(self.path[1:])
				if play != '':
					subtitle = play['sub']
					self.redirect(play['link'])
				else:self.dummy(404,'')
			elif self.path.endswith('.ts'):
				#self.redirect(echots(self.path[1:]))
				self.dummy(200,echots(self.path[1:]),'video/mp2t')
			elif self.path.endswith('.nfo'):
				self.dummy(200,echonfo(self.path[1:]))
			elif self.path.endswith('.strm'):
				pathx = self.path[1:]
				f = pathx[0:-5]
				play = mkvdirect('%s.mkv'%f)
				if play != '':
					subtitle = play['sub']
					lnk = play['link']
					if lnk.startswith('HDVIETM3ULINK'):lnk = lnk.replace('HDVIETM3ULINK/','http://')
					self.dummy(200,lnk)
				else:self.dummy(404,'')
				#self.dummy(200,'%s.mkv'%f)
			elif self.path.endswith('.m3u') or self.path.endswith('.m3u8'):
				self.dummy(200,echom3u(self.path[1:]),'application/vnd.apple.mpegurl')
			elif self.path.endswith('.srt'):
				self.dummy(200,echosrt(self.path[1:]))
			else:
				self.path = self.path[1:]
				if self.path.endswith('/'):self.path = self.path[0:-1];
				self.dummy(200,echofolder(self.path,scanning))
		#scanning = xbmc.getCondVisibility('Library.IsScanningVideo')
	
	def dummy(self,head,text,contentType='text/html'):
		self.send_response(int(head))
		self.send_header('Content-type', contentType)
		self.end_headers()
		if text != '':
			self.wfile.write(text)
			self.wfile.close()
			self.finish()
	
	def redirect(self, link):
		self.send_response(301)
		self.send_header('Content-type','text/html')
		self.send_header('Location', link)
		self.end_headers()
		self.finish()

class MyMonitor(xbmc.Monitor):
	
	def onScanStarted(self,library):
		global scanning
		scanning = True
	
	def onScanFinished(self,library):
		global scanning
		scanning = False

class MyPlayer(xbmc.Player):
	
	def onPlayBackStarted(self):
		kVer = int(xbmc.__date__[-4:])
		global subtitle
		for retry in range(0, 20):
			if player.isPlaying():break
			xbmc.sleep(250)
		if subtitle != '' and self.isPlayingVideo():
			link = self.getPlayingFile()
			if link.startswith('http://127.0.0.1:5735/'):
				if kVer < 2017 and link.endswith('mkv'):
					play = mkvdirect(link.replace('http://127.0.0.1:5735/',''))
					if play != '':
						lnk = play['link']
						if lnk.startswith('HDVIETM3ULINK'):
							lnk = lnk.replace('HDVIETM3ULINK/','http://')
							InfoTag = self.getVideoInfoTag()
							#self.stop()
							listitem = xbmcgui.ListItem (InfoTag.getTitle())
							infolabels = {'Title': InfoTag.getTitle(), 'Genre': InfoTag.getGenre(),'plot':InfoTag.getPlot(),'year':InfoTag.getYear()}
							if link.find('/Season')>-1:
								info2 = {'mediatype': 'episode','tvshowtitle': xbmc.getInfoLabel('VideoPlayer.TVShowTitle'),'season': int(xbmc.getInfoLabel('VideoPlayer.Season')),'episode':int(xbmc.getInfoLabel('VideoPlayer.Episode'))}
								infolabels.update(info2)
							else:infolabels.update({'mediatype': 'movie'})
							listitem.setInfo('video', infolabels)
							listitem.setArt({'thumb':InfoTag.getPictureURL()})
							listitem.setSubtitles([subtitle])
							self.play(lnk,listitem)
				else:
					try:
						sublink = subtitle.split('/')
						subfile = os.path.join(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode("utf-8"), "subtitle.%s"%sublink[len(sublink)-1][-3:])
						f = urllib2.urlopen(subtitle)
						with open(subfile, "wb") as code:
							code.write(f.read())
						self.setSubtitles(subfile)
					except:pass
					subtitle = ''

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == '__main__':
	
	PORT = 5735
	monitor = MyMonitor()
	player = MyPlayer()
	sys.stdout.write("Monitoring Schedule")
	handler = MyRequestHandler
	server = ThreadedTCPServer(("", PORT), MyRequestHandler)
	server_thread = threading.Thread(target=server.serve_forever)
	server_thread.daemon = True
	server_thread.start()
	sys.stdout.write("Server started at Port %d" % PORT)
	while not monitor.abortRequested():
		updatedata()
		if monitor.waitForAbort(2100):break
	del monitor
	del player
	server.shutdown()
	server.server_close()