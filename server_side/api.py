from flask import Flask, request, jsonify, render_template, redirect
from gevent.pywsgi import WSGIServer
import binascii
import string
import json
import threading

from auth import authorisation
import logger
from scripts.shared import shared

"""
TODO:
    - FUCK FASTAPI AND BENCHMARKS!
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
    if data == None:
        return "You must pass in some data"
    data = request.json
    data = jsonify(data)
    data = data.json
    if "user" not in data:
        return "username must be included inside json data"
    if "session" not in data:
        return "session must be included inside json data"
    check = auth.session_authentication(data["user"], data["session"])
    if check != "Session authorised!":
        return False
    return True

def usr_passwd_auth(data=None):
    if data == None:
        return "You must pass in some data"
    data = request.json
    data = jsonify(data)
    data = data.json
    if "user" not in data:
        return "username must be included inside json data"
    if "password" not in data:
        return "password must be included inside json data"
    session = auth.user_password_authentication(data["user"], data["password"])
    return session

def usr_pass_validate(data=None):
    if data == None:
        return "You must pass in some data"
    data = request.json
    data = jsonify(data)
    data = data.json
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

def permission_level_auth(data = None):
    if data == None:
        return "You must pass in some data"
    data = request.json
    data = jsonify(data)
    data = data.json
    if user not in data:
        return "User must be included!"
    if session not in data:
        return "Session must be included!"
    for char in data["user"]:
        if char not in user_input_whitelist:
            return False
    if(permission_level_authentication(usr, session) == 4):
        return True
    return False



#GET ENDPOINTS (GENERAL FRONTEND STUFF)
@app.route('/', methods=['GET'])
def index():
    log_info(request)
    return render_template('/index.html')

@app.route('/admin', methods=['GET'])
def admin():
    session = session_check(request)
    if session != True:
        return redirect("/")
    log_info(request)
    return render_template('/admin.html')

@app.route('/admin_dashbaord', methods=['GET'])
def admin_dashboard():
    session = session_check(request)
    if session != True:
        return redirect("/")
    permission_level_check = permission_level_auth(request)
    if  permission_level_check != True:
        return redirect("/")
    return render_template("/admin_dashbaord.html")

@app.route('/login', methods=['GET'])
def login():
    log_info(request)
    return render_template('/login.html')

@app.route('/register', methods=['GET'])
def register():
    log_info(request)
    return render_template('/register.html')


#POST ENDPOINTS (LOGIC)
@app.route('/authentication', methods=['POST'])
def authentication():
    check = usr_pass_validate(request)
    if  check != True:
        return check

    session = usr_passwd_auth(request)
    try:
        response_data = {"token": session.decode('utf-8'), "response_status": "Success!"}
    except:
        response_data = {"response_status": "Session Error!"}
    response = json.dumps(response_data)
    return response

@app.route('/logout', methods=['POST'])
def logout():
    session = session_check(request)
    if session != True:
        return False
    auth.delete_session(user, session)
    return redirect("/")

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