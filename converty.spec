# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Converty — Jade PDF Converter."""

from pathlib import Path
import sys

block_cipher = None

HERE = Path(SPEC).parent

a = Analysis(
    [str(HERE / "main.py")],
    pathex=[str(HERE)],
    binaries=[],
    datas=[
        (str(HERE / "assets"), "assets"),
        (str(HERE / "fonts"), "fonts"),
        (str(HERE / "vendor" / "poppler"), "vendor/poppler"),
    ],
    hiddenimports=[
        "pytesseract",
        "pdfplumber",
        "pdf2image",
        "docx",
        "PIL",
        "PIL.Image",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pandas", "scipy"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Converty",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(HERE / "assets" / "converty.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Converty",
)
