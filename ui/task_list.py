#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务列表组件
显示和管理所有任务
"""

import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView,
    QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor

from core.task_manager import TaskManager
from core.api_client import DashScopeClient
from core.models import TaskStatus
from config.settings import settings


class TaskMonitorThread(QThread):
    """任务监控线程"""
    
    task_updated = pyqtSignal(str, dict)  # task_id, task_data
    
    def __init__(self, task_id, api_client, task_manager, output_folder=None):
        super().__init__()
        self.task_id = task_id
        self.api_client = api_client
        self.task_manager = task_manager
        self.output_folder = output_folder or settings.OUTPUT_FOLDER
        self.running = True
    
    def run(self):
        """运行监控"""
        while self.running:
            try:
                task = self.task_manager.get_task(self.task_id)
                if not task or task.is_completed():
                    break
                
                if not task.async_task_id:
                    break
                
                # 查询任务状态
                result = self.api_client.query_task(task.async_task_id)
                task_data = result['output']
                
                # 更新任务状态
                status = task_data['task_status']
                message = task_data.get('message', '')
                
                updates = {
                    'status': TaskStatus(status),
                    'message': message
                }
                
                # 如果任务成功
                if status == 'SUCCEEDED':
                    video_url = task_data.get('video_url')
                    if video_url:
                        # 下载视频到指定输出文件夹
                        output_path = os.path.join(
                            self.output_folder,
                            f"{self.task_id}.mp4"
                        )
                        try:
                            downloaded_path = self.api_client.download_video(video_url, output_path)
                            updates['output_path'] = downloaded_path
                            updates['video_url'] = video_url
                            updates['completed_at'] = datetime.now().isoformat()
                        except Exception as e:
                            print(f"下载视频失败: {e}")
                            updates['error'] = str(e)
                
                elif status == 'FAILED':
                    updates['error'] = message
                    updates['error_code'] = task_data.get('code', 'UnknownError')
                
                # 更新任务
                self.task_manager.update_task(self.task_id, **updates)
                
                # 发送更新信号
                self.task_updated.emit(self.task_id, updates)
                
                # 如果完成则退出
                if status in ['SUCCEEDED', 'FAILED']:
                    break
                
                # 等待5秒
                self.msleep(5000)
                
            except Exception as e:
                print(f"监控任务 {self.task_id} 时出错: {e}")
                self.msleep(5000)
    
    def stop(self):
        """停止监控"""
        self.running = False


class TaskListWidget(QWidget):
    """任务列表组件"""
    
    task_updated = pyqtSignal(str)  # task_id
    
    def __init__(self, task_manager, project_manager=None, parent=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.project_manager = project_manager
        self.api_client = DashScopeClient()
        self.monitor_threads = {}  # task_id -> thread
        
        self.setup_ui()
        self.refresh_tasks()
        
        # 定时刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_tasks)
        self.refresh_timer.start(10000)  # 每10秒刷新
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建组框
        group_box = QGroupBox("任务列表")
        group_layout = QVBoxLayout(group_box)
        
        # 顶部按钮栏
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_tasks)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        group_layout.addLayout(button_layout)
        
        # 任务表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            '任务ID', '提示词', '模型', '分辨率', 
            '状态', '创建时间'
        ])
        
        # 设置表格属性
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        
        group_layout.addWidget(self.table)
        layout.addWidget(group_box)
    
    def refresh_tasks(self):
        """刷新任务列表"""
        tasks = self.task_manager.get_all_tasks()
        
        # 按创建时间倒序排列
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # 清空表格
        self.table.setRowCount(0)
        
        # 填充数据
        for row, task in enumerate(tasks):
            self.table.insertRow(row)
            
            # 任务ID
            id_item = QTableWidgetItem(task.id[:8] + '...')
            self.table.setItem(row, 0, id_item)
            
            # 提示词
            prompt_item = QTableWidgetItem(
                task.prompt[:30] + '...' if len(task.prompt) > 30 else task.prompt
            )
            self.table.setItem(row, 1, prompt_item)
            
            # 模型
            model_item = QTableWidgetItem(task.model)
            self.table.setItem(row, 2, model_item)
            
            # 分辨率
            resolution_item = QTableWidgetItem(task.resolution)
            self.table.setItem(row, 3, resolution_item)
            
            # 状态
            status_item = QTableWidgetItem(task.status.value)
            if task.status == TaskStatus.SUCCEEDED:
                status_item.setBackground(QColor(212, 237, 218))
            elif task.status == TaskStatus.FAILED:
                status_item.setBackground(QColor(248, 215, 218))
            elif task.status == TaskStatus.RUNNING:
                status_item.setBackground(QColor(255, 243, 205))
            self.table.setItem(row, 4, status_item)
            
            # 创建时间
            try:
                created_time = datetime.fromisoformat(task.created_at)
                time_str = created_time.strftime('%Y-%m-%d %H:%M')
            except:
                time_str = task.created_at[:16]
            time_item = QTableWidgetItem(time_str)
            self.table.setItem(row, 5, time_item)
    
    def start_monitoring_task(self, task_id):
        """开始监控任务"""
        if task_id in self.monitor_threads:
            return
        
        # 确定输出文件夹
        output_folder = settings.OUTPUT_FOLDER
        if self.project_manager and self.project_manager.has_project():
            project = self.project_manager.get_current_project()
            output_folder = project.outputs_folder
        
        thread = TaskMonitorThread(task_id, self.api_client, self.task_manager, output_folder)
        thread.task_updated.connect(self.on_task_updated)
        thread.finished.connect(lambda: self.on_monitoring_finished(task_id))
        thread.start()
        
        self.monitor_threads[task_id] = thread
    
    def on_task_updated(self, task_id, updates):
        """任务更新回调"""
        self.refresh_tasks()
        self.task_updated.emit(task_id)
    
    def on_monitoring_finished(self, task_id):
        """监控结束回调"""
        if task_id in self.monitor_threads:
            del self.monitor_threads[task_id]
        self.refresh_tasks()
        
        # 刷新工程资源管理器（如果有工程）
        if self.project_manager and self.project_manager.has_project():
            # 通过 parent 窗口刷新资源管理器
            main_window = self.window()
            if hasattr(main_window, 'project_explorer'):
                main_window.project_explorer.refresh()
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止所有监控线程
        for thread in self.monitor_threads.values():
            thread.stop()
            thread.wait()
        event.accept()
