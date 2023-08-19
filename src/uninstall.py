import os
import shutil
import time
import sys
import json

print("This script will uninstall the hoi4-presence in your game/save path\nPress enter to continue...")
input()

# Find save data
documents = os.environ['USERPROFILE'] + "\\Documents\\Paradox Interactive\\Hearts of Iron IV"
while True:
    try:
        if 'settings.txt' not in os.listdir(documents):
            raise Exception(f"Could not find 'settings.txt' in '{documents}'")
        else:
            print('Documents directory found')
            break
    except Exception as e:
        print(e)
        errorType = 'documents path' if str(e).startswith('[WinError 3]') else "'settings.txt'"

        documents = input(f"Can't find {errorType}, please enter the path manually: ")

# Revert settings.txt
try:
    print("Writing save_as_binary=yes in settings.txt...")
    with open(documents + "\\settings.txt", "r") as f:
        settings = f.read()
        settings = settings.replace('save_as_binary=no', 'save_as_binary=yes')
    with open(documents + "\\settings.txt", "w") as f:
        f.write(settings)
except Exception as e:
    print(e)
    print("Can't revert settings.txt\nExiting...")
    time.sleep(3)
    sys.exit()

# Find game directory
gameFolder = os.environ['PROGRAMFILES(X86)'] + "\\Steam\\steamapps\\common\\Hearts of Iron IV"
while True:
    try:
        if "hoi4.exe" not in os.listdir(gameFolder):
            raise Exception(f"Could not find 'hoi4.exe' in '{gameFolder}'")
        else:
            print('Game directory found')
            break
    except Exception as e:
        print(e)
        errorType = "game folder path" if str(e).startswith('[WinError 3]') else "'hoi4.exe'"

        gameFolder = input(f"Can't find {errorType}, please enter the path manually: ")

# Revert launcher-settings.json
try:
    print("Changing launcher-settings.json...")
    with open(gameFolder + "\\launcher-settings.json", "r") as f:
        launcher = json.load(f)
        launcher["exePath"] = "hoi4.exe"
    with open(gameFolder + "\\launcher-settings.json", "w") as f:
        json.dump(launcher, f, indent=4)
except Exception as e:
    print(e)
    print("Can't revert launcher-settings.json\nExiting...")
    time.sleep(3)
    sys.exit()

# Delete hoi4Presence and runRPC.bat
try:
    print("Deleting rich presence")
    shutil.rmtree(os.path.join(documents, "hoi4Presence"))
    os.remove(os.path.join(gameFolder, "runRPC.bat"))
except Exception as e:
    print(str(e))
    print("Could not delete rich presence, exiting...")
    time.sleep(3)
    sys.exit()

print("Uninstalled!\nPress 'Enter' or close this window.")
input()
