import os
import shutil
import time
import sys
import json
from pathlib import Path
# TODO: remove pathlib dependency to compile in onefile.
# TODO: verify if all files are included in /dist/ folder. (like version.json)

print("This script will install the hoi4-presence in your game/save path\nPress enter to continue...")
input()

# 1 - Move hoi4Presence to documents/paradox/hearts of iron/ WITH CURRENTLY version.json and uninstaller.py
    # 1.1 - If can't move, exit. 
    # 1.2 - If can't search, ask the user where is the path
# 2 - replace settings.txt .replace('save_as_binary=yes', 'save_as_binary=no')
# 3 - Move runRPC.bat to the game folder, usually C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\
    # 3.1 - If can't move, exit.
    # 3.2 - If can't search, ask the user where is the path
# 4 - change launcher-settings.json
    # "exePath": "runRPC.bat"
    # 4.1 - If can't, ask to user permission and exit.

# 5 - Success message (or failed)
# 6 - ask the user delete the folder and exit


# 1 
documents = os.environ['USERPROFILE'] + "\\Documents\\Paradox Interactive\\Hearts of Iron IV"
try:
    os.listdir(documents)
except Exception as e:
    print(e)
    # 1.2
    print("Can't find the game path, please enter the path manually: ")
    documents = input() # TODO: Check if the path is valid

 #moving...
try:
    if(os.path.exists(documents + "\\hoi4Presence")):
        print("Old installation found, deleting...")
        shutil.rmtree(documents + "\\hoi4Presence")
    time.sleep(2)
    print("\nMoving...")
    print(documents)
    print(documents + "\\hoi4Presence")

    source = Path(__file__).parent.resolve() / "discordRPC/dist"
    shutil.copytree(source, documents + "\\hoi4Presence")
except Exception as e:
    print(e)
    print("Can't move the hoi4Presence to the save Path\nExiting...")
    time.sleep(3)
    sys.exit()

# 2
try:
    print("Writing save_as_binary=no in settings.txt...")
    with open(documents + "\\settings.txt", "r") as f:
        settings = f.read()
        settings = settings.replace('save_as_binary=yes', 'save_as_binary=no')
    with open(documents + "\\settings.txt", "w") as f:
        f.write(settings)
except Exception as e:
    print(e)
    print("Can't change the settings.txt\nExiting...")
    time.sleep(3)
    sys.exit()

# 3
gameFolder = os.environ['PROGRAMFILES(X86)'] + "\\Steam\\steamapps\\common\\Hearts of Iron IV"
try:
    os.listdir(gameFolder)
except Exception as e:
    print(e)
    # 3.2
    print("Can't find the game path, please enter the path manually: ")
    gameFolder = input() # TODO: Check if the path is valid


#   moving...
try:
    print("Moving runRPC.bat to the game folder...")
    print(gameFolder)

    file = Path(__file__).parent.resolve() / "batch/runRPC.bat"
    shutil.copyfile(file, gameFolder + "\\runRPC.bat")
except Exception as e:
    print(e)
    print("Can't move the runRPC.bat to the game folder\nExiting...")
    time.sleep(3)
    sys.exit()

# 4
try:
    print("Changing launcher-settings.json...")
    with open(gameFolder + "\\launcher-settings.json", "r") as f:
        launcher = json.load(f)
        launcher["exePath"] = "runRPC.bat"
    with open(gameFolder + "\\launcher-settings.json", "w") as f:
        json.dump(launcher, f, indent=4)
except Exception as e:
    print(e)
    print("Can't change the launcher-settings.json\nExiting...")
    time.sleep(3)
    sys.exit()

# 5
print("\n\nSuccess! The hoi4Presence is installed in your game folder.\n\n")
print("Execute the game via launcher to auto activate the presence.\n\nYou can delete this folder now.\n\n")
print("See https://github.com/ThiaudioTT/hoi4-presence for updates and more information.\n\n")
input()
time.sleep(5)
sys.exit()