#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent 风格状态栏组件
基于 QFluentWidgets 的现代化状态栏实现
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer

try:
    from qfluentwidgets import (
        CaptionLabel, IndeterminateProgressRing, isDarkTheme
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    print("警告: QFluentWidgets 未安装，状态栏将使用原生组件")


class FluentStatusBar(QWidget):
    """Fluent 风格状态栏"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("fluentStatusBar")
        self._is_busy = False
        self._auto_hide_timer = QTimer(self)
        self._auto_hide_timer.timeout.connect(self._clear_message)
        
        self.setup_ui()
        self.apply_style()
    
    def setup_ui(self):
        """设置界面"""
        layout = QHBoxLayout(self)
        # 统一状态栏内边距：12px 水平，4px 垂直
        layout.setContentsMargins(12, 4, 12, 4)
        # 统一组件间距：8px
        layout.setSpacing(8)
        
        # 后台任务指示器（进度环）
        if FLUENT_AVAILABLE:
            self.progress_ring = IndeterminateProgressRing(self)
            self.progress_ring.setFixedSize(16, 16)
            # 设置更细的线条
            self.progress_ring.setStrokeWidth(2)
        else:
            # 降级方案：使用简单的文本指示器
            self.progress_ring = QLabel("⏳")
            self.progress_ring.setFixedSize(16, 16)
        
        self.progress_ring.hide()  # 默认隐藏
        layout.addWidget(self.progress_ring)
        
        # 状态文字标签
        if FLUENT_AVAILABLE:
            self.status_label = CaptionLabel("就绪")
        else:
            self.status_label = QLabel("就绪")
            self.status_label.setStyleSheet("font-size: 12px; color: #666;")
        
        layout.addWidget(self.status_label)
        
        # 弹性空间
        layout.addStretch()
        
        # 右侧附加信息标签（可选）
        if FLUENT_AVAILABLE:
            self.info_label = CaptionLabel("")
        else:
            self.info_label = QLabel("")
            self.info_label.setStyleSheet("font-size: 12px; color: #999;")
        
        self.info_label.hide()  # 默认隐藏
        layout.addWidget(self.info_label)
        
        # 设置固定高度
        self.setFixedHeight(28)
    
    def apply_style(self):
        """应用样式"""
        if FLUENT_AVAILABLE:
            # 根据当前主题设置背景色
            if isDarkTheme():
                bg_color = "rgba(32, 32, 32, 0.9)"
                border_color = "rgba(255, 255, 255, 0.1)"
            else:
                bg_color = "rgba(249, 249, 249, 0.9)"
                border_color = "rgba(0, 0, 0, 0.1)"
        else:
            bg_color = "rgba(249, 249, 249, 0.9)"
            border_color = "rgba(0, 0, 0, 0.1)"
        
        self.setStyleSheet(f"""
            QWidget#fluentStatusBar {{
                background-color: {bg_color};
                border-top: 1px solid {border_color};
            }}
        """)
    
    def showMessage(self, message: str, timeout: int = 0):
        """
        显示状态消息
        
        Args:
            message: 要显示的消息
            timeout: 自动清除时间（毫秒），0 表示不自动清除
        """
        self.status_label.setText(message)
        
        # 停止之前的定时器
        self._auto_hide_timer.stop()
        
        # 如果设置了超时，启动定时器
        if timeout > 0:
            self._auto_hide_timer.start(timeout)
    
    def _clear_message(self):
        """清除消息，恢复默认状态"""
        self._auto_hide_timer.stop()
        if self._is_busy:
            self.status_label.setText("处理中...")
        else:
            self.status_label.setText("就绪")
    
    def clearMessage(self):
        """清除当前消息"""
        self._clear_message()
    
    def setInfo(self, info: str):
        """
        设置右侧附加信息
        
        Args:
            info: 附加信息文本，空字符串则隐藏
        """
        if info:
            self.info_label.setText(info)
            self.info_label.show()
        else:
            self.info_label.hide()
    
    def setBusy(self, busy: bool, message: str = None):
        """
        设置忙碌状态（显示/隐藏进度指示器）
        
        Args:
            busy: 是否忙碌
            message: 可选的状态消息
        """
        self._is_busy = busy
        
        if busy:
            self.progress_ring.show()
            if message:
                self.status_label.setText(message)
            else:
                self.status_label.setText("处理中...")
        else:
            self.progress_ring.hide()
            if message:
                self.status_label.setText(message)
            else:
                self.status_label.setText("就绪")
    
    def isBusy(self) -> bool:
        """检查是否处于忙碌状态"""
        return self._is_busy
    
    def updateTheme(self):
        """更新主题（当应用主题切换时调用）"""
        self.apply_style()
