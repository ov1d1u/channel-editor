import pycurl, cStringIO, base64, json

class Imgur:
	def __init__(self):
		self.key = 'ee511d09eedef3d'
		
	def upload(self, data, callback=None, *args):
		response = cStringIO.StringIO()
		c = pycurl.Curl()
		data = base64.encodestring(data)
		values = [
			  ("image", data)
		]

		c.setopt(c.URL, "https://api.imgur.com/3/image")
		c.setopt(c.WRITEFUNCTION, response.write)
		c.setopt(c.HTTPHEADER, ["Authorization: Client-ID {0}".format(self.key)])
		c.setopt(c.HTTPPOST, values)

		c.perform()
		c.close()
		r_dict = json.loads(response.getvalue())
		if callback:
			callback(reply, args)
		return r_dict["link"]
