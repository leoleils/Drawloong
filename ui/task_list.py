#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务列表组件
显示和管理所有任务
使用 QFluentWidgets 美化
"""

import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor

from qfluentwidgets import (
    TableWidget, PushButton, CardWidget, SubtitleLabel,
    FluentIcon, ProgressBar, InfoBar, InfoBarPosition,
    ToolButton, setFont
)

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
                        # 检查任务是否已经有输出路径（说明已被其他地方下载）
                        if task.output_path and os.path.exists(task.output_path):
                            # 已经下载过，只更新状态
                            updates['video_url'] = video_url
                            updates['completed_at'] = datetime.now().isoformat()
                        else:
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
    """任务列表组件 - 使用 QFluentWidgets 美化"""
    
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
        # 统一外边距：16px（与其他组件保持一致）
        layout.setContentsMargins(16, 16, 16, 16)
        # 统一组件间距：12px
        layout.setSpacing(12)
        
        # 创建卡片容器
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        # 统一卡片内边距：16px
        card_layout.setContentsMargins(16, 16, 16, 16)
        # 统一卡片内组件间距：12px
        card_layout.setSpacing(12)
        
        # 标题和按钮栏
        header_layout = QHBoxLayout()
        
        # 标题
        title_label = SubtitleLabel("任务列表")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 刷新按钮 - 使用 PushButton 配合 FluentIcon
        self.refresh_btn = PushButton(FluentIcon.SYNC, "刷新")
        self.refresh_btn.clicked.connect(self.refresh_tasks)
        header_layout.addWidget(self.refresh_btn)
        
        card_layout.addLayout(header_layout)
        
        # 任务表格 - 使用 QFluentWidgets 的 TableWidget
        self.table = TableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            '状态', '任务ID', '提示词', '模型', '分辨率', '创建时间'
        ])
        
        # 设置表格属性
        self.table.setSelectRightClickedRow(True)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        card_layout.addWidget(self.table)
        layout.addWidget(card)
    
    def _get_status_icon(self, status) -> FluentIcon:
        """根据任务状态返回对应的 FluentIcon"""
        # 支持字符串和枚举两种类型
        if status == TaskStatus.SUCCEEDED or status == 'SUCCEEDED':
            return FluentIcon.COMPLETED
        elif status == TaskStatus.FAILED or status == 'FAILED':
            return FluentIcon.CLOSE
        elif status == TaskStatus.RUNNING or status == 'RUNNING':
            return FluentIcon.SYNC
        elif status == TaskStatus.PENDING or status == 'PENDING':
            return FluentIcon.HISTORY
        else:
            return FluentIcon.INFO
    
    def _get_status_text(self, status) -> str:
        """根据任务状态返回显示文本"""
        status_map = {
            TaskStatus.SUCCEEDED: "成功",
            TaskStatus.FAILED: "失败",
            TaskStatus.RUNNING: "运行中",
            TaskStatus.PENDING: "等待中",
        }
        # 如果是字符串，尝试转换为枚举
        if isinstance(status, str):
            str_map = {
                'SUCCEEDED': "成功",
                'FAILED': "失败",
                'RUNNING': "运行中",
                'PENDING': "等待中",
            }
            return str_map.get(status, status)
        return status_map.get(status, status.value if hasattr(status, 'value') else str(status))
    
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
            
            # 状态图标和文字
            status_icon = self._get_status_icon(task.status)
            status_text = self._get_status_text(task.status)
            
            # 创建状态单元格 - 使用 ToolButton 显示图标
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(8, 4, 8, 4)
            status_layout.setSpacing(6)
            
            status_btn = ToolButton(status_icon)
            status_btn.setFixedSize(24, 24)
            status_btn.setEnabled(False)  # 仅作为图标显示
            status_layout.addWidget(status_btn)
            
            from qfluentwidgets import BodyLabel
            status_label = BodyLabel(status_text)
            status_layout.addWidget(status_label)
            status_layout.addStretch()
            
            self.table.setCellWidget(row, 0, status_widget)
            
            # 任务ID
            id_item = QTableWidgetItem(task.id[:8] + '...')
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, id_item)
            
            # 提示词
            prompt_text = task.prompt[:30] + '...' if len(task.prompt) > 30 else task.prompt
            prompt_item = QTableWidgetItem(prompt_text)
            prompt_item.setToolTip(task.prompt)  # 完整提示词作为 tooltip
            self.table.setItem(row, 2, prompt_item)
            
            # 模型
            model_item = QTableWidgetItem(task.model)
            model_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, model_item)
            
            # 分辨率
            resolution_item = QTableWidgetItem(task.resolution)
            resolution_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, resolution_item)
            
            # 创建时间
            try:
                created_time = datetime.fromisoformat(task.created_at)
                time_str = created_time.strftime('%Y-%m-%d %H:%M')
            except:
                time_str = task.created_at[:16]
            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, time_item)
        
        # 调整行高
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 44)
    
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
