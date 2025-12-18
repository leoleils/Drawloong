#!/bin/bash

echo "🚀 开始打包烛龙绘影 Mac 应用..."

# 进入项目目录
cd "$(dirname "$0")"

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo "🔧 激活虚拟环境..."
    source .venv/bin/activate
fi

# 检查 PyInstaller 是否安装
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller 未安装，正在安装..."
    pip install pyinstaller
fi

# 清理之前的构建
echo "🧹 清理之前的构建..."
rm -rf build dist

# 使用 PyInstaller 打包
echo "📦 使用 PyInstaller 打包..."
pyinstaller --clean --noconfirm wanx.spec

# 检查打包是否成功
if [ -d "dist/Drawloong.app" ]; then
    echo "✅ 打包成功！"
    echo "📍 应用位置: dist/Drawloong.app"
    
    # 创建 DMG 文件
    echo "💿 创建 DMG 镜像..."
    
    # 创建临时文件夹
    mkdir -p dist/dmg
    cp -r dist/Drawloong.app dist/dmg/
    
    # 创建应用程序快捷方式
    ln -s /Applications dist/dmg/Applications
    
    # 移除 quarantine 属性（解决 App Translocation 问题）
    echo "🔓 移除 quarantine 属性..."
    xattr -cr dist/dmg/Drawloong.app
    
    # 创建 DMG
    hdiutil create -volname "烛龙绘影" -srcfolder dist/dmg -ov -format UDZO dist/Drawloong.dmg
    
    # 清理临时文件
    rm -rf dist/dmg
    
    if [ -f "dist/Drawloong.dmg" ]; then
        echo "✅ DMG 创建成功！"
        echo "📍 DMG 位置: dist/Drawloong.dmg"
        echo ""
        echo "📊 文件大小:"
        ls -lh dist/Drawloong.dmg
        echo ""
        echo "🎉 打包完成！可以分发 dist/Drawloong.dmg 文件"
        echo ""
        echo "💡 提示: 如果用户安装后遇到问题，可以运行以下命令移除 quarantine 属性:"
        echo "   xattr -cr /Applications/Drawloong.app"
    else
        echo "⚠️  DMG 创建失败，但 .app 文件可用"
    fi
else
    echo "❌ 打包失败！请检查错误信息"
    exit 1
fi
