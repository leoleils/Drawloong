#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责加载和管理应用配置
"""

import os
import json
from PyQt5.QtCore import QSettings


class Settings:
    """应用配置类"""
    
    def __init__(self):
        """初始化配置"""
        # 使用 QSettings 存储用户配置
        self.qsettings = QSettings('WanX', 'ImageToVideo')
        
        # 基础数据目录: 放在用户目录下,避免打包后无权限
        home_dir = os.path.expanduser("~")
        app_data_dir = os.path.join(home_dir, ".drawloong")
        os.makedirs(app_data_dir, exist_ok=True)
        
        # API 配置 - 只从 QSettings 读取
        self.DASHSCOPE_API_KEY = self.qsettings.value('api_key', '')
        
        # 如果QSettings中没有API密钥，尝试从.env文件迁移
        if not self.DASHSCOPE_API_KEY:
            self._migrate_from_env_file()
        
        self.DASHSCOPE_BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
        
        # 文件路径配置(默认放在用户数据目录下)
        self.UPLOAD_FOLDER = os.path.join(app_data_dir, 'uploads')
        self.OUTPUT_FOLDER = os.path.join(app_data_dir, 'downloads')
        self.TASKS_FILE = os.path.join(app_data_dir, 'tasks.json')
        
        # 文件限制
        self.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        self.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        
        # 确保目录存在
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)
    
    def _migrate_from_env_file(self):
        """从.env文件迁移API密钥到QSettings"""
        try:
            # 尝试读取.env文件
            env_file = '.env'
            if os.path.exists(env_file):
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('DASHSCOPE_API_KEY='):
                            api_key = line.split('=', 1)[1].strip()
                            # 移除引号（如果有）
                            if api_key.startswith('"') and api_key.endswith('"'):
                                api_key = api_key[1:-1]
                            elif api_key.startswith("'") and api_key.endswith("'"):
                                api_key = api_key[1:-1]
                            
                            # 验证API密钥格式
                            if api_key and api_key != 'your_api_key_here' and api_key != 'your_api_key':
                                self.set_api_key(api_key)
                                print(f"已从.env文件迁移API密钥到系统配置")
                                break
        except Exception as e:
            print(f"迁移.env文件时出错: {e}")
    
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
    
    # ========== Fluent 主题配置方法 ==========
    
    def get_fluent_theme(self) -> str:
        """
        获取 Fluent 主题设置
        
        Returns:
            主题名称 ('light', 'dark', 'auto')
        """
        theme = self.qsettings.value('fluent_theme', 'light')
        # 确保返回有效的主题名称
        if not theme or not isinstance(theme, str):
            return 'light'
        
        valid_themes = ['light', 'dark', 'auto']
        theme_lower = theme.lower().strip()
        if theme_lower not in valid_themes:
            return 'light'
        
        return theme_lower
    
    def set_fluent_theme(self, theme_name: str):
        """
        设置 Fluent 主题
        
        Args:
            theme_name: 主题名称 ('light', 'dark', 'auto')
        """
        # 处理 None 或空字符串
        if not theme_name or not isinstance(theme_name, str):
            theme_name = 'light'
        
        valid_themes = ['light', 'dark', 'auto']
        theme_name_lower = theme_name.lower().strip()
        if theme_name_lower not in valid_themes:
            theme_name_lower = 'light'
        
        self.qsettings.setValue('fluent_theme', theme_name_lower)
        self.qsettings.sync()
    
    def get_accent_color(self) -> str:
        """
        获取主题强调色
        
        Returns:
            颜色值 (十六进制格式，如 '#007bff')
        """
        return self.qsettings.value('accent_color', '#007bff')
    
    def set_accent_color(self, color: str):
        """
        设置主题强调色
        
        Args:
            color: 颜色值 (十六进制格式，如 '#007bff')
        """
        # 简单验证颜色格式
        if color and color.startswith('#') and len(color) in [4, 7, 9]:
            self.qsettings.setValue('accent_color', color)
            self.qsettings.sync()


# 全局配置实例
settings = Settings()
