# 烛龙绘影 打包指南

本文档详细说明如何在不同平台上打包烛龙绘影应用。

## 📋 前置要求

### 通用要求
- Python 3.7 或更高版本
- 已安装所有依赖：`pip install -r requirements.txt`
- PyInstaller：`pip install pyinstaller`

### Windows 特定要求
- Windows 7 或更高版本
- 如需图标，准备 `logo.ico` 文件

### macOS 特定要求
- macOS 10.13 或更高版本
- 如需图标，准备 `logo.icns` 文件
- Xcode Command Line Tools（可选，用于代码签名）

## 🪟 Windows 打包

### 方法一：使用打包脚本（推荐）

```batch
build_windows.bat
```

脚本会自动完成以下步骤：
1. 检查 Python 和 PyInstaller
2. 清理旧的构建文件
3. 执行打包
4. 复制文档文件
5. 创建使用说明

### 方法二：手动打包

```batch
# 1. 清理旧文件
rmdir /s /q build dist

# 2. 执行打包
pyinstaller drawloong_windows.spec

# 3. 测试运行
dist\Drawloong\Drawloong.exe
```

### 输出说明

打包完成后，在 `dist\Drawloong\` 目录下会生成：
- `Drawloong.exe` - 主程序
- 各种 DLL 和依赖文件
- `config/` - 配置文件
- `themes/` - 主题文件
- 资源文件（logo.png, welcome.png 等）

### 分发

将整个 `dist\Drawloong\` 文件夹打包为 ZIP 或制作安装程序：

```batch
# 创建 ZIP 压缩包
cd dist
powershell Compress-Archive -Path Drawloong -DestinationPath Drawloong-v1.14.0-Windows.zip
```

## 🍎 macOS 打包

### 方法一：使用打包脚本（推荐）

```bash
chmod +x build_mac.sh
./build_mac.sh
```

### 方法二：手动打包

```bash
# 1. 清理旧文件
rm -rf build dist

# 2. 执行打包
pyinstaller wanx.spec

# 3. 测试运行
open dist/Drawloong.app
```

### 输出说明

打包完成后，在 `dist/` 目录下会生成：
- `Drawloong.app` - macOS 应用程序包

### 代码签名（可选）

如果需要分发给其他用户，建议进行代码签名：

```bash
# 查看可用的签名证书
security find-identity -v -p codesigning

# 签名应用
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/Drawloong.app

# 验证签名
codesign --verify --deep --strict --verbose=2 dist/Drawloong.app
```

### 创建 DMG 安装包（可选）

```bash
# 安装 create-dmg
brew install create-dmg

# 创建 DMG
create-dmg \
  --volname "Drawloong" \
  --volicon "logo.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "Drawloong.app" 200 190 \
  --hide-extension "Drawloong.app" \
  --app-drop-link 600 185 \
  "Drawloong-v1.14.0-macOS.dmg" \
  "dist/"
```

## 🐧 Linux 打包

### 打包步骤

```bash
# 1. 清理旧文件
rm -rf build dist

# 2. 执行打包
pyinstaller wanx.spec

# 3. 测试运行
./dist/Drawloong/Drawloong
```

### 创建 AppImage（可选）

```bash
# 安装 appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# 创建 AppDir 结构
mkdir -p Drawloong.AppDir/usr/bin
cp -r dist/Drawloong/* Drawloong.AppDir/usr/bin/

# 创建 desktop 文件
cat > Drawloong.AppDir/drawloong.desktop << EOF
[Desktop Entry]
Name=Drawloong
Exec=Drawloong
Icon=drawloong
Type=Application
Categories=Graphics;
EOF

# 复制图标
cp logo.png Drawloong.AppDir/drawloong.png

# 生成 AppImage
./appimagetool-x86_64.AppImage Drawloong.AppDir Drawloong-v1.14.0-Linux.AppImage
```

## 🔧 常见问题

### 1. 打包后程序无法启动

**可能原因：**
- 缺少依赖库
- 路径问题

**解决方法：**
```bash
# 查看详细错误信息（Windows）
dist\Drawloong\Drawloong.exe --debug

# 查看详细错误信息（macOS/Linux）
./dist/Drawloong/Drawloong --debug
```

### 2. 图标未显示

**解决方法：**
- Windows: 确保 `logo.ico` 存在
- macOS: 确保 `logo.icns` 存在
- 检查 spec 文件中的 icon 路径

### 3. 打包体积过大

**优化方法：**
```python
# 在 spec 文件中添加排除项
excludes=[
    'matplotlib',
    'numpy',
    'pandas',
    # 其他不需要的库
]
```

### 4. opencv-python 打包问题

如果遇到 opencv 相关错误：

```bash
# 确保安装了 opencv-python
pip install opencv-python

# 在 spec 文件中添加隐藏导入
hiddenimports=[
    'cv2',
    'cv2.cv2',
]
```

### 5. Windows Defender 误报

打包后的 exe 可能被 Windows Defender 误报为病毒。

**解决方法：**
1. 添加代码签名证书
2. 向 Microsoft 提交误报申诉
3. 提供源代码和打包脚本供用户自行打包

## 📝 版本更新清单

每次发布新版本时，需要更新以下文件：

- [ ] `main.py` - `__version__`
- [ ] `wanx.spec` - `CFBundleVersion` 和 `CFBundleShortVersionString`
- [ ] `drawloong_windows.spec` - 如果有版本相关配置
- [ ] `version_info.txt` - `filevers` 和 `prodvers`
- [ ] `README.md` - 版本号徽章
- [ ] `CHANGELOG.md` - 更新日志

## 🚀 自动化打包（CI/CD）

### GitHub Actions 示例

创建 `.github/workflows/build.yml`：

```yaml
name: Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install pyinstaller
      - run: pyinstaller drawloong_windows.spec
      - uses: actions/upload-artifact@v2
        with:
          name: Drawloong-Windows
          path: dist/Drawloong

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install pyinstaller
      - run: pyinstaller wanx.spec
      - uses: actions/upload-artifact@v2
        with:
          name: Drawloong-macOS
          path: dist/Drawloong.app
```

## 📞 技术支持

如遇到打包问题，请：
1. 查看本文档的常见问题部分
2. 检查 PyInstaller 官方文档
3. 提交 Issue 并附上详细的错误信息

---

**最后更新**：2025-12-16
**适用版本**：v1.14.0
