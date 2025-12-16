@echo off
REM ========================================
REM 烛龙绘影 Windows 打包脚本
REM ========================================

echo ========================================
echo 烛龙绘影 Windows 打包脚本
echo ========================================
echo.

REM 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo [1/5] 检查依赖...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装 PyInstaller...
    pip install pyinstaller
)

echo.
echo [2/5] 清理旧的构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo.
echo [3/5] 开始打包...
pyinstaller drawloong_windows.spec

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo [4/5] 复制额外文件...
REM 复制文档文件
copy README.md dist\Drawloong\ >nul 2>&1
copy CHANGELOG.md dist\Drawloong\ >nul 2>&1
copy LICENSE dist\Drawloong\ >nul 2>&1

REM 创建快捷方式说明
echo 双击 Drawloong.exe 启动应用 > dist\Drawloong\使用说明.txt
echo. >> dist\Drawloong\使用说明.txt
echo 首次使用请在应用中配置 API 密钥 >> dist\Drawloong\使用说明.txt
echo 访问 https://dashscope.console.aliyun.com/ 获取密钥 >> dist\Drawloong\使用说明.txt

echo.
echo [5/5] 打包完成！
echo.
echo ========================================
echo 输出目录: dist\Drawloong
echo 可执行文件: dist\Drawloong\Drawloong.exe
echo ========================================
echo.
echo 提示：
echo 1. 可以将整个 Drawloong 文件夹分发给用户
echo 2. 用户双击 Drawloong.exe 即可运行
echo 3. 首次运行需要配置 API 密钥
echo.

pause
