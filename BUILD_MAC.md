# Mac 应用打包指南

本文档说明如何为 WanX QT 客户端创建 Mac 应用程序包。

## 📦 快速打包

### 一键打包

```bash
cd qt_client
./build_mac.sh
```

打包完成后，将在 `dist/` 目录生成：
- `WanX.app` - Mac 应用程序（可直接运行）
- `WanX.dmg` - 安装镜像文件（推荐分发）

## 🔧 环境要求

### Python 环境
```bash
# Python 3.x
python --version

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller
```

### macOS 要求
- macOS 10.13 或更高版本
- Xcode Command Line Tools（用于代码签名）

## 📋 打包配置

### wanx.spec 文件

打包配置文件 `wanx.spec` 包含以下关键设置：

```python
# 应用名称
name='WanX'

# 包含的数据文件
datas=[
    ('config', 'config'),
    ('.env.example', '.'),
]

# 隐藏导入（确保打包所有依赖）
hiddenimports=[
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'requests',
    'dotenv',
]

# 应用信息
info_plist={
    'CFBundleName': 'WanX',
    'CFBundleDisplayName': 'WanX 图生视频',
    'CFBundleVersion': "1.0.0",
    'CFBundleShortVersionString': "1.0.0",
}
```

## 📁 打包产物

### dist/WanX.app
- Mac 应用程序包
- 可直接双击运行
- 大小约 400MB（包含 Python 运行时和所有依赖）

### dist/WanX.dmg
- Mac 安装镜像文件
- 大小约 162MB（压缩后）
- 推荐用于分发
- 用户可拖拽到 Applications 文件夹安装

## 🚀 分发流程

### 1. 本地测试
```bash
# 打开应用
open dist/WanX.app

# 或挂载 DMG
open dist/WanX.dmg
```

### 2. 分发给用户

**推荐方式：分发 DMG 文件**

用户操作：
1. 下载 `WanX.dmg`
2. 双击打开镜像
3. 拖拽 `WanX.app` 到 `Applications` 文件夹
4. 从 Launchpad 或 Applications 启动应用

### 3. 首次运行

用户首次运行可能遇到安全提示：

```
"WanX.app" 无法打开，因为它来自未验证的开发者
```

**解决方法：**
```bash
# 方法1：右键打开
右键点击应用 → 选择"打开" → 点击"打开"按钮

# 方法2：系统设置
系统偏好设置 → 安全性与隐私 → 通用 → 点击"仍要打开"

# 方法3：命令行（推荐）
xattr -cr /Applications/WanX.app
```

## 🔐 代码签名（可选）

### 免费签名（开发者账号）
```bash
# 查看可用签名
security find-identity -v -p codesigning

# 签名应用
codesign --deep --force --verify --verbose --sign "Developer ID" dist/WanX.app

# 验证签名
codesign --verify --verbose dist/WanX.app
spctl -a -vv dist/WanX.app
```

### 公证（App Store）
如需分发到 App Store 或通过公证，需要：
1. Apple Developer 账号（$99/年）
2. Developer ID 证书
3. 应用公证流程

## 📊 打包大小优化

### 当前大小
- 未压缩：~400MB
- DMG 压缩：~162MB

### 优化建议
1. **排除不必要的依赖**
   ```python
   # wanx.spec
   excludes=['test', 'pytest', 'unittest']
   ```

2. **UPX 压缩**（已启用）
   ```python
   upx=True
   ```

3. **移除调试信息**
   ```python
   debug=False
   strip=True
   ```

## 🛠️ 故障排除

### 问题1：打包失败
```bash
# 清理缓存
rm -rf build dist __pycache__

# 重新打包
./build_mac.sh
```

### 问题2：缺少模块
```bash
# 检查依赖
pip list

# 安装缺失的包
pip install -r requirements.txt
```

### 问题3：应用无法启动
```bash
# 从终端启动查看错误
./dist/WanX.app/Contents/MacOS/WanX

# 查看打包警告
cat build/wanx/warn-wanx.txt
```

### 问题4：找不到配置文件
确保 `wanx.spec` 中包含了所有需要的数据文件：
```python
datas=[
    ('config', 'config'),
    ('.env.example', '.'),
    # 添加其他需要的文件
]
```

## 📝 注意事项

### .env 配置
- 应用首次运行需要配置 API 密钥
- 用户需要复制 `.env.example` 为 `.env` 并填写密钥
- 配置文件位置：`~/Library/Application Support/WanX/.env`

### 数据目录
应用数据保存在：
```
~/Library/Application Support/WanX/
├── .env              # API 配置
├── projects/         # 工程文件
├── uploads/          # 上传的图片
└── downloads/        # 生成的视频
```

### 权限要求
应用需要以下权限：
- 文件访问（读写用户文件）
- 网络访问（调用 API）

## 🔄 更新版本

修改版本号：
```python
# wanx.spec
info_plist={
    'CFBundleVersion': "1.1.0",
    'CFBundleShortVersionString': "1.1.0",
}
```

重新打包：
```bash
./build_mac.sh
```

## 📚 相关文档

- [PyInstaller 官方文档](https://pyinstaller.org/)
- [Mac 应用打包指南](https://developer.apple.com/documentation/xcode/distributing-your-app-to-registered-devices)
- [代码签名文档](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

## 💡 最佳实践

1. **测试充分**
   - 在干净的 Mac 系统测试
   - 测试各种 macOS 版本
   - 验证所有功能正常

2. **版本管理**
   - 每次发布更新版本号
   - 保留历史版本的 DMG
   - 记录更新日志

3. **用户文档**
   - 提供安装指南
   - 说明首次运行步骤
   - 列出常见问题

4. **持续集成**
   - 可集成到 CI/CD 流程
   - 自动化打包和测试
   - 自动生成发布包

---

**🎉 现在你已经可以创建专业的 Mac 应用程序包了！**
