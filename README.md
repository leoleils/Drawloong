<p align="center">
  <img src="logo.png" alt="Drawloong Logo" width="120" height="120">
</p>

<h1 align="center">烛龙绘影 Drawloong</h1>

<p align="center">
  <strong>基于阿里云 DashScope 的多功能 AI 创作桌面客户端</strong>
</p>

<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPL v3">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.7+-green.svg" alt="Python 3.7+">
  </a>
  <a href="https://pypi.org/project/PyQt5/">
    <img src="https://img.shields.io/badge/PyQt5-5.15+-orange.svg" alt="PyQt5 5.15+">
  </a>
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Version-1.17.0-brightgreen.svg" alt="Version">
</p>

<p align="center">
  <img src="welcome-cover.png" alt="Drawloong Welcome Screen" width="800">
</p>

---

## 功能特性

| 功能 | 说明 |
|------|------|
| **首帧生视频** | 单张图片生成动态视频 |
| **首尾帧生视频** | 两帧图片生成过渡动画 |
| **参考生视频** | 参考视频生成新场景 |
| **文生图** | 文字描述生成图片 |
| **图像编辑** | AI 智能修图与融合 |

### 核心亮点

- **工程管理** - 类似 VSCode 的项目管理体验，自动组织输入/输出文件
- **拖拽支持** - 从资源管理器拖拽图片，支持外部文件导入
- **内置预览** - 图片查看器支持缩放，视频播放器即时预览
- **实时监控** - 任务进度实时更新，支持历史记录管理
- **多模型支持** - 万相2.6、万相2.5、万相2.2、通义千问等多种模型

---

## 快速开始

### 环境要求

- Python 3.7+
- PyQt5 5.15+
- macOS / Windows / Linux

### 安装步骤

**方式一：一键启动（推荐）**

```bash
# macOS / Linux
./run.sh

# Windows
run.bat
```

**方式二：手动安装**

```bash
# 克隆项目
git clone https://github.com/your-username/drawloong.git
cd drawloong

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动应用
python main.py
```

### 配置 API 密钥

1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/) 获取 API Key
2. 启动应用后，点击「设置」按钮
3. 在设置页面输入 API 密钥并保存

---

## 使用指南

### 创建工程

启动应用 → 点击「新建工程」→ 输入工程名称 → 选择保存位置 → 创建

### 工程结构

```
我的工程/
├── pictures/        # 图集（输入图片）
├── videos/          # 视频集（输出视频）
├── project.json     # 工程配置
└── tasks.json       # 任务记录
```

### 功能使用

| 功能 | 操作步骤 |
|------|----------|
| **首帧生视频** | 上传图片 → 填写提示词 → 选择模型/分辨率 → 生成 |
| **首尾帧生视频** | 上传首帧+尾帧 → 描述过渡效果 → 生成动画 |
| **参考生视频** | 上传参考视频 → 使用 character1/2 描述 → 生成新场景 |
| **文生图** | 输入文字描述 → 选择风格/尺寸 → 生成图片 |
| **图像编辑** | 上传图片 → 输入编辑指令 → AI 处理 |

---

## 项目结构

```
drawloong/
├── main.py                 # 应用入口
├── requirements.txt        # Python 依赖
├── config/                 # 配置管理
├── core/                   # 核心业务（API、任务、工程管理）
├── ui/                     # 用户界面组件
└── themes/                 # 主题配置
```

---

## 打包发布

### Windows

```batch
build_windows.bat
```

输出：`dist\Drawloong\Drawloong.exe`

### macOS

```bash
./build_mac.sh
```

输出：`dist/Drawloong.app`

详细说明请查看 [BUILD_GUIDE.md](BUILD_GUIDE.md)

---

## 安全性

- **密钥存储** - 使用系统安全存储，支持界面配置
- **数据隐私** - 所有数据本地存储，仅 API 调用时上传
- **工程隔离** - 各工程数据独立，互不干扰

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 开源许可

本项目采用 **GNU General Public License v3.0** 开源协议。

### 第三方组件

| 组件 | 许可证 | 用途 |
|------|--------|------|
| PyQt5 | GPL-3.0 | GUI 框架 |
| QFluentWidgets | GPL-3.0 | Fluent UI 组件 |
| requests | Apache-2.0 | 网络请求 |
| opencv-python | MIT | 视频缩略图生成 |

---

## 更新日志

### v1.17.0 (2025-12-23)
- **新增 Z-Image Turbo 模型** - 极速文生图，轻量级快速生成
- **万相2.6 批量生成支持** - 支持1-4张图片批量生成，大幅提升效率
- **万相2.5/2.2 批量优化** - 使用单次API调用代替多次调用，减少75%请求次数
- **通义千问模型限制修正** - 正确限制为单张生成，避免API错误
- **智能错误处理系统** - 详细的错误分类和解决建议，提升用户体验
- **动态UI调整** - 根据不同模型能力自动调整界面选项

### v1.16.2 (2025-12-19)
- 欢迎页面全屏背景图优化
- 修复 QFluentWidgets TabWidget 兼容性问题
- Windows 打包脚本支持多镜像源
- README 简化，去掉拟物化图标

### v1.16.1 (2025-12-19)
- 全面 UI 优化 - 参考视频生成页面和首尾帧生成页面 Fluent 化
- 四象限布局 - 统一布局风格
- 修复任务完成时视频被下载两次的问题
- 修复 QFluentWidgets ComboBox 兼容性问题

### v1.16.0 (2025-12-18)
- 全新 QFluent UI 界面美化
- 新增 Fluent Design 风格主题系统
- 新增抽屉式项目资源管理器和任务列表
- 新增 Fluent 风格状态栏

### v1.15.2 (2025-12-16)
- 图集和视频集严格文件类型控制
- 拖拽导入时自动识别文件类型

### v1.14.0 (2025-12-15)
- 新增万相2.6模型支持
- 支持5秒、10秒、15秒三种时长选择
- 新增智能镜头类型选择

<details>
<summary>查看更多版本</summary>

### v1.13.0 (2025-12-15)
- 首尾帧页面图片预览区域增大
- 视频集点击播放功能
- 资源管理器界面优化

### v1.12.0 (2025-12-14)
- 新增图集拖拽到各功能页面
- 首帧生成视频新增双按钮选择

### v1.11.0 (2025-12-12)
- 提示词展示功能优化

### v1.10.0 (2025-12-12)
- 智能错误提示系统

</details>

---

## 致谢

- [阿里云 DashScope](https://dashscope.console.aliyun.com/) - AI 能力支持
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
- [QFluentWidgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) - Fluent UI 组件

---

<p align="center">
  <sub>Made with ❤️ by Drawloong Team</sub>
</p>
