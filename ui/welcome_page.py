#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
欢迎页面
在没有打开工程时显示
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap


class WelcomePage(QWidget):
    """欢迎页面"""
    
    # 定义信号
    new_project_clicked = pyqtSignal()
    open_project_clicked = pyqtSignal()
    recent_project_clicked = pyqtSignal(str)  # project_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 设置暗黑背景
        self.setStyleSheet("""
            WelcomePage {
                background-color: #1a1a1a;
            }
        """)
        
        # 添加Logo - 使用welcome.png
        import os
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'welcome.png')
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            # Logo尺寸 - 限制最大尺寸
            scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # 快捷操作 - 左右布局的按钮
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setSpacing(20)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        # 新建工程按钮 - 波尔红、左侧
        new_btn = QPushButton("新建工程")
        new_btn.setMinimumSize(150, 50)
        new_btn.setMaximumSize(200, 60)
        new_btn.setStyleSheet("""
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
        new_btn.clicked.connect(self.new_project_clicked.emit)
        actions_layout.addWidget(new_btn)
        
        # 打开工程按钮 - 金属色、右侧
        open_btn = QPushButton("打开工程")
        open_btn.setMinimumSize(150, 50)
        open_btn.setMaximumSize(200, 60)
        open_btn.setStyleSheet("""
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
        open_btn.clicked.connect(self.open_project_clicked.emit)
        actions_layout.addWidget(open_btn)
        
        layout.addWidget(actions_widget, alignment=Qt.AlignCenter)
        
        layout.addStretch()
