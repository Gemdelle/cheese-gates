# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('font', 'font'), ('assets', 'assets'), ('audio\\\\audio_config.json', 'audio'), ('background.jpg', '.'), ('bar.png', '.'), ('box.png', '.'), ('button.png', '.'), ('cage.png', '.'), ('character-moving.png', '.'), ('character-standing.png', '.'), ('cheese.png', '.'), ('circuit-1.png', '.'), ('circuit-2.png', '.'), ('circuit-3.png', '.'), ('circuit-4.png', '.'), ('final-bg.png', '.'), ('level-1.png', '.'), ('level-2.png', '.'), ('level-3.png', '.'), ('level-4.png', '.'), ('level-5.png', '.'), ('level-bg.png', '.'), ('level-selection-bg.png', '.'), ('lose-bg.png', '.'), ('platform.png', '.'), ('rock-big.png', '.'), ('rock-small.png', '.'), ('splash.png', '.'), ('summary-instructions.png', '.'), ('tutorial-bg.png', '.'), ('win-bg.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CheeseGates',
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
