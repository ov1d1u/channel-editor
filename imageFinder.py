import urllib2, json, threading, socket, gobject, gtk, imgtools

class imageFinder:
	def __init__(self, main):
		self.gui = main.gui
		self.url = 'https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%QUERY%&start=%PAGENUM%&rsz=8&as_filetype=png&userip=' + self.getMyIP()
		self.progress = [0, 40] # current, total
		self.test_query = None
		
	def getMyIP(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("tv-maxe.org",80))
		return s.getsockname()[0]

	def searchLogos(self, query):
		self.gui.get_object('liststore5').clear()
		self.gui.get_object('filechooserbutton1').set_filename('')
		self.gui.get_object('label13').set_text('Logos for ' + query)
		self.progress = [0, 40]
		self.updateProgress()
		self.gui.get_object('window5').show()
		threading.Thread(target=self.googleSearch, args=(urllib2.quote(query),)).start()
	
	def googleSearch(self, query):
		for i in range(0, 5):
			if not self.test_query == query:
				return
			url = self.url.replace('%QUERY%', query)
			url = url.replace('%PAGENUM%', str(i*8))
			request = urllib2.Request(url, None, {'Referer': 'http://www.tv-maxe.org'})
			response = urllib2.urlopen(request)
			results = json.loads(response.read())
			self.progress[0] = self.progress[0] + 1
			gobject.idle_add(self.updateProgress)
			for x in results['responseData']['results']:
				if not self.test_query == query:
					return
				gobject.idle_add(self.appendResult, query, x['titleNoFormatting'], x['unescapedUrl'])
			
	def appendResult(self, query, title, url):
		icon = gtk.gdk.pixbuf_new_from_file('tvmaxe.png')
		iter = self.gui.get_object('liststore5').append([icon, title[:10] + '...', url])
		threading.Thread(target=self.updateIcon, args=(query, iter, url)).start()
		return False
		
	def updateIcon(self, query, iter, url):
		try:
			if not self.test_query == query:
				return
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			data = response.read()
			if not self.test_query == query:
				return
			pixbuf = imgtools.data2pixbuf(data, False)
			image = imgtools.thumbnail(pixbuf, (64, 64))
			gobject.idle_add(self.setIcon, iter, image)
		except:
			pass

	def setIcon(self, iter, image):
		self.progress[0] = self.progress[0] + 1
		self.updateProgress()
		self.gui.get_object('liststore5').set(iter, 0, image)

	def updateProgress(self):
		percent = float(self.progress[0]) / float(self.progress[1])
		if percent > 1.0:
			self.gui.get_object('hbox10').hide()
		else:
			self.gui.get_object('hbox10').show()
			self.gui.get_object('progressbar1').set_fraction(percent)
