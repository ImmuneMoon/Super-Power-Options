# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec - works on Windows, macOS and Linux.
# PyInstaller can only build for the OS it runs on; GitHub Actions builds all three.

import os
import sys
import customtkinter

customtkinter_path = os.path.dirname(customtkinter.__file__)
IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"

APP_NAME = "Super Power Options"
ICON = "assets/icon.ico" if IS_WIN else "assets/icon.png"  # PyInstaller converts PNG -> .icns on macOS

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/icon.ico', 'assets'),
        ('assets/icon.png', 'assets'),
        ('assets/alert.wav', 'assets'),
        ('assets/*_Button.png', 'assets'),
        (customtkinter_path, 'customtkinter'),
    ],
    hiddenimports=['CTkToolTip', 'PowerApp.PowerPlatform'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if IS_MAC:
    # macOS: a proper .app bundle (onedir inside the bundle)
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=APP_NAME,
        debug=False,
        strip=False,
        upx=False,
        console=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=ICON,
    )
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=APP_NAME)
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon=ICON,
        bundle_identifier="com.fulllion.superpoweroptions",
        info_plist={
            "NSHighResolutionCapable": True,
            # Needed for "tell System Events to restart / shut down"
            "NSAppleEventsUsageDescription": "Super Power Options uses System Events to restart or shut down your Mac.",
        },
    )
else:
    # Windows / Linux: single-file executable
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name=APP_NAME,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=IS_WIN,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=ICON,
        version='version.txt' if IS_WIN and os.path.exists('version.txt') else None,
    )
