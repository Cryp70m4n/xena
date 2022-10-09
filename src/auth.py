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
import string

import logger
import configs


class authorisation():
    def __init__(self):
        self.configs = configs.config_parser()
        self.setup_configs = self.configs.setup_config_parser("configs/setup.cfg")
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