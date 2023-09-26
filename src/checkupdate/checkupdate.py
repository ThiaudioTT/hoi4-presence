# COMPILE THIS USING --onefile
import subprocess
import semantic_version
import time
import urllib.request
import time
import json
import sys
import os

from downloadupdate import downloadUpdate

def checkUpdate():
    try:

        print("Checking for updates in hoi4 presence...")

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

    if semantic_version.Version(localVersion["version"]) < semantic_version.Version(cloudVersion["version"]):

        print("Update found!")

        downloadPath = downloadUpdate()

        if downloadPath is not None:

            installerPath = os.path.join(downloadPath, "setup.exe")

            print('Updating...\n\n')

            gameFolder = os.path.dirname(os.getcwd())

            print(gameFolder)

            # Starting setup.exe in -update mode so it will automatically install and start up the mod
            subprocess.Popen([installerPath, "-update", gameFolder], start_new_session=True)

            # Close checkUpdate.exe (setup.exe will still run and in the new window)
            sys.exit(0)

checkUpdate()
