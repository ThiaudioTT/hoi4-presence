import semantic_version
import time
import urllib.request
import time
import json
import sys

def checkUpdate():
    try:
        localVersion = open("version.json", "r")
        localVersion = json.load(localVersion)
        print(localVersion)
    except Exception as e:
        print(e)
        print("Error while reading version.json")
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

checkUpdate()