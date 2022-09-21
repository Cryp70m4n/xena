#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bcrypt
import mariadb
import time
import os
import binascii
import pyaes
import base64
import inspect

import logger

"""
TODO:
    - Parse permission level from config file instead of predefining them in code
    - Parse DB data from config file
"""


class authorisation():
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
        self.iv = 100
        self.token_duration = 30*60  # 30 minutes in seconds
        logger.setup_logger('auth_logger', r'logs/auth.log')
        self.auth_logger = logger.logging.getLogger('auth_logger')
    
    def throw_error(self, error_code=5, error=None):
        log_error = "function:" + inspect.stack()[1][3] + " | " + "error_type:" + error.replace("\n", " | error:")
        match error_code:
            case 1:
                self.auth_logger.warning(log_error)
            case 2:
                self.auth_logger.debug(log_error)
            case 3:
                self.auth_logger.error(log_error)
            case 4:
                self.auth_logger.critical(log_error)
            case _:
                self.auth_logger.critical("Invalid error code supplied!")
                return "Invalid error_code supplied to function throw_error"

        return error

    def throw_success(self, success=None):
        self.auth_logger.info(success)
        return True

    def generate_hash(self, password=None):
        if password == None:
            return self.throw_error(1, "Password cannot be none!")
        try:
            password_bytes = password.encode("utf-8")
            salt = bcrypt.gensalt() 
            password_hash = bcrypt.hashpw(password_bytes, salt)
            return base64.b64encode(password_hash)
        except:
            return self.throw_error(3, "failed to generate hash")

    def check_hash(self, password=None, password_hash=None):
        if password == None or password_hash == None:
            return self.throw_error(1, "Password or password_hash cannot be none!")
        password_bytes = password.encode("utf-8")
        result = bcrypt.checkpw(password_bytes, password_hash)
        return result

    def create_session(self, usr=None):
        if usr == None:
            return self.throw_error(1, "User cannot be none!")
        key = os.urandom(32)
        generate_nonce = os.urandom(64)
        nonce = binascii.hexlify(generate_nonce)
        nonce = str(nonce)[0:][2:][:-1]
        token = usr + " " + nonce
        counter = pyaes.Counter(initial_value=self.iv)
        aes = pyaes.AESModeOfOperationCTR(key, counter=counter)
        session = aes.encrypt(token)
        get_id = "SELECT id FROM users WHERE user = ?"
        self.cursor.execute(get_id, [usr])
        rows = self.cursor.fetchall()
        self.conn.commit()
        usr_id = rows[0][0]
        sql_check = "DELETE FROM sessions WHERE user_id = ?"
        self.cursor.execute(sql_check, [usr_id])
        self.conn.commit()
        sql = "INSERT IGNORE INTO sessions(enc_key, nonce, user_id, creation_time) VALUES(?, ?, ?, ?)"
        self.cursor.execute(sql, (str(key)[0:][2:][:-1], nonce, usr_id, int(time.time()+self.token_duration)))
        self.conn.commit()
        return base64.b64encode(session)

    def user_password_authentication(self, usr=None, passwd=None):
        if usr == None or passwd == None:
            return self.throw_error(2, "User and/or Password can't be None!")
        sql = "SELECT password FROM users WHERE user = ?"
        self.cursor.execute(sql, [usr])
        rows = self.cursor.fetchall()
        self.conn.commit()
        if rows == []:
            return self.throw_error(1, "User error!\nGiven user were not found in database!")
        password_hash = base64.b64decode(rows[0][0])
        attempt = self.check_hash(passwd, password_hash)
        if attempt == True:
            user = usr
            return self.create_session(user)
        return self.throw_error(1, "Unauthorised")

    def session_authentication(self, usr=None, session=None):
        if usr == None or session == None:
            return self.throw_error(1, "User and/or sesion can't be None!")
        sql = "SELECT id FROM users WHERE user = ?"
        self.cursor.execute(sql, [usr])
        rows = self.cursor.fetchall()
        self.conn.commit()
        if rows == []:
            return self.throw_error(1, "User error!\nGiven user were not found in database!")
        usr_id = rows[0][0]
        sql2 = "SELECT enc_key, nonce, creation_time FROM sessions WHERE user_id = ?"
        self.cursor.execute(sql2, [usr_id])
        rows2 = self.cursor.fetchall()
        self.conn.commit()
        if rows2 == []:
            return self.throw_error(3, "Key error!\nKey for given ID were not found in database!")
        nonce = rows2[0][1]
        creation_timestamp = int(rows2[0][2])
        key = bytes(rows2[0][0], 'utf-8')
        key = key.decode('unicode-escape').encode('ISO-8859-1')
        counter = pyaes.Counter(initial_value=self.iv)
        aes = pyaes.AESModeOfOperationCTR(key, counter=counter)
        try:
            token = aes.decrypt(base64.b64decode(session))
        except:
            return self.throw_error(4, "Unexpected error occured while trying to decrypt your session!\nPlease try again!")
        token = str(token)[0:][2:][:-1].split(" ")
        sql_remove = "DELETE FROM sessions WHERE user_id = ?"
        try:
            token_user = token[0]
            token_nonce = token[1]
        except:
            return self.throw_error(1, "Token error!\nInvalid token!")
        if token_user != usr:
            self.cursor.execute(sql_remove, [usr_id])
            self.conn.commit()
            return self.throw_error(1, "Token error!\nInvalid user!")
        if token_nonce != nonce:
            self.cursor.execute(sql_remove, [usr_id])
            self.conn.commit()
            return self.throw_error(1, "Token error!\nInvalid nonce!")
        if int(time.time()) >= creation_timestamp:
            self.cursor.execute(sql_remove, [usr_id])
            self.conn.commit()
            return self.throw_error(1, "Token error!\nToken expired!")
        return self.throw_success("Session authorised!")

    def delete_session(self, usr=None, session=None):
        validate = self.session_authentication(usr, session)
        if  validate != True:
            return validate
        sql = "SELECT id FROM users WHERE user = ?"
        self.cursor.execute(sql, [usr])
        rows = self.cursor.fetchall()
        self.conn.commit()
        if rows == []:
            return self.throw_error(1, "User error!\nGiven user were not found in database!")
        usr_id = rows[0][0]
        sql2 = "DELETE FROM sessions WHERE user_id = ?"
        self.cursor.execute(sql2, [usr_id])
        self.conn.commit()
        return self.throw_success("Session deleted successfully!")

    def permission_level_authentication(self, usr=None, session=None):
        sql = "SELECT permission_level FROM users WHERE user = ?"
        permission_level = 0
        if self.session_authentication(usr, session) != True:
            return permission_level
        self.cursor.execute(sql, [usr])
        rows = self.cursor.fetchall()
        self.conn.commit()
        permission_level = int(rows[0][0])
        return permission_level

    def token_timestamp_check(self):
        sql = "SELECT user_id, creation_time FROM sessions"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        self.conn.commit()
        sql_remove = "DELETE FROM sessions WHERE user_id = ?"
        for row in rows:
            current_time = int(time.time())
            token_timestamp = int(row[1])
            if current_time >= token_timestamp:
                self.cursor.execute(sql_remove, [row[0]])
                self.conn.commit()
        return self.throw_success("Check completed!")

    def __del__(self):
        self.conn.close()


class authorisation_api_calls():
    def __init__(self):
        self.db = "xena.db"
        self.conn = sqlite3.connect(self.db)
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

    def __del__(self):
        self.conn.close()