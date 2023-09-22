import os
import shutil

import requests

def downloadUpdate() -> str | None:
    '''
    Downloads and installs the newest hoi4 update.

    Returns download path if successful, else None
    '''

    try:

        downloadTemp: str = None
        extractedTemp: str = None

        # Get latest release data
        latestRelease = requests.get("https://api.github.com/repos/ThiaudioTT/hoi4-presence/releases/latest")

        latestReleaseData: dict = latestRelease.json()

        # Find asset data api link
        assetUrl: str = latestReleaseData["assets_url"]

        # Get asset data
        assetsData: dict = requests.get(assetUrl , headers={"accept":"application/vnd.github+json"}).json()

        # Incase there are muiltiple assets create a for loop
        downloadLink: str = None
        fileName = f"hoi4-presence-{latestReleaseData['tag_name']}.zip"

        for asset in assetsData:

            if asset["name"] == fileName:

                # Found the download link
                downloadLink = asset["browser_download_url"]

                break

        if downloadLink:

            # Instance a session
            session = requests.Session()

            downloadTemp = os.path.join(os.environ["TEMP"], fileName)

            # Creating a new file in "write in binary" mode
            with open(downloadTemp, "wb") as f:

                # Get data for download
                request = session.get(downloadLink, allow_redirects=True, stream=True)

                # Write it to fileName in chunks
                for chunk in request.iter_content(1024**2):
                    f.write(chunk)

            print("Download successful!")

        extractedTemp = os.path.join(os.environ["TEMP"], f"hoi4-presence-{latestReleaseData['tag_name']}")

        # Unzipping
        shutil.unpack_archive(downloadTemp, extractedTemp)

        return extractedTemp

    except Exception as e:

        print(f"An error has occured while updating:\n{e}\n\nStarting current version...")

        return None
