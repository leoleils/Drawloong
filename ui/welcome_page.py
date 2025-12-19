#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
欢迎页面
全屏背景图，按钮和内容悬浮在上面
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QPainter, QBrush

try:
    from qfluentwidgets import (
        PrimaryPushButton, PushButton, SubtitleLabel, BodyLabel,
        CardWidget, FluentIcon, IconWidget, isDarkTheme
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False


class RecentProjectCard(CardWidget if FLUENT_AVAILABLE else QFrame):
    """最近项目卡片"""
    
    project_clicked = pyqtSignal(str)
    
    def __init__(self, project_name: str, project_path: str, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.project_name = project_name
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        if FLUENT_AVAILABLE:
            icon_widget = IconWidget(FluentIcon.FOLDER)
            icon_widget.setFixedSize(32, 32)
            layout.addWidget(icon_widget)
        else:
            icon_label = QLabel("📁")
            icon_label.setStyleSheet("font-size: 24px;")
            layout.addWidget(icon_label)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        if FLUENT_AVAILABLE:
            name_label = SubtitleLabel(self.project_name)
            path_label = BodyLabel(self.project_path)
            path_label.setStyleSheet("color: rgba(255,255,255,0.6);")
        else:
            name_label = QLabel(self.project_name)
            name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #fff;")
            path_label = QLabel(self.project_path)
            path_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.6);")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(path_label)
        layout.addLayout(info_layout, 1)
        
        self.setFixedHeight(70)
        self.setCursor(Qt.PointingHandCursor)
        
        self.setStyleSheet("""
            RecentProjectCard {
                background-color: rgba(0, 0, 0, 0.5);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
            RecentProjectCard:hover {
                background-color: rgba(0, 0, 0, 0.65);
                border: 1px solid rgba(255, 255, 255, 0.25);
            }
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.project_clicked.emit(self.project_path)
        super().mousePressEvent(event)


class WelcomePage(QWidget):
    """欢迎页面 - 全屏背景图"""
    
    new_project_clicked = pyqtSignal()
    open_project_clicked = pyqtSignal()
    recent_project_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recent_projects = []
        self.background_pixmap = None
        self.load_background()
        self.setup_ui()
    
    def load_background(self):
        """加载背景图"""
        bg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'welcome-cover.png')
        if os.path.exists(bg_path):
            self.background_pixmap = QPixmap(bg_path)
    
    def paintEvent(self, event):
        """绘制全屏背景图"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        if self.background_pixmap and not self.background_pixmap.isNull():
            # 缩放背景图填满整个区域
            scaled = self.background_pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            # 居中绘制
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            # 没有背景图时使用深色背景
            painter.fillRect(self.rect(), QColor(28, 28, 30))
        
        painter.end()
    
    def setup_ui(self):
        # 主布局 - 居中显示内容
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 内容容器 - 悬浮在背景上
        content_widget = QWidget()
        content_widget.setAttribute(Qt.WA_TranslucentBackground)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignCenter)
        
        # 半透明内容卡片
        card = QFrame()
        card.setObjectName("welcomeCard")
        card.setStyleSheet("""
            #welcomeCard {
                background-color: rgba(0, 0, 0, 0.6);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        card.setFixedWidth(460)
        
        # 阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 32, 36, 32)
        card_layout.setSpacing(14)
        
        # 标题
        title_label = QLabel("欢迎使用烛龙绘影")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)
        
        # 副标题
        desc_label = QLabel("创建或打开工程开始您的创作之旅")
        desc_label.setStyleSheet("font-size: 14px; color: rgba(255, 255, 255, 0.7);")
        desc_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(desc_label)
        
        card_layout.addSpacing(12)
        
        # 按钮
        btn_widget = QWidget()
        btn_widget.setAttribute(Qt.WA_TranslucentBackground)
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setSpacing(16)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        if FLUENT_AVAILABLE:
            self.new_btn = PrimaryPushButton(FluentIcon.ADD, "新建工程")
            self.new_btn.setMinimumSize(140, 46)
            self.new_btn.clicked.connect(self.new_project_clicked.emit)
            btn_layout.addWidget(self.new_btn)
            
            self.open_btn = PushButton(FluentIcon.FOLDER, "打开工程")
            self.open_btn.setMinimumSize(140, 46)
            self.open_btn.clicked.connect(self.open_project_clicked.emit)
            btn_layout.addWidget(self.open_btn)
        else:
            self.new_btn = QPushButton("新建工程")
            self.new_btn.setMinimumSize(140, 46)
            self.new_btn.setStyleSheet("""
                QPushButton {
                    background: #dc143c; color: white;
                    border: none; border-radius: 8px;
                    font-size: 15px; font-weight: bold;
                }
                QPushButton:hover { background: #ff1744; }
            """)
            self.new_btn.clicked.connect(self.new_project_clicked.emit)
            btn_layout.addWidget(self.new_btn)
            
            self.open_btn = QPushButton("打开工程")
            self.open_btn.setMinimumSize(140, 46)
            self.open_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.15); color: white;
                    border: 1px solid rgba(255,255,255,0.3); border-radius: 8px;
                    font-size: 15px; font-weight: bold;
                }
                QPushButton:hover { background: rgba(255,255,255,0.25); }
            """)
            self.open_btn.clicked.connect(self.open_project_clicked.emit)
            btn_layout.addWidget(self.open_btn)
        
        card_layout.addWidget(btn_widget, alignment=Qt.AlignCenter)
        
        # 最近项目
        self.recent_section = QWidget()
        self.recent_section.setAttribute(Qt.WA_TranslucentBackground)
        recent_layout = QVBoxLayout(self.recent_section)
        recent_layout.setContentsMargins(0, 16, 0, 0)
        recent_layout.setSpacing(12)
        
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.15);")
        recent_layout.addWidget(separator)
        
        recent_title = QLabel("最近项目")
        recent_title.setStyleSheet("font-size: 14px; font-weight: bold; color: rgba(255,255,255,0.85);")
        recent_layout.addWidget(recent_title, alignment=Qt.AlignCenter)
        
        self.recent_cards_widget = QWidget()
        self.recent_cards_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.recent_cards_layout = QVBoxLayout(self.recent_cards_widget)
        self.recent_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_cards_layout.setSpacing(8)
        
        recent_scroll = QScrollArea()
        recent_scroll.setWidgetResizable(True)
        recent_scroll.setWidget(self.recent_cards_widget)
        recent_scroll.setMaximumHeight(200)
        recent_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        recent_scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
        """)
        recent_layout.addWidget(recent_scroll)
        
        self.recent_section.setVisible(False)
        card_layout.addWidget(self.recent_section)
        
        content_layout.addStretch()
        content_layout.addWidget(card, alignment=Qt.AlignCenter)
        content_layout.addStretch()
        
        layout.addWidget(content_widget)
    
    def set_recent_projects(self, projects: list):
        self.recent_projects = projects
        
        while self.recent_cards_layout.count():
            item = self.recent_cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if projects:
            for project in projects[:5]:
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
        self.recent_project_clicked.emit(project_path)
    
    def update_theme(self):
        pass
