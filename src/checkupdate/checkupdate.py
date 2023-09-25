# COMPILE THIS USING --onefile
import semantic_version
import time
import urllib.request
import time
import json
import sys
import os

from checkupdate.downloadupdate import downloadUpdate

def checkUpdate():
    try:
        # picking the current dir
        version_path = ""
        if getattr(sys, 'frozen', False):
            version_path = os.path.dirname(sys.executable)
        else:
            version_path = os.path.dirname(os.path.abspath(__file__))

        with open(version_path + "/version.json", "r") as f:
            localVersion = json.load(f)

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

        downloadPath = downloadUpdate()

        if downloadPath is not None:

            installerPath = os.path.join(downloadPath, "setup.exe")

            # Starting setup.exe in -update mode so it will automatically install and start up the mod
            os.startfile(installerPath, "-update")

            sys.exit()

checkUpdate()
