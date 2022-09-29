# COMPILE THIS USING --onefile
import semantic_version
import time
import urllib.request
import time
import json
import sys
import os

def checkUpdate():
    try:
        # picking the current dir
        version_path = ""
        if getattr(sys, 'frozen', False):
            version_path = os.path.dirname(sys.executable)
        else:
            version_path = os.path.dirname(os.path.abspath(__file__))

        localVersion = open(version_path + "/version.json", "r") # use something like .resolve() or clean code
        localVersion = json.load(localVersion)

        print("\nLocal version: ")
        print(localVersion)
    except Exception as e:
        print(e)
        print("Error while reading version.json")
        time.sleep(5)
        sys.exit(1)

    URL = urllib.request.urlopen("https://raw.githubusercontent.com/ThiaudioTT/hoi4-presence/main/version.json")
    cloudVersion = json.loads(URL.read())

    print("Checking for updates in hoi4 presence...")
    if semantic_version.Version(localVersion["version"]) < semantic_version.Version(cloudVersion["version"]):
        print("\n\n\nUpdate available!")
        print("Please, download the latest version from:\nhttps://github.com/ThiaudioTT/hoi4-presence/releases")
        time.sleep(120)
    else:
        print("Update not found.")
        time.sleep(50)

checkUpdate()