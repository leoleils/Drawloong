# Requirements Document

## Introduction

本文档定义了使用 QFluentWidgets 对烛龙绘影 (Drawloong) 项目进行 UI 美化的需求规范。QFluentWidgets 是一个基于 PyQt5/PyQt6 的 Fluent Design 风格组件库，提供现代化、美观的 UI 组件。本次美化将替换现有的原生 PyQt5 组件，采用 QFluentWidgets 组件实现更现代化的用户界面。

## Glossary

- **QFluentWidgets**: 基于 PyQt5/PyQt6 的 Fluent Design 风格 UI 组件库
- **Fluent Design**: 微软设计的现代化 UI 设计语言，特点是流畅动画、亚克力效果、深度层次
- **Drawloong**: 烛龙绘影应用，本项目的目标应用
- **Theme_System**: 应用的主题管理系统，负责切换浅色/深色等主题
- **Navigation_Interface**: QFluentWidgets 提供的侧边导航界面组件
- **Fluent_Window**: QFluentWidgets 提供的主窗口基类，支持 Fluent 风格
- **Card_Widget**: QFluentWidgets 提供的卡片式容器组件
- **Info_Bar**: QFluentWidgets 提供的消息提示条组件

## Requirements

### Requirement 1: 集成 QFluentWidgets 依赖

**User Story:** 作为开发者，我希望项目能够正确集成 QFluentWidgets 库，以便使用其提供的 Fluent Design 组件。

#### Acceptance Criteria

1. THE Drawloong SHALL 在 requirements.txt 中添加 qfluentwidgets 依赖包
2. THE Drawloong SHALL 确保 QFluentWidgets 与现有 PyQt5 版本兼容
3. THE Drawloong SHALL 在应用启动时成功加载 QFluentWidgets 模块

### Requirement 2: 主窗口 Fluent 化改造

**User Story:** 作为用户，我希望应用主窗口采用 Fluent Design 风格，以获得更现代化的视觉体验。

#### Acceptance Criteria

1. THE Main_Window SHALL 继承自 QFluentWidgets 的 FluentWindow 或 MSFluentWindow 基类
2. THE Main_Window SHALL 使用 NavigationInterface 替代现有的标签页导航
3. THE Main_Window SHALL 支持侧边栏导航，包含首帧生视频、首尾帧生视频、文生图、图像编辑、参考生视频等功能入口
4. WHEN 用户点击侧边栏导航项时，THE Main_Window SHALL 切换到对应的功能页面
5. THE Main_Window SHALL 保留现有的菜单栏功能

### Requirement 3: 欢迎页面美化

**User Story:** 作为用户，我希望欢迎页面更加美观和现代化，以获得良好的第一印象。

#### Acceptance Criteria

1. THE Welcome_Page SHALL 使用 QFluentWidgets 的 PrimaryPushButton 替代普通按钮
2. THE Welcome_Page SHALL 使用 CardWidget 包装最近项目列表
3. THE Welcome_Page SHALL 使用 SubtitleLabel 和 BodyLabel 替代普通 QLabel
4. THE Welcome_Page SHALL 保持现有的新建工程、打开工程、最近项目功能

### Requirement 4: 配置面板组件替换

**User Story:** 作为用户，我希望配置面板的输入控件更加美观易用。

#### Acceptance Criteria

1. THE Config_Panel SHALL 使用 ComboBox 替代 QComboBox
2. THE Config_Panel SHALL 使用 LineEdit 替代 QLineEdit
3. THE Config_Panel SHALL 使用 TextEdit 替代 QTextEdit
4. THE Config_Panel SHALL 使用 PrimaryPushButton 作为生成按钮
5. THE Config_Panel SHALL 使用 SwitchButton 替代 QCheckBox（如适用）

### Requirement 5: 项目资源管理器美化

**User Story:** 作为用户，我希望项目资源管理器具有更好的视觉层次和交互体验。

#### Acceptance Criteria

1. THE Project_Explorer SHALL 使用 TreeWidget 替代 QTreeWidget
2. THE Project_Explorer SHALL 使用 FluentIcon 图标替代文本图标
3. THE Project_Explorer SHALL 支持右键菜单使用 RoundMenu 组件
4. WHEN 用户选中文件时，THE Project_Explorer SHALL 显示选中高亮效果

### Requirement 6: 对话框 Fluent 化

**User Story:** 作为用户，我希望所有对话框都采用统一的 Fluent Design 风格。

#### Acceptance Criteria

1. THE Settings_Dialog SHALL 继承自 QFluentWidgets 的 MessageBoxBase 或使用 Dialog 组件
2. THE Project_Dialog SHALL 使用 Fluent 风格的输入控件和按钮
3. THE Image_Viewer SHALL 使用 Fluent 风格的工具栏和按钮
4. IF 对话框需要显示消息提示，THEN THE Dialog SHALL 使用 InfoBar 组件

### Requirement 7: 主题系统集成

**User Story:** 作为用户，我希望应用能够支持 QFluentWidgets 的主题系统，实现更好的主题切换效果。

#### Acceptance Criteria

1. THE Theme_System SHALL 集成 QFluentWidgets 的 setTheme 和 setThemeColor 功能
2. THE Theme_System SHALL 支持浅色 (Light) 和深色 (Dark) 主题切换
3. THE Theme_System SHALL 支持自定义主题色
4. WHEN 用户切换主题时，THE Theme_System SHALL 实时更新所有 Fluent 组件的样式
5. THE Theme_System SHALL 保存用户的主题偏好设置

### Requirement 8: 消息提示优化

**User Story:** 作为用户，我希望应用的消息提示更加美观且不打断工作流程。

#### Acceptance Criteria

1. THE Drawloong SHALL 使用 InfoBar 替代 QMessageBox 显示成功、警告、错误等提示
2. THE InfoBar SHALL 支持自动消失功能
3. THE InfoBar SHALL 显示在窗口顶部或底部，不阻塞用户操作
4. IF 需要用户确认操作，THEN THE Drawloong SHALL 使用 MessageBox 组件

### Requirement 9: 任务列表美化

**User Story:** 作为用户，我希望任务列表能够清晰展示任务状态和进度。

#### Acceptance Criteria

1. THE Task_List SHALL 使用 ListWidget 或 TableWidget 替代原生组件
2. THE Task_List SHALL 使用 ProgressBar 显示任务进度
3. THE Task_List SHALL 使用 StateToolTip 显示任务状态提示
4. THE Task_List SHALL 使用 FluentIcon 图标表示不同任务状态

### Requirement 10: 上传组件美化

**User Story:** 作为用户，我希望图片上传区域更加直观和美观。

#### Acceptance Criteria

1. THE Upload_Widget SHALL 使用 CardWidget 作为拖放区域容器
2. THE Upload_Widget SHALL 使用 IconWidget 显示上传图标
3. THE Upload_Widget SHALL 使用 BodyLabel 显示提示文字
4. WHEN 用户拖放文件到上传区域时，THE Upload_Widget SHALL 显示视觉反馈效果

### Requirement 11: 视频浏览器美化

**User Story:** 作为用户，我希望视频浏览器具有现代化的播放控制界面。

#### Acceptance Criteria

1. THE Video_Viewer SHALL 使用 Slider 替代 QSlider 作为进度条
2. THE Video_Viewer SHALL 使用 ToolButton 替代普通按钮作为播放控制按钮
3. THE Video_Viewer SHALL 使用 FluentIcon 图标作为播放、暂停、停止等按钮图标
4. THE Video_Viewer SHALL 使用 CardWidget 包装视频播放区域

### Requirement 12: 状态栏优化

**User Story:** 作为用户，我希望状态栏能够更好地展示应用状态信息。

#### Acceptance Criteria

1. THE Status_Bar SHALL 使用 QFluentWidgets 风格的样式
2. THE Status_Bar SHALL 支持显示 ProgressRing 表示后台任务进行中
3. THE Status_Bar SHALL 使用 CaptionLabel 显示状态文字
