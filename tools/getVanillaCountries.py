from bs4 import BeautifulSoup
import requests
import os
import threading
from queue import Queue

# this script is used to get the vanilla countries from the wiki
# It creates a file with the countries and their codes in a python dictionary format
# it also downloads the flags of the countries
# execut to see the failed: python your_script.py > output.log


# Hint: use threads to be faster

HOI_SOURCE = "https://hoi4.paradoxwikis.com/"
N_THREADS = 5

# Thread lock, when writing the file, it must be locked to avoid conflicts
lock = threading.Lock()

# Helper functions:
def getCountryDetails(row) -> tuple[str, str]:
    country_name = row.find_all("td")[0].text.strip()
    country_code = row.find_all("td")[1].text.strip()
    return country_name, country_code

def appendCountryToFile(country_name: str, country_code: str, filename: str) -> None:
    # Write the country to the file
    with lock: # lock the file to avoid conflicts, at the end of the with block the lock is released
        with open(f"{filename}.py", "a") as countriesFile:
            # it must be in the format "ITA" : ("Italy", "ita"),
            countriesFile.write(f'"{country_code}": ("{country_name}", "{country_code.lower()}"),\n')


def getSoup(url: str, error_message: str) -> BeautifulSoup:
    response = requests.get(url)
    if response.status_code != 200:
        print(error_message)
        return None
    
    return BeautifulSoup(response.text, 'html.parser')

def downloadFlagImage(flagWebpage: BeautifulSoup, country_code: str) -> None:
    """Downloads the flag image of the country and saves it in the flags folder"""
    IMAGE = flagWebpage.select_one("#file > a > img") # get the image tag
    if not IMAGE:
        print(f"Failed to get flag IMAGE for {country_code}")
        return
    
    flag_url = HOI_SOURCE + IMAGE["src"]

    flag_response = requests.get(flag_url)
    if flag_response.status_code == 200:
        with lock: # in this case the lock is not necessary, but it is good to keep it
            with open(f"flags/{country_code}.png", "wb") as flag_file:
                flag_file.write(flag_response.content)
        print(f"Flag for {country_code} downloaded.")
    else:
        print(f"Failed to download flag for {country_code}")
    

def getCountry(row, filename):
    cName, cCode = getCountryDetails(row)
    # print(f"Country: {cName}Code: {cCode}")
    try:

        # Write the country to the file
        appendCountryToFile(cName, cCode, filename)

        # Download the flag of the country
        # the flag is in another webpage
        country_webpage_URL = HOI_SOURCE + row.find_all("td")[0].find("a")["href"][1:]
        country_webpage = getSoup(country_webpage_URL, f"Failed to get flag WEBPAGE for {cName}")


        # Enters another webpage to get the flag (the webpage has the flag in a different size)
        cFlag_webpage = HOI_SOURCE + country_webpage.select_one("div.mw-parser-output:nth-child(4) > div:nth-child(2) > a")["href"][1:]
        cFlag_webpage = getSoup(cFlag_webpage, f"Failed to get flag WEBPAGE for {cName}")

        downloadFlagImage(cFlag_webpage, cCode)
    except Exception as e:
        print(f"Failed to get flag for {cName} - {e}")

def getCountries(table: list[str], filename: str):
    """Downloads the flags of the countries and creates a file with the countries and their codes in a python dictionary format"""
    
    # Make threads to get the countries
    # Transform the table into a queue to be able to use threads #thread-safe!
    queue = Queue()
    for row in table.find_all("tr"):
        if not row.find_all("td"): continue
        queue.put(row)


    while not queue.empty():
        threads = [] # list of threads
        for _ in range(N_THREADS):
            if not queue.empty():
                row = queue.get()
                thread = threading.Thread(target=getCountry, args=(row, filename)) # create the thread
                threads.append(thread)
                thread.start()
        
        for thread in threads:
            thread.join() # wait for the threads to finish


def main():
    print("Getting countries from wiki...")
    countriesWiki = "https://hoi4.paradoxwikis.com/Countries"

    wikiSoup = getSoup(countriesWiki, "Failed to get countries from wiki.")

    os.makedirs("flags", exist_ok=True)

    # pick the table with the initial countries
    initialCountriesTable = wikiSoup.select_one("table.wikitable:nth-child(16) > tbody")

    # Download the images and create the dictionary with the countries
    getCountries(initialCountriesTable, "initialCountries")

    # todo: do the same for released countries (this is a bit more complicated becasuse the wiki doenst have it)
    # # pick the table with the released countries
    # releasedCountriesTable = soup.select_one("table.wikitable:nth-child(26) > tbody")

    # # Download the images and create the dictionary with the countries
    # getCountries(releasedCountriesTable, "releasedCountries")

    print("Done.")






if __name__ == '__main__':
    main()
