
class config_parser():
    def __init__(self):


    def setup_config(self, setup_config_file=None):
        if setup_config_file == None:
            return "You must provide setup config file path as function parameter!"
        try:
            with open(setup_config_file, "r") as setup_cfg_file:
                lines = readlines()
                for line in lines:
                    print(line)
        except:
            return "Invalid setup config file path!"

    def permission_config(self, permission_config_file=None):
        if permission_config_file == None:
            return "You must provide permission config file path as function parameter!"
        try:
            with open(permission_config_file, "r") as perm_cfg_file:
                lines = readlines()
                for line in lines:
                    print(line)
        except:
            return "Invalid permission config file path!"    