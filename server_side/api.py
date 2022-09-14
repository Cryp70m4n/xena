from flask import Flask, request, jsonify, render_template_string, render_template
from gevent.pywsgi import WSGIServer
from auth import authorisation
import binascii

import logger
from scripts.shared import shared

"""
TODO:
    Switch to DJANGO or FASTAPI
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

@app.route('/api/usr_passwd_auth', methods=['POST'])
def usr_passwd_auth():
    data = request.json
    data = jsonify(data)
    data = data.json
    if data == None:
        return "You must pass in some data"
    if "user" not in data:
        return "username must be included inside json data"
    if "password" not in data:
        return "password must be included inside json data"
    session = auth.user_password_authentication(data["user"], data["password"])
    return session

@app.route('/')
def index():
    log_info(request)
    #session = session_check(request)
    #if session != "Session authorised!":
    #    return usr_passwd_auth()

    return render_template('/index.html')

@app.route('/api/read_shared', methods=['GET'])
def read_shared():
    session = session_check(request)
    if session != 0:
        return usr_passwd_auth()
    return shared.read_shared()

@app.route('/api/download_shared', methods=['GET'])
def download_shared():
    session = session_check(request)
    if session != 0:
        return usr_passwd_auth()
    try:
        target_file = request.args["file"]
    except:
        return "Missing file argument in URL"
    return shared.download_shared(target_file)


@app.route('/api/whoami', methods=['GET']) 
def whoami():
    if session_check(request) == 0:
        return "Success!"
    return "False!"


if (__name__ == "__main__"):
    #app.run(port=port, debug=False,use_reloader=False)
    http_server = WSGIServer((ip, port), app)
    print(f"Starting Xena systems on http://{ip}:{port}")
    http_server.serve_forever()