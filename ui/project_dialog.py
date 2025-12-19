#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工程对话框
用于创建和打开工程
使用 QFluentWidgets 组件美化
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QFileDialog, QListWidgetItem, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import os

# QFluentWidgets 组件
from qfluentwidgets import (
    LineEdit, TextEdit, PrimaryPushButton, PushButton,
    CardWidget, SubtitleLabel, BodyLabel, CaptionLabel,
    ListWidget, TabWidget, FluentIcon, InfoBar, InfoBarPosition
)


class NewProjectDialog(QDialog):
    """新建工程对话框"""
    
    project_created = pyqtSignal(str, str, str)  # name, location, description
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("新建工程")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        # 统一对话框区块间距：16px
        layout.setSpacing(16)
        # 统一对话框内边距：24px
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title_label = SubtitleLabel("创建新工程")
        layout.addWidget(title_label)
        
        # 工程信息卡片
        info_card = CardWidget()
        info_layout = QVBoxLayout(info_card)
        # 统一卡片内组件间距：12px
        info_layout.setSpacing(12)
        # 统一卡片内边距：16px
        info_layout.setContentsMargins(16, 16, 16, 16)
        
        # 工程名称
        name_label = BodyLabel("工程名称")
        info_layout.addWidget(name_label)
        
        self.name_input = LineEdit()
        self.name_input.setPlaceholderText("例如: MyVideoProject")
        self.name_input.setClearButtonEnabled(True)
        info_layout.addWidget(self.name_input)
        
        # 工程位置
        location_label = BodyLabel("保存位置")
        info_layout.addWidget(location_label)
        
        location_layout = QHBoxLayout()
        location_layout.setSpacing(8)
        self.location_input = LineEdit()
        self.location_input.setPlaceholderText("选择工程保存位置")
        self.location_input.setText(os.path.expanduser("~/Documents"))
        self.location_input.setClearButtonEnabled(True)
        location_layout.addWidget(self.location_input)
        
        browse_btn = PushButton(FluentIcon.FOLDER, "浏览")
        browse_btn.clicked.connect(self.browse_location)
        location_layout.addWidget(browse_btn)
        info_layout.addLayout(location_layout)
        
        # 工程描述
        desc_label = BodyLabel("工程描述")
        info_layout.addWidget(desc_label)
        
        self.desc_input = TextEdit()
        self.desc_input.setPlaceholderText("简要描述工程用途（可选）")
        self.desc_input.setMaximumHeight(80)
        info_layout.addWidget(self.desc_input)
        
        layout.addWidget(info_card)
        
        # 提示信息
        hint_label = CaptionLabel(
            "💡 工程将包含以下文件夹：\n"
            "  • pictures/  - 图集（存放输入图片）\n"
            "  • videos/ - 视频集（存放生成的视频）\n"
            "  • tasks.json - 任务记录"
        )
        hint_label.setTextColor("#666666", "#999999")
        layout.addWidget(hint_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = PushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        create_btn = PrimaryPushButton(FluentIcon.ADD, "创建")
        create_btn.clicked.connect(self.create_project)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
    
    def browse_location(self):
        """浏览位置"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择工程保存位置",
            self.location_input.text()
        )
        if directory:
            self.location_input.setText(directory)
    
    def create_project(self):
        """创建工程"""
        name = self.name_input.text().strip()
        location = self.location_input.text().strip()
        description = self.desc_input.toPlainText().strip()
        
        # 验证
        if not name:
            InfoBar.warning(
                title="提示",
                content="请输入工程名称",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        if not location:
            InfoBar.warning(
                title="提示",
                content="请选择保存位置",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        # 检查名称合法性
        if any(c in name for c in r'\/:*?"<>|'):
            InfoBar.warning(
                title="提示",
                content="工程名称不能包含以下字符: \\ / : * ? \" < > |",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
            return
        
        # 发送信号
        self.project_created.emit(name, location, description)
        self.accept()


class OpenProjectDialog(QDialog):
    """打开工程对话框"""
    
    project_selected = pyqtSignal(str)  # project_path
    
    def __init__(self, recent_projects, parent=None):
        super().__init__(parent)
        self.recent_projects = recent_projects
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("打开工程")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        # 统一对话框区块间距：16px
        layout.setSpacing(16)
        # 统一对话框内边距：24px
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title_label = SubtitleLabel("打开工程")
        layout.addWidget(title_label)
        
        # 选项卡
        tabs = TabWidget()
        
        # 最近工程标签页
        recent_widget = QWidget()
        recent_layout = QVBoxLayout(recent_widget)
        recent_layout.setSpacing(12)
        recent_layout.setContentsMargins(16, 16, 16, 16)
        
        recent_label = BodyLabel("最近打开的工程:")
        recent_layout.addWidget(recent_label)
        
        self.recent_list = ListWidget()
        self.recent_list.itemDoubleClicked.connect(self.open_selected)
        recent_layout.addWidget(self.recent_list)
        
        # 填充最近工程
        self.populate_recent_projects()
        
        recent_widget.setObjectName("recentTab")
        tabs.addSubInterface(recent_widget, "recentTab", "最近工程", FluentIcon.HISTORY)
        
        # 浏览标签页
        browse_widget = QWidget()
        browse_widget.setObjectName("browseTab")
        browse_layout = QVBoxLayout(browse_widget)
        browse_layout.setSpacing(12)
        browse_layout.setContentsMargins(16, 16, 16, 16)
        
        browse_label = BodyLabel("浏览工程文件夹:")
        browse_layout.addWidget(browse_label)
        
        browse_btn = PrimaryPushButton(FluentIcon.FOLDER, "选择工程文件夹")
        browse_btn.clicked.connect(self.browse_project)
        browse_layout.addWidget(browse_btn)
        browse_layout.addStretch()
        
        tabs.addSubInterface(browse_widget, "browseTab", "浏览", FluentIcon.FOLDER)
        
        layout.addWidget(tabs)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = PushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        open_btn = PrimaryPushButton(FluentIcon.FOLDER_ADD, "打开")
        open_btn.clicked.connect(self.open_selected)
        button_layout.addWidget(open_btn)
        
        layout.addLayout(button_layout)
    
    def populate_recent_projects(self):
        """填充最近工程列表"""
        self.recent_list.clear()
        
        if not self.recent_projects:
            item = QListWidgetItem("暂无最近工程")
            item.setFlags(Qt.NoItemFlags)
            self.recent_list.addItem(item)
            return
        
        for project in self.recent_projects:
            name = project.get('name', 'Unknown')
            path = project.get('path', '')
            desc = project.get('description', '')
            last_opened = project.get('last_opened', '')
            
            item_text = f"{name}\n{path}"
            if desc:
                item_text += f"\n{desc}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, path)
            self.recent_list.addItem(item)
    
    def browse_project(self):
        """浏览工程"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择工程文件夹",
            os.path.expanduser("~/Documents")
        )
        if directory:
            self.project_selected.emit(directory)
            self.accept()
    
    def open_selected(self):
        """打开选中的工程"""
        current_item = self.recent_list.currentItem()
        if current_item:
            path = current_item.data(Qt.UserRole)
            if path:
                self.project_selected.emit(path)
                self.accept()
