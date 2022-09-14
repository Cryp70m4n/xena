from scripts.qrcode import qrcode
import gzip
import codecs
import base64

qr = qrcode()

qr_data = qr.generate_qrcode("crnicerak.com")
print(qr_data)
file = "qr_test.png"
data = gzip.decompress(base64.b64decode(qr_data))
print(qr.qrcode_to_string(data))
