# Hoi4 Discord Rich presence

![demonstration](/tests/demo.PNG)

## Download and install

Download the lastest presence from:

[Releases](https://github.com/ThiaudioTT/hoi4-presence/releases)

It's named as `hoi4-presence-vVERSION.zip`

Extract the files into a folder, and

Then, execute `setup.exe` to install.

The script will do all the work for you.

After the execution, you can delete the files.

## Uninstalling

Inside your game folder, you will see a file named `launcher-settings.json`.

Inside of it:

change `"exePath": "runRPC.exe",` to
`"exePath": "hoi4.exe",`

You can delete all the other files originated from discord presence.

## Submiting an issue

Found a bug? Submit it in:

[Issues](https://github.com/ThiaudioTT/hoi4-presence/issues)

## Contributing

Feel free to contribute! I will be happy to see your pull request.

First, read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## how the presence works?

It uses the saves to get data. So, spend one month in the game or save the game to update the presence.

TODO...

## Image sources

[Hoi4 Wiki](https://hoi4.paradoxwikis.com/Hearts_of_Iron_4_Wiki)

[Logo](https://www.reddit.com/r/hoi4/comments/85l962/new_game_icon_made_by_me_the_original_sucks_free/)

## Compiling from source

You dont believe in my .exe files? :(

Go to /DiscordRPC and execute it using pyinstaller:

```pyinstaller.exe main.py --name hoi4Presence --noconsole --clean```

Don't compile in one file, it wont work.

### Configuring the batch

The batch is for executing the presence without doing it yourself.

In `launcher-settings.json` (in your game folder), change exePath:

`"exePath": "runRPC.bat",`

if the save game folder isn't in your documents folder
change the line in `runRPC.bat` manually.

### Changing settings.txt

in settings.txt, (in your save folder) change:

save_as_binary=no

and you're done.
