#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置对话框
用于配置 API 密钥、主题等设置
使用 QFluentWidgets 组件实现 Fluent Design 风格
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QGridLayout, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QColor

from config.settings import settings

try:
    from qfluentwidgets import (
        PasswordLineEdit, ComboBox, PrimaryPushButton, PushButton,
        CardWidget, SubtitleLabel, BodyLabel, CaptionLabel,
        SwitchButton, FluentIcon, setTheme, Theme,
        ColorPickerButton, ToolButton
    )
    from themes.fluent_theme import fluent_theme_manager, AppTheme, FLUENT_AVAILABLE
    FLUENT_WIDGETS_AVAILABLE = True
except ImportError:
    FLUENT_WIDGETS_AVAILABLE = False
    from PyQt5.QtWidgets import (
        QLineEdit, QComboBox, QPushButton, QGroupBox, QLabel
    )
    print("警告: QFluentWidgets 未安装，将使用原生组件")

from utils.message_helper import MessageHelper


class SettingsDialog(QDialog):
    """设置对话框 - Fluent Design 风格"""
    
    # 定义信号
    api_key_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """初始化设置对话框"""
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()
        self.connect_signals()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("设置")
        self.setMinimumWidth(550)
        self.setMinimumHeight(600)
        self.setModal(True)
        
        # 设置窗口图标
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo.png')
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        if FLUENT_WIDGETS_AVAILABLE:
            self._setup_fluent_ui(layout)
        else:
            self._setup_fallback_ui(layout)
    
    def _setup_fluent_ui(self, layout: QVBoxLayout):
        """设置 Fluent 风格 UI"""
        # ========== API 配置卡片 ==========
        api_card = CardWidget(self)
        api_card_layout = QVBoxLayout(api_card)
        # 统一卡片内组件间距：12px
        api_card_layout.setSpacing(12)
        # 统一卡片内边距：16px
        api_card_layout.setContentsMargins(16, 16, 16, 16)
        
        # API 配置标题
        api_title = SubtitleLabel("API 配置", api_card)
        api_card_layout.addWidget(api_title)
        
        # API 密钥说明
        api_info = CaptionLabel(
            "请输入你的阿里云 DashScope API 密钥\n"
            "获取地址: https://dashscope.console.aliyun.com/",
            api_card
        )
        api_info.setWordWrap(True)
        api_card_layout.addWidget(api_info)
        
        # API 密钥标签
        key_label = BodyLabel("API 密钥 (SK):", api_card)
        api_card_layout.addWidget(key_label)
        
        # API 密钥输入框 - 使用 PasswordLineEdit
        self.api_key_input = PasswordLineEdit(api_card)
        self.api_key_input.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        api_card_layout.addWidget(self.api_key_input)
        
        # 状态指示
        self.status_label = CaptionLabel("", api_card)
        api_card_layout.addWidget(self.status_label)
        
        layout.addWidget(api_card)
        
        # ========== 主题配置卡片 ==========
        theme_card = CardWidget(self)
        theme_card_layout = QVBoxLayout(theme_card)
        # 统一卡片内组件间距：12px
        theme_card_layout.setSpacing(12)
        # 统一卡片内边距：16px
        theme_card_layout.setContentsMargins(16, 16, 16, 16)
        
        # 主题配置标题
        theme_title = SubtitleLabel("界面主题", theme_card)
        theme_card_layout.addWidget(theme_title)
        
        # 主题说明
        theme_info = CaptionLabel("选择你喜欢的界面主题风格", theme_card)
        theme_card_layout.addWidget(theme_info)
        
        # 主题选择行
        theme_row = QHBoxLayout()
        theme_row.setSpacing(12)
        
        theme_label = BodyLabel("主题风格:", theme_card)
        theme_row.addWidget(theme_label)
        
        # 主题下拉框 - 使用 Fluent ComboBox
        self.theme_combo = ComboBox(theme_card)
        self.theme_combo.addItem("浅色主题", userData="light")
        self.theme_combo.addItem("深色主题", userData="dark")
        self.theme_combo.addItem("跟随系统", userData="auto")
        self.theme_combo.setMinimumWidth(150)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        
        theme_card_layout.addLayout(theme_row)
        
        # 主题色选择行
        color_row = QHBoxLayout()
        color_row.setSpacing(12)
        
        color_label = BodyLabel("主题色:", theme_card)
        color_row.addWidget(color_label)
        
        # 主题色选择按钮
        self.color_picker = ColorPickerButton(
            QColor(fluent_theme_manager.current_accent_color),
            "选择主题色",
            theme_card
        )
        self.color_picker.setFixedSize(84, 32)
        color_row.addWidget(self.color_picker)
        
        # 预设颜色按钮
        self._add_preset_color_buttons(color_row, theme_card)
        
        color_row.addStretch()
        theme_card_layout.addLayout(color_row)
        
        # 实时预览开关
        preview_row = QHBoxLayout()
        preview_row.setSpacing(12)
        
        preview_label = BodyLabel("实时预览:", theme_card)
        preview_row.addWidget(preview_label)
        
        self.preview_switch = SwitchButton(theme_card)
        self.preview_switch.setChecked(True)
        preview_row.addWidget(self.preview_switch)
        
        preview_hint = CaptionLabel("开启后切换主题时立即预览效果", theme_card)
        preview_row.addWidget(preview_hint)
        preview_row.addStretch()
        
        theme_card_layout.addLayout(preview_row)
        
        layout.addWidget(theme_card)
        
        # 添加弹性空间
        layout.addStretch()
        
        # ========== 按钮区域 ==========
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # 测试连接按钮
        self.test_btn = PushButton(FluentIcon.WIFI, "测试连接", self)
        self.test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_btn)
        
        button_layout.addStretch()
        
        # 取消按钮
        self.cancel_btn = PushButton("取消", self)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        # 保存按钮
        self.save_btn = PrimaryPushButton(FluentIcon.SAVE, "保存", self)
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def _add_preset_color_buttons(self, layout: QHBoxLayout, parent: QWidget):
        """添加预设颜色按钮"""
        preset_colors = fluent_theme_manager.get_preset_colors()
        
        # 只显示部分常用颜色
        common_colors = ['blue', 'purple', 'pink', 'red', 'orange', 'green', 'teal']
        
        for color_name in common_colors:
            if color_name in preset_colors:
                color_value = preset_colors[color_name]
                btn = ToolButton(parent)
                btn.setFixedSize(24, 24)
                btn.setStyleSheet(f"""
                    ToolButton {{
                        background-color: {color_value};
                        border: 2px solid transparent;
                        border-radius: 12px;
                    }}
                    ToolButton:hover {{
                        border: 2px solid #666;
                    }}
                    ToolButton:pressed {{
                        border: 2px solid #333;
                    }}
                """)
                btn.setToolTip(color_name.capitalize())
                btn.clicked.connect(lambda checked, c=color_value: self._on_preset_color_clicked(c))
                layout.addWidget(btn)
    
    def _on_preset_color_clicked(self, color: str):
        """预设颜色按钮点击"""
        self.color_picker.setColor(QColor(color))
        if self.preview_switch.isChecked():
            fluent_theme_manager.set_accent_color(color)
    
    def _setup_fallback_ui(self, layout: QVBoxLayout):
        """设置降级 UI（当 QFluentWidgets 不可用时）"""
        from PyQt5.QtWidgets import QGroupBox, QLabel, QLineEdit, QComboBox, QPushButton
        
        # API 配置组
        api_group = QGroupBox("API 配置", self)
        api_layout = QVBoxLayout(api_group)
        
        info_label = QLabel(
            "请输入你的阿里云 DashScope API 密钥\n"
            "获取地址: https://dashscope.console.aliyun.com/"
        )
        info_label.setWordWrap(True)
        api_layout.addWidget(info_label)
        
        key_label = QLabel("API 密钥 (SK):")
        api_layout.addWidget(key_label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.api_key_input)
        
        self.status_label = QLabel()
        api_layout.addWidget(self.status_label)
        
        layout.addWidget(api_group)
        
        # 主题配置组
        theme_group = QGroupBox("界面主题", self)
        theme_layout = QVBoxLayout(theme_group)
        
        theme_label = QLabel("主题风格:")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("浅色主题", "light")
        self.theme_combo.addItem("深色主题", "dark")
        self.theme_combo.addItem("跟随系统", "auto")
        theme_layout.addWidget(self.theme_combo)
        
        layout.addWidget(theme_group)
        
        layout.addStretch()
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def connect_signals(self):
        """连接信号"""
        if FLUENT_WIDGETS_AVAILABLE:
            # 主题下拉框变化时实时预览
            self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
            # 颜色选择器变化时实时预览
            self.color_picker.colorChanged.connect(self._on_color_changed)
    
    def _on_theme_changed(self, index: int):
        """主题选择变化"""
        if not FLUENT_WIDGETS_AVAILABLE:
            return
        
        if self.preview_switch.isChecked():
            theme_value = self.theme_combo.currentData()
            if theme_value:
                fluent_theme_manager.set_theme_by_name(theme_value)
                # 强制刷新对话框
                self.update()
                self.repaint()
    
    def _on_color_changed(self, color: QColor):
        """主题色变化"""
        if not FLUENT_WIDGETS_AVAILABLE:
            return
        
        if self.preview_switch.isChecked():
            fluent_theme_manager.set_accent_color(color.name())
            # 强制刷新对话框
            self.update()
            self.repaint()
    
    def load_settings(self):
        """加载当前设置"""
        # 加载 API 密钥
        api_key = settings.get_api_key()
        if api_key:
            if FLUENT_WIDGETS_AVAILABLE:
                self.api_key_input.setText(api_key)
            else:
                self.api_key_input.setText(api_key)
            self.update_status(True)
        else:
            self.update_status(False)
        
        # 加载 Fluent 主题
        if FLUENT_WIDGETS_AVAILABLE:
            current_theme = fluent_theme_manager.current_theme.value
            for i in range(self.theme_combo.count()):
                if self.theme_combo.itemData(i) == current_theme:
                    self.theme_combo.setCurrentIndex(i)
                    break
            
            # 加载主题色
            current_color = fluent_theme_manager.current_accent_color
            self.color_picker.setColor(QColor(current_color))
        else:
            # 降级模式下加载旧主题
            current_theme = settings.get_theme()
            for i in range(self.theme_combo.count()):
                if self.theme_combo.itemData(i) == current_theme:
                    self.theme_combo.setCurrentIndex(i)
                    break
        
        # 保存原始设置用于取消时恢复
        self._original_theme = fluent_theme_manager.current_theme if FLUENT_WIDGETS_AVAILABLE else None
        self._original_color = fluent_theme_manager.current_accent_color if FLUENT_WIDGETS_AVAILABLE else None
    
    def update_status(self, is_valid: bool):
        """更新状态显示"""
        if FLUENT_WIDGETS_AVAILABLE:
            if is_valid:
                self.status_label.setText("✓ API 密钥已配置")
                self.status_label.setStyleSheet("color: #28a745;")
            else:
                self.status_label.setText("⚠ 未配置 API 密钥")
                self.status_label.setStyleSheet("color: #dc3545;")
        else:
            if is_valid:
                self.status_label.setText("✓ API 密钥已配置")
                self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            else:
                self.status_label.setText("⚠ 未配置 API 密钥")
                self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
    
    def test_connection(self):
        """测试 API 连接"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            MessageHelper.warning(self, "提示", "请先输入 API 密钥")
            return
        
        # 简单验证格式
        if not api_key.startswith('sk-'):
            MessageHelper.warning(
                self, 
                "提示", 
                "API 密钥格式不正确，应以 'sk-' 开头"
            )
            return
        
        # 格式验证通过
        MessageHelper.success(
            self,
            "验证通过",
            "API 密钥格式正确，请点击保存后在生成视频时验证"
        )
    
    def save_settings(self):
        """保存设置"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            if not MessageHelper.confirm(
                self,
                "确认",
                "API 密钥为空，确定要保存吗？\n这将导致无法使用生成功能。"
            ):
                return
        
        # 保存 API 密钥
        settings.set_api_key(api_key)
        
        # 保存主题设置
        if FLUENT_WIDGETS_AVAILABLE:
            theme_value = self.theme_combo.currentData()
            if theme_value:
                fluent_theme_manager.set_theme_by_name(theme_value)
                settings.set_fluent_theme(theme_value)
                # 发送主题变更信号（只在有有效值时发送）
                self.theme_changed.emit(theme_value)
            
            # 保存主题色
            color = self.color_picker.color.name()
            fluent_theme_manager.set_accent_color(color)
            settings.set_accent_color(color)
        else:
            theme_value = self.theme_combo.currentData()
            old_theme = settings.get_theme()
            if theme_value and theme_value != old_theme:
                settings.set_theme(theme_value)
                self.theme_changed.emit(theme_value)
        
        # 发送 API 密钥信号
        self.api_key_changed.emit(api_key)
        
        MessageHelper.success(self, "成功", "设置已保存")
        self.accept()
    
    def reject(self):
        """取消并恢复原始设置"""
        # 恢复原始主题设置
        if FLUENT_WIDGETS_AVAILABLE and self._original_theme:
            fluent_theme_manager.set_theme(self._original_theme)
        if FLUENT_WIDGETS_AVAILABLE and self._original_color:
            fluent_theme_manager.set_accent_color(self._original_color)
        
        super().reject()
