# COMPILE THIS USING --onefile
import subprocess
from semantic_version import Version
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

    isClientOutdated = Version(localVersion["version"]) < Version(cloudVersion["version"])

    if localVersion['auto-update'] and isClientOutdated:

        print("Update found!")

        downloadPath = downloadUpdate()

        if downloadPath is not None:

            installerPath = os.path.join(downloadPath, "setup.exe")

            print('Updating...\n\n')

            # Starting setup.exe in -update mode so it will automatically install and start up the mod
            subprocess.Popen([installerPath, "-update"], start_new_session=True, cwd=downloadPath) # passing cwd to the script knows where he is

            print('Closing checkUpdate.exe...')

            # Close checkUpdate.exe (setup.exe will still run and in the new window)
            sys.exit(0)

checkUpdate()
