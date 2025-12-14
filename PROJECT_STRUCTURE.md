# QT 客户端项目结构

## 目录结构

```
qt_client/
├── main.py                    # 应用程序入口
├── requirements.txt           # Python 依赖
├── .env.example              # 环境变量示例
├── .gitignore                # Git 忽略文件
├── README.md                 # 项目说明
├── run.sh                    # 启动脚本 (macOS/Linux)
├── run.bat                   # 启动脚本 (Windows)
│
├── config/                   # 配置管理
│   ├── __init__.py
│   └── settings.py           # 配置加载和管理
│
├── core/                     # 核心业务逻辑
│   ├── __init__.py
│   ├── models.py             # 数据模型定义
│   ├── api_client.py         # DashScope API 客户端
│   └── task_manager.py       # 任务管理器
│
├── ui/                       # 用户界面
│   ├── __init__.py
│   ├── main_window.py        # 主窗口
│   ├── upload_widget.py      # 图片上传组件
│   ├── config_panel.py       # 配置面板
│   └── task_list.py          # 任务列表
│
└── utils/                    # 工具函数
    ├── __init__.py
    ├── file_handler.py       # 文件处理工具
    └── helpers.py            # 辅助函数
```

## 模块说明

### 1. 配置模块 (config/)

**settings.py**
- 加载 .env 环境变量
- 管理应用配置（API 密钥、文件路径等）
- 提供配置验证功能

### 2. 核心模块 (core/)

**models.py**
- 定义数据模型：Task（任务）、TaskStatus（任务状态）
- 提供数据序列化/反序列化方法

**api_client.py**
- DashScope API 客户端
- 功能：
  - 提交图生视频任务
  - 查询任务状态
  - 下载视频文件

**task_manager.py**
- 任务管理器
- 功能：
  - 创建任务
  - 保存/加载任务数据
  - 更新任务状态
  - 查询任务列表

### 3. 界面模块 (ui/)

**main_window.py**
- 主窗口类
- 整合所有子组件
- 处理应用级事件

**upload_widget.py**
- 图片上传组件
- 支持拖拽和点击上传
- 图片预览功能

**config_panel.py**
- 配置面板
- 参数设置（提示词、模型、分辨率等）
- 模型与分辨率联动

**task_list.py**
- 任务列表组件
- 显示所有任务
- 任务状态监控（QThread）
- 视频下载功能

### 4. 工具模块 (utils/)

**file_handler.py**
- 文件操作工具
- 文件大小格式化
- 文件复制/删除

**helpers.py**
- 辅助函数
- 日期时间格式化
- 字符串处理
- 数据验证

## 技术架构

### 1. MVC 架构模式

- **Model (核心模块)**: 数据和业务逻辑
- **View (界面模块)**: 用户界面展示
- **Controller (主窗口)**: 协调 Model 和 View

### 2. 信号槽机制

使用 PyQt5 的信号槽机制实现组件间通信：

```python
# 定义信号
image_selected = pyqtSignal(str)

# 发送信号
self.image_selected.emit(file_path)

# 连接信号
self.upload_widget.image_selected.connect(self.on_image_selected)
```

### 3. 多线程处理

使用 QThread 进行任务状态监控，避免 UI 卡顿：

```python
class TaskMonitorThread(QThread):
    task_updated = pyqtSignal(str, dict)
    
    def run(self):
        # 后台轮询任务状态
        pass
```

### 4. 配置管理

使用 .env 文件管理配置，python-dotenv 加载环境变量。

### 5. 数据持久化

任务数据保存到 JSON 文件，便于重启后恢复。

## 核心流程

### 1. 应用启动流程

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

### 2. 视频生成流程

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

### 3. 任务监控流程

```
创建 TaskMonitorThread
  ↓
在后台线程中轮询
  ↓
调用 API 查询状态
  ↓
发送更新信号
  ↓
主线程更新 UI
  ↓
任务完成后退出线程
```

## 关键设计特点

### 1. 模块解耦

- 核心业务逻辑与 UI 分离
- 便于测试和维护
- 易于扩展新功能

### 2. 可复用代码

- 复用 Flask 版本的业务逻辑
- API 客户端代码几乎一致
- 数据模型保持兼容

### 3. 用户体验优化

- 拖拽上传
- 实时状态更新
- 友好的错误提示
- 响应式界面

### 4. 跨平台支持

- PyQt5 跨平台特性
- 提供 Windows 和 Unix 启动脚本
- 路径处理兼容不同系统

## 与 Web 版本对比

| 特性 | Web 版 (Flask) | QT 客户端 |
|------|---------------|-----------|
| 界面 | HTML/CSS/JS | PyQt5 Widget |
| 通信 | HTTP + SSE | 信号槽机制 |
| 实时更新 | SSE 推送 | QThread 轮询 |
| 文件上传 | 表单上传 | 文件对话框 + 拖拽 |
| 任务监控 | 后台线程 | QThread |
| 数据存储 | JSON 文件 | JSON 文件 |
| 部署 | 需要服务器 | 独立可执行文件 |

## 未来扩展方向

1. **视频播放器**: 集成 QMediaPlayer 预览视频
2. **批量处理**: 支持批量上传和生成
3. **历史管理**: 更强大的任务管理功能
4. **配置预设**: 保存常用配置模板
5. **SQLite**: 替换 JSON 存储
6. **打包发布**: PyInstaller 打包成可执行文件
7. **自动更新**: 应用自动更新机制
8. **云同步**: 任务数据云端同步

## 开发建议

### 添加新功能

1. 在 `core/` 添加业务逻辑
2. 在 `ui/` 创建界面组件
3. 在 `main_window.py` 中整合
4. 使用信号槽连接组件

### 调试技巧

- 使用 `print()` 输出调试信息
- PyQt5 Designer 可视化设计界面
- 使用 Python 调试器

### 性能优化

- 大文件处理使用流式读取
- 耗时操作放到 QThread
- 图片缩略图缓存
- 任务列表虚拟化（大量任务时）
