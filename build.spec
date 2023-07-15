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


# MERGE is used after the analysis phase and before EXE. Its variable-length list of arguments consists of a list of tuples, each tuple having three elements:

# The first element is an Analysis object, an instance of class Analysis, as applied to one of the apps.

# The second element is the script name of the analyzed app (without the .py extension).

# The third element is the name for the executable (usually the same as the script).
    
MERGE( (hoi4RPC_a, 'hoi4RPC', 'hoi4Presence'), (checkupdate_a, 'checkupdate', 'checkupdate'), (setup_a, 'setup', 'setup') )


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