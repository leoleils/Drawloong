#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI 功能测试脚本
测试 QFluentWidgets UI 组件的基本功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt


def test_fluent_widgets_import():
    """测试 QFluentWidgets 导入"""
    print("测试 1: QFluentWidgets 导入...")
    try:
        from qfluentwidgets import (
            FluentWindow, NavigationItemPosition, FluentIcon,
            PrimaryPushButton, PushButton, ComboBox, TextEdit,
            CardWidget, SubtitleLabel, BodyLabel, SwitchButton,
            TreeWidget, RoundMenu, Action, TableWidget,
            Slider, ToolButton, InfoBar, setTheme, Theme
        )
        print("  ✓ QFluentWidgets 导入成功")
        return True
    except ImportError as e:
        print(f"  ✗ QFluentWidgets 导入失败: {e}")
        return False


def test_theme_system():
    """测试主题系统"""
    print("\n测试 2: 主题系统...")
    try:
        from themes.fluent_theme import (
            fluent_theme_manager, AppTheme, FLUENT_AVAILABLE
        )
        
        if not FLUENT_AVAILABLE:
            print("  ⚠ QFluentWidgets 不可用，跳过主题测试")
            return True
        
        # 测试获取当前主题
        current_theme = fluent_theme_manager.current_theme
        print(f"  当前主题: {current_theme.value}")
        
        # 测试获取当前主题色
        current_color = fluent_theme_manager.current_accent_color
        print(f"  当前主题色: {current_color}")
        
        # 测试主题切换
        original_theme = current_theme
        
        # 切换到深色主题
        result = fluent_theme_manager.set_theme(AppTheme.DARK)
        if result:
            print("  ✓ 切换到深色主题成功")
        else:
            print("  ✗ 切换到深色主题失败")
            return False
        
        # 切换到浅色主题
        result = fluent_theme_manager.set_theme(AppTheme.LIGHT)
        if result:
            print("  ✓ 切换到浅色主题成功")
        else:
            print("  ✗ 切换到浅色主题失败")
            return False
        
        # 恢复原始主题
        fluent_theme_manager.set_theme(original_theme)
        
        # 测试主题色设置
        result = fluent_theme_manager.set_accent_color("#007bff")
        if result:
            print("  ✓ 设置主题色成功")
        else:
            print("  ✗ 设置主题色失败")
            return False
        
        # 测试预设颜色
        result = fluent_theme_manager.set_preset_color("purple")
        if result:
            print("  ✓ 设置预设颜色成功")
        else:
            print("  ✗ 设置预设颜色失败")
            return False
        
        # 恢复原始颜色
        fluent_theme_manager.set_accent_color(current_color)
        
        print("  ✓ 主题系统测试通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 主题系统测试失败: {e}")
        return False


def test_message_helper():
    """测试消息提示工具"""
    print("\n测试 3: 消息提示工具...")
    try:
        from utils.message_helper import MessageHelper
        
        # 检查方法是否存在
        assert hasattr(MessageHelper, 'success'), "缺少 success 方法"
        assert hasattr(MessageHelper, 'warning'), "缺少 warning 方法"
        assert hasattr(MessageHelper, 'error'), "缺少 error 方法"
        assert hasattr(MessageHelper, 'info'), "缺少 info 方法"
        assert hasattr(MessageHelper, 'confirm'), "缺少 confirm 方法"
        
        print("  ✓ MessageHelper 方法检查通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 消息提示工具测试失败: {e}")
        return False


def test_ui_components_import():
    """测试 UI 组件导入"""
    print("\n测试 4: UI 组件导入...")
    
    components = [
        ("ui.welcome_page", "WelcomePage"),
        ("ui.config_panel", "ConfigPanel"),
        ("ui.upload_widget", "UploadWidget"),
        ("ui.task_list", "TaskListWidget"),
        ("ui.project_explorer", "ProjectExplorer"),
        ("ui.video_viewer", "VideoViewerWidget"),
        ("ui.settings_dialog", "SettingsDialog"),
        ("ui.project_dialog", "NewProjectDialog"),
        ("ui.project_dialog", "OpenProjectDialog"),
        ("ui.image_viewer", "ImageViewer"),
        ("ui.fluent_status_bar", "FluentStatusBar"),
        ("ui.fluent_main_window", "FluentMainWindow"),
    ]
    
    all_passed = True
    for module_name, class_name in components:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  ✓ {class_name} 导入成功")
        except Exception as e:
            print(f"  ✗ {class_name} 导入失败: {e}")
            all_passed = False
    
    return all_passed


def test_navigation_items():
    """测试导航项配置"""
    print("\n测试 5: 导航项配置...")
    try:
        from qfluentwidgets import FluentIcon
        
        # 检查所需的图标是否存在
        icons = [
            ("HOME", "首页"),
            ("VIDEO", "首帧生视频"),
            ("MOVIE", "首尾帧生视频"),
            ("PHOTO", "文生图"),
            ("EDIT", "图像编辑"),
            ("SYNC", "参考生视频"),
            ("SETTING", "设置"),
        ]
        
        for icon_name, desc in icons:
            if hasattr(FluentIcon, icon_name):
                print(f"  ✓ {icon_name} ({desc}) 图标存在")
            else:
                print(f"  ✗ {icon_name} ({desc}) 图标不存在")
                return False
        
        print("  ✓ 导航项配置测试通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 导航项配置测试失败: {e}")
        return False


def test_config_panel_models():
    """测试配置面板模型配置"""
    print("\n测试 6: 配置面板模型配置...")
    try:
        from ui.config_panel import ConfigPanel
        
        # 检查模型配置
        model_config = ConfigPanel.MODEL_CONFIG
        
        required_models = [
            'wan2.6-i2v',
            'wan2.5-i2v-preview',
            'wan2.2-i2v-flash',
            'wan2.2-i2v-plus',
        ]
        
        for model in required_models:
            if model in model_config:
                config = model_config[model]
                assert 'name' in config, f"{model} 缺少 name"
                assert 'resolutions' in config, f"{model} 缺少 resolutions"
                assert 'durations' in config, f"{model} 缺少 durations"
                print(f"  ✓ {model} 配置完整")
            else:
                print(f"  ✗ {model} 配置缺失")
                return False
        
        print("  ✓ 配置面板模型配置测试通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 配置面板模型配置测试失败: {e}")
        return False


def test_settings_persistence():
    """测试设置持久化"""
    print("\n测试 7: 设置持久化...")
    try:
        from config.settings import settings
        
        # 检查设置方法
        assert hasattr(settings, 'get_api_key'), "缺少 get_api_key 方法"
        assert hasattr(settings, 'set_api_key'), "缺少 set_api_key 方法"
        assert hasattr(settings, 'get_theme'), "缺少 get_theme 方法"
        assert hasattr(settings, 'set_theme'), "缺少 set_theme 方法"
        
        # 检查 Fluent 主题相关方法
        assert hasattr(settings, 'get_fluent_theme'), "缺少 get_fluent_theme 方法"
        assert hasattr(settings, 'set_fluent_theme'), "缺少 set_fluent_theme 方法"
        assert hasattr(settings, 'get_accent_color'), "缺少 get_accent_color 方法"
        assert hasattr(settings, 'set_accent_color'), "缺少 set_accent_color 方法"
        
        print("  ✓ 设置持久化方法检查通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 设置持久化测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("烛龙绘影 UI 功能测试")
    print("=" * 60)
    
    # 创建 QApplication（某些测试需要）
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    results = []
    
    # 运行测试
    results.append(("QFluentWidgets 导入", test_fluent_widgets_import()))
    results.append(("主题系统", test_theme_system()))
    results.append(("消息提示工具", test_message_helper()))
    results.append(("UI 组件导入", test_ui_components_import()))
    results.append(("导航项配置", test_navigation_items()))
    results.append(("配置面板模型", test_config_panel_models()))
    results.append(("设置持久化", test_settings_persistence()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
