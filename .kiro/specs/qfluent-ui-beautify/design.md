# Design Document

## Overview

本设计文档描述了使用 QFluentWidgets 对烛龙绘影 (Drawloong) 项目进行 UI 美化的技术方案。QFluentWidgets 是一个成熟的 PyQt5/PyQt6 Fluent Design 组件库，提供了丰富的现代化 UI 组件。本次改造将采用渐进式迁移策略，在保持现有功能完整性的同时，逐步替换原生 PyQt5 组件为 QFluentWidgets 组件。

## Architecture

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Main Application                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │              FluentWindow (主窗口)                    │   │
│  │  ┌─────────┐  ┌─────────────────────────────────┐   │   │
│  │  │Navigation│  │        StackedWidget            │   │   │
│  │  │Interface │  │  ┌─────────────────────────┐   │   │   │
│  │  │          │  │  │    WelcomePage          │   │   │   │
│  │  │ - 首帧   │  │  ├─────────────────────────┤   │   │   │
│  │  │ - 首尾帧 │  │  │    FirstFrameTab        │   │   │   │
│  │  │ - 文生图 │  │  ├─────────────────────────┤   │   │   │
│  │  │ - 图编辑 │  │  │    KeyframeTab          │   │   │   │
│  │  │ - 参考   │  │  ├─────────────────────────┤   │   │   │
│  │  │ - 设置   │  │  │    TextToImageTab       │   │   │   │
│  │  │          │  │  ├─────────────────────────┤   │   │   │
│  │  └─────────┘  │  │    ImageEditTab         │   │   │   │
│  │               │  ├─────────────────────────┤   │   │   │
│  │               │  │    ReferenceVideoTab    │   │   │   │
│  │               │  └─────────────────────────┘   │   │   │
│  │               └─────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Theme System (QFluentWidgets)             │
│  - setTheme(Theme.LIGHT / Theme.DARK)                       │
│  - setThemeColor(QColor)                                     │
└─────────────────────────────────────────────────────────────┘
```

### 迁移策略

采用渐进式迁移，分为以下阶段：

1. **基础设施层**: 添加依赖、配置主题系统
2. **主窗口层**: 改造 MainWindow 为 FluentWindow
3. **组件层**: 逐个替换各功能组件
4. **优化层**: 统一样式、添加动画效果

## Components and Interfaces

### 1. 主窗口组件 (MainWindow)

**改造前**: 继承自 `QMainWindow`
**改造后**: 继承自 `qfluentwidgets.FluentWindow`

```python
from qfluentwidgets import (
    FluentWindow, NavigationInterface, NavigationItemPosition,
    FluentIcon, SubtitleLabel, setTheme, Theme
)

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.initNavigation()
        self.initWindow()
    
    def initNavigation(self):
        # 添加导航项
        self.addSubInterface(self.first_frame_page, FluentIcon.VIDEO, "首帧生视频")
        self.addSubInterface(self.keyframe_page, FluentIcon.MOVIE, "首尾帧生视频")
        self.addSubInterface(self.text_to_image_page, FluentIcon.PHOTO, "文生图")
        self.addSubInterface(self.image_edit_page, FluentIcon.EDIT, "图像编辑")
        self.addSubInterface(self.reference_page, FluentIcon.SYNC, "参考生视频")
        
        # 底部导航
        self.addSubInterface(
            self.settings_page, FluentIcon.SETTING, "设置",
            NavigationItemPosition.BOTTOM
        )
```

### 2. 欢迎页面组件 (WelcomePage)

**组件替换映射**:
| 原组件 | QFluentWidgets 组件 |
|--------|---------------------|
| QPushButton | PrimaryPushButton, PushButton |
| QLabel | SubtitleLabel, BodyLabel |
| QWidget | CardWidget |

```python
from qfluentwidgets import (
    PrimaryPushButton, PushButton, CardWidget,
    SubtitleLabel, BodyLabel, IconWidget, FluentIcon
)

class WelcomePage(QWidget):
    def setup_ui(self):
        # Logo 区域
        self.logo_label = ImageLabel(logo_path)
        
        # 操作按钮
        self.new_btn = PrimaryPushButton(FluentIcon.ADD, "新建工程")
        self.open_btn = PushButton(FluentIcon.FOLDER, "打开工程")
        
        # 最近项目卡片
        self.recent_card = CardWidget()
```

### 3. 配置面板组件 (ConfigPanel)

**组件替换映射**:
| 原组件 | QFluentWidgets 组件 |
|--------|---------------------|
| QComboBox | ComboBox |
| QTextEdit | TextEdit |
| QLineEdit | LineEdit |
| QCheckBox | SwitchButton |
| QPushButton | PrimaryPushButton |
| QGroupBox | CardWidget + SubtitleLabel |

```python
from qfluentwidgets import (
    ComboBox, TextEdit, LineEdit, SwitchButton,
    PrimaryPushButton, CardWidget, SubtitleLabel, BodyLabel
)

class ConfigPanel(QWidget):
    def setup_ui(self):
        # 提示词输入
        self.prompt_edit = TextEdit()
        self.prompt_edit.setPlaceholderText("描述你想要生成的视频内容...")
        
        # 模型选择
        self.model_combo = ComboBox()
        for model_key, model_info in self.MODEL_CONFIG.items():
            self.model_combo.addItem(model_info['name'], userData=model_key)
        
        # 智能改写开关
        self.prompt_extend_switch = SwitchButton("启用提示词智能改写")
        self.prompt_extend_switch.setChecked(True)
        
        # 生成按钮
        self.generate_btn = PrimaryPushButton(FluentIcon.PLAY, "生成视频")
```

### 4. 项目资源管理器 (ProjectExplorer)

**组件替换映射**:
| 原组件 | QFluentWidgets 组件 |
|--------|---------------------|
| QTreeWidget | TreeWidget |
| QMenu | RoundMenu |
| 文本图标 | FluentIcon |

```python
from qfluentwidgets import TreeWidget, RoundMenu, Action, FluentIcon

class ProjectExplorer(QWidget):
    def setup_ui(self):
        self.tree = TreeWidget()
        self.tree.setHeaderHidden(True)
    
    def show_context_menu(self, pos):
        menu = RoundMenu(parent=self)
        menu.addAction(Action(FluentIcon.SYNC, "刷新", triggered=self.refresh))
        menu.addAction(Action(FluentIcon.DELETE, "删除", triggered=self.delete_item))
        menu.exec_(self.tree.mapToGlobal(pos))
```

### 5. 上传组件 (UploadWidget)

**组件替换映射**:
| 原组件 | QFluentWidgets 组件 |
|--------|---------------------|
| QGroupBox | CardWidget |
| QPushButton | PushButton |
| QLabel | BodyLabel, IconWidget |

```python
from qfluentwidgets import (
    CardWidget, PushButton, BodyLabel, IconWidget, FluentIcon
)

class UploadWidget(QWidget):
    def setup_ui(self):
        # 拖放区域卡片
        self.drop_card = CardWidget()
        
        # 上传图标
        self.upload_icon = IconWidget(FluentIcon.PHOTO)
        self.upload_icon.setFixedSize(64, 64)
        
        # 提示文字
        self.hint_label = BodyLabel("拖拽图片到此处或点击选择")
        
        # 按钮
        self.browse_btn = PushButton(FluentIcon.FOLDER, "浏览...")
        self.project_btn = PushButton(FluentIcon.DOCUMENT, "从工程选择")
```

### 6. 任务列表组件 (TaskListWidget)

**组件替换映射**:
| 原组件 | QFluentWidgets 组件 |
|--------|---------------------|
| QTableWidget | TableWidget |
| QPushButton | PushButton |
| QGroupBox | CardWidget |
| 状态颜色 | InfoBadge |

```python
from qfluentwidgets import (
    TableWidget, PushButton, CardWidget, ProgressBar,
    InfoBadge, FluentIcon
)

class TaskListWidget(QWidget):
    def setup_ui(self):
        self.table = TableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            '任务ID', '提示词', '模型', '分辨率', '状态', '创建时间'
        ])
        
        # 刷新按钮
        self.refresh_btn = PushButton(FluentIcon.SYNC, "刷新")
```

### 7. 设置对话框 (SettingsDialog)

**组件替换映射**:
| 原组件 | QFluentWidgets 组件 |
|--------|---------------------|
| QDialog | MessageBoxBase 或自定义 |
| QLineEdit | PasswordLineEdit, LineEdit |
| QComboBox | ComboBox |
| QPushButton | PrimaryPushButton, PushButton |
| QGroupBox | SettingCardGroup |

```python
from qfluentwidgets import (
    MessageBoxBase, PasswordLineEdit, ComboBox,
    PrimaryPushButton, PushButton, SettingCardGroup,
    SettingCard, FluentIcon, SubtitleLabel
)

class SettingsDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # API 密钥输入
        self.api_key_input = PasswordLineEdit()
        self.api_key_input.setPlaceholderText("sk-xxxxxxxx")
        
        # 主题选择
        self.theme_combo = ComboBox()
        self.theme_combo.addItems(["浅色主题", "深色主题"])
```

### 8. 视频浏览器组件 (VideoViewerWidget)

**组件替换映射**:
| 原组件 | QFluentWidgets 组件 |
|--------|---------------------|
| QSlider | Slider |
| QPushButton | ToolButton |
| QLabel | BodyLabel |

```python
from qfluentwidgets import (
    Slider, ToolButton, BodyLabel, CardWidget, FluentIcon
)

class VideoViewerWidget(QWidget):
    def setup_ui(self):
        # 视频容器
        self.video_card = CardWidget()
        
        # 进度条
        self.progress_slider = Slider(Qt.Horizontal)
        
        # 控制按钮
        self.play_btn = ToolButton(FluentIcon.PLAY)
        self.pause_btn = ToolButton(FluentIcon.PAUSE)
        self.stop_btn = ToolButton(FluentIcon.CLOSE)
```

### 9. 消息提示系统

**替换 QMessageBox 为 InfoBar**:

```python
from qfluentwidgets import InfoBar, InfoBarPosition

class MessageHelper:
    @staticmethod
    def success(parent, title, content):
        InfoBar.success(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=parent
        )
    
    @staticmethod
    def warning(parent, title, content):
        InfoBar.warning(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=parent
        )
    
    @staticmethod
    def error(parent, title, content):
        InfoBar.error(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=-1,  # 不自动消失
            parent=parent
        )
```

## Data Models

### 主题配置模型

```python
from dataclasses import dataclass
from enum import Enum
from qfluentwidgets import Theme

class AppTheme(Enum):
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"

@dataclass
class ThemeConfig:
    theme: AppTheme = AppTheme.LIGHT
    accent_color: str = "#007bff"  # 主题强调色
    
    def to_qfluent_theme(self) -> Theme:
        if self.theme == AppTheme.LIGHT:
            return Theme.LIGHT
        elif self.theme == AppTheme.DARK:
            return Theme.DARK
        else:
            return Theme.AUTO
```

### 设置存储扩展

```python
# config/settings.py 扩展
class Settings:
    # 现有方法...
    
    def get_theme(self) -> str:
        return os.getenv('APP_THEME', 'light')
    
    def set_theme(self, theme: str):
        # 更新 .env 文件
        self._update_env('APP_THEME', theme)
    
    def get_accent_color(self) -> str:
        return os.getenv('ACCENT_COLOR', '#007bff')
    
    def set_accent_color(self, color: str):
        self._update_env('ACCENT_COLOR', color)
```

## Error Handling

### 组件兼容性错误处理

```python
def safe_import_fluent():
    """安全导入 QFluentWidgets，提供降级方案"""
    try:
        from qfluentwidgets import (
            FluentWindow, PrimaryPushButton, ComboBox, 
            InfoBar, setTheme, Theme
        )
        return True
    except ImportError as e:
        print(f"QFluentWidgets 导入失败: {e}")
        print("将使用原生 PyQt5 组件")
        return False

FLUENT_AVAILABLE = safe_import_fluent()
```

### 主题切换错误处理

```python
def apply_theme_safely(theme_name: str):
    """安全应用主题"""
    try:
        from qfluentwidgets import setTheme, Theme
        theme_map = {
            'light': Theme.LIGHT,
            'dark': Theme.DARK,
            'auto': Theme.AUTO
        }
        setTheme(theme_map.get(theme_name, Theme.LIGHT))
    except Exception as e:
        print(f"主题切换失败: {e}")
        # 降级到原有主题系统
        from themes.themes import Themes
        return Themes.get_theme(theme_name)
```

## Testing Strategy

### 单元测试

1. **组件渲染测试**: 验证各 Fluent 组件能正确渲染
2. **信号连接测试**: 验证组件信号正确连接
3. **主题切换测试**: 验证主题切换功能正常

### 集成测试

1. **导航测试**: 验证侧边栏导航功能
2. **功能流程测试**: 验证完整的用户操作流程
3. **兼容性测试**: 验证与现有功能的兼容性

### 视觉回归测试

1. **截图对比**: 对比改造前后的界面截图
2. **响应式测试**: 测试不同窗口尺寸下的显示效果

## 依赖配置

### requirements.txt 更新

```
PyQt5>=5.15.0
PyQt5-Fluent-Widgets>=1.5.0
requests>=2.25.0
python-dotenv>=0.19.0
opencv-python>=4.5.0
```

### 版本兼容性说明

- QFluentWidgets 1.5.0+ 支持 PyQt5 5.15.0+
- 建议使用 Python 3.8+
- macOS、Windows、Linux 均支持

## 实现优先级

1. **P0 - 核心**: 依赖安装、主题系统集成
2. **P1 - 高优先级**: 主窗口改造、导航系统
3. **P2 - 中优先级**: 配置面板、上传组件、任务列表
4. **P3 - 低优先级**: 对话框、消息提示、细节优化
