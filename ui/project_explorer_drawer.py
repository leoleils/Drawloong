#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浮动资源管理器抽屉
可以在任何页面打开的独立资源管理器组件
支持从任意位置拖拽文件到目标区域
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QGraphicsDropShadowEffect, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QColor

try:
    from qfluentwidgets import (
        ToolButton, FluentIcon, isDarkTheme, CardWidget
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    from PyQt5.QtWidgets import QPushButton

from .project_explorer import ProjectExplorer


class ProjectExplorerDrawer(QFrame):
    """
    浮动资源管理器抽屉
    可以从屏幕边缘滑出，支持拖拽文件到任意位置
    """
    
    # 信号
    closed = pyqtSignal()
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("projectExplorerDrawer")
        
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
        
        # 文件夹图标
        if FLUENT_AVAILABLE:
            from qfluentwidgets import IconWidget, BodyLabel
            folder_icon = IconWidget(FluentIcon.FOLDER)
            folder_icon.setFixedSize(20, 20)
            header_layout.addWidget(folder_icon)
            
            # 标题文字
            title_label = BodyLabel("资源管理器")
            header_layout.addWidget(title_label)
        else:
            from PyQt5.QtWidgets import QLabel
            title_label = QLabel("📁 资源管理器")
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
        
        # 资源管理器
        self.explorer = ProjectExplorer()
        self.explorer.file_selected.connect(self.file_selected.emit)
        content_layout.addWidget(self.explorer)
        
        main_layout.addWidget(self.content_frame)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.content_frame.setGraphicsEffect(shadow)
        
        # 设置固定宽度
        self.setFixedWidth(280)
    
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
    
    def set_project(self, project):
        """设置当前工程"""
        self.explorer.set_project(project)
    
    def refresh(self):
        """刷新资源管理器"""
        self.explorer.refresh()
    
    def show_drawer(self, parent_widget=None):
        """显示抽屉"""
        if parent_widget:
            # 计算位置 - 显示在父窗口左侧
            parent_pos = parent_widget.mapToGlobal(QPoint(0, 0))
            self.move(parent_pos.x() + 10, parent_pos.y() + 60)
            self.setFixedHeight(parent_widget.height() - 120)
        
        self.show()
        self.raise_()
        self._is_visible = True
        
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
