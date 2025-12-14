#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅助函数
"""

from datetime import datetime
from typing import Optional


def format_datetime(dt_str: str, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """格式化日期时间字符串"""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime(fmt)
    except:
        return dt_str


def truncate_string(s: str, max_length: int = 50, suffix: str = '...') -> str:
    """截断字符串"""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def validate_prompt(prompt: str) -> tuple[bool, Optional[str]]:
    """验证提示词"""
    if not prompt or not prompt.strip():
        return False, "提示词不能为空"
    
    if len(prompt) > 1000:
        return False, "提示词过长（最多1000字符）"
    
    return True, None
