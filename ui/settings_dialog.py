#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置对话框
用于配置 API 密钥等设置
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGroupBox, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from config.settings import settings
from themes.themes import Themes


class SettingsDialog(QDialog):
    """设置对话框"""
    
    # 定义信号
    api_key_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)  # 主题变更信号
    
    def __init__(self, parent=None):
        """初始化设置对话框"""
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("设置")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        # 设置窗口图标
        import os
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo.png')
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        layout = QVBoxLayout(self)
        
        # API 配置组
        api_group = QGroupBox("API 配置")
        api_layout = QVBoxLayout(api_group)
        
        # API 密钥说明
        info_label = QLabel(
            "请输入你的阿里云 DashScope API 密钥\n"
            "获取地址: https://dashscope.console.aliyun.com/"
        )
        info_label.setStyleSheet("color: #666; font-size: 12px;")
        info_label.setWordWrap(True)
        api_layout.addWidget(info_label)
        
        # API 密钥标签
        key_label = QLabel("API 密钥 (SK):")
        key_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        api_layout.addWidget(key_label)
        
        # API 密钥输入框
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.api_key_input)
        
        # 显示/隐藏密钥按钮
        show_btn_layout = QHBoxLayout()
        self.show_key_btn = QPushButton("显示密钥")
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.clicked.connect(self.toggle_key_visibility)
        self.show_key_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #007bff;
                border: none;
                padding: 5px;
                text-align: left;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        show_btn_layout.addWidget(self.show_key_btn)
        show_btn_layout.addStretch()
        api_layout.addLayout(show_btn_layout)
        
        # 状态指示
        self.status_label = QLabel()
        self.status_label.setStyleSheet("margin-top: 5px;")
        api_layout.addWidget(self.status_label)
        
        layout.addWidget(api_group)
        
        # 主题配置组
        theme_group = QGroupBox("界面主题")
        theme_layout = QVBoxLayout(theme_group)
        
        # 主题说明
        theme_info_label = QLabel("选择你喜欢的界面主题风格")
        theme_info_label.setStyleSheet("color: #666; font-size: 12px;")
        theme_layout.addWidget(theme_info_label)
        
        # 主题选择标签
        theme_label = QLabel("主题风格:")
        theme_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        theme_layout.addWidget(theme_label)
        
        # 主题下拉框
        self.theme_combo = QComboBox()
        themes = Themes.get_all_themes()
        for theme_id, (theme_name, _) in themes.items():
            self.theme_combo.addItem(theme_name, theme_id)
        theme_layout.addWidget(self.theme_combo)
        
        # 预览按钮
        preview_btn = QPushButton("👁️ 预览主题")
        preview_btn.clicked.connect(self.preview_theme)
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        theme_layout.addWidget(preview_btn)
        
        layout.addWidget(theme_group)
        
        # 添加分隔线
        layout.addSpacing(10)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 测试连接按钮
        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self.test_connection)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        button_layout.addWidget(test_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        # 保存按钮
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def load_settings(self):
        """加载当前设置"""
        # 加载 API 密钥
        api_key = settings.get_api_key()
        if api_key:
            self.api_key_input.setText(api_key)
            self.update_status(True)
        else:
            self.update_status(False)
        
        # 加载主题
        current_theme = settings.get_theme()
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme:
                self.theme_combo.setCurrentIndex(i)
                break
    
    def toggle_key_visibility(self, checked):
        """切换密钥可见性"""
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.show_key_btn.setText("隐藏密钥")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.show_key_btn.setText("显示密钥")
    
    def update_status(self, is_valid):
        """更新状态显示"""
        if is_valid:
            self.status_label.setText("✓ API 密钥已配置")
            self.status_label.setStyleSheet(
                "color: #28a745; font-weight: bold; margin-top: 5px;"
            )
        else:
            self.status_label.setText("⚠ 未配置 API 密钥")
            self.status_label.setStyleSheet(
                "color: #dc3545; font-weight: bold; margin-top: 5px;"
            )
    
    def test_connection(self):
        """测试 API 连接"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "提示", "请先输入 API 密钥")
            return
        
        # 简单验证格式
        if not api_key.startswith('sk-'):
            QMessageBox.warning(
                self, 
                "提示", 
                "API 密钥格式不正确\n应以 'sk-' 开头"
            )
            return
        
        # 这里可以添加实际的 API 测试调用
        # 目前只做格式验证
        QMessageBox.information(
            self,
            "提示",
            "API 密钥格式正确\n\n"
            "注意：完整的连接测试需要实际调用 API\n"
            "请点击保存后在生成视频时验证"
        )
    
    def save_settings(self):
        """保存设置"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            reply = QMessageBox.question(
                self,
                "确认",
                "API 密钥为空，确定要保存吗？\n这将导致无法使用生成功能。",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # 保存 API 密钥
        settings.set_api_key(api_key)
        
        # 保存主题
        theme_id = self.theme_combo.currentData()
        old_theme = settings.get_theme()
        if theme_id != old_theme:
            settings.set_theme(theme_id)
            # 发送主题变更信号
            self.theme_changed.emit(theme_id)
        
        # 发送 API 密钥信号
        self.api_key_changed.emit(api_key)
        
        QMessageBox.information(self, "成功", "设置已保存")
        self.accept()
    
    def preview_theme(self):
        """预览主题"""
        theme_id = self.theme_combo.currentData()
        theme_stylesheet = Themes.get_theme(theme_id)
        
        # 应用主题到对话框
        self.setStyleSheet(theme_stylesheet)
        
        QMessageBox.information(
            self,
            "预览",
            f"这是 '{self.theme_combo.currentText()}' 的预览效果\n\n"
            f"点击保存后将应用到整个应用\n"
            f"关闭对话框后将恢复原有主题"
        )
        
        # 恢复原有主题
        old_theme = settings.get_theme()
        old_stylesheet = Themes.get_theme(old_theme)
        self.setStyleSheet(old_stylesheet)
