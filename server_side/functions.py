import string
import mariadb
from auth import authorisation

class functions():
    def __init__(self):
        self.auth = authorisation()
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
        self.allowed_characters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
                                   'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.auth = authorisation()

    def input_validation(self, usr_input=None):
        for char in usr_input:
            if char not in self.allowed_characters:
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
        passwd_check = self.input_validation(passwd)
        if passwd_check != True:
            return self.auth.throw_error(1, "Input error!\nPassword contains characters which aren't allowed!")
        usr_check = self.input_validation(usr)
        if usr_check != True:
            return self.auth.throw_error(1, "Input error!\nUser contains characters which aren't allowed!")
        required_permission_level = 3
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
        if usr_exist_check[0][0] != True:
            return self.auth.throw_error(1, "Database error!\nUser already exists in database!")
        password = self.generate_hash(passwd)
        self.cursor.execute(sql, (usr, password, perm_lvl))
        self.conn.commit()
        return self.auth.throw_success("Account created successfully!")

    def delete_account(self, caller_usr=None, caller_session=None, usr=None):
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        if usr == None:
            return self.auth.throw_error(2, "Argument error!\nUser cannot be None!")
        required_permission_level = 3
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
        passwd_check = self.input_validation(passwd)
        if passwd_check != True:
            return self.auth.throw_error(1, "Input error!\nPassword contains characters which aren't allowed!")
        if usr != None:
            usr_check = self.input_validation(usr)
            if usr_check != True:
                return self.auth.throw_error(1, "Input error\nUser contains characters which aren't allowed!")
        required_permission_level = 3
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
            password = self.generate_hash(passwd)
            sql = "UPDATE users SET password = ? WHERE user = ?"
            self.cursor.execute(sql, (password, usr))
            self.conn.commit()
        if usr == None and passwd != None:
            password = self.generate_hash(passwd)
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
        required_permission_level = 3
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
        required_permission_level = 4
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
        required_permission_level = 3
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
        return self.auth.throw_success("Vault created successfully!")

    def delete_vault(self, caller_usr=None, caller_session=None, vault_name=None, vault_owner=None):
        if vault_name == None or vault_owner == None:
            return self.auth.throw_error(2, "Vault name or vault owner cannot be None!")
        if self.auth.session_authentication(caller_usr, caller_session) != True:
            return self.auth.throw_error(2, "Session error!\nInvalid session!")
        required_permission_level = 3
        caller_permission_level = self.auth.permission_level_authentication(caller_usr, caller_session)
        if caller_permission_level < required_permission_level:
            return self.auth.throw_error(3, "You are not authorised to delete vault of other users!")
        users = self.get_users(caller_usr, caller_session)
        if vault_owner not in users:
            return self.auth.throw_error(2, "User not found in database!")
        sql = "DELETE FROM vaults WHERE vault_name=? AND vault_owner=?"
        self.cursor.execute(sql, [vault_name, vault_owner])
        self.conn.commit()
        return self.auth.throw_success("Vault deleted successfully!")

    def __del__(self):
        self.conn.close()