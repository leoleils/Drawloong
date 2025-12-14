# 烛龙绘影 Drawloong

基于 PyQt5 的多功能 AI 创作桌面客户端，集成了阿里云 DashScope API，支持图片转视频、文生图、图像编辑等多种 AI 创作功能。

<div align="center">
  <img src="logo.png" alt="Drawloong Logo" width="200">
</div>

## 🌟 项目简介

烛龙绘影 (Drawloong) 是一款功能强大的 AI 创作工具，采用现代化的标签页架构设计，支持多种 AI 生成功能。它提供了类似 VSCode 的工程管理系统，让用户能够轻松管理和组织多个创作项目。

## 🎯 核心功能

### 📁 工程管理系统
- 类似 VSCode 的项目管理体验
- 支持创建和打开本地工程
- 自动组织输入/输出文件
- 最近使用工程快速访问
- 独立的任务历史记录

### 🎬 多功能标签页架构
- **🎬 首帧生视频**：上传单张图片生成视频动画
- **🔄 首尾帧生视频**：上传起始帧和结束帧生成过渡动画
- **🎨 文生图**：通过文字描述生成图片
- **✂️ 图像编辑**：AI智能修图、背景移除/替换等

### 🖼️ 文件管理与浏览
- 可视化工程资源管理器
- 内置图片查看器，支持缩放、快捷键操作
- 双击视频文件即可播放
- 图片缩略图预览
- 文件重命名功能

### 🔄 拖拽支持
- 从资源管理器拖拽图片到上传区域
- 从外部拖拽文件到资源管理器导入
- 从外部拖拽图片到上传区域
- 智能文件分类导入（图片→inputs，视频→outputs）

### ⚙️ 实时任务监控
- 实时任务进度监控
- 视频预览与下载
- 历史任务管理
- 自定义提示词配置
- 多模型、多分辨率支持

## 🛠️ 技术架构

### 前端技术栈
- **GUI 框架**：PyQt5
- **异步处理**：QThread
- **界面设计**：现代化标签页架构，类似 VSCode 的三栏式布局

### 后端技术栈
- **网络请求**：requests
- **数据持久化**：JSON
- **配置管理**：QSettings + dotenv
- **API 服务**：阿里云 DashScope

### 核心模块
```
drawloong/
├── main.py                 # 应用入口
├── requirements.txt        # Python 依赖
├── .env.example           # 环境变量示例
├── README.md              # 项目说明
├── run.sh                 # 启动脚本 (macOS/Linux)
├── run.bat                # 启动脚本 (Windows)
├── build_mac.sh           # macOS 打包脚本
├── wanx.spec              # PyInstaller 配置
│
├── config/                # 配置管理
│   ├── __init__.py
│   └── settings.py        # 配置加载和管理
│
├── core/                  # 核心业务逻辑
│   ├── __init__.py
│   ├── models.py          # 数据模型定义
│   ├── api_client.py      # DashScope API 客户端
│   ├── task_manager.py    # 任务管理器
│   └── project_manager.py # 工程管理器
│
├── ui/                    # 用户界面
│   ├── __init__.py
│   ├── main_window.py     # 主窗口
│   ├── upload_widget.py   # 图片上传组件
│   ├── config_panel.py    # 配置面板
│   ├── task_list.py       # 任务列表
│   ├── settings_dialog.py # 设置对话框
│   ├── welcome_page.py    # 欢迎页面
│   ├── project_explorer.py# 工程资源管理器
│   ├── project_dialog.py  # 工程对话框
│   ├── image_viewer.py    # 图片查看器
│   ├── video_player.py    # 视频播放器
│   ├── video_viewer.py    # 视频浏览器
│   ├── text_to_image_widget.py # 文生图组件
│   ├── image_edit_widget.py    # 图像编辑组件
│   └── keyframe_to_video_widget.py # 首尾帧生视频组件
│
├── utils/                 # 工具函数
│   ├── __init__.py
│   ├── file_handler.py    # 文件处理工具
│   └── helpers.py        # 辅助函数
│
└── themes/                # 主题管理
    ├── __init__.py
    └── themes.py         # 主题配置
```

## 🚀 快速开始

### 环境要求
- Python 3.7+
- PyQt5 5.15+
- 阿里云 DashScope API 密钥

### 安装步骤

#### 方法一：使用启动脚本（推荐）
```bash
# macOS/Linux
./run.sh

# Windows
run.bat
```

#### 方法二：手动安装
1. 克隆项目：
   ```bash
   git clone git@gitlab.alibaba-inc.com:drawloong/drawloong.git
   cd drawloong
   ```

2. 创建虚拟环境：
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # 或
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 配置 API 密钥：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入您的 DashScope API 密钥
   ```

5. 运行应用：
   ```bash
   python main.py
   ```

### 首次使用

1. **配置 API 密钥**
   - 启动应用后会提示配置 API 密钥
   - 点击 "是" 打开设置对话框
   - 输入你的阿里云 DashScope API 密钥
   - 点击 "保存"

2. **创建工程**
   - 在欢迎页面点击 "新建工程" 或使用菜单 "文件" -> "新建工程"
   - 输入工程名称和选择保存位置
   - 可选填写工程描述
   - 点击 "创建"

3. **开始创作**
   - 点击不同的标签页切换功能
   - 上传图片或输入文字描述
   - 配置生成参数
   - 点击生成按钮
   - 在资源管理器中查看结果

## 📁 工程管理

### 工程结构
每个工程包含以下文件夹：
```
我的工程/
├── inputs/          # 输入素材文件夹
├── outputs/         # 输出结果文件夹
├── project.json     # 工程配置文件
└── tasks.json       # 任务记录文件
```

### 操作指南

#### 创建工程
1. 在欢迎页面点击 "新建工程"
2. 输入工程名称和选择保存位置
3. 可选填写工程描述
4. 点击 "创建"

#### 打开工程
- 使用菜单 "文件" -> "打开工程"
- 或在欢迎页面选择最近使用的工程
- 选择工程文件夹即可打开

#### 关闭工程
- 使用菜单 "文件" -> "关闭工程"
- 关闭后会返回到欢迎页面

## 🎨 功能详解

### 🎬 首帧生视频
将单张图片转换为视频动画：
1. 上传首帧图片
2. 填写提示词和参数
3. 选择模型和分辨率
4. 点击"生成视频"
5. 在视频浏览器中查看效果

### 🔄 首尾帧生视频
通过起始帧和结束帧生成过渡动画：
1. 上传起始帧和结束帧图片
2. 填写过渡描述
3. 配置动画参数
4. 点击"生成动画"
5. 查看生成的过渡视频

### 🎨 文生图
通过文字描述生成图片：
1. 在文本框中输入描述
2. 选择风格和尺寸
3. 配置生成参数
4. 点击"生成图片"
5. 在画廊中查看结果

### ✂️ 图像编辑
AI智能修图功能：
1. 上传需要编辑的图片
2. 输入编辑指令（如"移除背景"）
3. 选择编辑模型
4. 点击"开始编辑"
5. 查看编辑后的结果

## 🔧 开发指南

### 项目结构说明

#### MVC 架构模式
- **Model (核心模块)**: 数据和业务逻辑 (`core/`)
- **View (界面模块)**: 用户界面展示 (`ui/`)
- **Controller (主窗口)**: 协调 Model 和 View (`ui/main_window.py`)

#### 信号槽机制
使用 PyQt5 的信号槽机制实现组件间通信，确保松耦合和良好的可维护性。

### 核心流程

#### 应用启动流程
```
main.py
  ↓
创建 QApplication
  ↓
初始化 MainWindow
  ↓
加载配置 (settings)
  ↓
初始化核心组件 (TaskManager, APIClient)
  ↓
创建 UI 组件
  ↓
显示主窗口
```

#### 视频生成流程
```
用户上传图片
  ↓
UploadWidget 发送信号
  ↓
MainWindow 接收并保存图片路径
  ↓
用户配置参数并点击生成
  ↓
ConfigPanel 发送配置信号
  ↓
MainWindow 创建任务
  ↓
调用 API 提交任务
  ↓
启动监控线程 (TaskMonitorThread)
  ↓
定期查询任务状态
  ↓
任务完成后下载视频
  ↓
更新任务列表
```

## 📦 打包发布

### macOS 打包
```bash
./build_mac.sh
```

### 通用打包
使用 PyInstaller 打包为独立可执行文件：
```bash
pip install pyinstaller
pyinstaller --name="烛龙绘影" --windowed --icon=logo.icns main.py
```

## 🔒 安全性

### API 密钥管理
- 使用 QSettings 安全存储 API 密钥
- 支持界面配置，无需手动编辑文件
- 密钥在系统配置中加密存储
- 支持 .env 文件作为备用配置方案

### 数据隐私
- 所有数据本地存储
- 不会上传用户图片到第三方服务器（除调用 API 外）
- 工程数据独立存储，互不干扰

## 🐛 常见问题

### API 密钥配置问题
**问题**：设置无法保存或密钥保存后仍提示未配置
**解决方案**：
1. 检查应用是否有写入权限
2. 重启应用
3. 检查密钥格式（应以 sk- 开头）

### 依赖安装问题
**问题**：无法安装 PyQt5 或其他依赖
**解决方案**：
1. 确保 Python 版本 >= 3.7
2. 更新 pip 到最新版本
3. 尝试使用国内镜像源安装

### 启动问题
**问题**：应用无法启动或闪退
**解决方案**：
1. 检查是否安装了完整的 PyQt5
2. 查看控制台错误信息
3. 确保 .env 文件配置正确

## 📈 版本更新

### v1.3.3 - 文件重命名功能 (2025-12-11)
- 新增文件重命名功能
- 支持直接在资源管理器中重命名文件
- 智能扩展名处理和重名检测

### v1.3.2 - 图片缩略图功能 (2025-12-11)
- 资源管理器中的图片文件显示真实缩略图预览
- 提升文件识别效率

### v1.3.0 - 拖拽与文件浏览功能 (2025-12-11)
- 实现完整的拖拽支持和文件浏览功能
- 新增图片查看器和视频播放器
- 增强的拖拽功能

### v1.2.0 - 工程管理功能 (2025-12-11)
- 实现类似 VSCode 的工程管理系统
- 支持本地工程创建、打开和管理
- 文件自动组织功能

## 🤝 技术支持

如遇问题请检查：
- API 密钥配置是否正确
- 网络连接是否正常
- Python 和依赖版本是否满足要求
- 是否有足够的磁盘空间

## 📄 开源许可证

烛龙绘影 (Drawloong) 是一个开源项目，遵循 GNU General Public License v3.0 (GPL-3.0) 许可证发布。

- [LICENSE](LICENSE) - 项目许可证文件
- [NOTICE](NOTICE) - 第三方组件声明文件

本项目使用了以下第三方开源组件：
- PyQt5 (GPL-3.0)
- requests (Apache License 2.0)
- python-dotenv (BSD 3-Clause)

详细信息请参阅 [NOTICE](NOTICE) 文件。

## 🙏 致谢

感谢阿里云 DashScope 提供强大的 AI 能力支持。