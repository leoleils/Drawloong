#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口
应用的主界面窗口
"""

import os
import shutil
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QStatusBar, QMessageBox, QSplitter, QPushButton, QAction, QStackedWidget, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap

from .upload_widget import UploadWidget
from .config_panel import ConfigPanel
from .task_list import TaskListWidget
from .settings_dialog import SettingsDialog
from .project_explorer import ProjectExplorer
from .welcome_page import WelcomePage
from .project_dialog import NewProjectDialog, OpenProjectDialog
from .image_viewer import ImageViewer
from .video_player import VideoPlayer
from .video_viewer import VideoViewerWidget
from .text_to_image_widget import TextToImageWidget
from .image_edit_widget import ImageEditWidget
from .keyframe_to_video_widget import KeyframeToVideoWidget
from core.task_manager import TaskManager
from core.api_client import DashScopeClient
from core.project_manager import ProjectManager
from config.settings import settings
from themes.themes import Themes


class MainWindow(QMainWindow):
    """主窗口类"""
    
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
        
        # 设置窗口
        self.setup_ui()
        
        # 应用主题
        self.apply_theme()
        
        # 连接信号
        self.connect_signals()
        
        # 检查 API 密钥
        self.check_api_key()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("烛龙绘影 Drawloong")
        # 默认欢迎页尺寸较小
        self.resize(450, 550)
        self.setMinimumSize(450, 550)
        
        # 设置窗口图标
        import os
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo.png')
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 默认隐藏菜单栏(欢迎页时隐藏)
        self.menuBar().hide()
        
        # 中心部件 - 使用堆叠布局
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)
        
        # 创建欢迎页面容器(居中显示)
        welcome_container = QWidget()
        welcome_container.setStyleSheet("background-color: #1a1a1a;")  # 暗黑背景
        welcome_layout = QVBoxLayout(welcome_container)
        welcome_layout.setAlignment(Qt.AlignCenter)
        self.welcome_page = WelcomePage()
        welcome_layout.addWidget(self.welcome_page, alignment=Qt.AlignCenter)
        self.central_stack.addWidget(welcome_container)
        
        # 创建工作区
        self.work_area = self.create_work_area()
        self.central_stack.addWidget(self.work_area)
        
        # 默认显示欢迎页面容器
        self.central_stack.setCurrentWidget(welcome_container)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 默认隐藏状态栏(欢迎页时隐藏)
        self.status_bar.hide()
    
    def create_work_area(self):
        """创建工作区域"""
        work_widget = QWidget()
        layout = QHBoxLayout(work_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 主分割器 - 水平
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(0)  # 设置手柄宽度为0
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background: transparent;
                width: 0px;
                margin: 0px;
                padding: 0px;
            }
            QSplitter::handle:horizontal {
                width: 0px;
            }
        """)
        
        # 左侧：工程资源管理器
        self.project_explorer = ProjectExplorer()
        self.project_explorer.setMaximumWidth(300)
        self.project_explorer.setMinimumWidth(200)
        main_splitter.addWidget(self.project_explorer)
        
        # 中间和右侧：内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题栏
        title_layout = QHBoxLayout()
        self.project_title = QLabel("未打开工程")
        self.project_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
        """)
        title_layout.addWidget(self.project_title)
        title_layout.addStretch()
        
        # 设置按钮
        settings_btn = QPushButton("⚙ 设置")
        settings_btn.clicked.connect(self.open_settings)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        title_layout.addWidget(settings_btn)
        content_layout.addLayout(title_layout)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background: white;
            }
            QTabBar::tab {
                background: #f8f9fa;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #ddd;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #e9ecef;
            }
        """)
        
        # 标签页 1：首帧生视频（当前功能）
        self.first_frame_tab = self.create_first_frame_tab()
        self.tab_widget.addTab(self.first_frame_tab, "首帧生视频")
        
        # 标签页 2：首尾帧生视频（已实现）
        self.keyframe_tab = KeyframeToVideoWidget(self.api_client, self.project_manager, self.task_manager)
        self.tab_widget.addTab(self.keyframe_tab, "首尾帧生视频")
        
        # 标签页 3：文生图（已实现）
        self.text_to_image_tab = TextToImageWidget(self.api_client, self.project_manager)
        self.tab_widget.addTab(self.text_to_image_tab, "文生图")
        
        # 标签页 4:图像编辑(已实现)
        self.image_edit_tab = ImageEditWidget(self.api_client, self.project_manager)
        self.tab_widget.addTab(self.image_edit_tab, "图像编辑")
        
        content_layout.addWidget(self.tab_widget)
        main_splitter.addWidget(content_widget)
        
        # 设置分割比例
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 4)
        
        layout.addWidget(main_splitter)
        return work_widget
    
    def create_first_frame_tab(self):
        """创建首帧生视频标签页"""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # 主水平分割器 - 左右布局
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：上传图片和视频浏览（上下对称）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_splitter = QSplitter(Qt.Vertical)
        
        # 上：上传图片
        self.upload_widget = UploadWidget()
        self.upload_widget.set_project_manager(self.project_manager)
        left_splitter.addWidget(self.upload_widget)
        
        # 下：视频浏览
        self.video_viewer = VideoViewerWidget()
        left_splitter.addWidget(self.video_viewer)
        
        # 上下各占一半
        left_splitter.setStretchFactor(0, 1)
        left_splitter.setStretchFactor(1, 1)
        
        left_layout.addWidget(left_splitter)
        main_splitter.addWidget(left_widget)
        
        # 右侧：配置面板和任务列表
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        right_splitter = QSplitter(Qt.Vertical)
        
        # 上：配置面板（占大部分）
        self.config_panel = ConfigPanel()
        right_splitter.addWidget(self.config_panel)
        
        # 下：任务列表
        self.task_list = TaskListWidget(self.task_manager, self.project_manager)
        right_splitter.addWidget(self.task_list)
        
        # 配置面板占更多空间
        right_splitter.setStretchFactor(0, 3)
        right_splitter.setStretchFactor(1, 1)
        
        right_layout.addWidget(right_splitter)
        main_splitter.addWidget(right_widget)
        
        # 左右比例：左侧占1份，右侧占1份
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
        
        tab_layout.addWidget(main_splitter)
        return tab_widget
    
    def create_placeholder_tab(self, title, message):
        """创建占位标签页"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # 占位内容
        placeholder = QLabel(message)
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #999;
                padding: 100px;
            }
        """)
        layout.addWidget(placeholder)
        
        return tab_widget
    
    def create_menu_bar(self):
        """创建菜单栏"""
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
        settings_action.setShortcut('Ctrl+,')  # macOS 风格快捷键
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # 退出菜单项
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
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
    
    def check_api_key(self):
        """检查 API 密钥配置"""
        if not settings.is_api_key_valid():
            reply = QMessageBox.question(
                self,
                "配置提醒",
                "未检测到 API 密钥配置\n\n"
                "是否现在打开设置页面配置？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.open_settings()
            else:
                self.config_panel.generate_btn.setEnabled(False)
    
    def on_image_selected(self, image_path):
        """图片选择回调"""
        self.current_image_path = image_path
        self.status_bar.showMessage(f"已选择图片: {os.path.basename(image_path)}")
        self.config_panel.generate_btn.setEnabled(True)
    
    def on_generate_clicked(self, config):
        """生成按钮点击回调"""
        if not self.current_image_path:
            QMessageBox.warning(self, "提示", "请先选择一张图片")
            return
        
        if not settings.is_api_key_valid():
            QMessageBox.warning(self, "提示", "API 密钥未配置或无效")
            return
        
        # 检查是否有工程
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "提示", "请先创建或打开工程")
            return
        
        project = self.project_manager.get_current_project()
        
        # 复制图片到工程 inputs 文件夹
        try:
            image_name = os.path.basename(self.current_image_path)
            dest_path = os.path.join(project.inputs_folder, image_name)
            
            # 如果源文件不在工程文件夹中，则复制
            if os.path.abspath(self.current_image_path) != os.path.abspath(dest_path):
                shutil.copy2(self.current_image_path, dest_path)
                self.current_image_path = dest_path
                self.project_explorer.refresh()
        except Exception as e:
            print(f"复制图片失败: {e}")
        
        # 禁用生成按钮并更新文本
        self.config_panel.generate_btn.setEnabled(False)
        self.config_panel.generate_btn.setText("生成中...")
        self.status_bar.showMessage("正在提交任务...")
        
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
            
            # 解析时长（从"5秒"、"10秒"等格式中提取数字）
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
            
            # 如果配置中有shot_type参数（2.6模型），添加到请求中
            if 'shot_type' in config:
                submit_params['shot_type'] = config['shot_type']
            
            result = self.api_client.submit_task(**submit_params)
            
            # 更新任务信息
            async_task_id = result['output']['task_id']
            self.task_manager.update_task(
                task.id,
                async_task_id=async_task_id
            )
            
            # 保存当前任务ID，用于完成后加载视频
            self.current_generating_task_id = task.id
            
            # 刷新任务列表并开始监控
            self.task_list.refresh_tasks()
            self.task_list.start_monitoring_task(task.id)
            
            self.status_bar.showMessage("任务已提交，正在生成视频...")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"任务提交失败：{str(e)}")
            self.status_bar.showMessage("任务提交失败")
            # 恢复按钮
            self.config_panel.generate_btn.setEnabled(True)
            self.config_panel.generate_btn.setText("生成视频")
    
    def on_task_updated(self, task_id):
        """任务更新回调"""
        task = self.task_manager.get_task(task_id)
        if task and task.is_completed():
            # 检查是否是当前正在生成的任务
            if hasattr(self, 'current_generating_task_id') and task_id == self.current_generating_task_id:
                # 恢复生成按钮
                self.config_panel.generate_btn.setEnabled(True)
                self.config_panel.generate_btn.setText("生成视频")
                
                if task.is_success():
                    self.status_bar.showMessage(f"视频生成成功！")
                    
                    # 自动加载视频到播放器
                    if task.output_path and os.path.exists(task.output_path):
                        self.video_viewer.load_video(task.output_path)
                        QMessageBox.information(self, "成功", "视频生成完成！已自动加载到播放器。")
                    else:
                        QMessageBox.information(self, "成功", "视频生成完成！")
                else:
                    self.status_bar.showMessage(f"视频生成失败")
                    QMessageBox.warning(self, "失败", "视频生成失败，请查看任务列表了解详情。")
                
                # 清除当前任务ID
                self.current_generating_task_id = None
            else:
                # 其他任务完成
                if task.is_success():
                    self.status_bar.showMessage(f"任务 {task_id[:8]} 已完成")
                else:
                    self.status_bar.showMessage(f"任务 {task_id[:8]} 失败")
    
    def open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self)
        dialog.api_key_changed.connect(self.on_api_key_changed)
        dialog.theme_changed.connect(self.on_theme_changed)  # 连接主题变更信号
        dialog.exec_()
    
    def on_api_key_changed(self, api_key):
        """API 密钥变更回调"""
        # 重新创建 API 客户端
        self.api_client = DashScopeClient()
        
        # 更新状态
        if settings.is_api_key_valid():
            self.status_bar.showMessage("API 密钥已更新")
            self.config_panel.generate_btn.setEnabled(True)
        else:
            self.status_bar.showMessage("API 密钥无效")
            self.config_panel.generate_btn.setEnabled(False)
    
    def show_about(self):
        """显示关于对话框"""
        import os
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
        from PyQt5.QtCore import Qt
        
        # 创建自定义对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("关于")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        
        # 添加logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo.png')
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            # 缩放到适当大小
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # 添加信息
        info_label = QLabel(
            "<h2>烛龙绘影 Drawloong</h2>"
            "<p><b>版本:</b> 1.0.0</p>"
            "<p>基于 PyQt5 的桌面客户端应用</p>"
            "<p>调用阿里云 DashScope API 实现图片转视频功能</p>"
            "<p><a href='https://dashscope.console.aliyun.com/'>获取 API 密钥</a></p>"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setOpenExternalLinks(True)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 添加关闭按钮
        from PyQt5.QtWidgets import QPushButton, QHBoxLayout
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
            self.status_bar.showMessage(f"工程 '{name}' 创建成功")
            QMessageBox.information(self, "成功", f"工程 '{name}' 已创建")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建工程失败：{str(e)}")
    
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
            self.status_bar.showMessage(f"工程 '{project.name}' 已打开")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开工程失败：{str(e)}")
    
    def close_project(self):
        """关闭工程"""
        if self.project_manager.has_project():
            reply = QMessageBox.question(
                self,
                "确认关闭",
                "确定要关闭当前工程吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.project_manager.close_project()
                self.switch_to_welcome_page()
                self.status_bar.showMessage("已关闭工程")
    
    def switch_to_project(self, project):
        """切换到工程工作区"""
        # 调整窗口大小为工作区尺寸
        self.setMinimumSize(1200, 800)
        self.resize(1200, 800)
        
        # 显示菜单栏和状态栏
        self.menuBar().show()
        self.status_bar.show()
        
        # 更新项目标题
        self.project_title.setText(project.name)
        
        # 更新资源管理器
        self.project_explorer.set_project(project)
        
        # 更新任务管理器的文件路径
        self.task_manager.tasks_file = project.tasks_file
        self.task_manager.load_tasks()
        self.task_list.refresh_tasks()
        
        # 切换到工作区
        self.central_stack.setCurrentWidget(self.work_area)
        
        # 启用关闭工程菜单
        self.close_project_action.setEnabled(True)
    
    def switch_to_welcome_page(self):
        """切换到欢迎页面"""
        # 调整窗口大小为欢迎页尺寸
        self.setMinimumSize(450, 550)
        self.resize(450, 550)
        
        # 隐藏菜单栏和状态栏
        self.menuBar().hide()
        self.status_bar.hide()
        
        # 切换到欢迎页面容器
        welcome_container = self.central_stack.widget(0)
        self.central_stack.setCurrentWidget(welcome_container)
        
        # 清空资源管理器
        self.project_explorer.set_project(None)
        
        # 禁用关闭工程菜单
        self.close_project_action.setEnabled(False)
    
    def refresh_project(self):
        """刷新工程"""
        if self.project_manager.has_project():
            self.task_list.refresh_tasks()
    
    def on_file_selected(self, file_path):
        """文件选中回调"""
        # 判断文件类型
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            # 图片文件 - 打开图片查看器
            viewer = ImageViewer(file_path, self)
            viewer.exec_()
            
            # 如果是 inputs 文件夹中的图片，自动加载到上传组件
            if self.project_manager.has_project():
                project = self.project_manager.get_current_project()
                if file_path.startswith(project.inputs_folder):
                    self.upload_widget.load_image(file_path)
                    self.status_bar.showMessage(f"已加载图片: {os.path.basename(file_path)}")
        
        elif file_path.lower().endswith('.mp4'):
            # 视频文件 - 在视频浏览器中播放
            if self.project_manager.has_project():
                project = self.project_manager.get_current_project()
                # 如果是 outputs 文件夹中的视频，在视频浏览器中播放
                if file_path.startswith(project.outputs_folder):
                    # 获取当前激活的标签页
                    current_tab = self.tab_widget.currentWidget()
                    
                    # 根据当前标签页选择对应的视频浏览器
                    if current_tab == self.keyframe_tab:
                        # 首尾帧页面 - 使用该页面的视频浏览器
                        self.keyframe_tab.video_viewer.load_video(file_path)
                    else:
                        # 其他页面 - 使用首帧生视频页面的视频浏览器
                        self.video_viewer.load_video(file_path)
                    
                    self.status_bar.showMessage(f"正在播放: {os.path.basename(file_path)}")
                else:
                    # 其他视频文件用系统播放器
                    VideoPlayer.play(file_path, self)
                    self.status_bar.showMessage(f"正在播放: {os.path.basename(file_path)}")
            else:
                # 没有工程时用系统播放器
                VideoPlayer.play(file_path, self)
                self.status_bar.showMessage(f"正在播放: {os.path.basename(file_path)}")
    
    def apply_theme(self, theme_name=None):
        """应用主题"""
        if theme_name is None:
            theme_name = settings.get_theme()
        
        theme_stylesheet = Themes.get_theme(theme_name)
        self.setStyleSheet(theme_stylesheet)
        
        self.status_bar.showMessage(f"已切换主题: {theme_name}")
    
    def on_theme_changed(self, theme_name):
        """主题变更处理"""
        self.apply_theme(theme_name)
        QMessageBox.information(
            self,
            "主题已更改",
            f"主题已成功切换!\n\n新主题已应用到整个应用。"
        )
