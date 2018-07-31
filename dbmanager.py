# -*- coding: utf-8 -*-
import os, sqlite3, base64, shutil

class DBManager:
	def __init__(self, dbfile):
		self.conn = sqlite3.connect(dbfile)
		self.conn.row_factory = sqlite3.Row
		self.conn.text_factory = str
		self.data = self.conn.cursor()
		self.tables = {
			'tv_channels' : {'id' : str, 'icon' : str, 'name' : str, 'streamurls' : list, 'params' : dict, 'guide' : str, 'audiochannels' : list},
			'info' : {'name' : str, 'version' : str, 'author' : str, 'url' : str, 'epgurl' : str},
			'radio_channels' : {'id' : str, 'icon' : str, 'name' : str, 'streamurls' : list, 'params' : dict}
		}
		
	def open(self, dbfile):
		self.data.close()
		olddb = sqlite3.connect(dbfile)
		self.conn = sqlite3.connect(':memory:')
		self.conn.row_factory = sqlite3.Row
		self.conn.text_factory = str
		self.data = self.conn.cursor()
		query = "".join(line for line in olddb.iterdump())
		self.conn.executescript(query)
		self.conn.commit()
		self.fix()
		
	def build(self):
		self.data.execute("CREATE TABLE IF NOT EXISTS tv_channels (id, icon, name, streamurls, params, guide, audiochannels)")
		self.data.execute("CREATE TABLE IF NOT EXISTS info (name, version, author, url, epgurl)")
		self.data.execute("CREATE TABLE IF NOT EXISTS radio_channels (id, icon, name, streamurls, params)")
		self.conn.commit()
		
	def fix(self):
		import json
		for table in self.tables:
			for col in self.tables[table]:
				try:
					self.data.execute('ALTER TABLE `'+table+'` ADD COLUMN `'+col+'`')
					print _("Missing column", col + ", creating...")
				except Exception, e:
					pass
		for table in self.tables:
			if table == 'info':
				continue
			self.data.execute("SELECT * FROM `"+table+"`")
			channels = self.data.fetchall()
			for channel in channels:
				for col in self.tables[table]:
					if self.tables[table][col] == list:
						try:
							row = json.loads(channel[col])
						except:
							row = None
						if self.tables[table][col] != type(row):
							print _('Invalid data type for '+col+' in '+table+', fixing...')
							self.data.execute("UPDATE `"+table+"` SET "+col+"=? WHERE id=?", ['[]', row['id']])
					if self.tables[table][col] == dict:
						try:
							row = json.loads(channel[col])
						except:
							row = None
						if self.tables[table][col] != type(row):
							print _("Invalid data type for "+col+" in "+table+", fixing...")
							params = {}
							for url in json.loads(channel['streamurls']):
								params[url] = ''
							self.data.execute("UPDATE `"+table+"` SET "+col+"=? WHERE id=?", [json.dumps(params), channel['id']])
		self.conn.commit()
	
	def set_info(self, **args):
		self.data.execute("DELETE FROM info")
		name = 'name' in args and args['name'] or ''
		version = 'version' in args and args['version'] or '0.01'
		author = 'author' in args and args['author'] or 'Unknown'
		url = 'url' in args and args['url'] or ''
		epgurl = 'epgurl' in args and args['epgurl'] or ''
		self.data.execute("INSERT INTO info VALUES (?, ?, ?, ?, ?)", [name, version, author, url, epgurl])
		self.conn.commit()
		
	def get_info(self):
		self.data.execute("SELECT * FROM info")
		r = self.data.fetchone()
		return r
	
	def add_tv(self, row):
		self.data.execute("INSERT INTO tv_channels VALUES (?,?,?,?,?,?,?)", [row[0], base64.b64encode(row[1]), row[2], row[3], row[4], row[5], row[6]])
		self.conn.commit()
	
	def add_radio(self, row):
		self.data.execute("INSERT INTO radio_channels VALUES (?,?,?,?,?)", [row[0], base64.b64encode(row[1]), row[2], row[3], row[4]])
		self.conn.commit()
		
	def update_tv(self, id, col, val):
		self.data.execute("UPDATE tv_channels SET "+col+"=? WHERE id=?", [val, id])
		self.conn.commit()
		
	def update_radio(self, id, col, val):
		self.data.execute("UPDATE radio_channels SET "+col+"=? WHERE id=?", [val, id])
		self.conn.commit()
		
	def get_tv(self, id, col):
		self.data.execute("SELECT * FROM tv_channels WHERE id=?", (id,))
		r = self.data.fetchone()
		return r[col]
		
	def get_radio(self, id, col):
		self.data.execute("SELECT * FROM radio_channels WHERE id=?", (id,))
		r = self.data.fetchone()
		return r[col]
	
	def get_all_tv(self):
		self.data.execute("SELECT * FROM tv_channels ORDER BY name")
		return self.data
		
	def get_all_radio(self):
		self.data.execute("SELECT * FROM radio_channels ORDER BY name")
		return self.data
		
	def delete_tv(self, id):
		self.data.execute("DELETE FROM tv_channels WHERE id=?", (id, ))
		self.conn.commit()
	
	def delete_radio(self, id):
		self.data.execute("DELETE FROM radio_channels WHERE id=?", (id, ))
		self.conn.commit()
		
	def save(self, filename):
		self.data.close()
		if os.path.exists(filename):
			os.remove(filename)
		newdb = sqlite3.connect(filename)
		query = "".join(line for line in self.conn.iterdump())
		newdb.executescript(query)
		newdb.commit()
		self.open(filename)
		return True
