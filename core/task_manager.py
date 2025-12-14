#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理器
负责任务的创建、存储、查询和状态更新
"""

import json
import os
import uuid
from typing import List, Optional
from datetime import datetime
from .models import Task, TaskStatus
from config.settings import settings


class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        """初始化任务管理器"""
        self.tasks = {}
        self.tasks_file = settings.TASKS_FILE
        self.load_tasks()
    
    def create_task(self, prompt: str, model: str, resolution: str,
                   negative_prompt: str = "", prompt_extend: bool = True,
                   input_file: str = "") -> Task:
        """
        创建新任务
        
        Args:
            prompt: 提示词
            model: 模型名称
            resolution: 分辨率
            negative_prompt: 反向提示词
            prompt_extend: 是否启用智能改写
            input_file: 输入文件路径
            
        Returns:
            创建的任务对象
        """
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            prompt=prompt,
            model=model,
            resolution=resolution,
            negative_prompt=negative_prompt,
            prompt_extend=prompt_extend,
            input_file=input_file,
            created_at=datetime.now().isoformat()
        )
        
        self.tasks[task_id] = task
        self.save_tasks()
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        return list(self.tasks.values())
    
    def update_task(self, task_id: str, **kwargs):
        """
        更新任务信息
        
        Args:
            task_id: 任务 ID
            **kwargs: 要更新的字段
        """
        task = self.tasks.get(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self.save_tasks()
    
    def save_tasks(self):
        """保存任务到文件"""
        try:
            serializable_tasks = {
                task_id: task.to_dict() 
                for task_id, task in self.tasks.items()
            }
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务失败: {e}")
    
    def load_tasks(self):
        """从文件加载任务"""
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = {
                        task_id: Task.from_dict(task_data)
                        for task_id, task_data in data.items()
                    }
            else:
                self.tasks = {}
        except Exception as e:
            print(f"加载任务失败: {e}")
            self.tasks = {}
    
    def get_pending_tasks(self) -> List[Task]:
        """获取未完成的任务"""
        return [
            task for task in self.tasks.values()
            if not task.is_completed()
        ]
