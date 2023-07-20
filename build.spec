# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


hoi4RPC_a = Analysis(
    ['src/discordRPC/hoi4RPC.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
hoi4RPC_pyz = PYZ(hoi4RPC_a.pure, hoi4RPC_a.zipped_data, cipher=block_cipher)
hoi4RPC_exe = EXE(
    hoi4RPC_pyz,
    hoi4RPC_a.scripts,
    hoi4RPC_a.binaries,
    hoi4RPC_a.zipfiles,
    hoi4RPC_a.datas,
    [],
    name='hoi4Presence',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

checkupdate_a = Analysis(
    ['src/checkupdate/checkupdate.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
checkupdate_pyz = PYZ(checkupdate_a.pure, checkupdate_a.zipped_data, cipher=block_cipher)
checkupdate_exe = EXE(
    checkupdate_pyz,
    checkupdate_a.scripts,
    checkupdate_a.binaries,
    checkupdate_a.zipfiles,
    checkupdate_a.datas,
    [],
    name='checkupdate',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

setup_a = Analysis(
    ['src/setup.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
setup_pyz = PYZ(setup_a.pure, setup_a.zipped_data, cipher=block_cipher)
setup_exe = EXE(
    setup_pyz,
    setup_a.scripts,
    setup_a.binaries,
    setup_a.zipfiles,
    setup_a.datas,
    [],
    name='setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# script to bundle

print("Starting to bundle...")
import shutil

# copy files 
print("Copying runRPC.bat...")
shutil.copy("src/runRPC.bat", "dist/runRPC.bat")

print("Copying version.json...")
shutil.copy("./version.json", "dist/version.json")

# todo: add readme.txt with instruction of the installation


# Moving files
# Note: probably we dont need it since we can zip the files directly from the dist folder, but is good for testing and development
import os
if not os.path.exists("dist/discordRPC"): os.mkdir("dist/discordRPC")

print("Moving hoi4Presence.exe...")
shutil.move("dist/hoi4Presence.exe", "dist/discordRPC/hoi4Presence.exe")

print("Moving checkupdate.exe...")
shutil.move("dist/checkupdate.exe", "dist/discordRPC/checkupdate.exe")

print("Moving runRPC.bat...")
shutil.move("dist/runRPC.bat", "dist/discordRPC/runRPC.bat")

print("Moving version.json...")
shutil.move("dist/version.json", "dist/discordRPC/version.json")

# zipping files:
print("Preparing to zip files...")
import json
import zipfile

# reading version.json to get the version
print("Getting version...")
with open("./version.json", "r") as f: version = json.load(f)["version"]

print("Version: " + version)

print("Zipping files...")

# example of zip name: hoi4-presence-vVERSION.zip
with zipfile.ZipFile("hoi4-presence-v" + version + ".zip", "w") as zip:
    zip.write("dist/discordRPC/hoi4Presence.exe", "./discordRPC/hoi4Presence.exe")
    zip.write("dist/discordRPC/checkupdate.exe", "./discordRPC/checkupdate.exe")
    zip.write("dist/discordRPC/runRPC.bat", "./discordRPC/runRPC.bat")
    zip.write("dist/discordRPC/version.json", "./discordRPC/version.json")
    # zip.write("README.txt", "./README.txt")
    zip.write("dist/setup.exe", "./setup.exe")

print("Done!")
