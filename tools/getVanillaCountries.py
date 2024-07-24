from bs4 import BeautifulSoup
import requests
import os

# this script is used to get the vanilla countries from the wiki
# It creates a file with the countries and their codes in a python dictionary format
# it also downloads the flags of the countries
# execut to see the failed: python your_script.py > output.log

# Todo: this was made in a hurry, LMAO. Refactor it!
# Hint: use threads to be faster

HOI_SOURCE = "https://hoi4.paradoxwikis.com/"

# Helper functions

def getCountryDetails(row) -> tuple[str, str]:
    country_name = row.find_all("td")[0].text.strip()
    country_code = row.find_all("td")[1].text.strip()
    return country_name, country_code

def appendCountryToFile(country_name: str, country_code: str, filename: str) -> None:
    # Write the country to the file
    with open(f"{filename}.py", "a") as countriesFile:
        # it must be in the format "ITA" : ("Italy", "ita"),
        countriesFile.write(f'"{country_code}": ("{country_name}", "{country_code.lower()}"),\n')


def getSoup(url: str, error_message: str) -> BeautifulSoup:
    response = requests.get(url)
    if response.status_code != 200:
        print(error_message)
        return None
    
    return BeautifulSoup(response.text, 'html.parser')

def getCountries(table: list[str], filename: str):
    """Donwloads the flags of the countries and creates a file with the countries and their codes in a python dictionary format"""
    for row in table.find_all("tr"):
        if not row.find_all("td"): continue

        cName, cCode = getCountryDetails(row)
        print(f"Country: {cName}Code: {cCode}")
        try:

            # Write the country to the file
            appendCountryToFile(cName, cCode, filename)

            # Download the flag of the country
            # the flag is in another webpage
            image_webpage = HOI_SOURCE + row.find_all("td")[0].find("a")["href"][1:]

            image_webpage_response = requests.get(image_webpage)
            if image_webpage_response.status_code != 200:
                print(f"Failed to get flag WEBPAGE for {cName}")
                continue
                
            image_webpage_soup = BeautifulSoup(image_webpage_response.text, 'html.parser')

            # image = image_webpage_soup.select_one("div.eu4box:nth-child(2) > a:nth-child(2) > img")
            image_location = HOI_SOURCE + image_webpage_soup.select_one("div.mw-parser-output:nth-child(4) > div:nth-child(2) > a")["href"][1:]

            image_response = requests.get(image_location)
            if image_response.status_code != 200:
                print(f"Failed to get flag IMAGE for {cName}")
                continue

            image_soup = BeautifulSoup(image_response.text, 'html.parser')

            image = image_soup.select_one("#file > a > img")

            if not image:
                print(f"Failed to get flag IMAGE for {cName}")
                continue

            flag_url = HOI_SOURCE + image["src"]

            flag_response = requests.get(flag_url)
            if flag_response.status_code == 200:
                with open(f"flags/{cCode}.png", "wb") as flag_file:
                    flag_file.write(flag_response.content)
                print(f"Flag for {cName} downloaded.")
            else:
                print(f"Failed to download flag for {cName}")
        except Exception as e:
            print(f"Failed to get flag for {cName} - {e}")


def main():
    countriesWiki = "https://hoi4.paradoxwikis.com/Countries"
    responseCountriesWiki = requests.get(countriesWiki)
    if responseCountriesWiki.status_code != 200:
        print("Failed to get countries from wiki.")
        return
    soup = BeautifulSoup(responseCountriesWiki.text, 'html.parser')

    os.makedirs("flags", exist_ok=True)


    # pick the table with the initial countries
    initialCountriesTable = soup.select_one("table.wikitable:nth-child(16) > tbody")

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
