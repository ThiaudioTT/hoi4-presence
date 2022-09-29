from pypresence import Presence
import re
import time
import os
import psutil
import sys
import glob

try:
   client_id = '1021549599732809820'
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