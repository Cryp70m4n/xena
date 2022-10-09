import pyqrcode
from pyzbar.pyzbar import decode
from PIL import Image
import uuid
import codecs
import gzip
import base64

class qrcode:
	def generate_qrcode(self, text=None):
		if text == None:
			return "Text cannot be none"
		qr = pyqrcode.create(text)
		nonce = uuid.uuid4().hex
		qr_output_img = "/tmp/" + nonce + ".png"
		qr.png(qr_output_img, scale=6)

		file_data = codecs.open(qr_output_img, 'rb').read()
		compressed = gzip.compress(file_data)
		compressed_data = base64.b64encode(compressed)
		return compressed_data

	def qrcode_to_string(self, qrcode_image_data):
		if qrcode_image_data == None:
			return "You must provide an image of QR code"
		nonce = uuid.uuid4().hex
		qr_img_path = "/tmp/" + nonce + ".png"
		with codecs.open(qr_img_path, "wb") as f:
			f.write(qrcode_image_data)
		try:
			decocdeQR = decode(Image.open(qr_img_path))
			string = decocdeQR[0].data.decode('ascii')
			return string
		except:
			return "QRcode error!"