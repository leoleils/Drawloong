#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
欢迎页面
在没有打开工程时显示
使用 QFluentWidgets 组件实现现代化 UI
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap

try:
    from qfluentwidgets import (
        PrimaryPushButton, PushButton, SubtitleLabel, BodyLabel,
        CardWidget, FluentIcon, IconWidget, isDarkTheme
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    print("警告: QFluentWidgets 未安装，将使用原生 PyQt5 组件")


class RecentProjectCard(CardWidget if FLUENT_AVAILABLE else QFrame):
    """最近项目卡片"""
    
    # 使用 project_clicked 避免与 CardWidget.clicked 信号冲突
    project_clicked = pyqtSignal(str)  # project_path
    
    def __init__(self, project_name: str, project_path: str, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.project_name = project_name
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QHBoxLayout(self)
        # 统一间距：16px 水平内边距，12px 垂直内边距
        layout.setContentsMargins(16, 12, 16, 12)
        # 统一组件间距：12px
        layout.setSpacing(12)
        
        # 文件夹图标
        if FLUENT_AVAILABLE:
            icon_widget = IconWidget(FluentIcon.FOLDER)
            icon_widget.setFixedSize(32, 32)
            layout.addWidget(icon_widget)
        else:
            icon_label = QLabel("📁")
            icon_label.setStyleSheet("font-size: 24px;")
            layout.addWidget(icon_label)
        
        # 项目信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        if FLUENT_AVAILABLE:
            name_label = SubtitleLabel(self.project_name)
            path_label = BodyLabel(self.project_path)
            path_label.setStyleSheet("color: #888;")
        else:
            name_label = QLabel(self.project_name)
            name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            path_label = QLabel(self.project_path)
            path_label.setStyleSheet("font-size: 12px; color: #888;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(path_label)
        layout.addLayout(info_layout, 1)
        
        # 设置卡片样式
        self.setFixedHeight(70)
        self.setCursor(Qt.PointingHandCursor)
        
        if not FLUENT_AVAILABLE:
            self.setStyleSheet("""
                RecentProjectCard {
                    background-color: #2d2d2d;
                    border-radius: 8px;
                    border: 1px solid #3d3d3d;
                }
                RecentProjectCard:hover {
                    background-color: #3d3d3d;
                    border: 1px solid #4d4d4d;
                }
            """)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.project_clicked.emit(self.project_path)
        super().mousePressEvent(event)


class WelcomePage(QWidget):
    """欢迎页面"""
    
    # 定义信号
    new_project_clicked = pyqtSignal()
    open_project_clicked = pyqtSignal()
    recent_project_clicked = pyqtSignal(str)  # project_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recent_projects = []
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        # 统一页面边距：40px
        layout.setContentsMargins(40, 40, 40, 40)
        # 统一大区块间距：24px
        layout.setSpacing(24)
        
        # 添加Logo - 使用welcome.png
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'welcome.png')
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            # Logo尺寸 - 限制最大尺寸
            scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # 欢迎标题
        if FLUENT_AVAILABLE:
            title_label = SubtitleLabel("欢迎使用烛龙绘影")
            title_label.setAlignment(Qt.AlignCenter)
        else:
            title_label = QLabel("欢迎使用烛龙绘影")
            title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff;")
            title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 副标题描述
        if FLUENT_AVAILABLE:
            desc_label = BodyLabel("创建或打开工程开始您的创作之旅")
            desc_label.setAlignment(Qt.AlignCenter)
        else:
            desc_label = QLabel("创建或打开工程开始您的创作之旅")
            desc_label.setStyleSheet("font-size: 14px; color: #888;")
            desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        layout.addSpacing(16)
        
        # 快捷操作 - 左右布局的按钮
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setSpacing(20)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        if FLUENT_AVAILABLE:
            # 新建工程按钮 - 使用 PrimaryPushButton
            self.new_btn = PrimaryPushButton(FluentIcon.ADD, "新建工程")
            self.new_btn.setMinimumSize(150, 50)
            self.new_btn.setMaximumSize(200, 60)
            self.new_btn.clicked.connect(self.new_project_clicked.emit)
            actions_layout.addWidget(self.new_btn)
            
            # 打开工程按钮 - 使用 PushButton
            self.open_btn = PushButton(FluentIcon.FOLDER, "打开工程")
            self.open_btn.setMinimumSize(150, 50)
            self.open_btn.setMaximumSize(200, 60)
            self.open_btn.clicked.connect(self.open_project_clicked.emit)
            actions_layout.addWidget(self.open_btn)
        else:
            # 降级到原生按钮
            self.new_btn = QPushButton("新建工程")
            self.new_btn.setMinimumSize(150, 50)
            self.new_btn.setMaximumSize(200, 60)
            self.new_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #dc143c, stop:1 #a00000);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff1744, stop:1 #c00000);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #b00000, stop:1 #800000);
                }
            """)
            self.new_btn.clicked.connect(self.new_project_clicked.emit)
            actions_layout.addWidget(self.new_btn)
            
            self.open_btn = QPushButton("打开工程")
            self.open_btn.setMinimumSize(150, 50)
            self.open_btn.setMaximumSize(200, 60)
            self.open_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #c0c0c0, stop:1 #808080);
                    color: #2c3e50;
                    border: 1px solid #909090;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #d0d0d0, stop:1 #909090);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #a0a0a0, stop:1 #707070);
                }
            """)
            self.open_btn.clicked.connect(self.open_project_clicked.emit)
            actions_layout.addWidget(self.open_btn)
        
        layout.addWidget(actions_widget, alignment=Qt.AlignCenter)
        
        layout.addSpacing(24)
        
        # 最近项目区域
        self.recent_section = QWidget()
        recent_layout = QVBoxLayout(self.recent_section)
        recent_layout.setContentsMargins(0, 0, 0, 0)
        recent_layout.setSpacing(12)
        
        # 最近项目标题
        if FLUENT_AVAILABLE:
            recent_title = SubtitleLabel("最近项目")
        else:
            recent_title = QLabel("最近项目")
            recent_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #fff;")
        recent_layout.addWidget(recent_title, alignment=Qt.AlignCenter)
        
        # 最近项目卡片容器
        self.recent_cards_widget = QWidget()
        self.recent_cards_layout = QVBoxLayout(self.recent_cards_widget)
        self.recent_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_cards_layout.setSpacing(8)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.recent_cards_widget)
        scroll_area.setMaximumHeight(250)
        scroll_area.setMinimumWidth(400)
        scroll_area.setMaximumWidth(500)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        recent_layout.addWidget(scroll_area, alignment=Qt.AlignCenter)
        
        # 初始隐藏最近项目区域
        self.recent_section.setVisible(False)
        layout.addWidget(self.recent_section)
        
        layout.addStretch()
    
    def set_recent_projects(self, projects: list):
        """
        设置最近项目列表
        
        Args:
            projects: 项目列表，每项为 (name, path) 元组或字典
        """
        self.recent_projects = projects
        
        # 清空现有卡片
        while self.recent_cards_layout.count():
            item = self.recent_cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加新卡片
        if projects:
            for project in projects[:5]:  # 最多显示5个
                if isinstance(project, dict):
                    name = project.get('name', '未命名项目')
                    path = project.get('path', '')
                elif isinstance(project, (list, tuple)) and len(project) >= 2:
                    name, path = project[0], project[1]
                else:
                    continue
                
                card = RecentProjectCard(name, path)
                card.project_clicked.connect(self._on_recent_project_clicked)
                self.recent_cards_layout.addWidget(card)
            
            self.recent_section.setVisible(True)
        else:
            self.recent_section.setVisible(False)
    
    def _on_recent_project_clicked(self, project_path: str):
        """最近项目点击回调"""
        self.recent_project_clicked.emit(project_path)
    
    def update_theme(self):
        """更新主题（当主题切换时调用）"""
        # 重新设置样式以适应新主题
        pass
