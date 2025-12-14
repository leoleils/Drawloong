#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用主题样式表
提供多种主题风格
"""


class Themes:
    """主题样式表集合"""
    
    # 浅色主题 (默认)
    LIGHT = """
    QWidget {
        background-color: #ffffff;
        color: #333333;
        font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif;
        font-size: 13px;
    }
    
    QMainWindow {
        background-color: #f5f5f5;
    }
    
    QPushButton {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
    }
    
    QPushButton:hover {
        background-color: #0056b3;
    }
    
    QPushButton:pressed {
        background-color: #004085;
    }
    
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #ffffff;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 5px;
        color: #333333;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 1px solid #007bff;
    }
    
    QComboBox {
        background-color: #ffffff;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 5px;
        color: #333333;
    }
    
    QComboBox:hover {
        border: 1px solid #007bff;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QGroupBox {
        border: 1px solid #dee2e6;
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        color: #495057;
    }
    
    QTabWidget::pane {
        border: 1px solid #dee2e6;
        background-color: #ffffff;
    }
    
    QTabBar::tab {
        background-color: #f8f9fa;
        color: #495057;
        padding: 8px 16px;
        border: 1px solid #dee2e6;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #ffffff;
        color: #007bff;
        font-weight: bold;
    }
    
    QTabBar::tab:hover {
        background-color: #e9ecef;
    }
    
    QScrollBar:vertical {
        background-color: #f8f9fa;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #adb5bd;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #6c757d;
    }
    
    QScrollBar:horizontal {
        background-color: #f8f9fa;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #adb5bd;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #6c757d;
    }
    
    QMenuBar {
        background-color: #f8f9fa;
        color: #333333;
    }
    
    QMenuBar::item:selected {
        background-color: #e9ecef;
    }
    
    QMenu {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
    }
    
    QMenu::item:selected {
        background-color: #007bff;
        color: white;
    }
    """
    
    # 深色主题
    DARK = """
    QWidget {
        background-color: #1e1e1e;
        color: #e0e0e0;
        font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif;
        font-size: 13px;
    }
    
    QMainWindow {
        background-color: #252525;
    }
    
    QPushButton {
        background-color: #0d6efd;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
    }
    
    QPushButton:hover {
        background-color: #0b5ed7;
    }
    
    QPushButton:pressed {
        background-color: #0a58ca;
    }
    
    QPushButton:disabled {
        background-color: #3a3a3a;
        color: #777777;
    }
    
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #2d2d2d;
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        padding: 5px;
        color: #e0e0e0;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 1px solid #0d6efd;
    }
    
    QComboBox {
        background-color: #2d2d2d;
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        padding: 5px;
        color: #e0e0e0;
    }
    
    QComboBox:hover {
        border: 1px solid #0d6efd;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        color: #e0e0e0;
        selection-background-color: #0d6efd;
    }
    
    QGroupBox {
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
        color: #e0e0e0;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
    }
    
    QTabWidget::pane {
        border: 1px solid #3a3a3a;
        background-color: #1e1e1e;
    }
    
    QTabBar::tab {
        background-color: #2d2d2d;
        color: #b0b0b0;
        padding: 8px 16px;
        border: 1px solid #3a3a3a;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #1e1e1e;
        color: #0d6efd;
        font-weight: bold;
    }
    
    QTabBar::tab:hover {
        background-color: #353535;
    }
    
    QScrollBar:vertical {
        background-color: #2d2d2d;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #5a5a5a;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #707070;
    }
    
    QScrollBar:horizontal {
        background-color: #2d2d2d;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #5a5a5a;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #707070;
    }
    
    QMenuBar {
        background-color: #2d2d2d;
        color: #e0e0e0;
    }
    
    QMenuBar::item:selected {
        background-color: #353535;
    }
    
    QMenu {
        background-color: #2d2d2d;
        border: 1px solid #3a3a3a;
        color: #e0e0e0;
    }
    
    QMenu::item:selected {
        background-color: #0d6efd;
        color: white;
    }
    
    QListWidget {
        background-color: #2d2d2d;
        border: 1px solid #3a3a3a;
        color: #e0e0e0;
    }
    
    QListWidget::item:selected {
        background-color: #0d6efd;
        color: white;
    }
    
    QTreeWidget {
        background-color: #2d2d2d;
        border: 1px solid #3a3a3a;
        color: #e0e0e0;
    }
    
    QTreeWidget::item:selected {
        background-color: #0d6efd;
        color: white;
    }
    """
    
    # 蓝色主题
    BLUE = """
    QWidget {
        background-color: #f0f4f8;
        color: #1a365d;
        font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif;
        font-size: 13px;
    }
    
    QMainWindow {
        background-color: #e6f2ff;
    }
    
    QPushButton {
        background-color: #2563eb;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
    }
    
    QPushButton:hover {
        background-color: #1d4ed8;
    }
    
    QPushButton:pressed {
        background-color: #1e40af;
    }
    
    QPushButton:disabled {
        background-color: #cbd5e1;
        color: #94a3b8;
    }
    
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #ffffff;
        border: 1px solid #3b82f6;
        border-radius: 4px;
        padding: 5px;
        color: #1e293b;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 2px solid #2563eb;
    }
    
    QComboBox {
        background-color: #ffffff;
        border: 1px solid #3b82f6;
        border-radius: 4px;
        padding: 5px;
        color: #1e293b;
    }
    
    QComboBox:hover {
        border: 2px solid #2563eb;
    }
    
    QGroupBox {
        border: 2px solid #60a5fa;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
        color: #1e40af;
    }
    
    QTabWidget::pane {
        border: 2px solid #60a5fa;
        background-color: #ffffff;
    }
    
    QTabBar::tab {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 8px 16px;
        border: 1px solid #60a5fa;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #ffffff;
        color: #1e3a8a;
        font-weight: bold;
        border-bottom: 2px solid #ffffff;
    }
    
    QTabBar::tab:hover {
        background-color: #bfdbfe;
    }
    
    QMenuBar {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    QMenuBar::item:selected {
        background-color: #bfdbfe;
    }
    
    QMenu {
        background-color: #ffffff;
        border: 1px solid #60a5fa;
    }
    
    QMenu::item:selected {
        background-color: #2563eb;
        color: white;
    }
    """
    
    # 绿色护眼主题
    GREEN = """
    QWidget {
        background-color: #f0fdf4;
        color: #14532d;
        font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif;
        font-size: 13px;
    }
    
    QMainWindow {
        background-color: #dcfce7;
    }
    
    QPushButton {
        background-color: #16a34a;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
    }
    
    QPushButton:hover {
        background-color: #15803d;
    }
    
    QPushButton:pressed {
        background-color: #166534;
    }
    
    QPushButton:disabled {
        background-color: #d1d5db;
        color: #9ca3af;
    }
    
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #ffffff;
        border: 1px solid #22c55e;
        border-radius: 4px;
        padding: 5px;
        color: #166534;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 2px solid #16a34a;
    }
    
    QComboBox {
        background-color: #ffffff;
        border: 1px solid #22c55e;
        border-radius: 4px;
        padding: 5px;
        color: #166534;
    }
    
    QComboBox:hover {
        border: 2px solid #16a34a;
    }
    
    QGroupBox {
        border: 2px solid #4ade80;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
        color: #15803d;
    }
    
    QTabWidget::pane {
        border: 2px solid #4ade80;
        background-color: #ffffff;
    }
    
    QTabBar::tab {
        background-color: #d1fae5;
        color: #15803d;
        padding: 8px 16px;
        border: 1px solid #4ade80;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #ffffff;
        color: #14532d;
        font-weight: bold;
    }
    
    QTabBar::tab:hover {
        background-color: #bbf7d0;
    }
    
    QMenuBar {
        background-color: #d1fae5;
        color: #15803d;
    }
    
    QMenuBar::item:selected {
        background-color: #bbf7d0;
    }
    
    QMenu {
        background-color: #ffffff;
        border: 1px solid #4ade80;
    }
    
    QMenu::item:selected {
        background-color: #16a34a;
        color: white;
    }
    """
    
    @staticmethod
    def get_all_themes():
        """获取所有主题"""
        return {
            'light': ('浅色主题', Themes.LIGHT),
            'dark': ('深色主题', Themes.DARK),
            'blue': ('蓝色主题', Themes.BLUE),
            'green': ('绿色护眼', Themes.GREEN)
        }
    
    @staticmethod
    def get_theme(theme_name):
        """根据名称获取主题样式表"""
        themes = {
            'light': Themes.LIGHT,
            'dark': Themes.DARK,
            'blue': Themes.BLUE,
            'green': Themes.GREEN
        }
        return themes.get(theme_name, Themes.LIGHT)
