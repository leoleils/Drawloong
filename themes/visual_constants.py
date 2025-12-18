#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视觉一致性常量
定义 UI 组件的统一间距、尺寸和样式标准
"""

# ==================== 间距常量 ====================

# 页面级别边距
PAGE_MARGIN = 40  # 页面外边距（如欢迎页面）

# 对话框边距
DIALOG_MARGIN = 24  # 对话框内边距

# 卡片内边距
CARD_PADDING = 16  # 卡片内边距
CARD_PADDING_SMALL = 12  # 小型卡片内边距（如视频播放器）

# 组件间距
SPACING_LARGE = 24  # 大区块间距（如页面主要区域之间）
SPACING_MEDIUM = 16  # 中等间距（如对话框区块之间）
SPACING_NORMAL = 12  # 标准间距（如卡片内组件之间）
SPACING_SMALL = 8   # 小间距（如按钮组、工具栏按钮之间）

# 工具栏
TOOLBAR_PADDING_H = 12  # 工具栏水平内边距
TOOLBAR_PADDING_V = 8   # 工具栏垂直内边距

# 状态栏
STATUSBAR_PADDING_H = 12  # 状态栏水平内边距
STATUSBAR_PADDING_V = 4   # 状态栏垂直内边距
STATUSBAR_HEIGHT = 28     # 状态栏高度

# 标题栏
HEADER_PADDING_H = 10  # 标题栏水平内边距
HEADER_PADDING_V = 5   # 标题栏垂直内边距

# ==================== 尺寸常量 ====================

# 按钮尺寸
BUTTON_HEIGHT_NORMAL = 36  # 标准按钮高度
BUTTON_HEIGHT_LARGE = 48   # 大按钮高度（如生成按钮）
BUTTON_MIN_WIDTH = 80      # 按钮最小宽度

# 工具按钮尺寸
TOOL_BUTTON_SIZE = 36      # 工具按钮尺寸
TOOL_BUTTON_SIZE_SMALL = 28  # 小工具按钮尺寸
TOOL_BUTTON_SIZE_MINI = 24   # 迷你工具按钮尺寸

# 图标尺寸
ICON_SIZE_LARGE = 64   # 大图标（如上传区域图标）
ICON_SIZE_NORMAL = 48  # 标准图标（如缩略图）
ICON_SIZE_SMALL = 32   # 小图标（如列表项图标）
ICON_SIZE_MINI = 24    # 迷你图标（如状态图标）
ICON_SIZE_TINY = 16    # 微型图标（如进度环）

# 输入框尺寸
INPUT_HEIGHT = 36      # 输入框高度
TEXTAREA_MIN_HEIGHT = 60   # 文本域最小高度
TEXTAREA_MAX_HEIGHT = 120  # 文本域最大高度

# 卡片尺寸
CARD_MIN_HEIGHT = 70   # 卡片最小高度（如最近项目卡片）

# 表格行高
TABLE_ROW_HEIGHT = 44  # 表格行高

# ==================== 动画常量 ====================

# 动画时长（毫秒）
ANIMATION_DURATION_FAST = 150    # 快速动画
ANIMATION_DURATION_NORMAL = 250  # 标准动画
ANIMATION_DURATION_SLOW = 400    # 慢速动画

# 消息提示时长（毫秒）
MESSAGE_DURATION_SHORT = 3000   # 短消息（成功提示）
MESSAGE_DURATION_NORMAL = 5000  # 标准消息（警告提示）
MESSAGE_DURATION_LONG = -1      # 长消息（错误提示，不自动消失）

# ==================== 颜色常量 ====================

# 状态颜色
COLOR_SUCCESS = "#28a745"  # 成功/完成
COLOR_WARNING = "#ffc107"  # 警告
COLOR_ERROR = "#dc3545"    # 错误/失败
COLOR_INFO = "#17a2b8"     # 信息

# 边框颜色
BORDER_COLOR_LIGHT = "rgba(0, 0, 0, 0.1)"   # 浅色主题边框
BORDER_COLOR_DARK = "rgba(255, 255, 255, 0.1)"  # 深色主题边框

# 背景颜色
BG_COLOR_LIGHT = "rgba(249, 249, 249, 0.9)"  # 浅色主题背景
BG_COLOR_DARK = "rgba(32, 32, 32, 0.9)"      # 深色主题背景

# 高亮颜色
HIGHLIGHT_COLOR = "#0078d4"  # 高亮/选中颜色

# ==================== 辅助函数 ====================

def get_theme_colors(is_dark: bool) -> dict:
    """
    根据主题获取颜色配置
    
    Args:
        is_dark: 是否为深色主题
        
    Returns:
        颜色配置字典
    """
    if is_dark:
        return {
            'background': BG_COLOR_DARK,
            'border': BORDER_COLOR_DARK,
            'text_primary': '#ffffff',
            'text_secondary': '#999999',
        }
    else:
        return {
            'background': BG_COLOR_LIGHT,
            'border': BORDER_COLOR_LIGHT,
            'text_primary': '#333333',
            'text_secondary': '#666666',
        }
