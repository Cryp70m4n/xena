import codecs
import sys
import base64
import gzip
import mariadb
import string


import logger


"""
	TODO:
	- Read files from db make table shared(file, folder) shared1 shared2 shared3,...
	- Add directory check(if files > limit create new one) using glob
"""
#INPUT WHITELISTS
chars = list(string.ascii_lowercase)
nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

insert_whitelist = chars+nums+["."]

class shared():
	def __init__(self):
		self.db = "xena"
		self.db_user = "root"
		self.db_password = "S3curE123#!"
		self.db_host = "127.0.0.1"
		self.db_port = 3306
		self.conn = mariadb.connect(
			user=self.db_user,
			password=self.db_password,
			host=self.db_host,
			port=self.db_port,
			database=self.db
		)
		self.cursor = self.conn.cursor()

	def read_shared(self):
		sql = "SELECT original_filename, id filename FROM shared"
		self.cursor.execute(sql)
		rows = self.cursor.fetchall()
		self.conn.commit()
		files = {}
		file_ids = {}
		for row in rows:
			files[row[0]] = row[1]
			file_ids[row[0]] = row[2]
		return [files, file_ids]

	def download_shared(self, target_file=None):
		if target_file == None:
			return "Target file cannot be none!"
		whitelist = []
		items = self.read_shared()
		items = items[0]
		for item in items:
			whitelist.append(item)
		if target_file not in whitelist:
			return "Target file couldn't be found in shared folder"
		target_file = "shared/" + target_file
		file_data = codecs.open(target_file, 'rb').read()
		compressed = gzip.compress(file_data)
		compressed_data = base64.b64encode(compressed)
		return compressed_data

	def insert_shared(self, file=None):
		filename=file[0]
		file_data=file[1]
		if filename == None or file_data == None:
			return "Target file cannot be none!"
		i = 0
		for ch in filename:
			if ch == ".":
				i+=1
			if ch not in insert_whitelist:
				return "Filename contains illegal characters!"
		if i > 1:
			return "Invalid filename!"
		#base64 gzip decompress(probably) and rb and then wb

	def __del__(self):
		self.conn.close()