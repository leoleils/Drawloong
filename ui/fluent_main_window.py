#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent 风格主窗口
基于 QFluentWidgets 的 FluentWindow 实现现代化 UI
"""

import os
import shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter,
    QPushButton, QAction, QStackedWidget, QApplication, QMenuBar
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
import sys

try:
    from qfluentwidgets import (
        FluentWindow, NavigationItemPosition, FluentIcon,
        SubtitleLabel, setTheme, Theme, NavigationAvatarWidget
    )
    FLUENT_AVAILABLE = True
    
    # macOS 临时解决方案：使用原生 QMainWindow 但保持 Fluent 样式
    if sys.platform == 'darwin':
        print("macOS 检测到，使用原生窗口以避免标题栏问题")
        from PyQt5.QtWidgets import QMainWindow
        FluentWindow = QMainWindow
        
except ImportError:
    FLUENT_AVAILABLE = False
    from PyQt5.QtWidgets import QMainWindow as FluentWindow
    print("警告: QFluentWidgets 未安装，将使用原生 QMainWindow")

from .upload_widget import UploadWidget
from .config_panel import ConfigPanel
from .task_list import TaskListWidget
from .settings_dialog import SettingsDialog
from .project_explorer import ProjectExplorer
from .project_explorer_drawer import ProjectExplorerDrawer
from .task_list_drawer import TaskListDrawer
from .welcome_page import WelcomePage
from .project_dialog import NewProjectDialog, OpenProjectDialog
from .image_viewer import ImageViewer
from .video_player import VideoPlayer
from .video_viewer import VideoViewerWidget
from .text_to_image_widget import TextToImageWidget
from .image_edit_widget import ImageEditWidget
from .keyframe_to_video_widget import KeyframeToVideoWidget
from .reference_video_to_video_widget import ReferenceVideoToVideoWidget
from .fluent_status_bar import FluentStatusBar
from core.task_manager import TaskManager
from core.api_client import DashScopeClient
from core.project_manager import ProjectManager
from config.settings import settings
from themes.fluent_theme import fluent_theme_manager, FLUENT_AVAILABLE as THEME_AVAILABLE
from utils.message_helper import MessageHelper


class FirstFrameInterface(QWidget):
    """首帧生视频界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("firstFrameInterface")
        self._first_show = True
    
    def showEvent(self, event):
        """显示事件 - 仅首次显示时刷新布局"""
        super().showEvent(event)
        # 只在首次显示时刷新，避免抖动
        if self._first_show:
            self._first_show = False
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, self.updateGeometry)


class KeyframeInterface(QWidget):
    """首尾帧生视频界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("keyframeInterface")


class TextToImageInterface(QWidget):
    """文生图界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("textToImageInterface")


class ImageEditInterface(QWidget):
    """图像编辑界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("imageEditInterface")


class ReferenceVideoInterface(QWidget):
    """参考生视频界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("referenceVideoInterface")


class SettingsInterface(QWidget):
    """设置界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsInterface")


class FluentMainWindow(FluentWindow):
    """Fluent 风格主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 初始化核心组件
        self.project_manager = ProjectManager()
        self.task_manager = TaskManager()
        self.api_client = DashScopeClient()
        
        # 当前选择的图片路径
        self.current_image_path = None
        
        # 当前正在生成的任务ID
        self.current_generating_task_id = None
        
        # 是否已打开工程
        self._project_opened = False
        
        # 设置窗口
        self.setup_window()
        
        # 创建界面
        self.init_interfaces()
        
        # 创建浮动资源管理器
        self.init_floating_explorer()
        
        # 创建浮动任务列表
        self.init_floating_task_list()
        
        # 初始化导航
        self.init_navigation()
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 连接信号
        self.connect_signals()
        
        # 应用 Fluent 主题
        self.apply_fluent_theme()
        
        # 检查 API 密钥
        self.check_api_key()
    
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        # macOS 的标题栏修复已经在 __init__ 中处理了
    
    
    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("烛龙绘影 Drawloong")
        self.resize(1200, 750)
        self.setMinimumSize(1000, 600)
        
        # macOS 特定设置：现在使用原生窗口，红绿灯按钮应该在正确位置
        if sys.platform == 'darwin':
            print("macOS 使用原生窗口，标题栏按钮应该在正确位置")
        
        # 窗口居中显示
        self.center_window()
        
        # 设置窗口图标
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo.png')
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        # 创建状态栏
        if sys.platform == 'darwin':
            # macOS 原生窗口：使用标准 QStatusBar，但保持 Fluent 样式
            from PyQt5.QtWidgets import QStatusBar
            self.status_bar = QStatusBar(self)
            self.setStatusBar(self.status_bar)
            
            # 添加 Fluent 风格的状态信息显示
            self.fluent_status_widget = FluentStatusBar(self)
            self.status_bar.addPermanentWidget(self.fluent_status_widget, 1)
        else:
            # 其他平台：FluentWindow 使用 vBoxLayout
            self.status_bar = FluentStatusBar(self)
            if hasattr(self, 'vBoxLayout'):
                self.vBoxLayout.addWidget(self.status_bar)
        
        # macOS 额外设置：确保标题栏正常显示
        # 注意：现在使用原生窗口，不需要特殊处理
    
    def _get_status_widget(self):
        """获取状态栏组件（兼容 macOS 和其他平台）"""
        if sys.platform == 'darwin':
            return self.fluent_status_widget
        else:
            return self.status_bar
    
    
    def init_interfaces(self):
        """初始化各功能界面"""
        # 创建欢迎页面
        self.welcome_page = WelcomePage()
        self.welcome_interface = QWidget()
        self.welcome_interface.setObjectName("welcomeInterface")
        welcome_layout = QVBoxLayout(self.welcome_interface)
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        welcome_layout.setSpacing(0)
        welcome_layout.addWidget(self.welcome_page)
        
        # 加载最近项目到欢迎页面
        self._load_recent_projects_to_welcome()
        
        # 创建首帧生视频界面
        self.first_frame_interface = self.create_first_frame_interface()
        
        # 创建首尾帧生视频界面
        self.keyframe_interface = QWidget()
        self.keyframe_interface.setObjectName("keyframeInterface")
        keyframe_layout = QVBoxLayout(self.keyframe_interface)
        keyframe_layout.setContentsMargins(0, 0, 0, 0)
        self.keyframe_tab = KeyframeToVideoWidget(self.api_client, self.project_manager, self.task_manager)
        keyframe_layout.addWidget(self.keyframe_tab)
        
        # 创建文生图界面
        self.text_to_image_interface = QWidget()
        self.text_to_image_interface.setObjectName("textToImageInterface")
        t2i_layout = QVBoxLayout(self.text_to_image_interface)
        t2i_layout.setContentsMargins(0, 0, 0, 0)
        self.text_to_image_tab = TextToImageWidget(self.api_client, self.project_manager)
        t2i_layout.addWidget(self.text_to_image_tab)
        
        # 创建图像编辑界面
        self.image_edit_interface = QWidget()
        self.image_edit_interface.setObjectName("imageEditInterface")
        ie_layout = QVBoxLayout(self.image_edit_interface)
        ie_layout.setContentsMargins(0, 0, 0, 0)
        self.image_edit_tab = ImageEditWidget(self.api_client, self.project_manager)
        ie_layout.addWidget(self.image_edit_tab)
        
        # 创建参考生视频界面
        self.reference_video_interface = QWidget()
        self.reference_video_interface.setObjectName("referenceVideoInterface")
        rv_layout = QVBoxLayout(self.reference_video_interface)
        rv_layout.setContentsMargins(0, 0, 0, 0)
        self.reference_video_tab = ReferenceVideoToVideoWidget(self.api_client, self.project_manager, self.task_manager)
        rv_layout.addWidget(self.reference_video_tab)
        
        # 创建设置界面（占位）
        self.settings_interface = QWidget()
        self.settings_interface.setObjectName("settingsInterface")
        settings_layout = QVBoxLayout(self.settings_interface)
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_label = QLabel("点击此处打开设置对话框")
        settings_label.setAlignment(Qt.AlignCenter)
        settings_label.setStyleSheet("font-size: 16px; color: #666;")
        settings_layout.addWidget(settings_label)
    
    def create_first_frame_interface(self):
        """创建首帧生视频界面"""
        interface = FirstFrameInterface()
        layout = QHBoxLayout(interface)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 主分割器 - 水平（左右两栏布局）
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(1)
        main_splitter.setChildrenCollapsible(False)  # 防止子组件被折叠
        
        # 创建隐藏的资源管理器（用于信号连接，不显示在界面上）
        self.project_explorer = ProjectExplorer()
        self.project_explorer.hide()
        
        # 创建隐藏的任务列表（用于信号连接，实际使用浮动任务列表）
        self.task_list = TaskListWidget(self.task_manager, self.project_manager)
        self.task_list.hide()
        
        # 左侧：上传和视频浏览
        left_widget = QWidget()
        left_widget.setMinimumWidth(400)  # 设置最小宽度，避免被压缩为0
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.setChildrenCollapsible(False)  # 防止子组件被折叠
        
        # 上：上传图片
        self.upload_widget = UploadWidget()
        self.upload_widget.set_project_manager(self.project_manager)
        self.upload_widget.setMinimumHeight(250)  # 设置最小高度，避免被压缩为0
        left_splitter.addWidget(self.upload_widget)
        
        # 下：视频浏览
        self.video_viewer = VideoViewerWidget()
        self.video_viewer.setMinimumHeight(300)  # 设置最小高度，避免被压缩为0
        left_splitter.addWidget(self.video_viewer)
        
        left_splitter.setStretchFactor(0, 1)
        left_splitter.setStretchFactor(1, 1)
        
        left_layout.addWidget(left_splitter)
        main_splitter.addWidget(left_widget)
        
        # 右侧：配置面板
        right_widget = QWidget()
        right_widget.setMinimumWidth(350)  # 设置最小宽度，避免被压缩为0
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # 配置面板
        self.config_panel = ConfigPanel()
        right_layout.addWidget(self.config_panel)
        
        main_splitter.addWidget(right_widget)
        
        # 设置分割比例（左右各占一半）
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
        
        layout.addWidget(main_splitter)
        return interface

    def init_floating_explorer(self):
        """初始化浮动资源管理器"""
        self.floating_explorer = ProjectExplorerDrawer(self)
        self.floating_explorer.file_selected.connect(self.on_file_selected)
        self.floating_explorer.hide()
    
    def toggle_floating_explorer(self):
        """切换浮动资源管理器显示/隐藏"""
        if not self.project_manager.has_project():
            MessageHelper.warning(self, "提示", "请先创建或打开工程")
            return
        
        self.floating_explorer.toggle(self)
    
    def init_floating_task_list(self):
        """初始化浮动任务列表"""
        self.floating_task_list = TaskListDrawer(self.task_manager, self.project_manager, self)
        self.floating_task_list.task_updated.connect(self.on_task_updated)
        self.floating_task_list.hide()
    
    def toggle_floating_task_list(self):
        """切换浮动任务列表显示/隐藏"""
        if not self.project_manager.has_project():
            MessageHelper.warning(self, "提示", "请先创建或打开工程")
            return
        
        self.floating_task_list.toggle(self)
    
    def init_navigation(self):
        """初始化导航栏"""
        if not FLUENT_AVAILABLE or sys.platform == 'darwin':
            # 在 macOS 上或没有 QFluentWidgets 时，创建简单的工具栏导航
            self._create_toolbar_navigation()
            return
        
        # 其他平台使用 FluentWindow 导航
        self._create_fluent_navigation()
    
    def _create_toolbar_navigation(self):
        """创建工具栏风格的导航（用于 macOS 或降级情况）"""
        from PyQt5.QtWidgets import QToolBar, QAction
        
        # 创建工具栏
        self.nav_toolbar = QToolBar("导航", self)
        self.addToolBar(self.nav_toolbar)
        
        # 创建堆叠窗口部件
        if not hasattr(self, 'stackedWidget'):
            from PyQt5.QtWidgets import QStackedWidget
            self.stackedWidget = QStackedWidget()
            self.setCentralWidget(self.stackedWidget)
        
        # 添加所有界面到堆叠窗口部件
        self.stackedWidget.addWidget(self.welcome_interface)
        self.stackedWidget.addWidget(self.first_frame_interface)
        self.stackedWidget.addWidget(self.keyframe_interface)
        self.stackedWidget.addWidget(self.text_to_image_interface)
        self.stackedWidget.addWidget(self.image_edit_interface)
        self.stackedWidget.addWidget(self.reference_video_interface)
        
        # 设置默认页面
        self.stackedWidget.setCurrentWidget(self.welcome_interface)
        
        # 添加导航项
        nav_items = [
            ("欢迎", "welcome_interface"),
            ("首帧生视频", "first_frame_interface"),
            ("首尾帧生视频", "keyframe_interface"),
            ("文生图", "text_to_image_interface"),
            ("图像编辑", "image_edit_interface"),
            ("参考生视频", "reference_video_interface"),
        ]
        
        # 添加导航动作
        for name, interface_name in nav_items:
            action = QAction(name, self)
            action.setData(interface_name)
            action.triggered.connect(lambda checked, iface=interface_name: self._switch_to_interface(iface))
            self.nav_toolbar.addAction(action)
        
        # 添加分隔符
        self.nav_toolbar.addSeparator()
        
        # 添加资源管理器和任务列表按钮
        explorer_action = QAction("资源管理器", self)
        explorer_action.triggered.connect(self.toggle_floating_explorer)
        self.nav_toolbar.addAction(explorer_action)
        
        task_action = QAction("任务列表", self)
        task_action.triggered.connect(self.toggle_floating_task_list)
        self.nav_toolbar.addAction(task_action)
        
        # 连接堆叠窗口部件的切换信号
        self.stackedWidget.currentChanged.connect(self.on_interface_changed)
    
    def _create_fluent_navigation(self):
        """创建 Fluent 风格导航（非 macOS 平台）"""
        # 添加欢迎页面（首页）
        self.addSubInterface(
            self.welcome_interface,
            FluentIcon.HOME,
            "欢迎",
            NavigationItemPosition.TOP
        )
        
        # 添加首帧生视频导航项
        self.addSubInterface(
            self.first_frame_interface,
            FluentIcon.VIDEO,
            "首帧生视频",
            NavigationItemPosition.TOP
        )
        
        # 添加首尾帧生视频导航项
        self.addSubInterface(
            self.keyframe_interface,
            FluentIcon.MOVIE,
            "首尾帧生视频",
            NavigationItemPosition.TOP
        )
        
        # 添加文生图导航项
        self.addSubInterface(
            self.text_to_image_interface,
            FluentIcon.PHOTO,
            "文生图",
            NavigationItemPosition.TOP
        )
        
        # 添加图像编辑导航项
        self.addSubInterface(
            self.image_edit_interface,
            FluentIcon.EDIT,
            "图像编辑",
            NavigationItemPosition.TOP
        )
        
        # 添加参考生视频导航项
        self.addSubInterface(
            self.reference_video_interface,
            FluentIcon.SYNC,
            "参考生视频",
            NavigationItemPosition.TOP
        )
        
        # 在底部添加资源管理器导航项
        self.addSubInterface(
            QWidget(),  # 占位符
            FluentIcon.FOLDER,
            "资源管理器",
            onClick=self.toggle_floating_explorer,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )
        
        # 在底部添加任务列表导航项
        self.addSubInterface(
            QWidget(),  # 占位符
            FluentIcon.HISTORY,
            "任务列表",
            onClick=self.toggle_floating_task_list,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )
        
        # 在底部添加设置导航项
        self.addSubInterface(
            self.settings_interface,
            FluentIcon.SETTING,
            "设置",
            NavigationItemPosition.BOTTOM
        )
        
        # 更新导航项可见性
        self._update_navigation_visibility()
    
    def _switch_to_interface(self, interface_name):
        """切换到指定界面（用于工具栏导航）"""
        interface_map = {
            "welcome_interface": self.welcome_interface,
            "first_frame_interface": self.first_frame_interface,
            "keyframe_interface": self.keyframe_interface,
            "text_to_image_interface": self.text_to_image_interface,
            "image_edit_interface": self.image_edit_interface,
            "reference_video_interface": self.reference_video_interface,
        }
        
        if interface_name in interface_map:
            interface = interface_map[interface_name]
            if hasattr(self, 'stackedWidget'):
                # 确保界面已添加到堆叠窗口部件
                if self.stackedWidget.indexOf(interface) == -1:
                    self.stackedWidget.addWidget(interface)
                self.stackedWidget.setCurrentWidget(interface)
                
                # 调用界面切换回调
                self.on_interface_changed(self.stackedWidget.currentIndex())
    
        # 初始状态：隐藏功能导航项（未打开工程时）
        self._update_navigation_visibility()
    
    def on_interface_changed(self, index):
        """界面切换回调"""
        current_widget = self.stackedWidget.currentWidget()
        
        # 如果切换到设置界面，打开设置对话框
        if current_widget == self.settings_interface:
            self.open_settings()
            # 切换回之前的界面
            if self._project_opened:
                self.stackedWidget.setCurrentWidget(self.first_frame_interface)
            else:
                self.stackedWidget.setCurrentWidget(self.welcome_interface)
        
        # 如果未打开工程，阻止切换到功能页面
        elif not self._project_opened and current_widget != self.welcome_interface:
            MessageHelper.warning(self, "提示", "请先创建或打开工程")
            self.stackedWidget.setCurrentWidget(self.welcome_interface)
        

    
    def _update_navigation_visibility(self):
        """更新导航项可见性（通过启用/禁用导航项）"""
        if not FLUENT_AVAILABLE:
            return
        
        # 功能页面的 objectName 列表
        feature_interfaces = [
            'firstFrameInterface',
            'keyframeInterface', 
            'textToImageInterface',
            'imageEditInterface',
            'referenceVideoInterface'
        ]
        
        # 根据工程状态设置导航项的启用状态
        for interface_name in feature_interfaces:
            try:
                # 尝试使用 setItemVisible（如果可用）
                if hasattr(self.navigationInterface, 'setItemVisible'):
                    self.navigationInterface.setItemVisible(interface_name, self._project_opened)
                else:
                    # 降级方案：通过 widget 方法获取导航项并设置启用状态
                    widget = self.navigationInterface.widget(interface_name)
                    if widget:
                        widget.setEnabled(self._project_opened)
                        # 设置透明度来表示禁用状态
                        widget.setStyleSheet("opacity: 0.5;" if not self._project_opened else "")
            except Exception as e:
                print(f"更新导航项 {interface_name} 可见性失败: {e}")
    
    def create_menu_bar(self):
        """创建菜单栏"""
        # FluentWindow 没有 menuBar() 方法，需要手动创建
        if FLUENT_AVAILABLE:
            # 创建菜单栏并添加到布局顶部
            menubar = QMenuBar(self)
            # 将菜单栏插入到 vBoxLayout 的最顶部
            if hasattr(self, 'vBoxLayout'):
                self.vBoxLayout.insertWidget(0, menubar)
        else:
            # 降级模式下使用 QMainWindow 的 menuBar
            menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        # 新建工程
        new_project_action = QAction('新建工程', self)
        new_project_action.setShortcut('Ctrl+Shift+N')
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)
        
        # 打开工程
        open_project_action = QAction('打开工程', self)
        open_project_action.setShortcut('Ctrl+O')
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)
        
        # 关闭工程
        self.close_project_action = QAction('关闭工程', self)
        self.close_project_action.triggered.connect(self.close_project)
        self.close_project_action.setEnabled(False)
        file_menu.addAction(self.close_project_action)
        
        file_menu.addSeparator()
        
        # 设置菜单项
        settings_action = QAction('设置', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # 退出菜单项
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        # 资源管理器
        explorer_action = QAction('资源管理器', self)
        explorer_action.setShortcut('Ctrl+E')
        explorer_action.triggered.connect(self.toggle_floating_explorer)
        view_menu.addAction(explorer_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def connect_signals(self):
        """连接信号槽"""
        # 欢迎页面信号
        self.welcome_page.new_project_clicked.connect(self.new_project)
        self.welcome_page.open_project_clicked.connect(self.open_project)
        self.welcome_page.recent_project_clicked.connect(self.open_project_by_path)
        
        # 工程资源管理器信号
        self.project_explorer.file_selected.connect(self.on_file_selected)
        self.project_explorer.refresh_requested.connect(self.refresh_project)
        
        # 上传组件信号
        self.upload_widget.image_selected.connect(self.on_image_selected)
        
        # 配置面板信号
        self.config_panel.generate_clicked.connect(self.on_generate_clicked)
        
        # 任务列表信号
        self.task_list.task_updated.connect(self.on_task_updated)
    
    def center_window(self):
        """将窗口居中显示"""
        screen = QApplication.primaryScreen().availableGeometry()
        window_size = self.frameGeometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
    
    def _apply_macos_native_titlebar(self):
        """在 macOS 上强制使用原生标题栏"""
        try:
            print("应用 macOS 原生标题栏设置...")
            
            # 强制设置原生窗口标志
            native_flags = (Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | 
                           Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | 
                           Qt.WindowCloseButtonHint)
            
            self.setWindowFlags(native_flags)
            
            # 确保使用原生窗口
            self.setAttribute(Qt.WA_NativeWindow, True)
            self.setAttribute(Qt.WA_DontCreateNativeAncestors, False)
            
            print("macOS 原生标题栏设置完成")
            
        except Exception as e:
            print(f"设置原生标题栏时出错: {e}")
    
    def _fix_macos_titlebar(self):
        """修复 macOS 上的标题栏按钮位置问题（备用方法）"""
        if sys.platform == 'darwin' and FLUENT_AVAILABLE:
            try:
                print("执行备用标题栏修复...")
                
                # 如果仍然有自定义标题栏，尝试隐藏它
                if hasattr(self, 'titleBar') and self.titleBar and self.titleBar.isVisible():
                    print("隐藏自定义标题栏")
                    self.titleBar.hide()
                
                # 重新应用原生标题栏
                self._apply_macos_native_titlebar()
                
                print("备用标题栏修复完成")
                
            except Exception as e:
                print(f"备用修复时出错: {e}")
    
    def apply_fluent_theme(self):
        """应用 Fluent 主题"""
        if THEME_AVAILABLE:
            fluent_theme_manager.apply_saved_theme()
    
    def check_api_key(self):
        """检查 API 密钥配置"""
        if not settings.is_api_key_valid():
            if MessageHelper.confirm(
                self,
                "配置提醒",
                "未检测到 API 密钥配置\n\n是否现在打开设置页面配置？"
            ):
                self.open_settings()
            else:
                self.config_panel.generate_btn.setEnabled(False)

    
    def on_image_selected(self, image_path):
        """图片选择回调"""
        self.current_image_path = image_path
        self._get_status_widget().showMessage(f"已选择图片: {os.path.basename(image_path)}", 5000)
        MessageHelper.info(self, "图片已选择", f"已选择: {os.path.basename(image_path)}")
        self.config_panel.generate_btn.setEnabled(True)
    
    def on_generate_clicked(self, config):
        """生成按钮点击回调"""
        if not self.current_image_path:
            MessageHelper.warning(self, "提示", "请先选择一张图片")
            return
        
        if not settings.is_api_key_valid():
            MessageHelper.warning(self, "提示", "API 密钥未配置或无效")
            return
        
        # 检查是否有工程
        if not self.project_manager.has_project():
            MessageHelper.warning(self, "提示", "请先创建或打开工程")
            return
        
        project = self.project_manager.get_current_project()
        
        # 复制图片到工程 inputs 文件夹
        try:
            image_name = os.path.basename(self.current_image_path)
            dest_path = os.path.join(project.inputs_folder, image_name)
            
            if os.path.abspath(self.current_image_path) != os.path.abspath(dest_path):
                shutil.copy2(self.current_image_path, dest_path)
                self.current_image_path = dest_path
                self.project_explorer.refresh()
        except Exception as e:
            print(f"复制图片失败: {e}")
        
        # 禁用生成按钮并更新文本
        self.config_panel.generate_btn.setEnabled(False)
        self.config_panel.generate_btn.setText("生成中...")
        self._get_status_widget().setBusy(True, "正在提交任务...")
        MessageHelper.info(self, "任务提交", "正在提交任务...")
        
        try:
            # 创建任务
            task = self.task_manager.create_task(
                prompt=config['prompt'],
                model=config['model'],
                resolution=config['resolution'],
                negative_prompt=config['negative_prompt'],
                prompt_extend=config['prompt_extend'],
                input_file=self.current_image_path
            )
            
            # 解析时长
            duration_str = config.get('duration', '5秒')
            duration = int(''.join(filter(str.isdigit, duration_str))) if duration_str else 5
            
            # 提交到 API
            submit_params = {
                'image_path': self.current_image_path,
                'prompt': config['prompt'],
                'model': config['model'],
                'resolution': config['resolution'],
                'negative_prompt': config['negative_prompt'],
                'prompt_extend': config['prompt_extend'],
                'duration': duration
            }
            
            if 'shot_type' in config:
                submit_params['shot_type'] = config['shot_type']
            
            result = self.api_client.submit_task(**submit_params)
            
            # 更新任务信息
            async_task_id = result['output']['task_id']
            self.task_manager.update_task(
                task.id,
                async_task_id=async_task_id
            )
            
            self.current_generating_task_id = task.id
            
            # 刷新浮动任务列表并开始监控
            self.floating_task_list.refresh_tasks()
            self.floating_task_list.start_monitoring_task(task.id)
            # 自动打开浮动任务列表
            if not self.floating_task_list.is_drawer_visible():
                self.floating_task_list.show_drawer(self)
            
            self._get_status_widget().setBusy(True, "任务已提交，正在生成视频...")
            MessageHelper.success(self, "任务已提交", "正在生成视频...")
            
        except Exception as e:
            self._get_status_widget().setBusy(False, "任务提交失败")
            MessageHelper.error(self, "错误", f"任务提交失败：{str(e)}")
            self.config_panel.generate_btn.setEnabled(True)
            self.config_panel.generate_btn.setText("生成视频")
    
    def on_task_updated(self, task_id):
        """任务更新回调"""
        task = self.task_manager.get_task(task_id)
        if task and task.is_completed():
            if hasattr(self, 'current_generating_task_id') and task_id == self.current_generating_task_id:
                self.config_panel.generate_btn.setEnabled(True)
                self.config_panel.generate_btn.setText("生成视频")
                
                if task.is_success():
                    self._get_status_widget().setBusy(False, "视频生成成功！")
                    if task.output_path and os.path.exists(task.output_path):
                        self.video_viewer.load_video(task.output_path)
                        MessageHelper.success(self, "成功", "视频生成完成！已自动加载到播放器。")
                    else:
                        MessageHelper.success(self, "成功", "视频生成完成！")
                else:
                    self._get_status_widget().setBusy(False, "视频生成失败")
                    MessageHelper.warning(self, "失败", "视频生成失败，请查看任务列表了解详情。")
                
                self.current_generating_task_id = None
            else:
                if task.is_success():
                    self._get_status_widget().showMessage(f"任务 {task_id[:8]} 已完成", 5000)
                    MessageHelper.info(self, "任务完成", f"任务 {task_id[:8]} 已完成")
                else:
                    self._get_status_widget().showMessage(f"任务 {task_id[:8]} 失败", 5000)
                    MessageHelper.warning(self, "任务失败", f"任务 {task_id[:8]} 失败")
    
    def open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self)
        dialog.api_key_changed.connect(self.on_api_key_changed)
        dialog.theme_changed.connect(self.on_theme_changed)
        dialog.exec_()
    
    def on_api_key_changed(self, api_key):
        """API 密钥变更回调"""
        self.api_client = DashScopeClient()
        
        if settings.is_api_key_valid():
            self._get_status_widget().showMessage("API 密钥已更新", 3000)
            MessageHelper.success(self, "成功", "API 密钥已更新")
            self.config_panel.generate_btn.setEnabled(True)
        else:
            self._get_status_widget().showMessage("API 密钥无效", 5000)
            MessageHelper.warning(self, "警告", "API 密钥无效")
            self.config_panel.generate_btn.setEnabled(False)
    
    def on_theme_changed(self, theme_name):
        """主题变更处理"""
        if THEME_AVAILABLE:
            fluent_theme_manager.set_theme_by_name(theme_name)
        
        # 强制刷新主窗口
        self.update()
        self.repaint()
        
        # 更新所有子界面
        for i in range(self.stackedWidget.count()):
            widget = self.stackedWidget.widget(i)
            if widget:
                widget.update()
                widget.repaint()
        
        # 更新状态栏主题
        self._get_status_widget().updateTheme()
        # 更新浮动资源管理器主题
        self.floating_explorer.updateTheme()
        # 更新浮动任务列表主题
        self.floating_task_list.updateTheme()
        
        self._get_status_widget().showMessage(f"主题已切换到 {theme_name}", 3000)
        MessageHelper.success(self, "主题已更改", f"主题已成功切换到 {theme_name}！")

    
    def show_about(self):
        """显示关于对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("关于")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        
        # 添加logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo.png')
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # 添加信息
        info_label = QLabel(
            "<h2>烛龙绘影 Drawloong</h2>"
            "<p><b>版本:</b> 1.15.1</p>"
            "<p>基于 PyQt5 + QFluentWidgets 的桌面客户端应用</p>"
            "<p>调用阿里云 DashScope API 实现图片转视频功能</p>"
            "<p><a href='https://dashscope.console.aliyun.com/'>获取 API 密钥</a></p>"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setOpenExternalLinks(True)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 添加关闭按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    # ==================== 工程管理相关方法 ====================
    
    def new_project(self):
        """新建工程"""
        dialog = NewProjectDialog(self)
        dialog.project_created.connect(self.on_project_created)
        dialog.exec_()
    
    def on_project_created(self, name, location, description):
        """工程创建回调"""
        try:
            project = self.project_manager.create_project(name, location, description)
            self.switch_to_project(project)
            self._get_status_widget().showMessage(f"工程 '{name}' 创建成功", 3000)
            MessageHelper.success(self, "成功", f"工程 '{name}' 已创建")
        except Exception as e:
            self._get_status_widget().showMessage("创建工程失败", 5000)
            MessageHelper.error(self, "错误", f"创建工程失败：{str(e)}")
    
    def open_project(self):
        """打开工程"""
        recent_projects = self.project_manager.get_recent_projects()
        dialog = OpenProjectDialog(recent_projects, self)
        dialog.project_selected.connect(self.open_project_by_path)
        dialog.exec_()
    
    def open_project_by_path(self, project_path):
        """通过路径打开工程"""
        try:
            project = self.project_manager.open_project(project_path)
            self.switch_to_project(project)
            self._get_status_widget().showMessage(f"工程 '{project.name}' 已打开", 3000)
            MessageHelper.success(self, "成功", f"工程 '{project.name}' 已打开")
        except Exception as e:
            self._get_status_widget().showMessage("打开工程失败", 5000)
            MessageHelper.error(self, "错误", f"打开工程失败：{str(e)}")
    
    def close_project(self):
        """关闭工程"""
        if self.project_manager.has_project():
            if MessageHelper.confirm(self, "确认关闭", "确定要关闭当前工程吗？"):
                self.project_manager.close_project()
                self.switch_to_welcome_page()
                self._get_status_widget().showMessage("已关闭工程", 3000)
                MessageHelper.info(self, "提示", "已关闭工程")
    
    def switch_to_project(self, project):
        """切换到工程工作区"""
        self._project_opened = True
        
        # 更新导航项可见性
        self._update_navigation_visibility()
        
        # 更新资源管理器
        self.project_explorer.set_project(project)
        
        # 更新浮动资源管理器
        self.floating_explorer.set_project(project)
        
        # 更新任务管理器的文件路径
        self.task_manager.tasks_file = project.tasks_file
        self.task_manager.load_tasks()
        self.floating_task_list.refresh_tasks()
        
        # 切换到首帧生视频界面
        if FLUENT_AVAILABLE:
            self.stackedWidget.setCurrentWidget(self.first_frame_interface)
    
        # 启用关闭工程菜单
        self.close_project_action.setEnabled(True)
    
    def switch_to_welcome_page(self):
        """切换到欢迎页面"""
        self._project_opened = False
        
        # 更新导航项可见性
        self._update_navigation_visibility()
        
        # 刷新最近项目列表
        self._load_recent_projects_to_welcome()
        
        # 切换到欢迎页面
        if FLUENT_AVAILABLE:
            self.stackedWidget.setCurrentWidget(self.welcome_interface)
        
        # 清空资源管理器
        self.project_explorer.set_project(None)
        
        # 清空浮动资源管理器并隐藏
        self.floating_explorer.set_project(None)
        if self.floating_explorer.is_drawer_visible():
            self.floating_explorer.hide_drawer()
        
        # 隐藏浮动任务列表
        if self.floating_task_list.is_drawer_visible():
            self.floating_task_list.hide_drawer()
        
        # 禁用关闭工程菜单
        self.close_project_action.setEnabled(False)
    
    def _load_recent_projects_to_welcome(self):
        """加载最近项目到欢迎页面"""
        recent_projects = self.project_manager.get_recent_projects()
        self.welcome_page.set_recent_projects(recent_projects)
    
    def refresh_project(self):
        """刷新工程"""
        if self.project_manager.has_project():
            self.floating_task_list.refresh_tasks()
    
    def on_file_selected(self, file_path):
        """文件选中回调"""
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            viewer = ImageViewer(file_path, self)
            viewer.exec_()
            
            if self.project_manager.has_project():
                project = self.project_manager.get_current_project()
                if file_path.startswith(project.inputs_folder):
                    self.upload_widget.load_image(file_path)
                    self._get_status_widget().showMessage(f"已加载图片: {os.path.basename(file_path)}", 3000)
                    MessageHelper.info(self, "图片已加载", f"已加载: {os.path.basename(file_path)}")
        
        elif file_path.lower().endswith('.mp4'):
            if self.project_manager.has_project():
                project = self.project_manager.get_current_project()
                if file_path.startswith(project.outputs_folder):
                    current_widget = self.stackedWidget.currentWidget() if FLUENT_AVAILABLE else None
                    
                    if current_widget == self.keyframe_interface:
                        self.keyframe_tab.video_viewer.load_video(file_path)
                    else:
                        self.video_viewer.load_video(file_path)
                    
                    self._get_status_widget().showMessage(f"正在播放: {os.path.basename(file_path)}", 3000)
                    MessageHelper.info(self, "正在播放", f"正在播放: {os.path.basename(file_path)}")
                else:
                    VideoPlayer.play(file_path, self)
                    self._get_status_widget().showMessage(f"正在播放: {os.path.basename(file_path)}", 3000)
            else:
                VideoPlayer.play(file_path, self)
                self._get_status_widget().showMessage(f"正在播放: {os.path.basename(file_path)}", 3000)
