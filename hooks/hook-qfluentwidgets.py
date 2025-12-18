# -*- coding: utf-8 -*-
"""
PyInstaller hook for QFluentWidgets
确保 QFluentWidgets 的所有资源文件都被正确打包
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all

# 收集所有子模块、数据文件和二进制文件
datas, binaries, hiddenimports = collect_all('qfluentwidgets')

# 额外添加一些可能遗漏的隐藏导入
hiddenimports += [
    'qfluentwidgets._rc',
    'qfluentwidgets._rc.resource',
    'qfluentwidgets.common.config',
    'qfluentwidgets.common.style_sheet',
    'qfluentwidgets.common.theme_listener',
]
