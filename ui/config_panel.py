#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置面板
用于设置视频生成参数
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QPushButton, QGroupBox, QScrollArea
)
from PyQt5.QtCore import pyqtSignal, Qt


class ConfigPanel(QWidget):
    """配置面板组件"""
    
    # 定义信号
    generate_clicked = pyqtSignal(dict)  # 配置字典
    
    # 模型配置映射（分辨率、时长、描述）
    MODEL_CONFIG = {
        'wan2.6-i2v': {
            'name': '🌟 万相2.6（最新）',
            'resolutions': ['720P', '1080P'],
            'durations': ['5秒', '10秒', '15秒'],
            'fps': 30,
            'audio': False,
            'shot_type': True,  # 支持镜头类型选择
            'description': '最新模型，支持5/10/15秒时长，支持智能多镜头'
        },
        'wan2.5-i2v-preview': {
            'name': '万相2.5 Preview（有声视频）',
            'resolutions': ['480P', '720P', '1080P'],
            'durations': ['5秒', '10秒'],
            'fps': 24,
            'audio': True,
            'shot_type': False,
            'description': '支持自动配音或自定义音频'
        },
        'wan2.2-i2v-flash': {
            'name': '万相2.2 极速版（无声视频）',
            'resolutions': ['480P', '720P', '1080P'],
            'durations': ['5秒'],
            'fps': 30,
            'audio': False,
            'shot_type': False,
            'description': '较2.1模型速度提升50%'
        },
        'wan2.2-i2v-plus': {
            'name': '万相2.2 专业版（无声视频）',
            'resolutions': ['480P', '720P', '1080P'],
            'durations': ['5秒'],
            'fps': 30,
            'audio': False,
            'shot_type': False,
            'description': '较2.1模型稳定性与成功率全面提升'
        },
        'wanx2.1-i2v-plus': {
            'name': '万相2.1 专业版（无声视频）',
            'resolutions': ['720P'],
            'durations': ['5秒'],
            'fps': 30,
            'audio': False,
            'shot_type': False,
            'description': '稳定版本'
        },
        'wanx2.1-i2v-turbo': {
            'name': '万相2.1 极速版（无声视频）',
            'resolutions': ['480P', '720P'],
            'durations': ['3秒', '4秒', '5秒'],
            'fps': 30,
            'audio': False,
            'shot_type': False,
            'description': '快速生成'
        }
    }
    
    def __init__(self, parent=None):
        """初始化配置面板"""
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # 滚动内容容器
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(5, 5, 10, 5)
        
        # 创建组框
        group_box = QGroupBox("生成配置")
        group_layout = QVBoxLayout(group_box)
        
        # 提示词
        prompt_label = QLabel("提示词:")
        prompt_label.setStyleSheet("font-weight: bold;")
        group_layout.addWidget(prompt_label)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("描述你想要生成的视频内容...")
        self.prompt_edit.setMinimumHeight(80)
        self.prompt_edit.setText("让画面动起来，添加自然的动态效果")
        group_layout.addWidget(self.prompt_edit)
        
        # 反向提示词
        neg_prompt_label = QLabel("反向提示词:")
        neg_prompt_label.setStyleSheet("font-weight: bold;")
        group_layout.addWidget(neg_prompt_label)
        
        self.neg_prompt_edit = QTextEdit()
        self.neg_prompt_edit.setPlaceholderText("描述不希望出现的内容...")
        self.neg_prompt_edit.setMinimumHeight(60)
        group_layout.addWidget(self.neg_prompt_edit)
        
        # 模型选择
        model_label = QLabel("模型:")
        model_label.setStyleSheet("font-weight: bold;")
        group_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumHeight(30)
        # 按照版本顺序添加模型
        for model_key, model_info in self.MODEL_CONFIG.items():
            self.model_combo.addItem(model_info['name'], model_key)
        group_layout.addWidget(self.model_combo)
        
        # 模型说明
        self.model_desc_label = QLabel()
        self.model_desc_label.setStyleSheet("color: #666; font-size: 12px; padding: 4px;")
        self.model_desc_label.setWordWrap(True)
        group_layout.addWidget(self.model_desc_label)
        
        # 分辨率选择
        resolution_label = QLabel("分辨率:")
        resolution_label.setStyleSheet("font-weight: bold;")
        group_layout.addWidget(resolution_label)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.setMinimumHeight(30)
        group_layout.addWidget(self.resolution_combo)
        
        # 视频时长选择
        duration_label = QLabel("视频时长:")
        duration_label.setStyleSheet("font-weight: bold;")
        group_layout.addWidget(duration_label)
        
        self.duration_combo = QComboBox()
        self.duration_combo.setMinimumHeight(30)
        group_layout.addWidget(self.duration_combo)
        
        # 智能改写选项
        self.prompt_extend_check = QCheckBox("启用提示词智能改写")
        self.prompt_extend_check.setChecked(True)
        self.prompt_extend_check.setMinimumHeight(30)
        group_layout.addWidget(self.prompt_extend_check)
        
        # 镜头类型选择（仅2.6模型显示）
        self.shot_type_label = QLabel("镜头类型:")
        self.shot_type_label.setStyleSheet("font-weight: bold;")
        group_layout.addWidget(self.shot_type_label)
        
        self.shot_type_combo = QComboBox()
        self.shot_type_combo.setMinimumHeight(30)
        self.shot_type_combo.addItem("智能多镜头（推荐）", "multi")
        self.shot_type_combo.addItem("单镜头生成", "single")
        group_layout.addWidget(self.shot_type_combo)
        
        # 默认隐藏镜头类型选择
        self.shot_type_label.hide()
        self.shot_type_combo.hide()
        
        # 生成按钮
        self.generate_btn = QPushButton("生成视频")
        self.generate_btn.setMinimumHeight(45)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.generate_btn.setEnabled(False)
        group_layout.addWidget(self.generate_btn)
        
        scroll_layout.addWidget(group_box)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
    
    def connect_signals(self):
        """连接信号槽"""
        self.generate_btn.clicked.connect(self.on_generate_clicked)
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        
        # 初始化默认模型配置
        self.on_model_changed(0)
    
    def on_model_changed(self, index):
        """模型改变事件"""
        model_key = self.model_combo.itemData(index)
        if not model_key:
            return
        
        model_config = self.MODEL_CONFIG.get(model_key, {})
        
        # 更新模型说明
        description = model_config.get('description', '')
        fps = model_config.get('fps', 30)
        audio = '支持音频' if model_config.get('audio', False) else '无声视频'
        self.model_desc_label.setText(f"{description} | {fps}fps | {audio}")
        
        # 更新可用分辨率
        current_resolution = self.resolution_combo.currentText()
        available_resolutions = model_config.get('resolutions', ['720P'])
        
        self.resolution_combo.clear()
        self.resolution_combo.addItems(available_resolutions)
        
        # 尝试保持之前的选择
        if current_resolution in available_resolutions:
            self.resolution_combo.setCurrentText(current_resolution)
        
        # 更新可用时长
        current_duration = self.duration_combo.currentText()
        available_durations = model_config.get('durations', ['5秒'])
        
        self.duration_combo.clear()
        self.duration_combo.addItems(available_durations)
        
        # 尝试保持之前的选择
        if current_duration in available_durations:
            self.duration_combo.setCurrentText(current_duration)
        
        # 显示/隐藏镜头类型选择（仅2.6模型支持）
        if model_config.get('shot_type', False):
            self.shot_type_label.show()
            self.shot_type_combo.show()
        else:
            self.shot_type_label.hide()
            self.shot_type_combo.hide()
    
    def on_generate_clicked(self):
        """生成按钮点击事件"""
        # 获取当前模型 key
        model_key = self.model_combo.currentData()
        model_config = self.MODEL_CONFIG.get(model_key, {})
        
        # 收集配置
        config = {
            'prompt': self.prompt_edit.toPlainText().strip(),
            'negative_prompt': self.neg_prompt_edit.toPlainText().strip(),
            'model': model_key,
            'resolution': self.resolution_combo.currentText(),
            'duration': self.duration_combo.currentText(),
            'prompt_extend': self.prompt_extend_check.isChecked()
        }
        
        # 如果是2.6模型，添加镜头类型参数
        if model_config.get('shot_type', False):
            config['shot_type'] = self.shot_type_combo.currentData()
        
        # 验证提示词
        if not config['prompt']:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提示", "请输入提示词")
            return
        
        # 发送信号
        self.generate_clicked.emit(config)
