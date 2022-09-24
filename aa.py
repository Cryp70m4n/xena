import os
i = 0

while i < 10000:
    com = f"mkdir dire/dir{i}"
    os.system(com)
    i+=1
