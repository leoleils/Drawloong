# Implementation Plan

- [x] 1. 添加 QFluentWidgets 依赖并配置主题系统
  - [x] 1.1 更新 requirements.txt 添加 PyQt5-Fluent-Widgets 依赖
    - 添加 `PyQt5-Fluent-Widgets>=1.5.0` 到 requirements.txt
    - _Requirements: 1.1, 1.2_
  - [x] 1.2 创建 Fluent 主题管理模块
    - 在 themes/ 目录创建 fluent_theme.py
    - 实现 setTheme、setThemeColor 封装
    - 实现主题配置持久化
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  - [x] 1.3 更新 config/settings.py 支持 Fluent 主题配置
    - 添加 get_fluent_theme、set_fluent_theme 方法
    - 添加 get_accent_color、set_accent_color 方法
    - _Requirements: 7.5_

- [x] 2. 创建消息提示工具类
  - [x] 2.1 创建 utils/message_helper.py 消息提示工具
    - 实现 InfoBar 封装的 success、warning、error、info 方法
    - 支持自动消失和手动关闭
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 3. 改造主窗口为 FluentWindow
  - [x] 3.1 创建新的 FluentMainWindow 类
    - 继承 qfluentwidgets.FluentWindow
    - 实现 NavigationInterface 侧边栏导航
    - 添加首帧生视频、首尾帧生视频、文生图、图像编辑、参考生视频导航项
    - 在底部添加设置导航项
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [x] 3.2 迁移现有功能到新主窗口
    - 迁移工程管理功能
    - 迁移信号连接
    - 保留菜单栏功能
    - _Requirements: 2.5_
  - [x] 3.3 更新 main.py 使用新主窗口
    - 导入并使用 FluentMainWindow
    - 初始化 Fluent 主题
    - _Requirements: 1.3_

- [x] 4. 美化欢迎页面
  - [x] 4.1 改造 WelcomePage 使用 Fluent 组件
    - 使用 PrimaryPushButton 替代新建工程按钮
    - 使用 PushButton 替代打开工程按钮
    - 使用 SubtitleLabel 和 BodyLabel 替代 QLabel
    - _Requirements: 3.1, 3.2, 3.3_
  - [x] 4.2 添加最近项目卡片列表
    - 使用 CardWidget 包装最近项目
    - 保持现有功能不变
    - _Requirements: 3.4_

- [x] 5. 美化配置面板
  - [x] 5.1 改造 ConfigPanel 使用 Fluent 组件
    - 使用 ComboBox 替代 QComboBox
    - 使用 TextEdit 替代 QTextEdit
    - 使用 SwitchButton 替代 QCheckBox
    - 使用 PrimaryPushButton 作为生成按钮
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  - [x] 5.2 使用 CardWidget 重构布局
    - 将配置项分组到卡片中
    - 添加 SubtitleLabel 作为分组标题
    - _Requirements: 4.1_

- [x] 6. 美化项目资源管理器
  - [x] 6.1 改造 ProjectExplorer 使用 Fluent 组件
    - 使用 TreeWidget 替代 QTreeWidget
    - 使用 FluentIcon 替代文本图标
    - _Requirements: 5.1, 5.2_
  - [x] 6.2 实现 Fluent 风格右键菜单
    - 使用 RoundMenu 替代 QMenu
    - 使用 Action 配合 FluentIcon
    - _Requirements: 5.3, 5.4_

- [x] 7. 美化上传组件
  - [x] 7.1 改造 UploadWidget 使用 Fluent 组件
    - 使用 CardWidget 作为拖放区域容器
    - 使用 IconWidget 显示上传图标
    - 使用 BodyLabel 显示提示文字
    - 使用 PushButton 替代按钮
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 8. 美化任务列表
  - [x] 8.1 改造 TaskListWidget 使用 Fluent 组件
    - 使用 TableWidget 替代 QTableWidget
    - 使用 ProgressBar 显示任务进度
    - 使用 PushButton 替代刷新按钮
    - _Requirements: 9.1, 9.2, 9.4_
  - [x] 8.2 添加任务状态图标
    - 使用 FluentIcon 表示不同任务状态
    - 成功用 COMPLETED 图标，失败用 CLOSE 图标，运行中用 SYNC 图标
    - _Requirements: 9.3_

- [x] 9. 美化设置对话框
  - [x] 9.1 改造 SettingsDialog 使用 Fluent 组件
    - 使用 PasswordLineEdit 替代密码输入框
    - 使用 ComboBox 替代主题选择下拉框
    - 使用 PrimaryPushButton 和 PushButton 替代按钮
    - _Requirements: 6.1, 6.2_
  - [x] 9.2 集成 Fluent 主题选择
    - 添加浅色/深色主题切换
    - 添加主题色选择
    - 实时预览主题效果
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 10. 美化视频浏览器
  - [x] 10.1 改造 VideoViewerWidget 使用 Fluent 组件
    - 使用 Slider 替代 QSlider
    - 使用 ToolButton 配合 FluentIcon 作为控制按钮
    - 使用 CardWidget 包装视频区域
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [x] 11. 美化其他对话框
  - [x] 11.1 改造 ProjectDialog 使用 Fluent 组件
    - 使用 LineEdit 替代 QLineEdit
    - 使用 PrimaryPushButton 和 PushButton 替代按钮
    - _Requirements: 6.2_
  - [x] 11.2 改造 ImageViewer 使用 Fluent 组件
    - 使用 ToolButton 配合 FluentIcon 作为工具栏按钮
    - _Requirements: 6.3_

- [x] 12. 替换全局消息提示
  - [x] 12.1 替换 QMessageBox 为 InfoBar
    - 在 main_window.py 中替换所有 QMessageBox.information 为 InfoBar.success
    - 替换 QMessageBox.warning 为 InfoBar.warning
    - 替换 QMessageBox.critical 为 InfoBar.error
    - _Requirements: 8.1, 8.2, 8.3_
  - [x] 12.2 保留确认对话框使用 MessageBox
    - 需要用户确认的操作继续使用 MessageBox 组件
    - _Requirements: 8.4_

- [x] 13. 状态栏优化
  - [x] 13.1 美化状态栏样式
    - 应用 Fluent 风格样式
    - 使用 CaptionLabel 显示状态文字
    - _Requirements: 12.1, 12.3_
  - [x] 13.2 添加后台任务指示器
    - 使用 ProgressRing 或 IndeterminateProgressBar 表示后台任务
    - _Requirements: 12.2_

- [x] 14. 测试与优化
  - [x] 14.1 功能测试
    - 测试所有导航功能正常
    - 测试所有按钮点击响应正常
    - 测试主题切换功能正常
  - [x] 14.2 视觉优化
    - 统一组件间距和对齐
    - 优化动画效果
    - 确保深色/浅色主题下显示正常

- [x] 15. 欢迎页独立化与全局资源管理器
  - [x] 15.1 欢迎页独立化
    - 在未打开工程时，阻止用户切换到功能页面
    - 添加 _update_navigation_visibility 方法控制导航项可见性
    - 在 switch_to_project 和 switch_to_welcome_page 中更新导航状态
    - _Requirements: 用户必须先新建或打开工程才能进入主功能页面_
  - [x] 15.2 全局资源管理器
    - 在导航栏底部添加"资源管理器"按钮（非页面切换按钮）
    - 点击按钮打开/关闭浮动资源管理器抽屉
    - 浮动资源管理器可在任何页面使用（类似 VSCode 侧边栏）
    - 增强抽屉标题栏，添加图标和标题文字
    - _Requirements: 资源管理器不再只依赖于图生视频页面_
