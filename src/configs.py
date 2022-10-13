class config_parser():
    def __init__(self):
        self.config_syntax = ["//"]
        self.setup_syntax = ["db", "db_user", "db_password", "db_host", "db_port"]
        self.permissions_syntax = ["admin", "create_account", "delete_account", "change_password", "create_vault", "delete_vault", "change_permission_level", "get_users", "get_vaults"]

    def setup_config_parser(self, setup_config_file=None):
        if setup_config_file == None:
            return "You must provide setup config file path as function parameter!"
        setup_configs = {}
        try:
            with open(setup_config_file, "r") as setup_cfg_file:
                lines = setup_cfg_file.readlines()
                for line in lines:
                    if len(line) < 2:
                        continue
                    comment_check=line[0]
                    comment_check+=line[1]
                    if comment_check == "//":
                        continue
                    last_ind = 0
                    token = ""
                    for char in line:
                        if char != "=":
                            if char != " ":
                                token += char
                                last_ind += 1
                        else:
                            break
                    if token not in self.setup_syntax:
                        return "Invalid config syntax!"
                    value = ""
                    equals = False
                    cnt = 0
                    while last_ind < len(line):
                        space_line = False
                        if line[last_ind] == '"':
                            cnt+=1
                            last_ind+=1
                        if line[last_ind] == " ":
                            last_ind+=1
                            space_line = True
                        if line[last_ind] == "=":
                            last_ind+=1
                            equals = True
                        if equals == True and space_line == False:
                            value+=line[last_ind]
                            last_ind+=1

                    if cnt != 2 and cnt > 0:
                        return 'Missing "" for string specification inside setup config file!'
                    if cnt == 0:
                        try:
                            int(value)
                        except:
                            return "Invalid setup config syntax!"
                        value = value.replace("\n", "")
                        setup_configs[token] = int(value)
                    if cnt == 2:    
                        value = value.replace('"', "")
                        value = value.replace("\n", "")
                        setup_configs[token] = value
                    
        except:
            return "Invalid setup config file path!"
        
        return setup_configs

    def permission_config_parser(self, permissions_config_file=None):
        if permissions_config_file == None:
            return "You must provide permission config file path as function parameter!"
        permission_configs = {}
        try:
            with open(permissions_config_file, "r") as perm_cfg_file:
                lines = perm_cfg_file.readlines()
                for line in lines:
                    if len(line) < 2:
                        continue
                    comment_check=line[0]
                    comment_check+=line[1]
                    if comment_check == "//":
                        continue
                    last_ind = 0
                    token = ""
                    for char in line:
                        if char != "=":
                            if char != " ":
                                token += char
                                last_ind += 1
                        else:
                            break
                    if token not in self.permissions_syntax:
                        return "Invalid config syntax!"
                    value = ""
                    equals = False
                    cnt = 0
                    while last_ind < len(line):
                        space_line = False
                        if line[last_ind] == " ":
                            last_ind+=1
                            space_line = True
                        if line[last_ind] == "=":
                            last_ind+=1
                            equals = True
                        if equals == True and space_line == False:
                            value+=line[last_ind]
                            last_ind+=1

                    try:
                        int(value)
                    except:
                        return "Invalid setup config syntax!"
                    value = value.replace("\n", "")
                    permission_configs[token] = int(value)
        except:
            return "Invalid permission config file path!"

        return permission_configs

class config_editor():
    def __init__(self):
        self.a = "b"

    def setup_config_editor(self, setup_config_file=None):
        if setup_config_file == None:
            return "You must provide setup config file path as function parameter!"
        try:
            with open(setup_config_file, "w") as setup_cfg_file:
                print("a")
        except:
            return "Invalid setup config file path!"

    def permission_config_parser(self, permission_config_file=None):
        if permission_config_file == None:
            return "You must provide permission config file path as function parameter!"
        try:
            with open(permission_config_file, "w") as perm_cfg_file:
                print("a")
        except:
            return "Invalid permission config file path!"