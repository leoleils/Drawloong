#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent 主题管理模块
基于 QFluentWidgets 的主题系统封装
"""

from enum import Enum
from typing import Optional

from PyQt5.QtGui import QColor
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget

try:
    from qfluentwidgets import (
        setTheme, setThemeColor, Theme,
        isDarkTheme, theme
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    print("警告: QFluentWidgets 未安装，将使用原生主题系统")


class AppTheme(Enum):
    """应用主题枚举"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class FluentThemeManager:
    """Fluent 主题管理器"""
    
    # 默认主题色
    DEFAULT_ACCENT_COLOR = "#007bff"
    
    # 预设主题色
    PRESET_COLORS = {
        'blue': '#007bff',
        'purple': '#6f42c1',
        'pink': '#e83e8c',
        'red': '#dc3545',
        'orange': '#fd7e14',
        'yellow': '#ffc107',
        'green': '#28a745',
        'teal': '#20c997',
        'cyan': '#17a2b8',
    }
    
    def __init__(self):
        """初始化主题管理器"""
        self.qsettings = QSettings('WanX', 'ImageToVideo')
        self._current_theme = self._load_theme()
        self._current_accent_color = self._load_accent_color()
    
    def _load_theme(self) -> AppTheme:
        """从配置加载主题"""
        theme_str = self.qsettings.value('fluent_theme', 'light')
        # 处理 None 或空字符串的情况
        if not theme_str or not isinstance(theme_str, str):
            return AppTheme.LIGHT
        try:
            return AppTheme(theme_str)
        except (ValueError, TypeError):
            return AppTheme.LIGHT
    
    def _load_accent_color(self) -> str:
        """从配置加载主题色"""
        return self.qsettings.value('accent_color', self.DEFAULT_ACCENT_COLOR)
    
    def _save_theme(self, theme: AppTheme):
        """保存主题到配置"""
        self.qsettings.setValue('fluent_theme', theme.value)
        self.qsettings.sync()
    
    def _save_accent_color(self, color: str):
        """保存主题色到配置"""
        self.qsettings.setValue('accent_color', color)
        self.qsettings.sync()
    
    @property
    def current_theme(self) -> AppTheme:
        """获取当前主题"""
        return self._current_theme
    
    @property
    def current_accent_color(self) -> str:
        """获取当前主题色"""
        return self._current_accent_color
    
    def set_theme(self, app_theme: AppTheme) -> bool:
        """
        设置应用主题
        
        Args:
            app_theme: 主题枚举值
            
        Returns:
            是否设置成功
        """
        if not FLUENT_AVAILABLE:
            return False
        
        try:
            # 映射到 QFluentWidgets 主题
            theme_map = {
                AppTheme.LIGHT: Theme.LIGHT,
                AppTheme.DARK: Theme.DARK,
                AppTheme.AUTO: Theme.AUTO,
            }
            
            fluent_theme = theme_map.get(app_theme, Theme.LIGHT)
            # 使用 lazy=False 确保立即更新样式表
            # save=False 因为我们自己用 QSettings 保存配置
            setTheme(fluent_theme, save=False, lazy=False)
            
            # 保存配置
            self._current_theme = app_theme
            self._save_theme(app_theme)
            
            # 强制刷新所有窗口和子组件
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                # 处理所有事件，确保样式表更新
                app.processEvents()
                
                # 刷新所有顶层窗口
                for widget in app.topLevelWidgets():
                    # 递归刷新所有子组件
                    self._refresh_widget_recursive(widget)
            
            return True
        except Exception as e:
            print(f"设置主题失败: {e}")
            return False
    
    def _refresh_widget_recursive(self, widget):
        """递归刷新组件及其所有子组件"""
        if widget is None:
            return
        
        # 刷新当前组件
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()
        
        # 递归刷新所有子组件
        for child in widget.findChildren(QWidget):
            child.style().unpolish(child)
            child.style().polish(child)
            child.update()
    
    def set_theme_by_name(self, theme_name: str) -> bool:
        """
        通过名称设置主题
        
        Args:
            theme_name: 主题名称 ('light', 'dark', 'auto')
            
        Returns:
            是否设置成功
        """
        # 处理 None 或空字符串 - 静默返回，不打印警告
        if not theme_name or not isinstance(theme_name, str):
            return False
        
        # 清理输入
        theme_name_clean = theme_name.lower().strip()
        if not theme_name_clean:
            return False
        
        try:
            app_theme = AppTheme(theme_name_clean)
            return self.set_theme(app_theme)
        except (ValueError, TypeError, AttributeError):
            print(f"未知主题: {theme_name}")
            return False
    
    def set_accent_color(self, color: str) -> bool:
        """
        设置主题强调色
        
        Args:
            color: 颜色值 (十六进制格式，如 '#007bff')
            
        Returns:
            是否设置成功
        """
        if not FLUENT_AVAILABLE:
            return False
        
        try:
            qcolor = QColor(color)
            if not qcolor.isValid():
                print(f"无效的颜色值: {color}")
                return False
            
            setThemeColor(qcolor)
            
            # 保存配置
            self._current_accent_color = color
            self._save_accent_color(color)
            
            # 强制刷新所有窗口
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                for widget in app.topLevelWidgets():
                    widget.update()
                    widget.repaint()
            
            return True
        except Exception as e:
            print(f"设置主题色失败: {e}")
            return False
    
    def set_preset_color(self, color_name: str) -> bool:
        """
        设置预设主题色
        
        Args:
            color_name: 预设颜色名称
            
        Returns:
            是否设置成功
        """
        color = self.PRESET_COLORS.get(color_name.lower())
        if color:
            return self.set_accent_color(color)
        else:
            print(f"未知的预设颜色: {color_name}")
            return False
    
    def apply_saved_theme(self) -> bool:
        """
        应用已保存的主题配置
        
        Returns:
            是否应用成功
        """
        if not FLUENT_AVAILABLE:
            return False
        
        success = True
        
        # 确保主题值有效
        if not isinstance(self._current_theme, AppTheme):
            print(f"警告: 无效的主题类型 {type(self._current_theme)}，重置为默认主题")
            self._current_theme = AppTheme.LIGHT
        
        # 应用主题
        if not self.set_theme(self._current_theme):
            success = False
        
        # 应用主题色
        if not self.set_accent_color(self._current_accent_color):
            success = False
        
        return success
    
    def is_dark_theme(self) -> bool:
        """
        检查当前是否为深色主题
        
        Returns:
            是否为深色主题
        """
        if FLUENT_AVAILABLE:
            return isDarkTheme()
        return self._current_theme == AppTheme.DARK
    
    def toggle_theme(self) -> AppTheme:
        """
        切换浅色/深色主题
        
        Returns:
            切换后的主题
        """
        if self.is_dark_theme():
            self.set_theme(AppTheme.LIGHT)
            return AppTheme.LIGHT
        else:
            self.set_theme(AppTheme.DARK)
            return AppTheme.DARK
    
    @staticmethod
    def is_fluent_available() -> bool:
        """检查 QFluentWidgets 是否可用"""
        return FLUENT_AVAILABLE
    
    @classmethod
    def get_preset_colors(cls) -> dict:
        """获取所有预设颜色"""
        return cls.PRESET_COLORS.copy()


# 全局主题管理器实例
fluent_theme_manager = FluentThemeManager()


# 便捷函数
def apply_fluent_theme(theme_name: str = None, accent_color: str = None) -> bool:
    """
    应用 Fluent 主题的便捷函数
    
    Args:
        theme_name: 主题名称，为 None 时使用已保存的配置
        accent_color: 主题色，为 None 时使用已保存的配置
        
    Returns:
        是否应用成功
    """
    if not FLUENT_AVAILABLE:
        return False
    
    success = True
    
    if theme_name:
        if not fluent_theme_manager.set_theme_by_name(theme_name):
            success = False
    
    if accent_color:
        if not fluent_theme_manager.set_accent_color(accent_color):
            success = False
    
    if not theme_name and not accent_color:
        # 应用已保存的配置
        success = fluent_theme_manager.apply_saved_theme()
    
    return success
