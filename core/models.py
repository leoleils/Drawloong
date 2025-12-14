#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@dataclass
class Task:
    """任务数据模型"""
    id: str
    prompt: str
    model: str
    resolution: str
    created_at: str
    status: TaskStatus = TaskStatus.PENDING
    async_task_id: Optional[str] = None
    negative_prompt: str = ""
    prompt_extend: bool = True
    input_file: Optional[str] = None
    output_path: Optional[str] = None
    video_url: Optional[str] = None
    message: str = ""
    error: Optional[str] = None
    error_code: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self):
        """转换为字典"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建任务对象"""
        # 转换状态
        if 'status' in data:
            if isinstance(data['status'], str):
                data['status'] = TaskStatus(data['status'])
        return cls(**data)
    
    def is_completed(self):
        """判断任务是否完成"""
        return self.status in [TaskStatus.SUCCEEDED, TaskStatus.FAILED]
    
    def is_success(self):
        """判断任务是否成功"""
        return self.status == TaskStatus.SUCCEEDED
