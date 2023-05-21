from pypresence import Presence
import re
import time
import os
import psutil
import sys
import glob

# FLAGS FOR THE COMPILER: --name hoi4Presence --noconsole --onefile

try:
   client_id = '1109742258309308477'
   RPC = Presence(client_id)  # Initialize the Presence class
   RPC.connect()  # Start the handshake loop

   playTime = time.time()

   # default values
   RPC.update(
      details="In menus...",
      large_image="hoi4-logo", # put this in a var?
      large_text="thiaudiott/hoi4-presence on Github!",
      start=playTime
   )
except Exception as e:
   print(e)
   time.sleep(5)
   sys.exit(1) # when discord isnt found, exit script

gameRunning = True
while gameRunning:  # The presence will stay on as long as the program is running, so use some lib
   try:

      path = "" # path to the saves
      if getattr(sys, 'frozen', False):
         path = os.path.dirname(sys.executable)
      else:
         path = os.path.dirname(os.path.abspath(__file__))
      
      path = os.path.abspath(path + "/../" + "/save games/*.hoi4")

      # getting the last modified save file
      listSaves = glob.glob(path)
      lastSavePath = max(listSaves, key=os.path.getmtime)

      dateFile = int(os.path.getmtime(lastSavePath))
      now = int(time.time())
      saveNew = False
      if (now - dateFile) <= 120: # calc to see if save is recently (2 min recently)
         saveNew = True
      else:
         saveNew = False
      
      if(saveNew): 
         # putting this in a function might be good.

         save = open(lastSavePath, "r")
         data = ""
         for i in range(5):
            data += save.readline()
         save.close() # close file, hoi4 needs to have access to write it, see path.py in tests.

         data = re.sub("(HOI4txt|player=|ideology=|date=|difficulty=|\")", "", data).split()
         # example of data:
         # ['GER', 'fascism', '1936.2.1.2', 'normal']

         # defining the country
         country = data[0]
         flag = "" # to be set later
         ideology = data[1]
         year = data[2][:4]
         mode = data[3]

         match country:
            case "GER":
               country = "German Reich"
               flag = "german_reich"
            case "AFG":
               country = "Afghanistan"
               flag = "afghanistan"
            case "ALB":
               country = "Albania"
               flag = "albania"
            case "ARG":
               country = "Argentina"
               flag = "argentina"
            case "AFA":
               country = "Sultanate of Aussa"
               flag = "aussa"
            case "AST":
               country = "Australia"
               flag = "australia"
            case "AUS":
               country = "Austria"
               flag = "austria"
            case "BEL":
               country = "Belgium"
               flag = "belgium"
            case "BHU":
               country = "Bhutan"
               flag = "bhutan"
            case "BOL":
               country = "Bolivia"
               flag = "bolivia"
            case "BRA":
               country = "Brazil"
               flag = "brazil"
            case "MAL":
               country = "British Malaya"
               flag = "british_malaya"
            case "RAJ":
               country = "British Raj"
               flag = "british_raj"
            case "BUL":
               country = "Bulgaria"
               flag = "bulgaria"
            case "CAN":
               country = "Dominion of Canada"
               flag = "canada"
            case "CHL":
               country = "Chile"
               flag = "chile"
            case "CHI":
               country = "China"
               flag = "china"
            case "COL":
               country = "Colombia"
               flag = "colombia"
            case "PRC":
               country = "People's Republic of China"
               flag = "prc"
            case "COS":
               country = "Costa Rica"
               flag = "costa_rica"
            case "CUB":
               country = "Cuba"
               flag = "cuba"
            case "CZE":
               country = "Czechoslovakia"
               flag = "czechoslovakia"
            case "DEN":
               country = "Denmark"
               flag = "denmark"
            case "DOM":
               country = "Dominican Republic"
               flag = "dominican_republic"
            case "INS":
               country = "Dutch East Indies"
               flag = "netherlands"
            case "ECU":
               country = "Ecuador"
               flag = "ecuador"
            case "ELS":
               country = "El Salvador"
               flag = "el_salvador"
            case "EST":
               country = "Estonia"
               flag = "estonia"
            case "ETH":
               country = "Ethiopia"
               flag = "ethiopia"
            case "FIN":
               country = "Finland"
               flag = "finland"
            case "FRA":
               country = "France"
               flag = "france"
            case "GRE":
               country = "Greece"
               flag = "greece"
            case "GXC":
               country = "Guangxi Clique"
               flag = "guangxi_clique"
            case "GUA":
               country = "Guatemala"
               flag = "guatemala"
            case "HAI":
               country = "Haiti"
               flag = "haiti"
            case "HON":
               country = "Honduras"
               flag = "honduras"
            case "HUN":
               country = "Hungary"
               flag = "hungary"
            case "PER":
               country = "Iran"
               flag = "iran"
            case "IRQ":
               country = "Iraq"
               flag = "iraq"
            case "IRE":
               country = "Ireland"
               flag = "ireland"
            case "ITA":
               country = "Italy"
               flag = "italy"
            case "JAP":
               country = "Japan"
               flag = "japan"
            case "LAT":
               country = "Latvia"
               flag = "latvia"
            case "LIB":
               country = "Liberia"
               flag = "liberia"
            case "LIT":
               country = "Lithuania"
               flag = "lithuania"
            case "LUX":
               country = "Luxembourg"
               flag = "luxembourg"
            case "MAN":
               country = "Manchukuo"
               flag = "manchukuo"
            case "MEN":
               country = "Mengkukuo"
               flag = "mengkukuo"
            case "MEX":
               country = "Mexico"
               flag = "mexico"
            case "MON":
               country = "Mongolia"
               flag = "mongolia"
            case "NEP":
               country = "Nepal"
               flag = "nepal"
            case "HOL":
               country = "Netherlands"
               flag = "netherlands"
            case "NZL":
               country = "New Zealand"
               flag = "new_zealand"
            case "NIC":
               country = "Nicaragua"
               flag = "nicaragua"
            case "OMA":
               country = "Oman"
               flag = "aussa"
            case "PAN":
               country = "Panama"
               flag = "panama"
            case "PAR":
               country = "Paraguay"
               flag = "paraguay"
            case "PRU":
               country = "Peru"
               flag = "peru"
            case "PHI":
               country = "Philippines"
               flag = "philipines"
            case "POL":
               country = "Poland"
               flag = "poland"
            case "POR":
               country = "Portugal"
               flag = "portugal"
            case "ROM":
               country = "Romania"
               flag = "kingdom_of_romania"
            case "SAU":
               country = "Saudi Arabia"
               flag = "saudiarabia"
            case "SHX":
               country = "Shanxi"
               flag = "shanxi"
            case "SIA":
               country = "Siam"
               flag = "siam"
            case "SIK":
               country = "Sinkiang"
               flag = "sinkiang"
            case "SAF":
               country = "South Africa"
               flag = "saf"
            case "SOV":
               country = "Soviet Union"
               flag = "soviet_union"
            case "SPR":
               country = "Spain"
               flag = "spain"
            case "SWE":
               country = "Sweden"
               flag = "sweden"
            case "SWI":
               country = "Switzerland"
               flag = "switzerland"
            case "TAN":
               country = "Tannu Tuva"
               flag = "tannu"
            case "TIB":
               country = "Tibet"
               flag = "tibet"
            case "TUR":
               country = "Turkey"
               flag = "turkey"
            case "ENG":
               country = "British Empire"
               flag = "british_empire"
            case "USA":
               country = "United States of America"
               flag = "usa"
            case "URG":
               country = "Uruguay"
               flag = "uruguay"
            case "VEN":
               country = "Venezuela"
               flag = "venezuela"
            case "XSM":
               country = "Xibei San Ma"
               flag = "shanxi"
            case "YEM":
               country = "Yemen"
               flag = "yemen"
            case "YUG":
               country = "Yugoslavia"
               flag = "yugoslavia"
            case "YUN":
               country = "Yunnan"
               flag = "shanxi"
            case other:
               country = data[1]
               flag = "hoi4-logo"
         
         # hint: use discord developer portal
         RPC.update(
            state="Year: " + year,
            details="Playing as " + country,
            large_image=flag,
            large_text="Ideology: " + ideology,
            small_image="hoi4-logo",
            small_text="In " + mode + " mode",
            start=playTime
         )
         
         print(data) # debug
   except Exception as e:
      print(e)
      time.sleep(5)
   
   time.sleep(30) #Wait a wee bit
   gameRunning = False
   for proc in psutil.process_iter():
      if proc.name() == "hoi4.exe":
         gameRunning = True
         break

sys.exit(0) # when game running is false, exit script