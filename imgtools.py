import Image, StringIO, base64, gtk

def data2pixbuf(strdata, b64 = True):
	if b64:
		imgdata = base64.b64decode(strdata)
	else:
		imgdata = strdata
	buff = StringIO.StringIO(imgdata)
	im = Image.open(buff)
	image = Image2pixbuf(im)
	buff.close()
	return image
	
def thumbnail(pixbuf, size=(24, 24)):
	bg = Image.new('RGBA',size)
	im = pixbuf2Image(pixbuf)
	im.thumbnail(size, Image.ANTIALIAS)
	logo_w,logo_h = im.size
	offset=((size[0]-logo_w)/2,(size[1]-logo_h)/2)
	bg.paste(im, offset)
	return Image2pixbuf(bg)
	
def Image2pixbuf(image):
	file = StringIO.StringIO()
	image.save(file, 'png')
	contents = file.getvalue()
	file.close()
	loader = gtk.gdk.PixbufLoader ('png')
	loader.write (contents, len (contents))
	pixbuf = loader.get_pixbuf()
	loader.close()
	return pixbuf
	
def pixbuf2Image(pb):
	assert(pb.get_colorspace() == gtk.gdk.COLORSPACE_RGB)
	dimensions = pb.get_width(), pb.get_height()
	stride = pb.get_rowstride()
	pixels = pb.get_pixels()
	mode = pb.get_has_alpha() and "RGBA" or "RGB"
	return Image.frombuffer(mode, dimensions, pixels,
				"raw", mode, stride, 1)

def saveImage(img, format = "PNG"):
	buf = StringIO.StringIO()
	img.save(buf, format)
	val = buf.getvalue()
	buf.close()
	return val
