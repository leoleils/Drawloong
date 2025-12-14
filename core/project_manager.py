#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工程管理器
负责工程的创建、打开、保存和管理
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict
from PyQt5.QtCore import QSettings, pyqtSignal, QObject


class Project:
    """工程类"""
    
    def __init__(self, name: str, path: str):
        """初始化工程"""
        self.name = name
        self.path = path
        self.config_file = os.path.join(path, 'project.json')
        self.inputs_folder = os.path.join(path, 'pictures')  # 图集文件夹
        self.outputs_folder = os.path.join(path, 'videos')  # 视频集文件夹
        self.tasks_file = os.path.join(path, 'tasks.json')
        
        # 工程配置
        self.config = {
            'name': name,
            'created_at': datetime.now().isoformat(),
            'last_opened': datetime.now().isoformat(),
            'description': '',
            'version': '1.0'
        }
    
    def create(self, description: str = ''):
        """创建工程文件夹结构"""
        # 创建主目录
        os.makedirs(self.path, exist_ok=True)
        
        # 创建子目录
        os.makedirs(self.inputs_folder, exist_ok=True)
        os.makedirs(self.outputs_folder, exist_ok=True)
        
        # 更新配置
        self.config['description'] = description
        
        # 保存配置
        self.save_config()
        
        # 创建空任务文件
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
    
    def load(self):
        """加载工程配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # 更新最后打开时间
            self.config['last_opened'] = datetime.now().isoformat()
            self.save_config()
            return True
        return False
    
    def save_config(self):
        """保存工程配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def is_valid(self) -> bool:
        """检查工程是否有效"""
        return (os.path.exists(self.path) and 
                os.path.exists(self.config_file))
    
    def get_info(self) -> Dict:
        """获取工程信息"""
        return {
            'name': self.name,
            'path': self.path,
            'description': self.config.get('description', ''),
            'created_at': self.config.get('created_at', ''),
            'last_opened': self.config.get('last_opened', '')
        }


class ProjectManager(QObject):
    """工程管理器"""
    
    # 工程变化信号
    project_changed = pyqtSignal()
    
    def __init__(self):
        """初始化工程管理器"""
        super().__init__()
        self.current_project: Optional[Project] = None
        self.settings = QSettings('WanX', 'ImageToVideo')
        self.recent_projects = self.load_recent_projects()
    
    def create_project(self, name: str, location: str, description: str = '') -> Project:
        """创建新工程"""
        project_path = os.path.join(location, name)
        
        if os.path.exists(project_path):
            raise Exception(f"工程文件夹已存在: {project_path}")
        
        project = Project(name, project_path)
        project.create(description)
        
        # 设置为当前工程
        self.current_project = project
        
        # 添加到最近工程
        self.add_to_recent(project_path)
        
        # 发出工程变化信号
        self.project_changed.emit()
        
        return project
    
    def open_project(self, project_path: str) -> Project:
        """打开已有工程"""
        if not os.path.exists(project_path):
            raise Exception(f"工程不存在: {project_path}")
        
        # 从路径获取工程名
        project_name = os.path.basename(project_path)
        project = Project(project_name, project_path)
        
        if not project.load():
            raise Exception(f"无效的工程: {project_path}")
        
        # 设置为当前工程
        self.current_project = project
        
        # 添加到最近工程
        self.add_to_recent(project_path)
        
        # 发出工程变化信号
        self.project_changed.emit()
        
        return project
    
    def close_project(self):
        """关闭当前工程"""
        self.current_project = None
        
        # 发出工程变化信号
        self.project_changed.emit()
    
    def get_current_project(self) -> Optional[Project]:
        """获取当前工程"""
        return self.current_project
    
    def has_project(self) -> bool:
        """是否有打开的工程"""
        return self.current_project is not None
    
    def add_to_recent(self, project_path: str):
        """添加到最近工程列表"""
        # 移除重复项
        if project_path in self.recent_projects:
            self.recent_projects.remove(project_path)
        
        # 添加到开头
        self.recent_projects.insert(0, project_path)
        
        # 限制数量
        self.recent_projects = self.recent_projects[:10]
        
        # 保存
        self.save_recent_projects()
    
    def load_recent_projects(self) -> List[str]:
        """加载最近工程列表"""
        recent = self.settings.value('recent_projects', [])
        if not isinstance(recent, list):
            recent = []
        
        # 过滤不存在的工程
        return [p for p in recent if os.path.exists(p)]
    
    def save_recent_projects(self):
        """保存最近工程列表"""
        self.settings.setValue('recent_projects', self.recent_projects)
        self.settings.sync()
    
    def get_recent_projects(self) -> List[Dict]:
        """获取最近工程信息"""
        projects = []
        for path in self.recent_projects:
            try:
                name = os.path.basename(path)
                project = Project(name, path)
                if project.load():
                    projects.append(project.get_info())
            except:
                continue
        return projects