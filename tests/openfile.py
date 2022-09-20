import re

# f = open("autosave.hoi4", "rb")
f = open("autosave.hoi4",  "r", errors="ignore")

str = f.readline()
info = re.findall("\w+", str, flags=re.A)

print(info)

# it stores the data in an array