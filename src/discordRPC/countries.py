import requests

class Country:
   def __init__(self, name: str, flag: str):
      self.name = name
      self.flag = flag

def getFlag(flag: str) -> str:
<<<<<<< HEAD

    ''' 
    Gets the corresponding image of said country using an online JSON file that's located on the repo.
    '''

=======
    """Gets the corresponding image of said country using an online JSON file that's located on the repo."""

>>>>>>> parent of 4693c8d (Fixed indentation and adjusted Exception return)
    try:

      JSON = requests.get("https://raw.githubusercontent.com/ThiaudioTT/hoi4-presence/main/src/discordRPC/countries.json")

      return JSON.json()[flag]

    except Exception as e:

<<<<<<< HEAD
        print(e)

        return flag
=======
      print(e)
        
      # Set a default value for this in case something goes wrong
      return flag
>>>>>>> parent of 4693c8d (Fixed indentation and adjusted Exception return)

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
         flag = getFlag("german_reich")
      case "ITA":
         country = "Italy"
         flag = getFlag("italy")
      case "JAP":
         country = "Japan"
         flag = getFlag("japan")
      case "SOV":
         country = "Soviet Union"
         flag = getFlag("soviet_union")
      case "POL":
         country = "Poland"
         flag = getFlag("poland")
      case "FRA":
         country = "France"
         flag = getFlag("france")
      case "USA":
         country = "United States"
         flag = getFlag("united_states")
      case "ENG":
         country = "United Kingdom"
         flag = getFlag("united_kingdom")
      case other:
         # country = country ||| others countries
         flag = "hoi4-logo"

   return Country(country, flag)
