#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

pip = ""
res = os.system("pip --version")
if res == 0:
    pip = "pip"

res2 = os.system("pip3 --version")
if res2 == 0:
    pip = "pip3"

else:
    print("Please install pip and run setup again in order to run Xena")
    exit()

if "hashlib" not in sys.modules:
    os.system(f"{pip} install hashlib")
if "pycryptodome" not in sys.modules:
    os.system(f"{pip} install pycryptodome")
if "flask" not in sys.modules:
    os.system(f"{pip} install flask")
if "gevent" not in sys.modules:
    os.system(f"{pip} install gevent")

try:
    os.system("CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user VARCHAR(24) UNIQUE NOT NULL, password VARCHAR(128) NOT NULL, permission_level TINYINT NOT NULL);CREATE TABLE sessions(key VARCHAR(32) UNIQUE NOT NULL, nonce VARCHAR(128) UNIQUE NOT NULL, user_id INTEGER UNIQUE NOT NULL, creation_time INTEGER NOT NULL);'")
except:
    print("Please install sqlite3 and run setup again in order to run Xena")
