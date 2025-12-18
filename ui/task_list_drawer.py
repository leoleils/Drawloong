#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浮动任务列表抽屉
可以在任何页面打开的独立任务列表组件
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QColor

try:
    from qfluentwidgets import (
        ToolButton, FluentIcon, isDarkTheme, IconWidget, BodyLabel
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    from PyQt5.QtWidgets import QPushButton, QLabel

from .task_list import TaskListWidget


class TaskListDrawer(QFrame):
    """
    浮动任务列表抽屉
    可以从屏幕边缘滑出，显示任务列表
    """
    
    # 信号
    closed = pyqtSignal()
    task_updated = pyqtSignal(str)  # task_id
    
    def __init__(self, task_manager, project_manager, parent=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.project_manager = project_manager
        self.setObjectName("taskListDrawer")
        
        # 设置为无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 动画
        self._animation = None
        self._is_visible = False
        
        self.setup_ui()
        self.apply_style()
    
    def setup_ui(self):
        """设置界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 内容容器（带圆角和阴影）
        self.content_frame = QFrame()
        self.content_frame.setObjectName("drawerContent")
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 标题栏
        header = QWidget()
        header.setObjectName("drawerHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 8, 8)
        header_layout.setSpacing(8)
        
        # 任务图标和标题
        if FLUENT_AVAILABLE:
            task_icon = IconWidget(FluentIcon.HISTORY)
            task_icon.setFixedSize(20, 20)
            header_layout.addWidget(task_icon)
            
            title_label = BodyLabel("任务列表")
            header_layout.addWidget(title_label)
        else:
            title_label = QLabel("📋 任务列表")
            title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 关闭按钮
        if FLUENT_AVAILABLE:
            self.close_btn = ToolButton(FluentIcon.CLOSE)
            self.close_btn.setFixedSize(28, 28)
        else:
            self.close_btn = QPushButton("×")
            self.close_btn.setFixedSize(28, 28)
        self.close_btn.clicked.connect(self.hide_drawer)
        header_layout.addWidget(self.close_btn)
        
        content_layout.addWidget(header)
        
        # 任务列表
        self.task_list = TaskListWidget(self.task_manager, self.project_manager)
        self.task_list.task_updated.connect(self.task_updated.emit)
        content_layout.addWidget(self.task_list)
        
        main_layout.addWidget(self.content_frame)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(-2, 2)
        self.content_frame.setGraphicsEffect(shadow)
        
        # 设置固定宽度
        self.setFixedWidth(400)
    
    def apply_style(self):
        """应用样式"""
        if FLUENT_AVAILABLE:
            is_dark = isDarkTheme()
        else:
            is_dark = False
        
        if is_dark:
            bg_color = "#2d2d2d"
            border_color = "#3d3d3d"
            header_bg = "#252525"
        else:
            bg_color = "#ffffff"
            border_color = "#e0e0e0"
            header_bg = "#f5f5f5"
        
        self.setStyleSheet(f"""
            QFrame#drawerContent {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            QWidget#drawerHeader {{
                background-color: {header_bg};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid {border_color};
            }}
        """)
    
    def refresh_tasks(self):
        """刷新任务列表"""
        self.task_list.refresh_tasks()
    
    def start_monitoring_task(self, task_id):
        """开始监控任务"""
        self.task_list.start_monitoring_task(task_id)
    
    def show_drawer(self, parent_widget=None):
        """显示抽屉"""
        if parent_widget:
            # 计算位置 - 显示在父窗口右侧
            parent_pos = parent_widget.mapToGlobal(QPoint(0, 0))
            self.move(parent_pos.x() + parent_widget.width() - self.width() - 10, 
                     parent_pos.y() + 60)
            self.setFixedHeight(parent_widget.height() - 120)
        
        self.show()
        self.raise_()
        self._is_visible = True
        
        # 刷新任务列表
        self.refresh_tasks()
        
        # 动画效果
        if self._animation:
            self._animation.stop()
        
        self._animation = QPropertyAnimation(self, b"windowOpacity")
        self._animation.setDuration(200)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.start()
    
    def hide_drawer(self):
        """隐藏抽屉"""
        if self._animation:
            self._animation.stop()
        
        self._animation = QPropertyAnimation(self, b"windowOpacity")
        self._animation.setDuration(150)
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.setEasingCurve(QEasingCurve.InCubic)
        self._animation.finished.connect(self._on_hide_finished)
        self._animation.start()
    
    def _on_hide_finished(self):
        """隐藏动画完成"""
        self.hide()
        self._is_visible = False
        self.closed.emit()
    
    def toggle(self, parent_widget=None):
        """切换显示/隐藏"""
        if self._is_visible:
            self.hide_drawer()
        else:
            self.show_drawer(parent_widget)
    
    def is_drawer_visible(self):
        """检查抽屉是否可见"""
        return self._is_visible
    
    def updateTheme(self):
        """更新主题"""
        self.apply_style()
