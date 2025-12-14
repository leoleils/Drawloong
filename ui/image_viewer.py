#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片浏览器
支持图片缩放、拖动
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QPainter


class ImageViewer(QDialog):
    """图片浏览器"""
    
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.scale_factor = 1.0
        self.drag_position = QPoint()
        
        self.setup_ui()
        self.load_image()
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("图片浏览")
        self.resize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        
        # 文件名
        self.filename_label = QLabel(os.path.basename(self.image_path))
        self.filename_label.setStyleSheet("font-weight: bold;")
        toolbar_layout.addWidget(self.filename_label)
        
        toolbar_layout.addStretch()
        
        # 缩放比例显示
        self.scale_label = QLabel("100%")
        toolbar_layout.addWidget(self.scale_label)
        
        # 缩小按钮
        zoom_out_btn = QPushButton("🔍-")
        zoom_out_btn.setToolTip("缩小 (Ctrl+-)")
        zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar_layout.addWidget(zoom_out_btn)
        
        # 适应窗口按钮
        fit_btn = QPushButton("⊡")
        fit_btn.setToolTip("适应窗口 (Ctrl+0)")
        fit_btn.clicked.connect(self.fit_to_window)
        toolbar_layout.addWidget(fit_btn)
        
        # 原始大小按钮
        actual_btn = QPushButton("1:1")
        actual_btn.setToolTip("实际大小 (Ctrl+1)")
        actual_btn.clicked.connect(self.actual_size)
        toolbar_layout.addWidget(actual_btn)
        
        # 放大按钮
        zoom_in_btn = QPushButton("🔍+")
        zoom_in_btn.setToolTip("放大 (Ctrl++)")
        zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar_layout.addWidget(zoom_in_btn)
        
        layout.addWidget(toolbar)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignCenter)
        
        # 图片标签
        self.image_label = QLabel()
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_image(self):
        """加载图片"""
        self.original_pixmap = QPixmap(self.image_path)
        if self.original_pixmap.isNull():
            self.image_label.setText("无法加载图片")
            return
        
        # 默认适应窗口
        self.fit_to_window()
    
    def update_image(self):
        """更新显示的图片"""
        if self.original_pixmap.isNull():
            return
        
        # 计算缩放后的尺寸
        new_size = self.original_pixmap.size() * self.scale_factor
        scaled_pixmap = self.original_pixmap.scaled(
            new_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
        self.scale_label.setText(f"{int(self.scale_factor * 100)}%")
    
    def zoom_in(self):
        """放大"""
        self.scale_factor *= 1.25
        self.update_image()
    
    def zoom_out(self):
        """缩小"""
        self.scale_factor /= 1.25
        self.update_image()
    
    def actual_size(self):
        """实际大小"""
        self.scale_factor = 1.0
        self.update_image()
    
    def fit_to_window(self):
        """适应窗口"""
        if self.original_pixmap.isNull():
            return
        
        # 获取可用空间
        available_width = self.width() - 50
        available_height = self.height() - 150
        
        # 计算缩放比例
        width_ratio = available_width / self.original_pixmap.width()
        height_ratio = available_height / self.original_pixmap.height()
        
        self.scale_factor = min(width_ratio, height_ratio, 1.0)
        self.update_image()
    
    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
                self.zoom_in()
            elif event.key() == Qt.Key_Minus:
                self.zoom_out()
            elif event.key() == Qt.Key_0:
                self.fit_to_window()
            elif event.key() == Qt.Key_1:
                self.actual_size()
        else:
            super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 如果是适应窗口模式，重新调整
        if hasattr(self, 'original_pixmap') and not self.original_pixmap.isNull():
            if self.scale_factor < 1.0:
                self.fit_to_window()
