#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视觉一致性测试脚本
测试主题切换和视觉常量
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication


def test_visual_constants():
    """测试视觉常量定义"""
    print("测试 1: 视觉常量定义...")
    try:
        from themes.visual_constants import (
            # 间距常量
            PAGE_MARGIN, DIALOG_MARGIN, CARD_PADDING,
            SPACING_LARGE, SPACING_MEDIUM, SPACING_NORMAL, SPACING_SMALL,
            # 尺寸常量
            BUTTON_HEIGHT_NORMAL, BUTTON_HEIGHT_LARGE,
            TOOL_BUTTON_SIZE, ICON_SIZE_NORMAL,
            # 动画常量
            ANIMATION_DURATION_NORMAL, MESSAGE_DURATION_SHORT,
            # 颜色常量
            COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR,
            # 辅助函数
            get_theme_colors
        )
        
        # 验证间距值
        assert PAGE_MARGIN == 40, "PAGE_MARGIN 应为 40"
        assert DIALOG_MARGIN == 24, "DIALOG_MARGIN 应为 24"
        assert CARD_PADDING == 16, "CARD_PADDING 应为 16"
        assert SPACING_NORMAL == 12, "SPACING_NORMAL 应为 12"
        
        # 验证尺寸值
        assert BUTTON_HEIGHT_NORMAL == 36, "BUTTON_HEIGHT_NORMAL 应为 36"
        assert BUTTON_HEIGHT_LARGE == 48, "BUTTON_HEIGHT_LARGE 应为 48"
        
        # 验证颜色值
        assert COLOR_SUCCESS == "#28a745", "COLOR_SUCCESS 应为 #28a745"
        assert COLOR_ERROR == "#dc3545", "COLOR_ERROR 应为 #dc3545"
        
        # 测试辅助函数
        light_colors = get_theme_colors(False)
        dark_colors = get_theme_colors(True)
        
        assert 'background' in light_colors, "浅色主题应包含 background"
        assert 'background' in dark_colors, "深色主题应包含 background"
        
        print("  ✓ 视觉常量定义测试通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 视觉常量定义测试失败: {e}")
        return False


def test_theme_switching():
    """测试主题切换功能"""
    print("\n测试 2: 主题切换功能...")
    try:
        from themes.fluent_theme import (
            fluent_theme_manager, AppTheme, FLUENT_AVAILABLE
        )
        
        if not FLUENT_AVAILABLE:
            print("  ⚠ QFluentWidgets 不可用，跳过主题切换测试")
            return True
        
        # 保存原始主题
        original_theme = fluent_theme_manager.current_theme
        original_color = fluent_theme_manager.current_accent_color
        
        # 测试浅色主题
        fluent_theme_manager.set_theme(AppTheme.LIGHT)
        assert not fluent_theme_manager.is_dark_theme(), "应为浅色主题"
        print("  ✓ 浅色主题设置正确")
        
        # 测试深色主题
        fluent_theme_manager.set_theme(AppTheme.DARK)
        assert fluent_theme_manager.is_dark_theme(), "应为深色主题"
        print("  ✓ 深色主题设置正确")
        
        # 测试主题切换
        new_theme = fluent_theme_manager.toggle_theme()
        assert new_theme == AppTheme.LIGHT, "切换后应为浅色主题"
        print("  ✓ 主题切换功能正常")
        
        # 恢复原始主题
        fluent_theme_manager.set_theme(original_theme)
        fluent_theme_manager.set_accent_color(original_color)
        
        print("  ✓ 主题切换功能测试通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 主题切换功能测试失败: {e}")
        return False


def test_theme_color_presets():
    """测试预设主题色"""
    print("\n测试 3: 预设主题色...")
    try:
        from themes.fluent_theme import (
            fluent_theme_manager, FLUENT_AVAILABLE
        )
        
        if not FLUENT_AVAILABLE:
            print("  ⚠ QFluentWidgets 不可用，跳过预设颜色测试")
            return True
        
        # 保存原始颜色
        original_color = fluent_theme_manager.current_accent_color
        
        # 获取预设颜色
        preset_colors = fluent_theme_manager.get_preset_colors()
        
        # 验证预设颜色存在
        expected_colors = ['blue', 'purple', 'pink', 'red', 'orange', 'green', 'teal']
        for color_name in expected_colors:
            assert color_name in preset_colors, f"缺少预设颜色: {color_name}"
        
        print(f"  ✓ 预设颜色数量: {len(preset_colors)}")
        
        # 测试设置预设颜色
        for color_name in ['blue', 'purple', 'green']:
            result = fluent_theme_manager.set_preset_color(color_name)
            assert result, f"设置预设颜色 {color_name} 失败"
            print(f"  ✓ 预设颜色 {color_name} 设置成功")
        
        # 恢复原始颜色
        fluent_theme_manager.set_accent_color(original_color)
        
        print("  ✓ 预设主题色测试通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 预设主题色测试失败: {e}")
        return False


def test_status_bar_theme():
    """测试状态栏主题更新"""
    print("\n测试 4: 状态栏主题更新...")
    try:
        from ui.fluent_status_bar import FluentStatusBar, FLUENT_AVAILABLE
        
        # 创建状态栏实例
        status_bar = FluentStatusBar()
        
        # 测试主题更新方法
        status_bar.updateTheme()
        print("  ✓ 状态栏主题更新方法调用成功")
        
        # 测试消息显示
        status_bar.showMessage("测试消息", 1000)
        assert status_bar.status_label.text() == "测试消息", "消息显示不正确"
        print("  ✓ 状态栏消息显示正常")
        
        # 测试忙碌状态
        status_bar.setBusy(True, "处理中...")
        assert status_bar.isBusy(), "忙碌状态设置失败"
        print("  ✓ 状态栏忙碌状态正常")
        
        status_bar.setBusy(False)
        assert not status_bar.isBusy(), "忙碌状态清除失败"
        print("  ✓ 状态栏忙碌状态清除正常")
        
        print("  ✓ 状态栏主题更新测试通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 状态栏主题更新测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("烛龙绘影 视觉一致性测试")
    print("=" * 60)
    
    # 创建 QApplication（某些测试需要）
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    results = []
    
    # 运行测试
    results.append(("视觉常量定义", test_visual_constants()))
    results.append(("主题切换功能", test_theme_switching()))
    results.append(("预设主题色", test_theme_color_presets()))
    results.append(("状态栏主题更新", test_status_bar_theme()))
    
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
