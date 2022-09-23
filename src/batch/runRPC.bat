@REM This is file for executing the game and the presence, delete if you have uninstalled and change launcher-settings.json

echo "starting hoi4RPC..."
start "hoi4.exe" "./hoi4.exe"

@REM start "hoi4RPC.exe" "PATH TO DISCORD RPC, IN CASE IT IS ON ANOTHER FOLDER"
start "hoi4RPC.exe" "C:\Users\%USERNAME%\Documents\Paradox Interactive\Hearts of Iron IV\discordRPC\hoi4Presence.exe"
exit