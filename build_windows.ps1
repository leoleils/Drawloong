# ========================================
# 烛龙绘影 Drawloong Windows 打包脚本 (PowerShell)
# 版本: v1.17.1
# 编码: UTF-8
# ========================================

# 设置输出编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 设置国内镜像源
$env:PIP_INDEX_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"
$env:PIP_TRUSTED_HOST = "pypi.tuna.tsinghua.edu.cn"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  烛龙绘影 Drawloong Windows 打包脚本" -ForegroundColor Cyan
Write-Host "  版本: v1.17.1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 函数：显示步骤信息
function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host "[$Step] $Message" -ForegroundColor Green
}

# 函数：显示错误信息
function Write-Error-Message {
    param([string]$Message)
    Write-Host "[错误] $Message" -ForegroundColor Red
}

# 函数：显示警告信息
function Write-Warning-Message {
    param([string]$Message)
    Write-Host "[警告] $Message" -ForegroundColor Yellow
}

# 函数：显示信息
function Write-Info {
    param([string]$Message)
    Write-Host "[信息] $Message" -ForegroundColor Gray
}

# 1. 检查 Python 环境
Write-Step "1/7" "检查 Python 环境..."
try {
    $pythonVersion = python --version 2>&1
    Write-Info "Python 版本: $pythonVersion"
} catch {
    Write-Error-Message "未找到 Python，请先安装 Python 3.7+"
    Write-Host "下载地址: https://www.python.org/downloads/"
    Read-Host "按回车键退出"
    exit 1
}

# 2. 创建/激活虚拟环境
Write-Host ""
Write-Step "2/7" "检查虚拟环境..."
if (-not (Test-Path "venv")) {
    Write-Info "创建虚拟环境..."
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Message "创建虚拟环境失败"
        Read-Host "按回车键退出"
        exit 1
    }
}

Write-Info "激活虚拟环境..."
& .\venv\Scripts\Activate.ps1

# 3. 安装依赖
Write-Host ""
Write-Step "3/7" "安装依赖（使用清华镜像源）..."
Write-Info "镜像源: $env:PIP_INDEX_URL"

# 升级pip
Write-Info "升级 pip..."
python -m pip install --upgrade pip -i $env:PIP_INDEX_URL --trusted-host $env:PIP_TRUSTED_HOST 2>&1 | Out-Null

# 安装项目依赖
Write-Info "安装项目依赖..."
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt -i $env:PIP_INDEX_URL --trusted-host $env:PIP_TRUSTED_HOST
    if ($LASTEXITCODE -ne 0) {
        Write-Warning-Message "部分依赖安装失败，尝试继续..."
    }
} else {
    Write-Warning-Message "未找到 requirements.txt，安装基本依赖..."
    pip install PyQt5 requests opencv-python -i $env:PIP_INDEX_URL --trusted-host $env:PIP_TRUSTED_HOST
}

# 安装PyInstaller
Write-Info "安装 PyInstaller..."
pip install pyinstaller -i $env:PIP_INDEX_URL --trusted-host $env:PIP_TRUSTED_HOST
if ($LASTEXITCODE -ne 0) {
    Write-Error-Message "PyInstaller 安装失败"
    Read-Host "按回车键退出"
    exit 1
}

# 安装OpenCV（可选）
Write-Info "安装 OpenCV（用于视频缩略图）..."
pip install opencv-python -i $env:PIP_INDEX_URL --trusted-host $env:PIP_TRUSTED_HOST 2>&1 | Out-Null

# 安装Pillow（用于生成图标）
Write-Info "安装 Pillow（用于生成图标）..."
pip install Pillow -i $env:PIP_INDEX_URL --trusted-host $env:PIP_TRUSTED_HOST 2>&1 | Out-Null

# 3.5 生成ICO图标
Write-Host ""
Write-Step "3.5/7" "生成程序图标..."
if ((Test-Path "logo.png") -and (Test-Path "create_icon.py")) {
    Write-Info "正在从 logo.png 生成 logo.ico..."
    python create_icon.py
} elseif (-not (Test-Path "logo.png")) {
    Write-Warning-Message "未找到 logo.png，将不使用自定义图标"
} else {
    Write-Warning-Message "未找到 create_icon.py 脚本"
}

# 4. 清理旧的构建文件
Write-Host ""
Write-Step "4/7" "清理旧的构建文件..."
if (Test-Path "build") {
    Write-Info "删除 build 目录..."
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Write-Info "删除 dist 目录..."
    Remove-Item -Recurse -Force "dist"
}

# 5. 检查spec文件
Write-Host ""
Write-Step "5/7" "检查打包配置..."
if (-not (Test-Path "drawloong_windows.spec")) {
    Write-Warning-Message "未找到 drawloong_windows.spec，将使用默认配置"
}

# 6. 开始打包
Write-Host ""
Write-Step "6/7" "开始打包（这可能需要几分钟）..."
Write-Host ""

if (Test-Path "drawloong_windows.spec") {
    pyinstaller drawloong_windows.spec --noconfirm
} else {
    pyinstaller main.py --name Drawloong --windowed --noconfirm `
        --add-data "logo.png;." `
        --add-data "welcome.png;." `
        --add-data "themes;themes" `
        --add-data "config;config" `
        --hidden-import PyQt5 `
        --hidden-import cv2 `
        --hidden-import requests
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Error-Message "打包失败！请检查错误信息"
    Read-Host "按回车键退出"
    exit 1
}

# 7. 复制额外文件
Write-Host ""
Write-Step "7/7" "复制额外文件..."

$distPath = "dist\Drawloong"

# 复制文档
if (Test-Path "README.md") { Copy-Item "README.md" $distPath -Force }
if (Test-Path "CHANGELOG.md") { Copy-Item "CHANGELOG.md" $distPath -Force }
if (Test-Path "LICENSE") { Copy-Item "LICENSE" $distPath -Force }
if (Test-Path "logo.png") { Copy-Item "logo.png" $distPath -Force }

# 创建使用说明
$readmeContent = @"
烛龙绘影 Drawloong v1.17.1
==========================

使用方法:
  双击 Drawloong.exe 启动应用

首次使用:
  1. 启动应用后，点击"设置"按钮
  2. 输入您的 DashScope API 密钥
  3. 点击保存即可开始使用

获取API密钥:
  访问 https://dashscope.console.aliyun.com/

功能说明:
  - 首帧生视频: 从图片生成视频
  - 首尾帧生视频: 从两张图片生成过渡视频
  - 参考生视频: 从参考视频生成新视频 (新功能!)
  - 文生图: 从文字描述生成图片
  - 图像编辑: AI智能修图

技术支持:
  查看 README.md 获取更多帮助
"@
$readmeContent | Out-File -FilePath "$distPath\使用说明.txt" -Encoding UTF8

# 创建.env示例
$envContent = @"
# 烛龙绘影配置文件（已弃用）
# 从 v1.17.1 开始，推荐使用应用内"设置"界面配置 API 密钥

# DashScope API 密钥（已弃用，请使用应用内设置）
# DASHSCOPE_API_KEY=your_api_key_here

# 注意：
# 1. 推荐在应用的"设置"界面配置 API 密钥，更安全便捷
# 2. 系统配置使用加密存储，比文件配置更安全
# 3. 如果此文件中有API密钥，应用启动时会自动迁移到系统配置
"@
$envContent | Out-File -FilePath "$distPath\.env.example" -Encoding UTF8

# 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  打包完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "输出目录: $distPath" -ForegroundColor Cyan
Write-Host "可执行文件: $distPath\Drawloong.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "分发说明:" -ForegroundColor Yellow
Write-Host "  1. 将整个 Drawloong 文件夹打包分发"
Write-Host "  2. 用户解压后双击 Drawloong.exe 即可运行"
Write-Host "  3. 首次运行需要配置 API 密钥"
Write-Host ""
Write-Host "========================================" -ForegroundColor Green

Read-Host "按回车键退出"
