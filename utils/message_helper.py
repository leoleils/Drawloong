#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息提示工具类
基于 QFluentWidgets InfoBar 的消息提示封装
"""

from typing import Optional
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

try:
    from qfluentwidgets import InfoBar, InfoBarPosition, MessageBox
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    print("警告: QFluentWidgets 未安装，消息提示将使用原生 QMessageBox")

# 如果 QFluentWidgets 不可用，使用原生 QMessageBox 作为降级方案
if not FLUENT_AVAILABLE:
    from PyQt5.QtWidgets import QMessageBox


class MessageHelper:
    """
    消息提示工具类
    
    提供统一的消息提示接口，基于 QFluentWidgets InfoBar 实现。
    支持 success、warning、error、info 四种消息类型。
    支持自动消失和手动关闭。
    """
    
    # 默认消息显示时长（毫秒）
    DEFAULT_SUCCESS_DURATION = 3000  # 成功消息 3 秒
    DEFAULT_INFO_DURATION = 3000     # 信息消息 3 秒
    DEFAULT_WARNING_DURATION = 5000  # 警告消息 5 秒
    DEFAULT_ERROR_DURATION = -1      # 错误消息不自动消失
    
    # 默认消息位置
    DEFAULT_POSITION = InfoBarPosition.TOP if FLUENT_AVAILABLE else None
    
    @staticmethod
    def success(
        parent: QWidget,
        title: str,
        content: str = "",
        duration: int = None,
        position: 'InfoBarPosition' = None,
        is_closable: bool = True
    ) -> Optional['InfoBar']:
        """
        显示成功消息
        
        Args:
            parent: 父窗口
            title: 消息标题
            content: 消息内容
            duration: 显示时长（毫秒），-1 表示不自动消失
            position: 消息位置
            is_closable: 是否可手动关闭
            
        Returns:
            InfoBar 实例，如果 QFluentWidgets 不可用则返回 None
        """
        if duration is None:
            duration = MessageHelper.DEFAULT_SUCCESS_DURATION
        if position is None and FLUENT_AVAILABLE:
            position = MessageHelper.DEFAULT_POSITION
        
        if FLUENT_AVAILABLE:
            return InfoBar.success(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=is_closable,
                position=position,
                duration=duration,
                parent=parent
            )
        else:
            # 降级到 QMessageBox
            QMessageBox.information(parent, title, content)
            return None
    
    @staticmethod
    def warning(
        parent: QWidget,
        title: str,
        content: str = "",
        duration: int = None,
        position: 'InfoBarPosition' = None,
        is_closable: bool = True
    ) -> Optional['InfoBar']:
        """
        显示警告消息
        
        Args:
            parent: 父窗口
            title: 消息标题
            content: 消息内容
            duration: 显示时长（毫秒），-1 表示不自动消失
            position: 消息位置
            is_closable: 是否可手动关闭
            
        Returns:
            InfoBar 实例，如果 QFluentWidgets 不可用则返回 None
        """
        if duration is None:
            duration = MessageHelper.DEFAULT_WARNING_DURATION
        if position is None and FLUENT_AVAILABLE:
            position = MessageHelper.DEFAULT_POSITION
        
        if FLUENT_AVAILABLE:
            return InfoBar.warning(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=is_closable,
                position=position,
                duration=duration,
                parent=parent
            )
        else:
            # 降级到 QMessageBox
            QMessageBox.warning(parent, title, content)
            return None
    
    @staticmethod
    def error(
        parent: QWidget,
        title: str,
        content: str = "",
        duration: int = None,
        position: 'InfoBarPosition' = None,
        is_closable: bool = True
    ) -> Optional['InfoBar']:
        """
        显示错误消息
        
        Args:
            parent: 父窗口
            title: 消息标题
            content: 消息内容
            duration: 显示时长（毫秒），-1 表示不自动消失（默认）
            position: 消息位置
            is_closable: 是否可手动关闭
            
        Returns:
            InfoBar 实例，如果 QFluentWidgets 不可用则返回 None
        """
        if duration is None:
            duration = MessageHelper.DEFAULT_ERROR_DURATION
        if position is None and FLUENT_AVAILABLE:
            position = MessageHelper.DEFAULT_POSITION
        
        if FLUENT_AVAILABLE:
            return InfoBar.error(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=is_closable,
                position=position,
                duration=duration,
                parent=parent
            )
        else:
            # 降级到 QMessageBox
            QMessageBox.critical(parent, title, content)
            return None
    
    @staticmethod
    def info(
        parent: QWidget,
        title: str,
        content: str = "",
        duration: int = None,
        position: 'InfoBarPosition' = None,
        is_closable: bool = True
    ) -> Optional['InfoBar']:
        """
        显示信息消息
        
        Args:
            parent: 父窗口
            title: 消息标题
            content: 消息内容
            duration: 显示时长（毫秒），-1 表示不自动消失
            position: 消息位置
            is_closable: 是否可手动关闭
            
        Returns:
            InfoBar 实例，如果 QFluentWidgets 不可用则返回 None
        """
        if duration is None:
            duration = MessageHelper.DEFAULT_INFO_DURATION
        if position is None and FLUENT_AVAILABLE:
            position = MessageHelper.DEFAULT_POSITION
        
        if FLUENT_AVAILABLE:
            return InfoBar.info(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=is_closable,
                position=position,
                duration=duration,
                parent=parent
            )
        else:
            # 降级到 QMessageBox
            QMessageBox.information(parent, title, content)
            return None
    
    @staticmethod
    def confirm(
        parent: QWidget,
        title: str,
        content: str
    ) -> bool:
        """
        显示确认对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            content: 对话框内容
            
        Returns:
            用户是否确认（True 表示确认，False 表示取消）
        """
        if FLUENT_AVAILABLE:
            dialog = MessageBox(title, content, parent)
            return dialog.exec_() == 1  # MessageBox 确认返回 1
        else:
            # 降级到 QMessageBox
            result = QMessageBox.question(
                parent, 
                title, 
                content,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return result == QMessageBox.Yes
    
    @staticmethod
    def is_fluent_available() -> bool:
        """检查 QFluentWidgets 是否可用"""
        return FLUENT_AVAILABLE


# 便捷函数，可直接导入使用
def show_success(parent: QWidget, title: str, content: str = "", **kwargs):
    """显示成功消息的便捷函数"""
    return MessageHelper.success(parent, title, content, **kwargs)


def show_warning(parent: QWidget, title: str, content: str = "", **kwargs):
    """显示警告消息的便捷函数"""
    return MessageHelper.warning(parent, title, content, **kwargs)


def show_error(parent: QWidget, title: str, content: str = "", **kwargs):
    """显示错误消息的便捷函数"""
    return MessageHelper.error(parent, title, content, **kwargs)


def show_info(parent: QWidget, title: str, content: str = "", **kwargs):
    """显示信息消息的便捷函数"""
    return MessageHelper.info(parent, title, content, **kwargs)


def show_confirm(parent: QWidget, title: str, content: str) -> bool:
    """显示确认对话框的便捷函数"""
    return MessageHelper.confirm(parent, title, content)
