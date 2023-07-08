set "documentsPath=C:\Users\%USERNAME%\Documents\Paradox Interactive\Hearts of Iron IV"
@REM This is file for executing the game and the presence, delete if you have uninstalled and change launcher-settings.json

echo "starting hoi4RPC..."
start "hoi4.exe" ".\hoi4.exe"

@REM Start checkupdate
start "checkupdate.exe" "%documentsPath%\hoi4Presence\checkupdate.exe"

@REM start "hoi4RPC.exe" "PATH TO DISCORD RPC, IN CASE IT IS ON ANOTHER FOLDER"
start "hoi4RPC.exe" "%documentsPath%\hoi4Presence\hoi4Presence.exe"
exit