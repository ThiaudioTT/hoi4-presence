import requests
import json
import os

def getFlag(flag: str) -> str:

    ''' 
    Gets the corresponding image of said country using an online JSON file that's located on the repo.

    If ran through the script it will use the local version of the JSON file which is located at:

    ./assets/countries.json
    '''

    try:

        # Checking if the script is being run in an exe
        if os.path.dirname(__file__)[-3:] != 'RPC':

            JSON = requests.get("https://raw.githubusercontent.com/ThiaudioTT/hoi4-presence/main/assets/countries.json")

        else:

            JSON = os.path.join(os.getcwd(), 'assets', 'countries.json')

        with open(JSON.text, 'r') as f:

            data = json.load(f)

            return data[flag]

    except Exception as e:

        print(e)