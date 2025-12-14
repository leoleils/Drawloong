#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责加载和管理应用配置
"""

import os
import json
from PyQt5.QtCore import QSettings
from dotenv import load_dotenv


class Settings:
    """应用配置类"""
    
    def __init__(self):
        """初始化配置"""
        # 使用 QSettings 存储用户配置
        self.qsettings = QSettings('WanX', 'ImageToVideo')
        
        # 加载环境变量（作为备用）
        load_dotenv()
        
        # 基础数据目录: 放在用户目录下,避免打包后无权限
        home_dir = os.path.expanduser("~")
        app_data_dir = os.path.join(home_dir, ".drawloong")
        os.makedirs(app_data_dir, exist_ok=True)
        
        # API 配置 - 优先从 QSettings 读取，其次从环境变量
        self.DASHSCOPE_API_KEY = self.qsettings.value(
            'api_key', 
            os.environ.get('DASHSCOPE_API_KEY', '')
        )
        self.DASHSCOPE_BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
        
        # 文件路径配置(默认放在用户数据目录下,也可通过环境变量覆盖)
        self.UPLOAD_FOLDER = os.environ.get(
            'UPLOAD_FOLDER',
            os.path.join(app_data_dir, 'uploads')
        )
        self.OUTPUT_FOLDER = os.environ.get(
            'OUTPUT_FOLDER',
            os.path.join(app_data_dir, 'downloads')
        )
        self.TASKS_FILE = os.environ.get(
            'TASKS_FILE',
            os.path.join(app_data_dir, 'tasks.json')
        )
        
        # 文件限制
        self.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        self.MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 10 * 1024 * 1024))
        
        # 确保目录存在
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)
    
    def set_api_key(self, api_key: str):
        """设置 API 密钥"""
        self.DASHSCOPE_API_KEY = api_key
        self.qsettings.setValue('api_key', api_key)
        self.qsettings.sync()
    
    def get_api_key(self) -> str:
        """获取 API 密钥"""
        return self.DASHSCOPE_API_KEY
    
    def is_api_key_valid(self):
        """检查 API 密钥是否有效"""
        return bool(self.DASHSCOPE_API_KEY and 
                   self.DASHSCOPE_API_KEY.strip() and
                   self.DASHSCOPE_API_KEY != 'your_api_key')
    
    def allowed_file(self, filename):
        """检查文件扩展名是否允许"""
        return ('.' in filename and 
                filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS)
    
    def set_theme(self, theme_name: str):
        """设置主题"""
        self.qsettings.setValue('theme', theme_name)
        self.qsettings.sync()
    
    def get_theme(self) -> str:
        """获取当前主题"""
        return self.qsettings.value('theme', 'light')


# 全局配置实例
settings = Settings()
