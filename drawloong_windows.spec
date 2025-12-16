# -*- mode: python ; coding: utf-8 -*-
"""
烛龙绘影 Drawloong Windows 打包配置
版本: v1.15.0
"""

import os
import sys

block_cipher = None

# 获取当前目录
CURRENT_DIR = os.path.dirname(os.path.abspath(SPEC))

# 数据文件
datas = []

# 添加图片资源
if os.path.exists('logo.png'):
    datas.append(('logo.png', '.'))
if os.path.exists('welcome.png'):
    datas.append(('welcome.png', '.'))

# 添加主题文件夹
if os.path.exists('themes'):
    datas.append(('themes', 'themes'))

# 添加配置文件夹
if os.path.exists('config'):
    datas.append(('config', 'config'))

# 隐藏导入
hiddenimports = [
    # PyQt5
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.QtMultimedia',
    'PyQt5.QtMultimediaWidgets',
    'PyQt5.sip',
    
    # 网络请求
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    
    # 图像处理
    'cv2',
    'numpy',
    'PIL',
    'PIL.Image',
    
    # 其他
    'json',
    'uuid',
    'datetime',
    'pathlib',
    'tempfile',
    'base64',
]

# 排除不需要的模块
excludes = [
    'tkinter',
    'matplotlib',
    'scipy',
    'pandas',
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    'sphinx',
]

a = Analysis(
    ['main.py'],
    pathex=[CURRENT_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# 检查图标文件
icon_file = None
if os.path.exists('logo.ico'):
    icon_file = 'logo.ico'

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
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
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
