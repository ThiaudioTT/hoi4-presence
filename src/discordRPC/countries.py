class Country:
   def __init__(self, name: str, flag: str):
      self.name = name
      self.flag = flag
   
   def __str__(self) -> str:
      return f"{self.name}, {self.flag}"

# List of countries, add more if you want
countries = {

   "GER" : ("Germany", "link"),
   "ITA" : ("Italy", "link"),
   "JAP" : ("Japan", "link"),
   "SOV" : ("Soviet Union", "link"),
   "POL" : ("Poland", "link"),
   "FRA" : ("France", "link"),
   "USA" : ("United States", "link"),
   "ENG" : ("United Kingdom", "link")

}

def getCountry(country: str) -> Country:
   """Returns a Country object from the country code."""
   if country == "" or not country:
      raise ValueError("Country code cannot be empty.")
   
   country = country.upper()

   # This is raised when there is a country that isn't in the countries dictionary
   if countries.get(country) is None:
      countries[country] = (country, "hoi4-icon")
   
   countryName = countries[country][0]
   flag = countries[country][1]

   return Country(countryName, flag)
