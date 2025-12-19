# -*- mode: python ; coding: utf-8 -*-
"""
烛龙绘影 Drawloong Windows 打包配置
版本: v1.16.0
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
if os.path.exists('welcome-cover.png'):
    datas.append(('welcome-cover.png', '.'))

# 添加开机动画视频
if os.path.exists('launch_animation.mp4'):
    datas.append(('launch_animation.mp4', '.'))

# 添加主题文件夹
if os.path.exists('themes'):
    datas.append(('themes', 'themes'))

# 添加配置文件夹
if os.path.exists('config'):
    datas.append(('config', 'config'))

# 添加工具文件夹
if os.path.exists('utils'):
    datas.append(('utils', 'utils'))

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
    hookspath=['hooks'],
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

# 图标文件路径
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
    icon=icon_file,  # 使用 logo.ico 作为程序图标
    version='version_info.txt',  # Windows 版本信息
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
