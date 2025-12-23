# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('.env.example', '.'),
        ('logo.png', '.'),
        ('welcome.png', '.'),
        ('welcome-cover.png', '.'),
        ('launch_animation.mp4', '.'),
        ('themes', 'themes'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtMultimedia',
        'PyQt5.QtMultimediaWidgets',
        'requests',
        'dotenv',
        'cv2',
        'numpy',
        # QFluentWidgets 相关
        'qfluentwidgets',
        'qfluentwidgets.common',
        'qfluentwidgets.common.config',
        'qfluentwidgets.common.style_sheet',
        'qfluentwidgets.common.theme_listener',
        'qfluentwidgets.components',
        'qfluentwidgets.window',
        'qfluentwidgets._rc',
        'qfluentwidgets._rc.resource',
    ],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Drawloong',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Drawloong',
)

app = BUNDLE(
    coll,
    name='Drawloong.app',
    icon='logo.icns',
    bundle_identifier='com.zhulong.drawloong',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleName': 'Drawloong',
        'CFBundleDisplayName': '烛龙绘影 Drawloong',
        'CFBundleGetInfoString': "烛龙绘影 - AI图像视频生成应用",
        'CFBundleVersion': "1.17.0",
        'CFBundleShortVersionString': "1.17.0",
        'NSHighResolutionCapable': 'True',
        # 解决 App Translocation 问题
        'LSUIElement': False,
        'NSRequiresAquaSystemAppearance': False,  # 支持深色模式
    },
)
