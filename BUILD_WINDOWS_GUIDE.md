# Windows 打包指南

## 📋 概述

本指南介绍如何在 Windows 系统上打包烛龙绘影 Drawloong 应用。

## 🔧 环境要求

### 必需
- Windows 10/11
- Python 3.7+ (推荐 3.10+)
- 网络连接（用于下载依赖）

### 推荐
- 8GB+ 内存
- 10GB+ 磁盘空间

## 🚀 快速开始

### 方法一：一键打包（推荐）

双击运行 `build.cmd`，选择打包方式：

```
1. 使用 BAT 脚本打包 (兼容性好)
2. 使用 PowerShell 脚本打包 (推荐)
```

### 方法二：使用 BAT 脚本

```cmd
build_windows.bat
```

### 方法三：使用 PowerShell 脚本

```powershell
# 允许执行脚本
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# 运行打包脚本
.\build_windows.ps1
```

## 📦 打包流程

### 1. 检查 Python 环境
脚本会自动检查 Python 是否已安装。

### 2. 创建虚拟环境
如果不存在 `venv` 目录，会自动创建虚拟环境。

### 3. 安装依赖
使用清华镜像源安装依赖，加速下载：
- PyQt5
- requests
- opencv-python
- PyInstaller

### 4. 清理旧文件
删除之前的 `build` 和 `dist` 目录。

### 5. 执行打包
使用 PyInstaller 打包应用。

### 6. 复制额外文件
复制文档、图标等文件到输出目录。

## 📁 输出结构

```
dist/
└── Drawloong/
    ├── Drawloong.exe      # 主程序
    ├── logo.png           # 图标
    ├── README.md          # 说明文档
    ├── CHANGELOG.md       # 更新日志
    ├── LICENSE            # 许可证
    ├── 使用说明.txt        # 中文使用说明
    ├── .env.example       # 配置示例
    └── _internal/         # 依赖文件
```

## 🌐 国内镜像源

脚本默认使用清华镜像源加速依赖下载：

```
https://pypi.tuna.tsinghua.edu.cn/simple
```

### 其他可用镜像源

| 镜像源 | 地址 |
|--------|------|
| 清华 | https://pypi.tuna.tsinghua.edu.cn/simple |
| 阿里云 | https://mirrors.aliyun.com/pypi/simple |
| 豆瓣 | https://pypi.douban.com/simple |
| 中科大 | https://pypi.mirrors.ustc.edu.cn/simple |

### 手动设置镜像源

```cmd
set PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
set PIP_TRUSTED_HOST=mirrors.aliyun.com
```

## 🔤 编码问题

### 解决乱码

脚本已自动处理编码问题：

**BAT 脚本**:
```cmd
chcp 65001 >nul 2>&1
```

**PowerShell 脚本**:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### 如果仍有乱码

1. 确保终端支持 UTF-8
2. 使用 PowerShell 脚本（推荐）
3. 检查系统区域设置

## ❓ 常见问题

### Q1: Python 未找到

**解决方案**:
1. 安装 Python: https://www.python.org/downloads/
2. 安装时勾选 "Add Python to PATH"
3. 重新打开命令行

### Q2: 依赖安装失败

**解决方案**:
1. 检查网络连接
2. 尝试其他镜像源
3. 手动安装依赖:
   ```cmd
   pip install PyQt5 requests opencv-python pyinstaller -i https://mirrors.aliyun.com/pypi/simple
   ```

### Q3: 打包失败

**解决方案**:
1. 检查错误信息
2. 确保所有依赖已安装
3. 尝试清理后重新打包:
   ```cmd
   rmdir /s /q build dist
   ```

### Q4: 程序无法启动

**解决方案**:
1. 检查是否缺少 DLL 文件
2. 安装 Visual C++ Redistributable
3. 以管理员身份运行

### Q5: 控制台窗口闪现

**解决方案**:
spec 文件中已设置 `console=False`，如果仍有问题：
1. 检查 spec 文件配置
2. 重新打包

## 🛠️ 自定义打包

### 修改应用名称

编辑 `drawloong_windows.spec`:
```python
exe = EXE(
    ...
    name='YourAppName',  # 修改这里
    ...
)
```

### 添加图标

1. 准备 `.ico` 格式图标文件
2. 命名为 `logo.ico`
3. 放在项目根目录
4. 重新打包

### 添加版本信息

编辑 `version_info.txt` 文件。

### 排除不需要的模块

编辑 `drawloong_windows.spec`:
```python
excludes = [
    'tkinter',
    'matplotlib',
    # 添加更多...
]
```

## 📊 打包大小优化

### 当前大小
约 150-200 MB（包含 PyQt5 和 OpenCV）

### 优化建议

1. **使用 UPX 压缩**（已启用）
2. **排除不需要的模块**
3. **使用 --onefile 模式**（会增加启动时间）

### 使用 --onefile 模式

```cmd
pyinstaller main.py --name Drawloong --windowed --onefile
```

注意：单文件模式启动较慢，不推荐。

## 📝 打包日志

打包过程中的日志保存在：
- `build/Drawloong/warn-Drawloong.txt`

## 🔄 更新打包

当代码更新后：

1. 拉取最新代码
2. 运行打包脚本
3. 测试新版本
4. 分发更新

## 📞 技术支持

如遇问题：
1. 查看错误日志
2. 检查 Python 和依赖版本
3. 参考常见问题
4. 提交 Issue

---

**最后更新**: 2025年12月16日  
**版本**: v1.15.0
