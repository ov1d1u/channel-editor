import pycurl, cStringIO, base64

class Imgur:
	def __init__(self):
		self.key = '72e52d4bdd04c9dd7e057eda9ef80cbf'
		
	def upload(self, data, callback=None, *args):
		response = cStringIO.StringIO()
		c = pycurl.Curl()
		data = base64.encodestring(data)
		values = [
			  ("key", self.key),
			  ("image", data)]

		c.setopt(c.URL, "http://imgur.com/api/upload.xml")
		c.setopt(c.WRITEFUNCTION, response.write)
		c.setopt(c.HTTPPOST, values)

		c.perform()
		c.close()
		r = response.getvalue().split('<original_image>')
		rr = r[1].split('</original_image>')
		reply = rr[0]
		if callback:
			callback(reply, args)
		return reply
