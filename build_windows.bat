@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM ========================================
REM 烛龙绘影 Drawloong Windows 打包脚本
REM 版本: v1.16.0
REM ========================================

echo.
echo ========================================
echo   烛龙绘影 Drawloong Windows 打包脚本
echo   版本: v1.16.0
echo ========================================
echo.

REM 设置国内镜像源
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

REM 检查 Python 环境
echo [1/7] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [信息] Python 版本: %PYTHON_VERSION%

REM 创建虚拟环境（如果不存在）
echo.
echo [2/7] 检查虚拟环境...
if not exist "venv" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo [信息] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip并安装依赖
echo.
echo [3/7] 安装依赖（使用清华镜像源）...
echo [信息] 镜像源: %PIP_INDEX_URL%

python -m pip install --upgrade pip -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%

REM 安装项目依赖
echo [信息] 安装项目依赖...
pip install -r requirements.txt -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%
if errorlevel 1 (
    echo [警告] 部分依赖安装失败，尝试继续...
)

REM 安装打包工具
echo [信息] 安装 PyInstaller...
pip install pyinstaller -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%
if errorlevel 1 (
    echo [错误] PyInstaller 安装失败
    pause
    exit /b 1
)

REM 安装可选依赖（OpenCV用于视频缩略图）
echo [信息] 安装 OpenCV（可选，用于视频缩略图）...
pip install opencv-python -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%

REM 安装Pillow（用于生成图标）
echo [信息] 安装 Pillow（用于生成图标）...
pip install Pillow -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%

REM 生成ICO图标文件
echo.
echo [3.5/7] 生成程序图标...
if exist "logo.png" (
    if exist "create_icon.py" (
        echo [信息] 正在从 logo.png 生成 logo.ico...
        python create_icon.py
    ) else (
        echo [警告] 未找到 create_icon.py 脚本
    )
) else (
    echo [警告] 未找到 logo.png，将不使用自定义图标
)

REM 清理旧的构建文件
echo.
echo [4/7] 清理旧的构建文件...
if exist "build" (
    echo [信息] 删除 build 目录...
    rmdir /s /q build
)
if exist "dist" (
    echo [信息] 删除 dist 目录...
    rmdir /s /q dist
)

REM 检查spec文件
echo.
echo [5/7] 检查打包配置...
if not exist "drawloong_windows.spec" (
    echo [信息] 创建打包配置文件...
    call :create_spec_file
)

REM 开始打包
echo.
echo [6/7] 开始打包（这可能需要几分钟）...
echo.
pyinstaller drawloong_windows.spec --noconfirm

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！请检查错误信息
    pause
    exit /b 1
)

REM 复制额外文件
echo.
echo [7/7] 复制额外文件...

REM 复制文档
if exist "README.md" copy /y README.md dist\Drawloong\ >nul 2>&1
if exist "CHANGELOG.md" copy /y CHANGELOG.md dist\Drawloong\ >nul 2>&1
if exist "LICENSE" copy /y LICENSE dist\Drawloong\ >nul 2>&1
if exist "logo.png" copy /y logo.png dist\Drawloong\ >nul 2>&1

REM 创建使用说明
echo 烛龙绘影 Drawloong v1.16.0 > dist\Drawloong\使用说明.txt
echo. >> dist\Drawloong\使用说明.txt
echo 使用方法: >> dist\Drawloong\使用说明.txt
echo   双击 Drawloong.exe 启动应用 >> dist\Drawloong\使用说明.txt
echo. >> dist\Drawloong\使用说明.txt
echo 首次使用: >> dist\Drawloong\使用说明.txt
echo   1. 启动应用后，点击"设置"按钮 >> dist\Drawloong\使用说明.txt
echo   2. 输入您的 DashScope API 密钥 >> dist\Drawloong\使用说明.txt
echo   3. 点击保存即可开始使用 >> dist\Drawloong\使用说明.txt
echo. >> dist\Drawloong\使用说明.txt
echo 获取API密钥: >> dist\Drawloong\使用说明.txt
echo   访问 https://dashscope.console.aliyun.com/ >> dist\Drawloong\使用说明.txt
echo. >> dist\Drawloong\使用说明.txt
echo 功能说明: >> dist\Drawloong\使用说明.txt
echo   - 首帧生视频: 从图片生成视频 >> dist\Drawloong\使用说明.txt
echo   - 首尾帧生视频: 从两张图片生成过渡视频 >> dist\Drawloong\使用说明.txt
echo   - 参考生视频: 从参考视频生成新视频 >> dist\Drawloong\使用说明.txt
echo   - 文生图: 从文字描述生成图片 >> dist\Drawloong\使用说明.txt
echo   - 图像编辑: AI智能修图 >> dist\Drawloong\使用说明.txt
echo. >> dist\Drawloong\使用说明.txt
echo 技术支持: >> dist\Drawloong\使用说明.txt
echo   查看 README.md 获取更多帮助 >> dist\Drawloong\使用说明.txt

REM 创建.env示例文件
echo # 烛龙绘影配置文件 > dist\Drawloong\.env.example
echo # 复制此文件为 .env 并填入您的API密钥 >> dist\Drawloong\.env.example
echo. >> dist\Drawloong\.env.example
echo # DashScope API 密钥 >> dist\Drawloong\.env.example
echo DASHSCOPE_API_KEY=your_api_key_here >> dist\Drawloong\.env.example

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 输出目录: dist\Drawloong
echo 可执行文件: dist\Drawloong\Drawloong.exe
echo.
echo 分发说明:
echo   1. 将整个 Drawloong 文件夹打包分发
echo   2. 用户解压后双击 Drawloong.exe 即可运行
echo   3. 首次运行需要配置 API 密钥
echo.
echo ========================================

pause
exit /b 0

:create_spec_file
REM 创建PyInstaller spec文件
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo block_cipher = None
echo.
echo a = Analysis^(
echo     ['main.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[
echo         ^('logo.png', '.'^^),
echo         ^('welcome.png', '.'^^),
echo         ^('themes', 'themes'^^),
echo         ^('config', 'config'^^),
echo     ],
echo     hiddenimports=[
echo         'PyQt5',
echo         'PyQt5.QtCore',
echo         'PyQt5.QtGui',
echo         'PyQt5.QtWidgets',
echo         'PyQt5.QtMultimedia',
echo         'PyQt5.QtMultimediaWidgets',
echo         'cv2',
echo         'numpy',
echo         'requests',
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^^)
echo.
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=block_cipher^^)
echo.
echo exe = EXE^(
echo     pyz,
echo     a.scripts,
echo     [],
echo     exclude_binaries=True,
echo     name='Drawloong',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo     icon='logo.ico' if os.path.exists^('logo.ico'^^) else None,
echo ^^)
echo.
echo coll = COLLECT^(
echo     exe,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     name='Drawloong',
echo ^^)
) > drawloong_windows.spec
goto :eof
