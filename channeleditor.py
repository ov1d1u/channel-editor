# -*- coding: utf-8 -*-
import gettext
import locale
import gtk.glade
import os
GETTEXT_DOMAIN = 'channeleditor'
try:
    LOCALE_PATH = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'lng')
except:
    LOCALE_PATH = 'lng'
locale.setlocale(locale.LC_ALL, '')
for module in gtk.glade, gettext:
    module.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
    module.textdomain(GETTEXT_DOMAIN)


def translate(text):
    try:
        # text = unicode(text, errors='ignore')
        return unicode(gettext.gettext(text), errors='ignore')
    except:
        return gettext.gettext(text)

import __builtin__
__builtin__._ = translate
import gobject, pygtk, gtk, os, re, random, base64
import threading, urllib2
import json, imgtools
from imageFinder import imageFinder
from imgur import Imgur
from dbmanager import DBManager
gtk.gdk.threads_init()

class Main:
	def __init__(self):
		print _('TV-Maxe Channel Editor is starting...')
		self.gui = gtk.Builder()
		self.gui.add_from_file('ceditor.glade')
		self.gui.connect_signals({
			"quit" : self.quit,
			"deschide" : self.deschide, #open
			"openFile" : self.openFile,
			"openURL" : self.openURL,
			"hideOpenURL" : self.hideOpenURL,
			"goURL" : self.goURL,
			"saveList" : self.saveList,
			"showAddWindow" : self.showAddWindow,
			"hideAddWindow" : self.hideAddWindow,
			"addChannel" : self.addChannel,
			"editChannel" : self.editChannel,
			"hideChannelEditor" : self.hideChannelEditor,
			"saveChannel" : self.saveChannel,
			"deleteChannel" : self.deleteChannel,
			"uploadImage" : self.uploadImage,
			"salveaza" : self.salveaza,
			"addChannelURL" : self.addChannelURL,
			"addChannelEdit" : self.addChannelEdit,
			"removeChannelURL" : self.removeChannelURL,
			"addAudio" : self.addAudio,
			"addAudioEdit" : self.addAudioEdit,
			"removeAudio" : self.removeAudio,
			"saveNew" : self.saveNew,
			"saveInfo" : self.saveNew2,
			"hideInfo" : self.hideInfo,
			"on_entry2_changed" : self.on_entry2_changed,
			"hideLogoWin" : self.hideLogoWin,
			"selectIcon" : self.selectIcon
		})
		self.imgur = Imgur()
		self.imageFinder = imageFinder(self)
		self.db = DBManager(':memory:')
		self.db.build()
		self.gui.get_object('cellrenderertext12').set_property('editable', True)
		self.gui.get_object('cellrenderertext10').set_property('editable', True)
		self.gui.get_object('cellrenderertext8').set_property('editable', True)
		self.gui.get_object('cellrenderertext9').set_property('editable', True)
		self.icons = {}
		
	def deschide(self, obj):
		menu = self.gui.get_object('menu1')
		menu.popup(None, None, None, 0, 0)
	
	def openFile(self, obj):
		chooser = gtk.FileChooserDialog(title='Open',action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
                response = chooser.run()
                if response == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
		else:
			chooser.destroy()
			return
		chooser.destroy()
		f = open(filename)
		data = f.read()
		f.close()
		if '|newchannel|' in data:
			self.parseOldList(data)
		else:
			self.db.open(filename)
			self.db.build()
			self.populateList()
		
	def openURL(self, obj):
		self.gui.get_object('entry1').set_text('')
		self.gui.get_object('window2').show()
	
	def hideOpenURL(self, obj, event=None):
		self.gui.get_object('window2').hide()
		return True
	
	def goURL(self, obj):
		url = self.gui.get_object('entry1').get_text()
		threading.Thread(target=self.getFromURL, args=(url,)).start()
		self.gui.get_object('window2').hide()
		
	def getFromURL(self, url):
		try:
			req = urllib2.Request(url)
			response = urllib2.urlopen(req)
			data = response.read()
			#gobject.idle_add(self.parseList, data)
		except Exception, e:
			print _('Failed to retrieve ') + url
			print e
			
	def populateList(self):
		self.gui.get_object('liststore1').clear()
		self.gui.get_object('liststore2').clear()
		for x in self.db.get_all_tv():
			liststore = self.gui.get_object('liststore1')
			id = x['id']
			image = imgtools.data2pixbuf(x['icon'])
			name = x['name']
			url = x['streamurls']
			params = x['params']
			tvguide = x['guide']
			audiochs = x['audiochannels']
			urls = self.getJSON(url)
			url = ''
			for x in urls:
				url = url + x + ';'
			audios = self.getJSON(audiochs)
			audio = ''
			for x in audios:
				audio = audio + x[0] + ':' + x[1] + ';'
			liststore.append([id, image, name, url, tvguide, audio])
		for x in self.db.get_all_radio():
			liststore = self.gui.get_object('liststore2')
			id = x['id']
			image = imgtools.data2pixbuf(x['icon'])
			name = x['name']
			url = x['streamurls']
			params = x['params']
			urls = self.getJSON(url)
			url = ''
			for x in urls:
				url = url + x + ';'
			liststore.append([id, image, name, url])
			
	def parseOldList(self, data):
		self.gui.get_object('liststore1').clear()
		self.gui.get_object('liststore2').clear()
		if '|tvchannels|' in data:
			gtvch = data.split('|tvchannels|')
        		gtvch = gtvch[1].split('|endoftvchannels|')
        		channels = gtvch[0]
        		channels = channels.split('|newchannel|')
	        	channels.pop(0)
	        	channelstore = self.gui.get_object('liststore1')
	        	for x in channels:
				cdata = x.split('|-|')
				nume = cdata[0]
				url = cdata[1]
				icon = cdata[2]
				if len(cdata) > 3:
					chid = cdata[3]
				else:
					chid = ''
				image = gtk.gdk.pixbuf_new_from_file('blank.gif')
				fh = open('blank.gif', 'rb')
				imgdata = fh.read()
				fh.close()
				id = re.sub(r'\W+', '', nume + str(random.randint(100, 999)))
				iter = channelstore.append([id, image, nume, url, chid, ''])
				self.db.add_tv([id, imgdata, nume, json.dumps([url]), '', chid, json.dumps([])])
				threading.Thread(target=self.updateIcon, args=(iter, icon, channelstore)).start()
		
		if '|radiochannels|' in data:
			gtvch = data.split('|radiochannels|')
        		gtvch = gtvch[1].split('|endofradiochannels|')
        		channels = gtvch[0]
        		channels = channels.split('|newchannel|')
	        	channels.pop(0)
	        	channelstore = self.gui.get_object('liststore2')
	        	for x in channels:
				cdata = x.split('|-|')
				nume = cdata[0]
				url = cdata[1]
				icon = cdata[2]
				if len(cdata) > 3:
					chid = cdata[3]
				else:
					chid = ''
				image = gtk.gdk.pixbuf_new_from_file('blank.gif')
				fh = open('blank.gif', 'rb')
				imgdata = fh.read()
				fh.close()
				id = re.sub(r'\W+', '', nume + str(random.randint(100, 999)))
				iter = channelstore.append([id, image, nume, url])
				self.db.add_radio([id, imgdata, nume, json.dumps([url]), ''])
				threading.Thread(target=self.updateIcon, args=(iter, icon, channelstore)).start()
				
	def updateIcon(self, iter, icon, channelstore):
		try:
			if not icon.startswith('http://'):
				icon = 'http://ov1d1u.net/sopcast/' + icon
			if not 'i.imgur.com' in icon:
				req = urllib2.Request(icon)
				response = urllib2.urlopen(req)
				data = response.read()
			else:
				req = urllib2.Request(icon)
				response = urllib2.urlopen(req)
				data = response.read()
			gobject.idle_add(self.setIcon, iter, data, channelstore)
		except Exception, e:
			print 'exception', icon
			
	def selectIcon(self, obj, event=None):
		if self.gui.get_object('filechooserbutton1').get_filename() and os.path.isfile(self.gui.get_object('filechooserbutton1').get_filename()):
			fh = open(self.gui.get_object('filechooserbutton1').get_filename(), 'rb')
			data = fh.read()
			fh.close()
			pixbuf = imgtools.data2pixbuf(data, False)
		else:
			selected = self.gui.get_object('iconview1').get_selected_items()[0]
			pixbuf = self.gui.get_object('liststore5')[selected][0]
		pixbuf = imgtools.thumbnail(pixbuf)
		self.gui.get_object('image8').set_from_pixbuf(pixbuf)
		self.imageFinder.test_query = None
		self.gui.get_object('window5').hide()
			
	def setIcon(self, iter, imgdata, channelstore):
		loader = gtk.gdk.PixbufLoader()
        	loader.write(imgdata)
        	loader.close()
        	id = channelstore.get_value(iter, 0)
        	if channelstore == self.gui.get_object('liststore1'):
			self.db.update_tv(id, 'icon', base64.b64encode(imgdata))
		else:
			self.db.update_radio(id, 'icon', base64.b64encode(imgdata))
        	channelstore.set_value(iter, 1, loader.get_pixbuf())
        	
        def salveaza(self, obj):
		menu = self.gui.get_object('menu2')
		menu.popup(None, None, None, 0, 0)
		
	def saveNew(self, obj):
		d = self.db.get_info()
		self.gui.get_object('listname').set_text('')
		self.gui.get_object('epgurl').set_text('')
		self.gui.get_object('listversion').set_text('')
		self.gui.get_object('listauthor').set_text('')
		self.gui.get_object('listurl').set_text('')
		if d:
			d = dict(d)
			self.gui.get_object('listname').set_text(d.has_key('name') and d['name'] or '')
			self.gui.get_object('epgurl').set_text(d.has_key('epgurl') and d['epgurl'] or '')
			self.gui.get_object('listversion').set_text(d.has_key('version') and d['version'] or '')
			self.gui.get_object('listauthor').set_text(d.has_key('author') and d['author'] or '')
			self.gui.get_object('listurl').set_text(d.has_key('url') and d['url'] or '')
		self.gui.get_object('window4').show()
		
	def saveNew2(self, obj):
		self.gui.get_object('window4').hide()
		listname = self.gui.get_object('listname').get_text()
		epgurl = self.gui.get_object('epgurl').get_text()
		listversion = self.gui.get_object('listversion').get_text()
		listauthor = self.gui.get_object('listauthor').get_text()
		listurl = self.gui.get_object('listurl').get_text()
		self.db.set_info(name = listname, epgurl = epgurl, version = listversion, author = listauthor, url = listurl)
		chooser = gtk.FileChooserDialog(title='Save',action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
		chooser.set_do_overwrite_confirmation(True)
                response = chooser.run()
                if response == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
		else:
			chooser.destroy()
			return
		chooser.destroy()
		if not self.db.save(filename):
				self.on_error_(_('Error while saving file...'))
				
	def hideInfo(self, obj, event=None):
		self.gui.get_object('window4').hide()
		return True
		
        def saveList(self, obj):
        	chooser = gtk.FileChooserDialog(title='Save',action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
		chooser.set_do_overwrite_confirmation(True)
                response = chooser.run()
                if response == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
		else:
			chooser.destroy()
			return
		chooser.destroy()
		
		data = ''
		channelstore = self.gui.get_object('liststore1')
		iter = channelstore.get_iter_root()
		if iter:
			data = data + '|tvchannels|'
			while iter:
				data = data + '|newchannel|'
				id = channelstore.get_value(iter, 0)
				name = self.db.get_tv(id, 'name')
				url = self.getJSON(self.db.get_tv(id, 'streamurls'))[0]
				guide = self.db.get_tv(id, 'guide')
				if channelstore.get_value(iter, 0) in self.icons:
					icon = self.icons[channelstore.get_value(iter, 0)]
				else:
					icon = ''
				row = [name, url, icon, guide]
				data = data + '|-|'.join(row)
				iter = channelstore.iter_next(iter)
			data = data + '|endoftvchannels|'
		channelstore = self.gui.get_object('liststore2')
		iter = channelstore.get_iter_root()
		if iter:
			data = data + '|radiochannels|'
			while iter:
				data = data + '|newchannel|'
				id = channelstore.get_value(iter, 0)
				name = self.db.get_radio(id, 'name')
				url = self.getJSON(self.db.get_radio(id, 'streamurls'))[0]
				if channelstore.get_value(iter, 0) in self.icons:
					icon = self.icons[channelstore.get_value(iter, 0)]
				else:
					icon = ''
				row = [name, url, icon]
				data = data + '|-|'.join(row)
				iter = channelstore.iter_next(iter)
			data = data + '|endofradiochannels|'
		
		fh = open(filename, 'w')
		fh.write(data)
		fh.close()
	
	def showAddWindow(self, obj):
		self.gui.get_object('entry2').set_text('')
		self.gui.get_object('image8').set_from_file('blank.gif')
		self.gui.get_object('liststore4').clear()
		self.gui.get_object('liststore3').clear()
		self.gui.get_object('entry5').set_text('')
		if self.gui.get_object('notebook1').get_current_page() == 0:
			self.gui.get_object('entry5').set_visible(True)
			self.gui.get_object('label7').set_visible(True)
			self.gui.get_object('scrolledwindow4').set_visible(True)
			self.gui.get_object('vbox9').set_visible(True)
		else:
			self.gui.get_object('entry5').set_visible(False)
			self.gui.get_object('label7').set_visible(False)
			self.gui.get_object('scrolledwindow4').set_visible(False)
			self.gui.get_object('vbox9').set_visible(False)
		self.gui.get_object('button10').set_visible(True)
		self.gui.get_object('button11').set_visible(False)
		self.gui.get_object('window3').show()
		
	def hideAddWindow(self, obj, event=None):
		self.gui.get_object('window3').hide()
		return True
		
	def addChannel(self, obj):
		if len(self.gui.get_object('entry2').get_text()) < 3:
			self.on_error(_("Channel name must have at least 3 characters."))
			return
		if self.gui.get_object('notebook1').get_current_page() == 0:
			if not self.gui.get_object('liststore4').get_iter_root():
				self.on_error(_("Please add at least one URL in Channel URLs."))
				return
			urls = []
			audios = []
			params = {}
			name = self.gui.get_object('entry2').get_text()
			tvguide = self.gui.get_object('entry5').get_text()
			
			urlstore = iter = self.gui.get_object('liststore4')
			iter = urlstore.get_iter_root()
			while (iter):
				url = urlstore.get_value(iter, 0)
				urls.append(url)
				params[url] = urlstore.get_value(iter, 1)
				iter = urlstore.iter_next(iter)
			audiostore = iter = self.gui.get_object('liststore3')
			iter = audiostore.get_iter_root()
			while (iter):
				audios.append([audiostore.get_value(iter, 0), audiostore.get_value(iter, 1)])
				iter = audiostore.iter_next(iter)
			
			model = self.gui.get_object('liststore1')
			image = self.gui.get_object('image8').get_pixbuf()
			url = ';'.join(urls)
			audio = ''
			for x in audios:
				audio = audio + x[0] + ':' + x[1] + ';'
			id = re.sub(r'\W+', '', name + str(random.randint(100, 999)))
			iter = model.append([id, image, name, url, tvguide, audio])
			img = imgtools.pixbuf2Image(image)
			imgdata = imgtools.saveImage(img)
			url = json.dumps(urls)
			param = json.dumps(params)
			audio = json.dumps(audios)
			threading.Thread(target=self.imgur.upload, args=(imgdata, self.setIconURL, id)).start()
			self.db.add_tv([id, imgdata, name, url, param, tvguide, audio])
			
		else:
			if not self.gui.get_object('liststore4').get_iter_root():
				self.on_error(_("Please add at least one URL in Channel URLs."))
				return
			urls = []
			params = {}
			image = self.gui.get_object('image8').get_pixbuf()
			name = self.gui.get_object('entry2').get_text()
			id = re.sub(r'\W+', '', name + str(random.randint(100, 999)))
			urlstore = iter = self.gui.get_object('liststore4')
			iter = urlstore.get_iter_root()
			while (iter):
				url = urlstore.get_value(iter, 0)
				urls.append(url)
				params[url] = urlstore.get_value(iter, 1)
				iter = urlstore.iter_next(iter)
			url = ';'.join(urls)
			model = self.gui.get_object('liststore2')
			iter = model.append([id, image, name, url])
			img = imgtools.pixbuf2Image(image)
			imgdata = imgtools.saveImage(img)
			url = json.dumps(urls)
			param = json.dumps(params)
			self.db.add_radio([id, imgdata, name, url, param])
			threading.Thread(target=self.imgur.upload, args=(imgdata, self.setIconURL, id)).start()
		self.gui.get_object('window3').hide()
	
	def editChannel(self, obj):
		if self.gui.get_object('notebook1').get_current_page() == 0:
			treeselection = self.gui.get_object('treeview1').get_selection()
			(model, iter) = treeselection.get_selected()
			if not iter:
				return
			self.gui.get_object('liststore4').clear()
			self.gui.get_object('liststore3').clear()
			id = model.get_value(iter, 0)
			self.gui.get_object('entry2').set_text(self.db.get_tv(id, 'name'))
			channels = self.getJSON(self.db.get_tv(id, 'streamurls'))
			params = self.getJSON(self.db.get_tv(id, 'params'))
			for x in channels:
				if len(params) > 0:
					param = params[x]
				else:
					param = ''
				self.gui.get_object('liststore4').append([x, param])
			image = imgtools.data2pixbuf(self.db.get_tv(id, 'icon'))
			self.gui.get_object('image8').set_from_pixbuf(image)
			self.gui.get_object('entry5').set_text(self.db.get_tv(id, 'guide'))
			achannels = self.getJSON(self.db.get_tv(id, 'audiochannels'))
			for x in achannels:
				self.gui.get_object('liststore3').append([x[0], x[1]])
		else:
			treeselection = self.gui.get_object('treeview2').get_selection()
			(model, iter) = treeselection.get_selected()
			if not iter:
				return
			self.gui.get_object('liststore4').clear()
			self.gui.get_object('liststore3').clear()
			self.gui.get_object('entry5').set_visible(False)
			self.gui.get_object('label7').set_visible(False)
			self.gui.get_object('scrolledwindow4').set_visible(False)
			self.gui.get_object('vbox9').set_visible(False)
			id = model.get_value(iter, 0)
			self.gui.get_object('entry2').set_text(self.db.get_radio(id, 'name'))
			channels = self.getJSON(self.db.get_radio(id, 'streamurls'))
			params = self.getJSON(self.db.get_radio(id, 'params'))
			for x in channels:
				self.gui.get_object('liststore4').append([x, params[x]])
			image = imgtools.data2pixbuf(self.db.get_radio(id, 'icon'))
			self.gui.get_object('image8').set_from_pixbuf(image)
		self.gui.get_object('button10').set_visible(False)
		self.gui.get_object('button11').set_visible(True)
		self.gui.get_object('window3').show()
	
	def hideChannelEditor(self, obj, event=None):
		self.gui.get_object('window3').hide()
		return True
	
	def saveChannel(self, obj):
		if len(self.gui.get_object('entry2').get_text()) < 3:
			self.on_error(_("Channel name must have at least 3 characters."))
			return
		if self.gui.get_object('notebook1').get_current_page() == 0:
			treeselection = self.gui.get_object('treeview1').get_selection()
			(model, m_iter) = treeselection.get_selected()
			if not m_iter:
				return
			if not self.gui.get_object('liststore4').get_iter_root():
				self.on_error(_("Please add at least one URL in Channel URLs."))
				return
			urls = []
			audios = []
			params = {}
			name = self.gui.get_object('entry2').get_text()
			tvguide = self.gui.get_object('entry5').get_text()
			
			urlstore = iter = self.gui.get_object('liststore4')
			iter = urlstore.get_iter_root()
			while (iter):
				url = urlstore.get_value(iter, 0)
				urls.append(url)
				params[url] = urlstore.get_value(iter, 1)
				iter = urlstore.iter_next(iter)
			audiostore = iter = self.gui.get_object('liststore3')
			iter = audiostore.get_iter_root()
			while (iter):
				audios.append([audiostore.get_value(iter, 0), audiostore.get_value(iter, 1)])
				iter = audiostore.iter_next(iter)
			
			image = self.gui.get_object('image8').get_pixbuf()
			url = ';'.join(urls)
			audio = ''
			for x in audios:
				audio = audio + x[0] + ':' + x[1] + ';'
			id = model.get_value(m_iter, 0)
			model.set_value(m_iter, 1, image)
			model.set_value(m_iter, 2, name)
			model.set_value(m_iter, 3, url)
			model.set_value(m_iter, 4, tvguide)
			model.set_value(m_iter, 5, audio)
			img = imgtools.pixbuf2Image(image)
			imgdata = imgtools.saveImage(img)
			url = json.dumps(urls)
			audio = json.dumps(audios)
			param = json.dumps(params)
			threading.Thread(target=self.imgur.upload, args=(imgdata, self.setIconURL, id)).start()
			self.db.delete_tv(id)
			self.db.add_tv([id, imgdata, name, url, param, tvguide, audio])
		else:
			treeselection = self.gui.get_object('treeview2').get_selection()
			(model, m_iter) = treeselection.get_selected()
			if not m_iter:
				return
			if not self.gui.get_object('liststore4').get_iter_root():
				self.on_error(_("Please add at least one URL in Channel URLs."))
				return
			urls = []
			params = {}
			image = self.gui.get_object('image8').get_pixbuf()
			name = self.gui.get_object('entry2').get_text()
			urlstore = iter = self.gui.get_object('liststore4')
			iter = urlstore.get_iter_root()
			while (iter):
				url = urlstore.get_value(iter, 0)
				urls.append(url)
				params[url] = urlstore.get_value(iter, 1)
				iter = urlstore.iter_next(iter)
			url = ';'.join(urls)
			id = model.get_value(m_iter, 0)
			model = self.gui.get_object('liststore2')
			model.set_value(m_iter, 1, image)
			model.set_value(m_iter, 2, name)
			model.set_value(m_iter, 3, url)
			img = imgtools.pixbuf2Image(image)
			imgdata = imgtools.saveImage(img)
			url = json.dumps(urls)
			param = json.dumps(params)
			self.db.delete_radio(id)
			self.db.add_radio([id, imgdata, name, url, param])
			threading.Thread(target=self.imgur.upload, args=(imgdata, self.setIconURL, id)).start()
		self.gui.get_object('window3').hide()
		
	def deleteChannel(self, obj):
		if self.gui.get_object('notebook1').get_current_page() == 0:
			treeselection = self.gui.get_object('treeview1').get_selection()
			(model, iter) = treeselection.get_selected()
			if not iter:
				return
			id = model.get_value(iter, 0)
			self.db.delete_tv(id)
			model.remove(iter)
		else:
			treeselection = self.gui.get_object('treeview2').get_selection()
			(model, iter) = treeselection.get_selected()
			if not iter:
				return
			id = model.get_value(iter, 0)
			self.db.delete_radio(id)
			model.remove(iter)
	
	def uploadImage(self, obj):
		self.imageFinder.test_query = urllib2.quote(self.gui.get_object('entry2').get_text())
		self.imageFinder.searchLogos(self.gui.get_object('entry2').get_text())
		
	def setIconURL(self, url, id):
		self.icons[id[0]] = url
	
	def addChannelURL(self, obj):
		treewidget = self.gui.get_object('treeview4')
		liststore = self.gui.get_object('liststore4')
		iter = liststore.append(['', ''])
		path = liststore.get_path(iter)
		treewidget.set_cursor(path, focus_column=self.gui.get_object('treeviewcolumn12'), start_editing=True)
		
	def addChannelEdit(self, obj, path=None, text=None):
		liststore = self.gui.get_object('liststore4')
		if not path:
			iter = liststore.get_iter_root()
			while iter:
				last_iter = iter
				iter = liststore.iter_next(iter)
			liststore.remove(last_iter)
			return
		iter = liststore.get_iter(path)
		if obj == self.gui.get_object('cellrenderertext10'):
			col = 0
		elif obj == self.gui.get_object('cellrenderertext12'):
			col = 1
		if len(text) > 0:
			if col == 1:
				text = text.replace('"', '')
			liststore.set_value(iter, col, text)
		else:
			if col == 0:
				liststore.remove(iter)
		
	def removeChannelURL(self, obj):
		treeselection = self.gui.get_object('treeview4').get_selection()
		(model, iter) = treeselection.get_selected()
		if not iter:
			return
		model.remove(iter)

	def addAudio(self, obj):
		treewidget = self.gui.get_object('treeview3')
		liststore = self.gui.get_object('liststore3')
		iter = liststore.append(['', ''])
		path = liststore.get_path(iter)
		treewidget.set_cursor(path, focus_column=self.gui.get_object('treeviewcolumn10'), start_editing=True)
	
	def addAudioEdit(self, obj, path, text):
		liststore = self.gui.get_object('liststore3')
		iter = liststore.get_iter(path)
		if obj == self.gui.get_object('cellrenderertext8'):
			if len(text) > 0:
				liststore.set_value(iter, 0, text)
				treewidget = self.gui.get_object('treeview3')
				treewidget.set_cursor(path, focus_column=self.gui.get_object('treeviewcolumn11'), start_editing=True)
			else:
				liststore.remove(iter)
		elif self.gui.get_object('cellrenderertext9'):
			if len(text) > 0:
				liststore.set_value(iter, 1, text)
			else:
				liststore.remove(iter)
			
	def removeAudio(self, obj):
		treeselection = self.gui.get_object('treeview3').get_selection()
		(model, iter) = treeselection.get_selected()
		if not iter:
			return
		model.remove(iter)
	
	def on_error(self, message):
		md = gtk.MessageDialog(None, 
			gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, 
			gtk.BUTTONS_CLOSE, message)
		md.run()
		md.destroy()
		
	def on_entry2_changed(self, obj, event=None):
		if len(obj.get_text()) > 2:
			self.gui.get_object('button13').set_sensitive(True)
		else:
			self.gui.get_object('button13').set_sensitive(False)
			
	def hideLogoWin(self, obj, event=None):
		self.imageFinder.test_query = None
		self.gui.get_object('window5').hide()
		return True
	
	def main(self):
		gtk.gdk.threads_enter()
		gtk.main()
		gtk.gdk.threads_leave()
		
	def quit(self, obj=None, event=None):
		os._exit(0)
					
	def getJSON(self, string):
		try:
			return json.loads(string)
		except:
			return []
		
if __name__ == "__main__":
    	main = Main()
    	main.main()
