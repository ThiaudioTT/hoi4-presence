from pypresence import Presence
from pathlib import Path
import re
import time
import os
import psutil

try:
   client_id = '1021549599732809820'
   RPC = Presence(client_id)  # Initialize the Presence class
   RPC.connect()  # Start the handshake loop

   playTime = time.time()

   # default values
   RPC.update(
      details="In launcher",
      large_image="hoi4-logo", # put this in a var?
      start=playTime
   )
except Exception as e:
   print(e)
   time.sleep(5)
   exit() # when discord isnt found, exit script

gameRunning = True
while gameRunning:  # The presence will stay on as long as the program is running, so use some lib
   try:

      path = Path(__file__).parent.parent / "save games/autosave.hoi4"
      dateFile = int(os.path.getmtime(path))
      now = int(time.time())
      saveNew = False
      if (now - dateFile) <= 65: # calc to see if autosave is renctly
         saveNew = True
      else:
         saveNew = False

      
      if(saveNew): 
         # putting this in a function might be good.

         save = open(path, "r", errors="ignore")
         data = save.readline() # it will be a line full of unicode chars
         save.close() # close file, hoi4 needs to have access to write it, see path.py in tests.
         data = re.findall("[A-Z_]+", data, flags=re.A|re.I) # now it is an array of data

         # define country, hint: use discord developer portal
         gov = data[3][:-1] # get the government type and remove J char
         mode = data[4]

         flag = ""
         country = data[2]

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
         
         RPC.update(
            state="In " + gov,
            details="Playing as " + country,
            large_image=flag,
            large_text="Hearts of Iron IV",
            small_image="hoi4-logo",
            small_text="In " + mode + " mode",
            start=playTime
         )
         
         print(data) # debug
   except Exception as e:
      print(e)
   
   time.sleep(60) #Wait a wee bit
   gameRunning = False
   for proc in psutil.process_iter():
      if proc.name() == "hoi4.exe" or proc.name() == "Paradox Launcher.exe":
         gameRunning = True
         break

exit() # when game running is false, exit script