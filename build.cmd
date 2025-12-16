@echo off
chcp 65001 >nul 2>&1
title 烛龙绘影 Drawloong 打包工具

echo.
echo ========================================
echo   烛龙绘影 Drawloong 打包工具
echo ========================================
echo.
echo 请选择打包方式:
echo.
echo   1. 使用 BAT 脚本打包 (兼容性好)
echo   2. 使用 PowerShell 脚本打包 (推荐)
echo   3. 退出
echo.

set /p choice=请输入选项 (1/2/3): 

if "%choice%"=="1" (
    echo.
    echo 正在启动 BAT 打包脚本...
    call build_windows.bat
) else if "%choice%"=="2" (
    echo.
    echo 正在启动 PowerShell 打包脚本...
    powershell -ExecutionPolicy Bypass -File build_windows.ps1
) else if "%choice%"=="3" (
    echo.
    echo 已退出
    exit /b 0
) else (
    echo.
    echo 无效选项，请重新运行
    pause
    exit /b 1
)
