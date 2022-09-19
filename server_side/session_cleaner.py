import threading
from auth import authorisation
def check_tokens():
    threading.Timer(5.0, check_tokens).start()
    auth.token_timestamp_check()
check_tokens()
