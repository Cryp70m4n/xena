from flask import Flask, request, jsonify, render_template, redirect
from gevent.pywsgi import WSGIServer
import binascii
import string
import json
import threading

from auth import authorisation
import configs
from functions import admin_functions
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
    api_logger.info(ip + "|" + request.method)
    return 0

auth = authorisation()
shared = shared()
functions = admin_functions()
configs = configs.config_parser()
permission_configs = configs.permission_config_parser("configs/permissions.cfg")

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
    if data["user"] == None or data["session"] == None:
        return "Session/user cannot be None!"

    session_string = data["session"].replace('"', '')
    session = str(session_string)
    user = data["user"]
    user = user.replace('"', '')
    check = auth.session_authentication(user, session)
    if check != True:
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
    if data["user"] == None or data["password"] == None:
        return "Password/user cannot be None!"
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
    if data["user"] == None or data["password"] == None:
        return "Password/user cannot be None!"
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
    if "user" not in data:
        return "User must be included!"
    if "session" not in data:
        return "Session must be included!"
    if data["user"] == None or data["session"] == None:
        return "Session/user cannot be None!"
    session_string = data["session"].replace('"', '')
    session = str(session_string)
    user = data["user"]
    user = user.replace('"', '')
    for char in user:
        if char not in user_input_whitelist:
            return False
    perm_lvl = auth.permission_level_authentication(user, session)
    return perm_lvl


#TEMPLATE ENDPOINTS (GENERAL FRONTEND STUFF)
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


#LOGICAL ENDPOINTS (GENERAL AUTHENTICATION STUFF)
@app.route('/authentication', methods=['POST'])
def authentication():
    log_info(request)
    fail_response_data = {"response_status": "You used illegal characters!", "response_code": 1}
    fail_response = json.dumps(fail_response_data)
    check = usr_pass_validate(request)
    if  check != True:
        return fail_response

    session = usr_passwd_auth(request)
    try:
        response_data = {"token": session.decode('utf-8'), "response_status": "Success!", "response_code": 0}
    except:
        response_data = {"response_status": "Session Error!", "response_code": 1}
    response = json.dumps(response_data)
    return response

@app.route('/admin_authentication', methods=['POST'])
def admin_authentication():
    log_info(request)
    fail_response_data = {"response_status": "You are not an admin!", "response_code": 1}
    fail_response = json.dumps(fail_response_data)
    session = session_check(request)
    if session != True:
        return fail_response
    permission_level_check = permission_level_auth(request)
    if  permission_level_check < permission_configs["admin"]:
        return fail_response
    return render_template("/admin_dashboard.html")

#ADMIN STUFF
@app.route('/create_account', methods=['POST'])
def create_account():
    fail_response_data = {"response_status": "You are not an admin!", "response_code": 1}
    fail_response = json.dumps(fail_response_data)
    session = session_check(request)
    if session != True:
        return fail_response
    permission_level_check = permission_level_auth(request)
    if permission_level_check < permission_configs["create_account"]:
        return fail_response
    data = request.json
    data = jsonify(data)
    data = data.json
    if "user" not in data or "session" not in data or "target_user" not in data or "password" not in data or "permission_level" not in data:
        missing_response_data = {"response_status": "You are missing some data!", "response_code": 2}
        missing_response = json.dumps(missing_response_data)
        return missing_response
    password = data["password"]
    session_string = data["session"].replace('"', '')
    sess = str(session_string)
    user = data["user"]
    user = user.replace('"', '')
    illegal_chars_response_data = {"response_status": "Input contains some illegal characters!", "response_code": 3}
    illegal_chars_response = json.dumps(illegal_chars_response_data)
    for char in user:
        if char not in user_input_whitelist:
            return illegal_chars_response
    for char in password:
        if char not in password_input_whitelist:
            return illegal_chars_response
    account_creation = functions.create_account(user, sess, data["target_user"], password, data["permission_level"])
    if account_creation != True:
        wrong_data_response = {"response_status": "Your input contains some wrong data!", "response_code": 4}
        wrong_response = json.dumps(wrong_data_response)
        return wrong_response
    success_response_data = {"response_status": "Success!", "response_code": 0}
    success_response = json.dumps(success_response_data)
    return success_response

@app.route('/delete_account', methods=['POST'])
def delete_account():
    fail_response_data = {"response_status": "You are not an admin!", "response_code": 1}
    fail_response = json.dumps(fail_response_data)
    session = session_check(request)
    if session != True:
        return fail_response
    permission_level_check = permission_level_auth(request)
    if permission_level_check < permission_configs["delete_account"]:
        return fail_response
    data = request.json
    data = jsonify(data)
    data = data.json
    if "user" not in data or "session" not in data or "target_user" not in data:
        missing_response_data = {"response_status": "You are missing some data!", "response_code": 2}
        missing_response = json.dumps(missing_response_data)
        return missing_response
    session_string = data["session"].replace('"', '')
    sess = str(session_string)
    user = data["user"]
    user = user.replace('"', '')
    account_delete = functions.delete_account(user, sess, data["target_user"])
    if account_delete != True:
        wrong_data_response = {"response_status": "Your input contains some wrong data!", "response_code": 4}
        wrong_response = json.dumps(wrong_data_response)
        return wrong_response
    success_response_data = {"response_status": "Success!", "response_code": 0}
    success_response = json.dumps(success_response_data)
    return success_response

@app.route('/create_vault', methods=['POST'])
def create_vault():
    fail_response_data = {"response_status": "You are not an admin!", "response_code": 1}
    fail_response = json.dumps(fail_response_data)
    session = session_check(request)
    if session != True:
        return fail_response
    permission_level_check = permission_level_auth(request)
    if permission_level_check < permission_configs["create_vault"]:
        return fail_response
    data = request.json
    data = jsonify(data)
    data = data.json
    if "user" not in data or "session" not in data or "vault_name" not in data or "vault_owner" not in data:
        missing_response_data = {"response_status": "You are missing some data!", "response_code": 2}
        missing_response = json.dumps(missing_response_data)
        return missing_response
    vault_name = data["vault_name"]
    vault_owner = data["vault_owner"]
    illegal_chars_response_data = {"response_status": "Input contains some illegal characters!", "response_code": 3}
    illegal_chars_response = json.dumps(illegal_chars_response_data)
    for char in vault_owner:
        if char not in user_input_whitelist:
            return illegal_chars_response
    for char in vault_name:
        if char not in user_input_whitelist:
            return illegal_chars_response
    session_string = data["session"].replace('"', '')
    sess = str(session_string)
    user = data["user"]
    user = user.replace('"', '')
    vault_create = functions.create_vault(user, sess, vault_name, vault_owner)
    if vault_create != True:
        wrong_data_response = {"response_status": "Your input contains some wrong data!", "response_code": 4}
        wrong_response = json.dumps(wrong_data_response)
        return wrong_response
    success_response_data = {"response_status": "Success!", "response_code": 0}
    success_response = json.dumps(success_response_data)
    return success_response

@app.route('/delete_vault', methods=['POST'])
def delete_vault():
    fail_response_data = {"response_status": "You are not an admin!", "response_code": 1}
    fail_response = json.dumps(fail_response_data)
    session = session_check(request)
    if session != True:
        return fail_response
    permission_level_check = permission_level_auth(request)
    if permission_level_check < permission_configs["delete_vault"]:
        return fail_response
    data = request.json
    data = jsonify(data)
    data = data.json
    if "user" not in data or "session" not in data or "vault_name" not in data or "vault_owner" not in data:
        missing_response_data = {"response_status": "You are missing some data!", "response_code": 2}
        missing_response = json.dumps(missing_response_data)
        return missing_response
    vault_name = data["vault_name"]
    vault_owner = data["vault_owner"]
    illegal_chars_response_data = {"response_status": "Input contains some illegal characters!", "response_code": 3}
    illegal_chars_response = json.dumps(illegal_chars_response_data)
    for char in vault_owner:
        if char not in user_input_whitelist:
            return illegal_chars_response
    for char in vault_name:
        if char not in user_input_whitelist:
            return illegal_chars_response
    session_string = data["session"].replace('"', '')
    sess = str(session_string)
    user = data["user"]
    user = user.replace('"', '')
    vault_delete = functions.delete_vault(user, sess, vault_name, vault_owner)
    if vault_delete != True:
        wrong_data_response = {"response_status": "Your input contains some wrong data!", "response_code": 4}
        wrong_response = json.dumps(wrong_data_response)
        return wrong_response
    success_response_data = {"response_status": "Success!", "response_code": 0}
    success_response = json.dumps(success_response_data)
    return success_response

@app.route('/get_users', methods=['POST'])
def get_users():
    fail_response_data = {"response_status": "You are not an admin!", "response_code": 1}
    fail_response = json.dumps(fail_response_data)
    session = session_check(request)
    if session != True:
        return fail_response
    permission_level_check = permission_level_auth(request)
    if permission_level_check < permission_configs["get_users"]:
        return fail_response
    data = request.json
    data = jsonify(data)
    data = data.json
    if "user" not in data or "session" not in data:
        missing_response_data = {"response_status": "You are missing some data!", "response_code": 2}
        missing_response = json.dumps(missing_response_data)
        return missing_response
    session_string = data["session"].replace('"', '')
    sess = str(session_string)
    user = data["user"]
    user = user.replace('"', '')
    users = functions.get_users(user, sess)
    success_response_data = {"users": users, "response_status": "Success!", "response_code": 0}
    success_response = json.dumps(success_response_data)
    return success_response

@app.route('/change_password', methods=['POST'])
def change_password():
    fail_response_data = {"response_status": "You are not an admin!", "response_code": 1}
    fail_response = json.dumps(fail_response_data)
    session = session_check(request)
    if session != True:
        return fail_response
    permission_level_check = permission_level_auth(request)
    if permission_level_check < permission_configs["change_password"]:
        return fail_response
    data = request.json
    data = jsonify(data)
    data = data.json
    if "user" not in data or "session" not in data or "target_user" not in data or "password" not in data:
        missing_response_data = {"response_status": "You are missing some data!", "response_code": 2}
        missing_response = json.dumps(missing_response_data)
        return missing_response
    session_string = data["session"].replace('"', '')
    sess = str(session_string)
    user = data["user"]
    user = user.replace('"', '')
    password = data["password"]
    illegal_chars_response_data = {"response_status": "Input contains some illegal characters!", "response_code": 3}
    illegal_chars_response = json.dumps(illegal_chars_response_data)
    for char in password:
        if char not in password_input_whitelist:
            return illegal_chars_response
    change_password = functions.change_password(user, sess, data["target_user"], data["password"])
    if change_password != True:
        wrong_data_response = {"response_status": "Your input contains some wrong data!", "response_code": 4}
        wrong_response = json.dumps(wrong_data_response)
        return wrong_response
    success_response_data = {"response_status": "Success!", "response_code": 0}
    success_response = json.dumps(success_response_data)
    return success_response

@app.route('/change_permission_level', methods=['POST'])
def change_permission_level():
    fail_response_data = {"response_status": "You are not an admin!", "response_code": 1}
    fail_response = json.dumps(fail_response_data)
    session = session_check(request)
    if session != True:
        return fail_response
    permission_level_check = permission_level_auth(request)
    if permission_level_check < permission_configs["change_permission_level"]:
        return fail_response
    data = request.json
    data = jsonify(data)
    data = data.json
    if "user" not in data or "session" not in data or "target_user" not in data or "permission_level" not in data:
        missing_response_data = {"response_status": "You are missing some data!", "response_code": 2}
        missing_response = json.dumps(missing_response_data)
        return missing_response
    session_string = data["session"].replace('"', '')
    sess = str(session_string)
    user = data["user"]
    user = user.replace('"', '')
    change_permission_level = functions.change_password(user, sess, data["target_user"], data["permission_level"])
    if change_permission_level != True:
        wrong_data_response = {"response_status": "Your input contains some wrong data!", "response_code": 4}
        wrong_response = json.dumps(wrong_data_response)
        return wrong_response
    success_response_data = {"response_status": "Success!", "response_code": 0}
    success_response = json.dumps(success_response_data)
    return success_response

@app.route('/logout', methods=['POST'])
def logout():
    log_info(request)
    session = session_check(request)
    if session != True:
        return "False"
    auth.delete_session(user, session)
    return redirect("/")

@app.route('/api/read_shared', methods=['POST'])
def read_shared():
    log_info(request)
    session = session_check(request)
    if session != True:
        return redirect('/')
    return shared.read_shared()

@app.route('/api/download_shared', methods=['POST'])
def download_shared():
    log_info(request)
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
    log_info(request)
    if session_check(request) == True:
        return "Success!"
    return "False!"



if (__name__ == "__main__"):
    #app.run(port=port, debug=False,use_reloader=False)
    http_server = WSGIServer((ip, port), app)
    print(f"Starting Xena systems on http://{ip}:{port}")
    http_server.serve_forever()