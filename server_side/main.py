from auth import authorisation
x = authorisation()

#y = x.user_password_authentication("test", "test")
#print(y)
#r = x.session_authentication("test", y)
r = x.token_timestamp_check()
print(r)
