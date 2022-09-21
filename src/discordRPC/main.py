from pypresence import Presence
from pathlib import Path
import re
import time

client_id = '1021549599732809820'
RPC = Presence(client_id)  # Initialize the Presence class
RPC.connect()  # Start the handshake loop

while True:  # The presence will stay on as long as the program is running, so use some lib
   try:
      # save = open("C:/Dev/hoi4RPCpy/src/save games/autosave.hoi4", "r", errors="ignore")
      path = Path(__file__).parent.parent / "save games/autosave.hoi4"
      save = open(path, "r", errors="ignore")
      data = save.readline() # it will be a line full of unicode chars
      save.close() # close file, hoi4 needs to have access to write it, see path.py in tests.

      data = re.findall("\w+", data, flags=re.A) # now it is an array of data

      # TODO: put the government type
      RPC.update(
         details="Playing as " + data[1], # put this in a var, use switch
         state=data[2],
         large_image="german_reich"
      )
      
      # TODO: use a switch case to get the country name
      print(data) # debug
   except Exception as e:
      print(e)
   # time.sleep(60) #Wait a wee bit
   time.sleep(5)