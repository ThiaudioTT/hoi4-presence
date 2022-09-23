import re

file = open("autosave.hoi4", "r")
data = ""
for i in range(5):
    data += file.readline()

data = re.sub("(HOI4txt|player=|ideology=|date=|difficulty=|\")", "", data).split()
print(data)
print(data[2][:4]) # year