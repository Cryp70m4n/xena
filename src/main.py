from auth import authorisation
x = authorisation()

r = x.generate_hash("root")
print(r)
