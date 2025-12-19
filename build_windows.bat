@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM ========================================
REM 烛龙绘影 Drawloong Windows 打包脚本
REM 版本: v1.16.1
REM ========================================

echo.
echo ========================================
echo   烛龙绘影 Drawloong Windows 打包脚本
echo   版本: v1.16.2
echo ========================================
echo.

REM 设置国内镜像源
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
set PIP_EXTRA_INDEX=https://mirrors.aliyun.com/pypi/simple/

REM 检查 Python 环境
echo [1/8] 检查 Python 环境...
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
echo [2/8] 检查虚拟环境...
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

REM 升级pip
echo.
echo [3/8] 升级 pip（使用清华镜像源）...
echo [信息] 镜像源: %PIP_INDEX_URL%
python -m pip install --upgrade pip -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%

REM 安装基础依赖
echo.
echo [4/8] 安装基础依赖...
pip install PyQt5 -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%
pip install requests python-dotenv -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%

REM 安装 QFluentWidgets（尝试多个源）
echo.
echo [5/8] 安装 QFluentWidgets...
echo [信息] 尝试从清华源安装...
pip install PyQt-Fluent-Widgets -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%
if errorlevel 1 (
    echo [信息] 清华源失败，尝试阿里云源...
    pip install PyQt-Fluent-Widgets -i %PIP_EXTRA_INDEX% --trusted-host mirrors.aliyun.com
)
if errorlevel 1 (
    echo [信息] 阿里云源失败，尝试官方源...
    pip install PyQt-Fluent-Widgets
)
if errorlevel 1 (
    echo [警告] QFluentWidgets 安装失败，应用将使用降级模式运行
)

REM 安装其他依赖
echo.
echo [6/8] 安装其他依赖...
pip install opencv-python -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%
pip install Pillow -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%
pip install pyinstaller -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%

REM 生成ICO图标文件
echo.
echo [6.5/8] 生成程序图标...
if exist "logo.png" (
    if exist "create_icon.py" (
        echo [信息] 正在从 logo.png 生成 logo.ico...
        python create_icon.py
    )
)

REM 清理旧的构建文件
echo.
echo [7/8] 清理旧的构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM 开始打包
echo.
echo [8/8] 开始打包（这可能需要几分钟）...
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
echo [完成] 复制额外文件...
if exist "README.md" copy /y README.md dist\Drawloong\ >nul 2>&1
if exist "CHANGELOG.md" copy /y CHANGELOG.md dist\Drawloong\ >nul 2>&1
if exist "LICENSE" copy /y LICENSE dist\Drawloong\ >nul 2>&1
if exist "logo.png" copy /y logo.png dist\Drawloong\ >nul 2>&1

REM 创建使用说明
echo 烛龙绘影 Drawloong v1.16.2 > dist\Drawloong\使用说明.txt
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

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 输出目录: dist\Drawloong
echo 可执行文件: dist\Drawloong\Drawloong.exe
echo.

pause
exit /b 0
