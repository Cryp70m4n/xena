import time
from auth import authorisation


auth = authorisation()
def check_tokens():
    time.sleep(3)
    auth.token_timestamp_check()
    check_tokens()
check_tokens()