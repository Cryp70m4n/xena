from flask import Flask, request, jsonify, render_template, redirect
from gevent.pywsgi import WSGIServer
from auth import authorisation
import binascii
import string
import json
import threading


import logger
from scripts.shared import shared

"""
TODO:
    - Switch to DJANGO or FASTAPI
    - FIX RACE CONDITION IF TOKEN TIMESTAMP CHECK THREAD RUNS IN THE SAME TIME WHEN SOMETHING IS WRITTEN OR READ FROM DB SEG FAULT WILL HAPPEN
"""

def log_info(request=None):
    logger.setup_logger('api_logger', r'logs/api.log')
    api_logger = logger.logging.getLogger('api_logger')
    if request == None:
        api_logger.error("Request was None")
        return 1

    ip = request.remote_addr
    data = request.json
    data = jsonify(data)
    data = str(data.json)
    api_logger.info(ip + "|" + data + "|" + request.method)
    return 0

auth = authorisation()

#token checking/cleaning
def check_tokens():
    threading.Timer(5.0, check_tokens).start()
    print("works")
    auth.token_timestamp_check()
check_tokens()
print("aaa")

ip = "127.0.0.1"
port = 4334
app = Flask(__name__, template_folder='templates')


#INPUT WHITELISTS
chars = list(string.ascii_lowercase)
nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

user_input_whitelist = chars+nums

up_chars = list(string.ascii_uppercase)
symbols = ['#', '!', '@', '?', '^', '$']
password_input_whitelist = chars + up_chars + symbols + nums



#AUTHENTICATION FUNCTIONS / LOGIC
def session_check(data=None):
    data = request.json
    data = jsonify(data)
    data = data.json
    if data == None:
        return "You must pass in some data"
    if "user" not in data:
        return "username must be included inside json data"
    if "session" not in data:
        return "session must be included inside json data"
    return auth.session_authentication(data["user"], data["session"])

def usr_passwd_auth(data=None):
    data = request.json
    data = jsonify(data)
    data = data.json
    if "user" not in data:
        return "username must be included inside json data"
    if "password" not in data:
        return "password must be included inside json data"
    session = auth.user_password_authentication(data["user"], data["password"])
    return session

def validate(data=None):
    print(data)
    if "user" not in data:
        return "username must be included inside json data"
    if "password" not in data:
        return "password must be included inside json data"
    user = data["user"]
    password = data["password"]
    for char in user:
        if char not in user_input_whitelist:
            return "Username contains illegal characters!"
    for char in password:
        if char not in password_input_whitelist:
            return "Password contains illegal chracters!"
    return True



#ENDPOINTS
@app.route('/', methods=['GET'])
def index():
    log_info(request)
    return render_template('/index.html')

@app.route('/admin', methods=['GET'])
def admin():
    log_info(request)
    return render_template('/admin.html')

@app.route('/login', methods=['GET'])
def login():
    log_info(request)
    return render_template('/login.html')

@app.route('/register', methods=['GET'])
def register():
    log_info(request)
    return render_template('/register.html')

@app.route('/authentication', methods=['POST'])
def authentication():
    data = request.json
    data = jsonify(data)
    data = data.json
    check = validate(data)
    if  check != True:
        return check
    return usr_passwd_auth(data)

@app.route('/api/read_shared', methods=['POST'])
def read_shared():
    session = session_check(request)
    if session != True:
        return redirect('/')
    return shared.read_shared()

@app.route('/api/download_shared', methods=['POST'])
def download_shared():
    session = session_check(request)
    if session !=  True:
        return redirect('/')
    try:
        target_file = request.args["file"]
    except:
        return "Missing file argument in URL"
    return shared.download_shared(target_file)


@app.route('/api/whoami', methods=['POST']) 
def whoami():
    if session_check(request) == True:
        return "Success!"
    return "False!"


if (__name__ == "__main__"):
    #app.run(port=port, debug=False,use_reloader=False)
    http_server = WSGIServer((ip, port), app)
    print(f"Starting Xena systems on http://{ip}:{port}")
    http_server.serve_forever()