# WIP
Currently working on it

## Won't work on all play modes

- Does not work on cloud
- Does not work when in Ironman mode
- Only Windows

## How it works

It uses the autosave to get data [ ... ]

TODO


# Source of the images:

https://hoi4.paradoxwikis.com/Hearts_of_Iron_4_Wiki
https://www.reddit.com/r/hoi4/comments/85l962/new_game_icon_made_by_me_the_original_sucks_free/
https://www.reddit.com/r/Steam/comments/enrddy/is_there_any_way_to_launch_another_program/

# Compiling from source:
go to /DiscordRPC and execute it using pyinstaller:

```pyinstaller.exe main.py --name hoi4RPC --onefile --noconsole --clean```

# Configuring the batch

The batch is for executing the RPC without doing it yourself

In `launcher-settings.json`, change exePath:

`"exePath": "runRPC.bat",`

Case if the save game folder isn't in C:/
In the batch, change the config...
TODO...