# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: builds the five executables and packs them into a release zip.

Run from the repository root with `pyinstaller build.spec`. This only works on
Windows and is exercised in CI by the workflows in .github/workflows/.

The exe names below are load-bearing -- the launcher shim, the installer and the
updater all refer to them as strings. Rename the source script, never the exe.
"""

import json
import os
import shutil
import zipfile

block_cipher = None

# `src` on the analysis path is what lets the entry scripts import hoi4presence.
# SPECPATH is injected by PyInstaller and points at this file's directory, so the
# build does not depend on the working directory it was launched from.
SRC_PATH = os.path.join(SPECPATH, "src")
ENTRYPOINTS = os.path.join(SRC_PATH, "entrypoints")

# (entry script, exe name, needs a console window)
TARGETS = [
    (os.path.join(ENTRYPOINTS, "hoi4RPC.py"), "hoi4Presence", False),
    (os.path.join(ENTRYPOINTS, "checkupdate.py"), "checkupdate", True),
    (os.path.join(ENTRYPOINTS, "launcher.py"), "runRPC", False),
    (os.path.join(ENTRYPOINTS, "installer.py"), "setup", True),
    (os.path.join(ENTRYPOINTS, "uninstaller.py"), "uninstall", True),
]

for scriptPath, exeName, hasConsole in TARGETS:
    analysis = Analysis(
        [scriptPath],
        pathex=[SRC_PATH],
        binaries=[],
        datas=[],
        hiddenimports=[],
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        # rich hard-depends on pygments and markdown-it-py, so pip installs them
        # into the build environment -- but only rich.syntax, rich.markdown and
        # rich.traceback reach them, and hoi4presence.ui imports none of those.
        # Excluding them keeps several MB per exe out of the release if a hook
        # ever decides to collect_all("rich"). Drop this if anyone wants
        # RichHandler(rich_tracebacks=True).
        excludes=["pygments", "markdown_it", "mdurl"],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False,
    )
    pyz = PYZ(analysis.pure, analysis.zipped_data, cipher=block_cipher)
    EXE(
        pyz,
        analysis.scripts,
        analysis.binaries,
        analysis.zipfiles,
        analysis.datas,
        [],
        name=exeName,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=hasConsole,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )


# --- Packaging -------------------------------------------------------------
# Everything below runs after PyInstaller has written dist/, and assembles the
# release zip. Written to be re-runnable without cleaning dist/ first.

print("Starting to bundle...")

# DISTPATH is where PyInstaller actually wrote the exes -- it is cwd-relative and
# --distpath can move it, so deriving it from SPECPATH would miss them.
DIST = DISTPATH
PAYLOAD = os.path.join(DIST, "discordRPC")

os.makedirs(PAYLOAD, exist_ok=True)

# Files that ship alongside the executables, copied straight into the payload.
EXTRA_FILES = [
    (os.path.join(SPECPATH, "version.json"), "version.json"),
]

# Executables that live inside discordRPC/; setup and uninstall stay at the root.
PAYLOAD_EXES = ["hoi4Presence.exe", "checkupdate.exe", "runRPC.exe"]

for exeName in PAYLOAD_EXES:
    built = os.path.join(DIST, exeName)
    if os.path.exists(built):
        print(f"Moving {exeName}...")
        # os.replace, not shutil.move: move falls back to os.rename here, which
        # raises on Windows when a previous build already left the file there.
        os.replace(built, os.path.join(PAYLOAD, exeName))

for sourcePath, name in EXTRA_FILES:
    print(f"Copying {name}...")
    shutil.copy(sourcePath, os.path.join(PAYLOAD, name))

with open(os.path.join(SPECPATH, "version.json")) as versionFile:
    version = json.load(versionFile)["version"]

print(f"Version: {version}")
print("Zipping files...")

# The release asset name the updater looks for is derived from the release tag,
# so a tag must be exactly "v<version>" for auto-update to find this. See AGENTS.md.
zipName = os.path.join(SPECPATH, f"hoi4-presence-v{version}.zip")

with zipfile.ZipFile(zipName, "w") as archive:
    for name in PAYLOAD_EXES + [name for _, name in EXTRA_FILES]:
        archive.write(os.path.join(PAYLOAD, name), f"./discordRPC/dist/{name}")
    archive.write(os.path.join(DIST, "setup.exe"), "./setup.exe")
    archive.write(os.path.join(DIST, "uninstall.exe"), "./uninstall.exe")

print(f"Done! Wrote {zipName}")
