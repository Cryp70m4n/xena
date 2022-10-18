import string
import mariadb
import os
import glob
import codecs
import base64

from auth import authorisation
import configs



"""
    TODO:
        - COULD ADD RSA ENCRYPTION TO FILES IN FUTURE
"""

class admin_functions():
    def __init__(self):
        self.configs = configs.config_parser()
        self.setup_configs = self.configs.setup_config_parser("configs/setup.cfg")
        self.permission_configs = self.configs.permission_config_parser("configs/permissions.cfg")
        self.db = self.setup_configs["db"]
        self.db_user = self.setup_configs["db_user"]
        self.db_password = self.setup_configs["db_password"]
        self.db_host = self.setup_configs["db_host"]
        self.db_port = self.setup_configs["db_port"]
        self.conn = mariadb.connect(
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db
        )
        self.cursor = self.conn.cursor()
        self.allowed_characters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
                                   'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.allowed_password_characters = self.allowed_characters + list(string.ascii_uppercase) + ['#', '!', '@', '?', '^', '$']
        self.auth = authorisation()

    def input_validation(self, usr_input=None):
        for char in usr_input:
            if char not in self.allowed_characters:
                return self.auth.throw_error(1, "Your input contains charaters which are not allowed to be used!\nPlease try again!")
        return self.auth.throw_success("Input authorised!")
    
    def password_input_validation(self, usr_input=None):
        for char in usr_input:
            if char not in self.allowed_password_characters:
                return self.auth.throw_error(1, "Your input contains charaters which are not allowed to be used!\nPlease try again!")
        return self.auth.throw_success("Input authorised!")

    def create_account(self, caller_usr=None, caller_session=None, usr=None, passwd=None, perm_lvl=None):
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        if passwd == None:
            return self.auth.throw_error(2, "Argument error!\nPassword cannot be None!")
        if usr == None:
            return self.auth.throw_error(2, "Argument error!\nUser cannot be None!")
        if perm_lvl == None:
            return self.auth.throw_error(2, "Argument error!\nPermission level cannot be None!")
        passwd_check = self.password_input_validation(passwd)
        if passwd_check != True:
            return self.auth.throw_error(1, "Input error!\nPassword contains characters which aren't allowed!")
        usr_check = self.input_validation(usr)
        if usr_check != True:
            return self.auth.throw_error(1, "Input error!\nUser contains characters which aren't allowed!")
        required_permission_level = self.permission_configs["create_account"]
        caller_permission_level = self.auth.permission_level_authentication(caller_usr, caller_session)
        if caller_permission_level < required_permission_level:
            return self.auth.throw_error(3, "You are not authorised to create new accounts!")
        sql = "INSERT IGNORE INTO users(user, password, permission_level) VALUES(?, ?, ?)"
        try:
            perm_lvl = int(perm_lvl)
        except:
            return self.auth.throw_error(2, "Argument error!\nPermission level must be an number between 1 and 4!")
        if perm_lvl > 4 or perm_lvl < 1:
            return self.auth.throw_error(2, "Argument error!\nPermission level must be an number between 1 and 4!")
        if caller_permission_level < perm_lvl:
            return self.auth.throw_error(3, "You can't assign permission level that is bigger than your current permission level!")
        usr_check_sql = "SELECT EXISTS(SELECT user FROM users WHERE user = ?)"
        self.cursor.execute(usr_check_sql, [usr])
        usr_exist_check = self.cursor.fetchall()
        self.conn.commit()
        if usr_exist_check[0][0] != 0:
            return self.auth.throw_error(1, "Database error!\nUser already exists in database!")
        password = self.auth.generate_hash(passwd)
        self.cursor.execute(sql, (usr, password, perm_lvl))
        self.conn.commit()
        return self.auth.throw_success("Account created successfully!")

    def delete_account(self, caller_usr=None, caller_session=None, usr=None):
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        if usr == None:
            return self.auth.throw_error(2, "Argument error!\nUser cannot be None!")
        required_permission_level = self.permission_configs["delete_account"]
        caller_permission_level = self.auth.permission_level_authentication(caller_usr, caller_session)
        get_perm_lvl = "SELECT permission_level FROM users WHERE user = ?"
        usr_execute = self.cursor.execute(get_perm_lvl, [usr])
        usr_fetch = self.cursor.fetchall()
        self.conn.commit()
        if usr_fetch == []:
            return self.auth.throw_error(1, "User were not found in database!")
        usr_permission_level = int(usr_fetch[0][0])
        if caller_permission_level < required_permission_level:
            return self.auth.throw_error(3, "You are not authorised to delete accounts!")
        if caller_permission_level <= usr_permission_level:
            return self.auth.throw_error(3, "You can't delete acount that has permission level that is bigger than or equal to your current permission level!")
        sql = "DELETE FROM users WHERE user = ?"
        self.cursor.execute(sql, [usr])
        self.conn.commit()
        return self.auth.throw_success("Account deleted successfully!")

    def change_password(self, caller_usr=None, caller_session=None, passwd=None, usr=None):
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        if passwd == None:
            return self.auth.throw_error(2, "Argument error!\nPassword cannot be None!")
        passwd_check = self.password_input_validation(passwd)
        if passwd_check != True:
            return self.auth.throw_error(1, "Input error!\nPassword contains characters which aren't allowed!")
        if usr != None:
            usr_check = self.input_validation(usr)
            if usr_check != True:
                return self.auth.throw_error(1, "Input error\nUser contains characters which aren't allowed!")
        required_permission_level = self.permission_configs["change_password"]
        caller_permission_level = self.auth.permission_level_authentication(caller_usr, caller_session)
        if usr != None and passwd != None:
            get_perm_lvl = "SELECT permission_level FROM users WHERE user = ?"
            usr_execute = self.cursor.execute(get_perm_lvl, [usr])
            usr_fetch = self.cursor.fetchall()
            self.conn.commit()
            if usr_fetch == []:
                return self.auth.throw_error(1, "User were not found in database!")
            usr_permission_level = int(usr_fetch[0][0])
            if caller_permission_level < required_permission_level:
                return self.auth.throw_error(3, "You are not authorised to change password to other users!")
            if caller_permission_level <= usr_permission_level:
                return self.auth.throw_error(3, "You can't change password of accounts that has higher or equal permission that you have!")
            password = self.auth.generate_hash(passwd)
            sql = "UPDATE users SET password = ? WHERE user = ?"
            self.cursor.execute(sql, (password, usr))
            self.conn.commit()
        if usr == None and passwd != None:
            password = self.auth.generate_hash(passwd)
            sql = "UPDATE users SET password = ? WHERE user = ?"
            self.cursor.execute(sql, (password, caller_usr))
            self.conn.commit()
        if usr == None and passwd == None:
            return self.auth.throw_error(2, "You must provide at least password in order to change password!")
        return self.auth.throw_success("Password changed successfully!")

    def change_permission_level(self, caller_usr=None, caller_session=None, usr=None, perm_lvl=0):
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        if usr == None:
            return self.auth.throw_error(2, "Argument error!\nUser cannot be None!")
        try:
            permission_level = int(perm_lvl)
        except:
            return self.auth.throw_error(2, "Argument error!\nPermision level must be an number between 1 and 4!")
        usr_check = self.input_validation(usr)
        if usr_check != True:
            return self.auth.throw_error(1, "Input error\nUser contains characters which aren't allowed!")
        if permission_level > 4 or permission_level < 1:
            return self.auth.throw_error(2, "Argument error!\nPermission level must be an number between 1 and 4!")
        required_permission_level = self.permission_configs["change_permission_level"]
        caller_permission_level = self.auth.permission_level_authentication(caller_usr, caller_session)
        get_perm_lvl = "SELECT permission_level FROM users WHERE user = ?"
        usr_execute = self.cursor.execute(get_perm_lvl, [usr])
        usr_fetch = self.cursor.fetchall()
        self.conn.commit()
        if usr_fetch == []:
            return self.auth.throw_error(1, "User were not found in database!")
        usr_permission_level = int(usr_fetch[0][0])
        if caller_permission_level < required_permission_level:
            return self.auth.throw_error(3, "You are not authorised to change permission level to other users!")
        if caller_permission_level <= usr_permission_level:
            return self.auth.throw_error(3, "You can't change permission level of accounts that has higher or equal permission that you have!")
        sql = "UPDATE users SET permission_level = ? WHERE user = ?"
        self.cursor.execute(sql, (permission_level, usr))
        self.conn.commit()
        return self.auth.throw_success("Permission level changed successfully!")

    def get_users(self, caller_usr=None, caller_session=None):
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        required_permission_level = self.permission_configs["get_users"]
        caller_permission_level = self.auth.permission_level_authentication(caller_usr, caller_session)
        if caller_permission_level < required_permission_level:
            return self.auth.throw_error(3, "You are not authorised to change password to other users!")
        self.cursor.execute("SELECT user FROM users")
        rows = self.cursor.fetchall()
        self.conn.commit()
        users = []
        for row in rows:
            users.append(row[0])
        return users

    def create_vault(self, caller_usr=None, caller_session=None, vault_name=None, vault_owner=None):
        if vault_name == None or vault_owner == None:
            return self.auth.throw_error(2, "Vault name or vault owner cannot be None!")
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        required_permission_level = self.permission_configs["create_vault"]
        caller_permission_level = self.auth.permission_level_authentication(caller_usr, caller_session)
        if caller_permission_level < required_permission_level:
            return self.auth.throw_error(3, "You are not authorised to create vault for users!")
        users = self.get_users(caller_usr, caller_session)
        if vault_owner not in users:
            return self.auth.throw_error(2, "User not found in database!")
        chars = list(string.ascii_lowercase)
        nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        vault_name_whitelist = chars+nums
        for char in vault_name:
            if char not in vault_name_whitelist:
                return self.auth.throw_error(2, "Vault name contains illegal characters!")
        sql = "INSERT IGNORE INTO vaults(vault_name, vault_owner) VALUES(?, ?)"
        self.cursor.execute(sql, [vault_name, vault_owner])
        self.conn.commit()
        cmd = f"mkdir vaults/{vault_owner}/{vault_name}"
        os.system(cmd)
        return self.auth.throw_success("Vault created successfully!")

    def delete_vault(self, caller_usr=None, caller_session=None, vault_name=None, vault_owner=None):
        if vault_name == None or vault_owner == None:
            return self.auth.throw_error(2, "Vault name or vault owner cannot be None!")
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        required_permission_level = self.permission_configs["delete_vault"]
        caller_permission_level = self.auth.permission_level_authentication(caller_usr, caller_session)
        if caller_permission_level < required_permission_level:
            return self.auth.throw_error(3, "You are not authorised to delete vault of other users!")
        users = self.get_users(caller_usr, caller_session)
        if vault_owner not in users:
            return self.auth.throw_error(2, "User not found in database!")
        sql = "DELETE FROM vaults WHERE vault_name=? AND vault_owner=?"
        self.cursor.execute(sql, [vault_name, vault_owner])
        self.conn.commit()
        cmd = f"shred -uzvn3 vaults/{vault_owner}/{vault_name}/*"
        os.system(cmd)
        cmd2 = f"rm -rf vaults/{vault_onwer}/{vault_name}"
        os.system(cmd2)
        return self.auth.throw_success("Vault deleted successfully!")


    def get_vaults(self, caller_usr=None, caller_session=None, target_usr=None):
        if caller_usr==None or caller_session==None or target_usr==None:
            return self.auth.throw_error(2, "Invalid data!")
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        required_permission_level = self.permission_configs["get_vaults"]
        caller_permission_level = self.auth.permission_level_authentication(caller_usr, caller_session)
        if caller_permission_level < required_permission_level and caller_usr != target_usr:
            return self.auth.throw_error(3, "You are not authorised to read others vaults!")
        sql = "SELECT vault_name FROM vaults WHERE vault_owner = ?"
        self.cursor.execute(sql, [target_usr])
        rows = self.cursor.fetchall()
        self.conn.commit()
        vaults = []
        for row in rows:
            vaults.append(row[0])
        return vaults
    
    def read_vault(self, caller_usr=None, caller_session=None, target_vault=None):
        if caller_usr==None or caller_session==None or target_vault==None:
            return self.auth.throw_error(2, "Invalid data!")
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        sql = "SELECT vault_name FROM vaults WHERE vault_owner = ?"
        self.cursor.execute(sql, [caller_usr])
        rows = self.cursor.fetchall()
        self.conn.commit()
        vaults = []
        for row in rows:
            vaults.append(row[0])
        if target_vault not in vaults:
            self.auth.throw_error(2, "Vault you are looking for doesn't exist!")
        vault_path = f"vaults/{caller_usr}/{target_vault}/*"
        files = glob.glob(vault_path)
        return files
    
    def insert_into_vault(self, caller_usr=None, caller_session=None, target_vault=None, file_data_b64=None, filename=None):
        if caller_usr == None or caller_session == None or target_vault == None or file_data_b64 == None or filename == None:
            return self.auth.throw_error(2, "Invalid data!")
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        files = self.read_vault(caller_usr, caller_session, target_vault)
        if filename in files:
            self.auth.throw_error(2, "Filename already exist in vault!")
        path = f"vaults/{caller_usr}/{target_vault}"
        fname = path + filename
        file_data = base64.b64decode(file_data_b64)
        with codecs.open(fname, "wb") as f:
            f.write(file_data)
        return self.auth.throw_success("File added successfully!")

    def delete_from_vault(self, caller_usr=None, caller_session=None, target_vault=None, filename=None):
        if caller_usr == None or caller_session == None or target_vault == None or filename == None:
            return self.auth.throw_error(2, "Invalid data!")
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        files = self.read_vault(caller_usr, caller_session, target_vault)
        if filename not in files:
            self.auth.throw_error(2, "Filename doesn't exist in vault!")
        path = f"vaults/{caller_usr}/{target_vault}"
        fname = path + filename
        cmd = f"rm -rf {fname}"
        os.system(cmd)
        self.auth.throw_success("File deleted successfully!")
    
    def get_from_vault(self, caller_usr=None, caller_session=None, target_vault=None, filename=None):
        if caller_usr == None or caller_session == None or target_vault == None or filename == None:
            return self.auth.throw_error(2, "Invalid data!")
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        files = self.read_vault(caller_usr, caller_session, target_vault)
        if filename not in files:
            self.auth.throw_error(2, "Filename doesn't exist in vault!")
        path = f"vaults/{caller_usr}/{target_vault}"
        fname = path + filename
        file_data = codecs.open(fname, "rb").read()
        file_data_b64 = base64.b64encode(file_data)
        return file_data_b64
    
    def delete_from_vault(self, caller_usr=None, caller_session=None, target_vault=None, target_file=None):
        if caller_usr==None or caller_session==None or target_vault==None or target_file==None:
            return self.auth.throw_error(2, "Invalid data!")
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        files = self.read_vault(caller_usr, caller_session, target_vault)
        if files == False:
            return self.auth.throw_error(3, "Invalid vault data!")
        if target_file not in files:
            return self.auth.throw_error(2, "Target file cannot be found inside specified vault!")
        cmd = f"shred -uzvn3 vaults/{caller_usr}/{target_vault}/{target_file}"
        os.system(cmd)
        return self.auth.throw_success("File have been deleted from your vault successfully!")
    def __del__(self):
        self.conn.close()