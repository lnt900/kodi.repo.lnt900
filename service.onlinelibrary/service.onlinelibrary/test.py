import xbmcaddon,xbmcgui,xbmc,json,string
from functions import *
import time
import sqlite3
import mediaget

#path = 'http://www.phimmoi.net/phim/ke-san-dem-4862/xem-phim.html'
path = 'http://www.phimmoi.net/phim/ky-an-zootopia-3259/xem-phim.html'
#path = 'movie/mov07/The.Edge.of.Seventeen.2016/www.phimmoi.net/phim/ky-an-zootopia-3259/xem-phim.html.m3u'
#paths = 'tv/tvshows/The.Flash'.split('/')
paths = 'tv/tvshows/The.Flash'.split('/')

#with open(os.path.join(datapath,'tvshows.txt'),'r') as f:list = f.read()
#if xbmc.getCondVisibility('Library.IsScanningVideo') != False:
#path = echofolder(paths)
#updatedata()
#my_addon.setSetting('syncmov06', '1486662799')
#my_addon.getSetting('syncmov06')
"""
list = open(os.path.join(datapath,'%s.txt' %paths[1]),'r').read()
namestring = list[list.find(paths[2]):list.find(paths[2])+len(paths[2])+22]
utime = int(list[list.find(paths[2])+len(paths[2])+1:list.find(paths[2])+len(paths[2])+11])
ltime = list[list.find(paths[2])+len(paths[2])+12:list.find(paths[2])+len(paths[2])+22]
namestring = namestring.replace(ltime,str(utime))
i =  0 if my_addon.getSetting('syncmov06') == '' else int(my_addon.getSetting('syncmov06'))
#xbmc.executebuiltin('UpdateLibrary(video, http://127.0.0.1:5735/movie/)')
a = 'a'

db_path = xbmc.translatePath('special://database')
db_files = glob.glob('%s/MyVideos*.db'%db_path)
conn = sqlite3.connect(db_files[0])
c = conn.cursor()
addlibpath(c,'http://127.0.0.1:5735/movie/mov01/')
#addlibpath(c,'http://127.0.0.1:5735/tv/',True)
conn.commit()
conn.close()
"""
file_url = '%s%s' %(server,'files.txt')
#addVideoSources()
#xbmc.executebuiltin('UpdateLibrary(video)')
#xbmc.executebuiltin('UpdateLibrary(movies)')
#xbmc.Player().play(mediaget.get_movieVSHD('http://www.vietsubhd.com/phim/nguoi-chi-tre-5481/')['link'])
#xbmcgui.Dialog().ok('test',mediaget.get_movieVSHD('http://www.vietsubhd.com/phim/nguoi-chi-tre-5481/')['link'])
xbmcgui.Dialog().ok('test',file_url)
#xbmc.executebuiltin((u'XBMC.Notification(%s,%s,%s)'%('MovieTV Lib','Scanning Lib',4000)).encode("utf-8"))
#xbmc.executebuiltin((u'XBMC.Notification(%s,%s,%s)'%('MovieTV Lib','%s'%a,4000)).encode("utf-8"))
#dialog = xbmcgui.Dialog()
#fn = dialog.browse(0, 'XBMC', 'files', '', False, False, 'http://127.0.0.1:5735/movie/mov01/')