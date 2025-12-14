#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工程对话框
用于创建和打开工程
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QFileDialog,
    QGroupBox, QMessageBox, QListWidget, QListWidgetItem,
    QTabWidget, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import os


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
        
        # 工程名称
        name_group = QGroupBox("工程信息")
        name_layout = QVBoxLayout(name_group)
        
        name_label = QLabel("工程名称:")
        name_label.setStyleSheet("font-weight: bold;")
        name_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: MyVideoProject")
        name_layout.addWidget(self.name_input)
        
        # 工程位置
        location_label = QLabel("保存位置:")
        location_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        name_layout.addWidget(location_label)
        
        location_layout = QHBoxLayout()
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("选择工程保存位置")
        self.location_input.setText(os.path.expanduser("~/Documents"))
        location_layout.addWidget(self.location_input)
        
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_location)
        location_layout.addWidget(browse_btn)
        name_layout.addLayout(location_layout)
        
        # 工程描述
        desc_label = QLabel("工程描述:")
        desc_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        name_layout.addWidget(desc_label)
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("简要描述工程用途（可选）")
        self.desc_input.setMaximumHeight(80)
        name_layout.addWidget(self.desc_input)
        
        layout.addWidget(name_group)
        
        # 提示信息
        info_label = QLabel(
            "💡 工程将包含以下文件夹：\n"
            "  • pictures/  - 图集（存放输入图片）\n"
            "  • videos/ - 视频集（存放生成的视频）\n"
            "  • tasks.json - 任务记录"
        )
        info_label.setStyleSheet("color: #666; font-size: 12px; padding: 10px;")
        layout.addWidget(info_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("创建")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
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
            QMessageBox.warning(self, "提示", "请输入工程名称")
            return
        
        if not location:
            QMessageBox.warning(self, "提示", "请选择保存位置")
            return
        
        # 检查名称合法性
        if any(c in name for c in r'\/:*?"<>|'):
            QMessageBox.warning(
                self, 
                "提示", 
                "工程名称不能包含以下字符: \\ / : * ? \" < > |"
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
        
        # 选项卡
        tabs = QTabWidget()
        
        # 最近工程标签页
        recent_widget = QWidget()
        recent_layout = QVBoxLayout(recent_widget)
        
        recent_label = QLabel("最近打开的工程:")
        recent_label.setStyleSheet("font-weight: bold;")
        recent_layout.addWidget(recent_label)
        
        self.recent_list = QListWidget()
        self.recent_list.itemDoubleClicked.connect(self.open_selected)
        recent_layout.addWidget(self.recent_list)
        
        # 填充最近工程
        self.populate_recent_projects()
        
        tabs.addTab(recent_widget, "最近工程")
        
        # 浏览标签页
        browse_widget = QWidget()
        browse_layout = QVBoxLayout(browse_widget)
        
        browse_label = QLabel("浏览工程文件夹:")
        browse_label.setStyleSheet("font-weight: bold;")
        browse_layout.addWidget(browse_label)
        
        browse_btn = QPushButton("选择工程文件夹")
        browse_btn.clicked.connect(self.browse_project)
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        browse_layout.addWidget(browse_btn)
        browse_layout.addStretch()
        
        tabs.addTab(browse_widget, "浏览")
        
        layout.addWidget(tabs)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        open_btn = QPushButton("打开")
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
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
