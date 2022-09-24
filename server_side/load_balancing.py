import glob
import string

chars = list(string.ascii_lowercase)
nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


class directory_balancing_controller():
	def direcotry_controller(self, target_dir=None):
		if target_dir == None:
			return "Target directory cannot be None!"
		directory_name_whitelist = chars+nums+["/"]
		for ch in target_dir:
			if ch not in directory_name_whitelist:
				return "Invalid directory name"
		target_dir = target_dir+"/*"
		files = glob.glob(target_dir)
		amount = 0
		for file in files:
			amount+=1
		return amount