#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频播放器
使用系统默认播放器打开视频
"""

import os
import subprocess
import platform
from PyQt5.QtWidgets import QMessageBox


class VideoPlayer:
    """视频播放器 - 使用系统默认应用"""
    
    @staticmethod
    def play(video_path, parent=None):
        """
        播放视频
        
        Args:
            video_path: 视频文件路径
            parent: 父窗口
        """
        if not os.path.exists(video_path):
            if parent:
                QMessageBox.warning(parent, "错误", "视频文件不存在")
            return False
        
        system = platform.system()
        
        try:
            if system == 'Darwin':  # macOS
                subprocess.run(['open', video_path])
            elif system == 'Windows':
                os.startfile(video_path)
            else:  # Linux
                subprocess.run(['xdg-open', video_path])
            return True
        except Exception as e:
            if parent:
                QMessageBox.critical(parent, "错误", f"无法播放视频: {str(e)}")
            return False
