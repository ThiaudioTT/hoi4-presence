class Country:
   def __init__(self, name: str, flag: str):
      self.name = name
      self.flag = flag

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
         flag = "german_reich"
      case "ITA":
         country = "Italy"
         flag = "italy"
      case "JAP":
         country = "Japan"
         flag = "japan"
      case "SOV":
         country = "Soviet Union"
         flag = "soviet_union"
      case "POL":
         country = "Poland"
         flag = "poland"
      case "FRA":
         country = "France"
         flag = "france"
      case "USA":
         country = "United States"
         flag = "united_states"
      case "ENG":
         country = "United Kingdom"
         flag = "united_kingdom"
      case other:
         # country = country ||| others countries
         flag = "hoi4-logo"

   return Country(country, flag)
