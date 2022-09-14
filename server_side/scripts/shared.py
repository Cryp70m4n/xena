import subprocess
import codecs
import sys
import base64
import gzip

import logger

class shared():
	def read_shared():
		output = output = subprocess.check_output("ls shared", shell=True)
		return output

	def download_shared(target_file=None):
		if target_file == None:
			return "Target file cannot be none!"
		white_list = subprocess.check_output(["ls", "shared"]).decode(sys.stdout.encoding).split("\n") #BEEN LAZY TO SPEND TOO MUCH TIME ON GETTING read_shared() FUNCTION TO WORK HERE SO I JUST DECIDED TO LEAVE IT LIKE THIS
		if '' in white_list:
			white_list.remove('') #THIS IF IS JUST TO MAKE IT FAIL SAFE IN CASE SUBPROCESS ADDS '' INTO LIST I WAS TOO LAZY TO SOLVE IT PROPERLY
		if target_file not in white_list:
			return "Target file couldn't be found in shared folder"
		target_file = "shared/" + target_file
		file_data = codecs.open(target_file, 'rb').read()
		compressed = gzip.compress(file_data)
		compressed_data = base64.b64encode(compressed)
		return compressed_data