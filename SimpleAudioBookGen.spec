# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Usuario\\Desktop\\AudioBookGen\\audiobook_gen\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Usuario\\Desktop\\AudioBookGen\\icon.ico', '.'), ('C:\\Users\\Usuario\\Desktop\\AudioBookGen\\.ffmpeg_bin', '.ffmpeg_bin'), ('C:\\Users\\Usuario\\Desktop\\AudioBookGen\\_build_assets\\tesseract_bin', 'tesseract_bin'), ('C:\\Users\\Usuario\\Desktop\\AudioBookGen\\audiobook_gen\\rules', 'audiobook_gen/rules')],
    hiddenimports=['pytesseract', 'PIL', 'pydub', 'imageio_ffmpeg', 'audiobook_gen'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'pandas', 'scipy', 'matplotlib', 'tkinter', 'numba', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtNetwork', 'PySide6.QtSql'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SimpleAudioBookGen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\Usuario\\Desktop\\AudioBookGen\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='SimpleAudioBookGen',
)
