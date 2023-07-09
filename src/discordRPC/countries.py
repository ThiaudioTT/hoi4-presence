import requests

class Country:
   def __init__(self, name: str, flag: str):
      self.name = name
      self.flag = flag

def getFlag(flag: str) -> str:
    """Gets the corresponding image of said country using an online JSON file that's located on the repo."""

    try:

      JSON = requests.get("https://raw.githubusercontent.com/ThiaudioTT/hoi4-presence/main/src/discordRPC/countries.json")

      return JSON.json()[flag]

    except Exception as e:

      print(e)
        
      # Set a default value for this in case something goes wrong
      return flag

def getCountry(country: str) -> Country:
   """Returns a Country object from the country code."""
   if country == "" or not country:
      raise ValueError("Country code cannot be empty.")
   
   country = country.upper()
   flag = ""

   # List of coutnries, add more if you want
   match country:
      case "GER":
         country = "Germany"
      case "ITA":
         country = "Italy"
      case "JAP":
         country = "Japan"
      case "SOV":
         country = "Soviet Union"
      case "POL":
         country = "Poland"
      case "FRA":
         country = "France"
      case "USA":
         country = "United States"
      case "ENG":
         country = "United Kingdom"
      case other:
         # country = country ||| others countries
         country = "other"
      
   flag = getFlag(country)

   return Country(country, flag)
