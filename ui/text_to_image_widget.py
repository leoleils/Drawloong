#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文生图组件
支持通过文字描述生成图片
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QComboBox, QCheckBox, QPushButton,
    QGroupBox, QSplitter, QScrollArea, QMessageBox,
    QGridLayout, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap


class TextToImageWorker(QThread):
    """文生图工作线程（异步模式）"""
    
    finished = pyqtSignal(str, str, dict)  # image_url, output_path, prompt_info
    error = pyqtSignal(str)  # error_message
    progress = pyqtSignal(str)  # status_message
    
    def __init__(self, api_client, prompt, model, size, negative_prompt, prompt_extend, seed, output_folder):
        super().__init__()
        self.api_client = api_client
        self.prompt = prompt
        self.model = model
        self.size = size
        self.negative_prompt = negative_prompt
        self.prompt_extend = prompt_extend
        self.seed = seed  # 随机种子（None表示随机）
        self.output_folder = output_folder
        self.user_negative_prompt = negative_prompt  # 保存用户输入的反向提示词
    
    def run(self):
        """执行文生图任务（异步）"""
        try:
            import requests
            import json
            import time
            from datetime import datetime
            
            # 1. 提交异步任务
            self.progress.emit("正在提交生成任务...")
            task_id = self.submit_task()
            if not task_id:
                return
            
            # 2. 轮询任务状态
            self.progress.emit(f"任务已提交，ID: {task_id}\n正在生成图片...")
            result = self.poll_task_status(task_id)
            if not result:
                return
            
            image_url = result.get('url')
            orig_prompt = result.get('orig_prompt', '')
            actual_prompt = result.get('actual_prompt', '')
            seed = result.get('seed', '')  # 获取实际使用的seed
            
            # 3. 下载图片
            self.progress.emit("正在下载图片...")
            output_path = self.download_image(image_url)
            if output_path:
                # 构建提示词信息（包括模型、反向提示词、seed）
                prompt_info = {
                    'model': self.model,
                    'size': self.size,
                    'orig_prompt': orig_prompt,
                    'actual_prompt': actual_prompt,
                    'negative_prompt': self.user_negative_prompt,
                    'seed': seed  # 添加seed信息
                }
                self.finished.emit(image_url, output_path, prompt_info)
            
        except Exception as e:
            self.error.emit(f"生成失败: {str(e)}")
    
    def submit_task(self):
        """提交异步生成任务"""
        try:
            import requests
            
            # 所有模型都使用text2image接口（包括万相2.6）
            url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_client.api_key}',
                'X-DashScope-Async': 'enable'
            }
            
            # 判断是否为万相模型（以wan开头）
            is_wanxiang = self.model.startswith('wan')
            
            if is_wanxiang:
                # 万相模型的API格式（包括2.6）
                data = {
                    "model": self.model,
                    "input": {
                        "prompt": self.prompt
                    },
                    "parameters": {
                        "size": self.size,
                        "n": 1,
                        "prompt_extend": self.prompt_extend
                    }
                }
                
                # 万相模型：negative_prompt 在 input 中
                if self.negative_prompt:
                    data["input"]["negative_prompt"] = self.negative_prompt
                
                # 添加seed参数（如果指定）
                if self.seed is not None:
                    data["parameters"]["seed"] = self.seed
            else:
                # 通义千问模型的API格式
                data = {
                    "model": self.model,
                    "input": {
                        "prompt": self.prompt
                    },
                    "parameters": {
                        "size": self.size,
                        "n": 1,
                        "prompt_extend": self.prompt_extend,
                        "watermark": False
                    }
                }
                
                # 通义千问模型：negative_prompt 在 parameters 中
                if self.negative_prompt:
                    data["parameters"]["negative_prompt"] = self.negative_prompt
                
                # 添加seed参数（如果指定）
                if self.seed is not None:
                    data["parameters"]["seed"] = self.seed
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            result = response.json()
            
            # 检查错误
            if 'code' in result:
                error_msg = result.get('message', 'Unknown error')
                self.error.emit(f"提交任务失败: {error_msg}")
                return None
            
            # 获取任务ID
            if 'output' in result and 'task_id' in result['output']:
                return result['output']['task_id']
            else:
                self.error.emit("未能获取任务ID")
                return None
                
        except Exception as e:
            self.error.emit(f"提交任务异常: {str(e)}")
            return None
    
    def poll_task_status(self, task_id):
        """轮询任务状态直到完成"""
        try:
            import requests
            import time
            
            url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}'
            headers = {
                'Authorization': f'Bearer {self.api_client.api_key}'
            }
            
            max_retries = 60  # 最多等待60次（约2分钟）
            retry_count = 0
            
            while retry_count < max_retries:
                response = requests.get(url, headers=headers, timeout=30)
                result = response.json()
                
                # 检查错误
                if 'code' in result:
                    error_msg = result.get('message', 'Unknown error')
                    self.error.emit(f"查询任务失败: {error_msg}")
                    return None
                
                if 'output' in result:
                    task_status = result['output'].get('task_status', '')
                    
                    if task_status == 'SUCCEEDED':
                        # 任务成功，获取图片URL和提示词
                        results = result['output'].get('results', [])
                        if results and len(results) > 0:
                            result_data = results[0]
                            image_url = result_data.get('url', '')
                            if image_url:
                                # 返回包含提示词信息的字典
                                return {
                                    'url': image_url,
                                    'orig_prompt': result_data.get('orig_prompt', ''),
                                    'actual_prompt': result_data.get('actual_prompt', ''),
                                    'seed': result_data.get('seed', '')  # 添加seed
                                }
                            else:
                                self.error.emit("任务成功但未获取到图片URL")
                                return None
                        else:
                            self.error.emit("任务成功但结果为空")
                            return None
                    
                    elif task_status == 'FAILED':
                        # 任务失败
                        error_code = result['output'].get('code', '')
                        error_msg = result['output'].get('message', '未知错误')
                        
                        # 友好化错误信息
                        friendly_msg = self.get_friendly_error_message(error_code, error_msg)
                        self.error.emit(friendly_msg)
                        return None
                    
                    elif task_status in ['PENDING', 'RUNNING']:
                        # 任务进行中，继续等待
                        retry_count += 1
                        time.sleep(2)  # 等待2秒后重试
                        continue
                    
                    else:
                        # 未知状态
                        self.error.emit(f"未知任务状态: {task_status}")
                        return None
                else:
                    self.error.emit("查询响应格式错误")
                    return None
            
            # 超时
            self.error.emit("任务超时，请稍后重试")
            return None
            
        except Exception as e:
            self.error.emit(f"查询任务异常: {str(e)}")
            return None
    
    def get_friendly_error_message(self, error_code, error_msg):
        """将错误代码转换为友好的提示信息"""
        # 常见错误的友好提示
        error_tips = {
            'InternalError.Algo': {
                'keyword': 'IP infringement',
                'message': '提示词可能涉及知识产权侵权内容，请修改后重试。\n\n建议：\n- 避免使用特定品牌、明星、动漫角色名称\n- 使用通用描述代替具体名称\n- 描述风格、特征而非具体对象'
            },
            'InternalError.Timeout': {
                'keyword': 'timeout',
                'message': '生成超时，请稍后重试。\n\n可能原因：\n- 服务器负载较高\n- 网络不稳定\n- 提示词过于复杂'
            },
            'InvalidParameter': {
                'keyword': '',
                'message': '参数错误，请检查配置。\n\n建议检查：\n- 图片尺寸是否符合模型约束\n- 提示词是否为空\n- 其他参数设置'
            },
            'InternalError': {
                'keyword': '',
                'message': '服务器内部错误，请稍后重试。\n\n如持续出现，请联系技术支持。'
            }
        }
        
        # 匹配错误类型
        for err_type, tip_info in error_tips.items():
            if error_code.startswith(err_type):
                # 检查是否需要匹配关键词
                if tip_info['keyword']:
                    if tip_info['keyword'].lower() in error_msg.lower():
                        return f"❌ {tip_info['message']}"
                else:
                    return f"❌ {tip_info['message']}"
        
        # 默认错误信息
        return f"❌ 生成失败: [{error_code}]\n{error_msg}\n\n请检查提示词或稍后重试。"
    
    def download_image(self, image_url):
        """下载生成的图片"""
        try:
            import requests
            from datetime import datetime
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"text2img_{timestamp}.png"
            output_path = os.path.join(self.output_folder, filename)
            
            img_response = requests.get(image_url, timeout=30)
            with open(output_path, 'wb') as f:
                f.write(img_response.content)
            
            return output_path
            
        except Exception as e:
            self.error.emit(f"下载图片失败: {str(e)}")
            return None


class ImageGalleryWidget(QWidget):
    """图片画廊组件"""
    
    image_clicked = pyqtSignal(str)  # image_path
    
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.images = []  # 存储字典：{'path': str, 'model': str, 'size': str, 'seed': str, 'orig_prompt': str, 'actual_prompt': str, 'negative_prompt': str}
        self.history_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'text2image_history.json')  # 默认全局历史文件
        self.setup_ui()
        self.load_history()  # 加载历史记录
    
    def set_project_context(self, project):
        """设置工程上下文，更新历史记录文件路径"""
        if project and hasattr(project, 'path'):
            # 将历史记录文件保存到工程文件夹中
            self.history_file = os.path.join(project.path, 'text2image_history.json')
            self.load_history()  # 重新加载该工程的历史记录
        else:
            # 没有工程时使用默认全局历史文件
            self.history_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'text2image_history.json')
            self.load_history()  # 加载全局历史记录
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #f5f5f5;
            }
        """)
        
        # 画廊容器
        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.gallery_layout.setSpacing(10)
        self.gallery_layout.setContentsMargins(10, 10, 10, 10)
        
        # 空状态提示
        self.empty_label = QLabel("👤 暂无生成的图片")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 18px;
                padding: 50px;
            }
        """)
        self.gallery_layout.addWidget(self.empty_label, 0, 0, Qt.AlignCenter)
        
        scroll.setWidget(self.gallery_widget)
        layout.addWidget(scroll)
    
    def add_image(self, image_path, model='', size='', seed='', orig_prompt='', actual_prompt='', negative_prompt=''):
        """添加图片到画廊"""
        if not os.path.exists(image_path):
            return
        
        # 存储图片和提示词信息
        image_info = {
            'path': image_path,
            'model': model,
            'size': size,
            'seed': seed,
            'orig_prompt': orig_prompt,
            'actual_prompt': actual_prompt,
            'negative_prompt': negative_prompt
        }
        self.images.insert(0, image_info)  # 新图片添加到开头
        self.save_history()  # 保存历史记录
        self.refresh_gallery()
    
    def refresh_gallery(self):
        """刷新画廊显示"""
        # 清空现有布局（但不删除empty_label）
        while self.gallery_layout.count():
            item = self.gallery_layout.takeAt(0)
            widget = item.widget()
            if widget and widget != self.empty_label:
                widget.deleteLater()
        
        if not self.images:
            # 显示空状态
            self.empty_label.show()
            self.gallery_layout.addWidget(self.empty_label, 0, 0, Qt.AlignCenter)
            return
        
        # 隐藏空状态
        self.empty_label.hide()
        
        # 每行3张图片
        columns = 3
        for i, image_info in enumerate(self.images):
            row = i // columns
            col = i % columns
            
            # 创建图片卡片
            card = self.create_image_card(
                image_info['path'],
                image_info.get('model', ''),
                image_info.get('size', ''),
                image_info.get('seed', ''),
                image_info.get('orig_prompt', ''),
                image_info.get('actual_prompt', ''),
                image_info.get('negative_prompt', '')
            )
            self.gallery_layout.addWidget(card, row, col)
    
    def create_image_card(self, image_path, model='', size='', seed='', orig_prompt='', actual_prompt='', negative_prompt=''):
        """创建图片卡片 - 整合布局"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QWidget:hover {
                border: 1px solid #999;
            }
        """)
        card.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # 图片标签
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # 缩放到固定大小
            scaled_pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("border: none;")
        
        layout.addWidget(image_label)
        
        # 文件名
        filename = os.path.basename(image_path)
        name_label = QLabel(filename)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("""
            color: #999; 
            font-size: 10px;
            border: none;
        """)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # 分隔线
        separator = QLabel()
        separator.setStyleSheet("""
            background: #e0e0e0;
            min-height: 1px;
            max-height: 1px;
            border: none;
        """)
        layout.addWidget(separator)
        
        # 任务信息区域
        info_widget = QWidget()
        info_widget.setStyleSheet("border: none;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        # 模型信息
        if model:
            model_label = QLabel(f"🦾 模型：{model}")
            model_label.setStyleSheet("""
                color: #333;
                font-size: 10px;
                font-weight: bold;
                border: none;
            """)
            info_layout.addWidget(model_label)
        
        # 尺寸信息
        if size:
            size_label = QLabel(f"📏 尺寸：{size}")
            size_label.setStyleSheet("""
                color: #666;
                font-size: 10px;
                border: none;
            """)
            info_layout.addWidget(size_label)
        
        # Seed信息
        if seed:
            seed_label = QLabel(f"🎲 Seed：{seed}")
            seed_label.setStyleSheet("""
                color: #666;
                font-size: 10px;
                border: none;
            """)
            seed_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 允许选择复制
            info_layout.addWidget(seed_label)
        
        # 原始提示词
        if orig_prompt:
            orig_title = QLabel("📝 原始提示词：")
            orig_title.setStyleSheet("""
                color: #666;
                font-size: 10px;
                font-weight: bold;
                margin-top: 2px;
                border: none;
            """)
            info_layout.addWidget(orig_title)
            
            orig_text = QLabel(orig_prompt)
            orig_text.setStyleSheet("""
                color: #555;
                font-size: 10px;
                padding: 4px;
                background: #f8f9fa;
                border-radius: 3px;
                border: none;
            """)
            orig_text.setWordWrap(True)
            orig_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
            info_layout.addWidget(orig_text)
        
        # 反向提示词
        if negative_prompt:
            neg_title = QLabel("⛔ 反向提示词：")
            neg_title.setStyleSheet("""
                color: #dc3545;
                font-size: 10px;
                font-weight: bold;
                margin-top: 2px;
                border: none;
            """)
            info_layout.addWidget(neg_title)
            
            neg_text = QLabel(negative_prompt)
            neg_text.setStyleSheet("""
                color: #dc3545;
                font-size: 10px;
                padding: 4px;
                background: #fff5f5;
                border-radius: 3px;
                border: none;
            """)
            neg_text.setWordWrap(True)
            neg_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
            info_layout.addWidget(neg_text)
        
        # 改写提示词
        if actual_prompt:
            actual_title = QLabel("✨ 改写提示词：")
            actual_title.setStyleSheet("""
                color: #28a745;
                font-size: 10px;
                font-weight: bold;
                margin-top: 2px;
                border: none;
            """)
            info_layout.addWidget(actual_title)
            
            actual_text = QLabel(actual_prompt)
            actual_text.setStyleSheet("""
                color: #28a745;
                font-size: 10px;
                padding: 4px;
                background: #f0fff4;
                border-radius: 3px;
                border: none;
            """)
            actual_text.setWordWrap(True)
            actual_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
            info_layout.addWidget(actual_text)
        
        layout.addWidget(info_widget)
        
        # 点击事件 - 只在图片区域设置，避免干扰文本选择
        def on_image_click(event):
            # 只处理左键点击
            if event.button() == Qt.LeftButton:
                self.image_clicked.emit(image_path)
        
        image_label.mousePressEvent = on_image_click
        
        return card
    
    def clear(self):
        """清空画廊"""
        self.images.clear()
        self.save_history()  # 保存更新
        self.refresh_gallery()
    
    def save_history(self):
        """保存历史记录到JSON文件"""
        try:
            import json
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            # 只保存存在的图片
            valid_images = []
            for img_info in self.images:
                if os.path.exists(img_info['path']):
                    valid_images.append(img_info)
            
            # 保存到文件
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(valid_images, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def load_history(self):
        """从 JSON 文件加载历史记录"""
        try:
            import json
            
            if not os.path.exists(self.history_file):
                return
            
            # 读取文件
            with open(self.history_file, 'r', encoding='utf-8') as f:
                loaded_images = json.load(f)
            
            # 只加载存在的图片
            self.images = []
            for img_info in loaded_images:
                if os.path.exists(img_info.get('path', '')):
                    self.images.append(img_info)
            
            # 刷新显示
            self.refresh_gallery()
            
        except Exception as e:
            print(f"加载历史记录失败: {e}")


class TextToImageWidget(QWidget):
    """文生图主组件"""
    
    # 模型配置（包含分辨率约束）
    MODEL_CONFIG = {
        'wan2.6-t2i': {
            'name': '🌟 万相2.6（最新）',
            'default_size': '1280*1280',
            'description': '最新模型，总像素[768², 1440²]，宽高比[1:4, 4:1]，PNG格式',
            'size_type': 'flexible',  # 灵活分辨率
            'presets': [
                '1:1 (1280*1280)',
                '1:1 (1024*1024)',
                '16:9 (1440*810)',
                '9:16 (810*1440)',
                '4:3 (1248*936)',
                '3:4 (936*1248)',
                '2:1 (1440*720)',
                '1:2 (720*1440)'
            ]
        },
        'wan2.5-t2i-preview': {
            'name': '万相2.5 Preview',
            'default_size': '1280*1280',
            'description': '支持灵活分辨率，总像素[768², 1440²]，宽高比[1:4, 4:1]',
            'size_type': 'flexible',  # 灵活分辨率
            'presets': [
                '1:1 (1280*1280)',
                '1:1 (1024*1024)',
                '16:9 (1440*810)',
                '9:16 (810*1440)',
                '4:3 (1248*936)',
                '3:4 (936*1248)',
                '2:1 (1440*720)',
                '1:2 (720*1440)'
            ]
        },
        'wan2.2-t2i-flash': {
            'name': '万相2.2 极速版（推荐）',
            'default_size': '1024*1024',
            'description': '图像宽高[512, 1440]，最大分辨率1440*1440',
            'size_type': 'fixed',  # 固定分辨率
            'presets': [
                '1:1 (1024*1024)',
                '1:1 (1440*1440)',
                '16:9 (1440*810)',
                '9:16 (810*1440)',
                '4:3 (1248*936)',
                '3:4 (936*1248)',
                '2:1 (1440*720)',
                '1:2 (720*1440)'
            ]
        },
        'wan2.2-t2i-plus': {
            'name': '万相2.2 专业版（推荐）',
            'default_size': '1024*1024',
            'description': '图像宽高[512, 1440]，最大分辨率1440*1440',
            'size_type': 'fixed',
            'presets': [
                '1:1 (1024*1024)',
                '1:1 (1440*1440)',
                '16:9 (1440*810)',
                '9:16 (810*1440)',
                '4:3 (1248*936)',
                '3:4 (936*1248)',
                '2:1 (1440*720)',
                '1:2 (720*1440)'
            ]
        },
        'qwen-image-plus': {
            'name': '通义千问Plus',
            'default_size': '1328*1328',
            'description': '支持65种预设分辨率',
            'size_type': 'preset',  # 预设分辨率
            'presets': [
                '1:1 (1328*1328)',
                '16:9 (1664*928)',
                '4:3 (1472*1140)',
                '3:4 (1140*1472)',
                '9:16 (928*1664)'
            ]
        },
        'qwen-image': {
            'name': '通义千问标准版',
            'default_size': '1328*1328',
            'description': '支持65种预设分辨率',
            'size_type': 'preset',
            'presets': [
                '1:1 (1328*1328)',
                '16:9 (1664*928)',
                '4:3 (1472*1140)',
                '3:4 (1140*1472)',
                '9:16 (928*1664)'
            ]
        }
    }
    
    def __init__(self, api_client, project_manager, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.project_manager = project_manager
        self.workers = []  # 存储多个工作线程
        self.completed_count = 0  # 完成数量
        self.total_count = 0  # 总数量
        self.setup_ui()
        
        # 监听工程变化事件
        self.project_manager.project_changed.connect(self.on_project_changed)
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 水平分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：配置面板
        config_widget = self.create_config_panel()
        splitter.addWidget(config_widget)
        
        # 右侧：图片画廊
        self.gallery = ImageGalleryWidget(self.project_manager)
        self.gallery.image_clicked.connect(self.on_image_clicked)
        splitter.addWidget(self.gallery)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # 初始化工程上下文
        self.on_project_changed()
    
    def create_config_panel(self):
        """创建配置面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group_box = QGroupBox("文生图配置")
        group_layout = QVBoxLayout(group_box)
        
        # 提示词
        prompt_label = QLabel("描述文本:")
        prompt_label.setStyleSheet("font-weight: bold;")
        group_layout.addWidget(prompt_label)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("描述你想要生成的图片内容...\n例如：一副典雅庄重的对联悬挂于厅堂之中...")
        self.prompt_edit.setMinimumHeight(150)
        group_layout.addWidget(self.prompt_edit)
        
        # 反向提示词
        neg_prompt_label = QLabel("反向提示词:")
        neg_prompt_label.setStyleSheet("font-weight: bold;")
        group_layout.addWidget(neg_prompt_label)
        
        self.neg_prompt_edit = QTextEdit()
        self.neg_prompt_edit.setPlaceholderText("描述不希望出现的内容...")
        self.neg_prompt_edit.setMaximumHeight(80)
        group_layout.addWidget(self.neg_prompt_edit)
        
        # 模型选择
        model_label = QLabel("模型:")
        model_label.setStyleSheet("font-weight: bold;")
        group_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        # 万相模型（推荐）
        self.model_combo.addItem("🌟 万相2.6（最新）", "wan2.6-t2i")
        self.model_combo.addItem("万相2.5 Preview", "wan2.5-t2i-preview")
        self.model_combo.addItem("万相2.2 极速版", "wan2.2-t2i-flash")
        self.model_combo.addItem("万相2.2 专业版", "wan2.2-t2i-plus")
        # 通义千问模型
        self.model_combo.addItem("通义千问Plus", "qwen-image-plus")
        self.model_combo.addItem("通义千问标准版", "qwen-image")
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        group_layout.addWidget(self.model_combo)
        
        # 模型说明
        self.model_desc_label = QLabel("")
        self.model_desc_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                padding: 5px;
                background: #f8f9fa;
                border-radius: 3px;
            }
        """)
        self.model_desc_label.setWordWrap(True)
        group_layout.addWidget(self.model_desc_label)
        
        # 尺寸选择
        size_label = QLabel("图片尺寸:")
        size_label.setStyleSheet("font-weight: bold;")
        group_layout.addWidget(size_label)
        
        self.size_combo = QComboBox()
        group_layout.addWidget(self.size_combo)
        
        # 初始化默认模型的尺寸选项
        self.on_model_changed(0)
        
        # Seed设置
        seed_layout = QHBoxLayout()
        seed_label = QLabel("Seed (空表示随机):")
        seed_label.setStyleSheet("font-weight: bold;")
        seed_layout.addWidget(seed_label)
        
        from PyQt5.QtWidgets import QLineEdit
        from PyQt5.QtGui import QRegExpValidator
        from PyQt5.QtCore import QRegExp
        self.seed_edit = QLineEdit()
        self.seed_edit.setPlaceholderText("留空随机生成，或输入正整数")
        # 使用正则验证，只允许数字
        self.seed_edit.setValidator(QRegExpValidator(QRegExp("[0-9]*")))
        seed_layout.addWidget(self.seed_edit)
        group_layout.addLayout(seed_layout)
        
        # 智能改写选项
        self.prompt_extend_check = QCheckBox("启用提示词智能改写")
        self.prompt_extend_check.setChecked(True)
        group_layout.addWidget(self.prompt_extend_check)
        
        # 批量生成数量
        batch_layout = QHBoxLayout()
        batch_label = QLabel("生成数量:")
        batch_label.setStyleSheet("font-weight: bold;")
        batch_layout.addWidget(batch_label)
        
        self.batch_spin = QSpinBox()
        self.batch_spin.setMinimum(1)
        self.batch_spin.setMaximum(4)  # 最多4个
        self.batch_spin.setValue(1)
        self.batch_spin.setToolTip("一次最多生成4张图片")
        batch_layout.addWidget(self.batch_spin)
        batch_layout.addStretch()
        group_layout.addLayout(batch_layout)
        
        # 生成按钮
        self.generate_btn = QPushButton("生成图片")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.generate_btn.clicked.connect(self.on_generate_clicked)
        group_layout.addWidget(self.generate_btn)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 5px;
            }
        """)
        self.status_label.setWordWrap(True)
        group_layout.addWidget(self.status_label)
        
        layout.addWidget(group_box)
        layout.addStretch()
        
        return widget
    
    def on_model_changed(self, index):
        """模型改变事件 - 更新尺寸选项"""
        model_key = self.model_combo.itemData(index)
        if not model_key:
            return
        
        model_config = self.MODEL_CONFIG.get(model_key, {})
        
        # 更新模型说明
        description = model_config.get('description', '')
        self.model_desc_label.setText(description)
        
        # 保存当前选择的尺寸
        current_size = None
        if self.size_combo.currentIndex() >= 0:
            current_size = self.size_combo.currentData()
        
        # 更新尺寸选项
        self.size_combo.clear()
        presets = model_config.get('presets', [])
        for preset in presets:
            # 从 preset 中提取实际尺寸值
            # 格式: '1:1 (1280*1280)' -> '1280*1280'
            size_value = preset.split('(')[1].rstrip(')')
            self.size_combo.addItem(preset, size_value)
        
        # 尝试恢复之前的选择
        if current_size:
            for i in range(self.size_combo.count()):
                if self.size_combo.itemData(i) == current_size:
                    self.size_combo.setCurrentIndex(i)
                    return
        
        # 如果没有找到匹配的，选择默认值
        default_size = model_config.get('default_size', '')
        for i in range(self.size_combo.count()):
            if self.size_combo.itemData(i) == default_size:
                self.size_combo.setCurrentIndex(i)
                return
    
    def on_generate_clicked(self):
        """生成按钮点击"""
        # 验证提示词
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "提示", "请输入描述文本")
            return
        
        # 检查是否有工程
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "提示", "请先创建或打开工程")
            return
        
        # 获取配置
        model = self.model_combo.currentData()
        size = self.size_combo.currentData()
        negative_prompt = self.neg_prompt_edit.toPlainText().strip()
        prompt_extend = self.prompt_extend_check.isChecked()
        batch_count = self.batch_spin.value()  # 批量数量
        
        # 获取seed（空表示随机）
        seed_text = self.seed_edit.text().strip()
        base_seed = int(seed_text) if seed_text else None
        
        # 获取输出文件夹
        project = self.project_manager.get_current_project()
        output_folder = project.inputs_folder  # 生成的图片保存到inputs
        
        # 禁用按钮
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText(f"生成中 (0/{batch_count})...")
        
        # 初始化批量生成状态
        self.workers = []
        self.completed_count = 0
        self.total_count = batch_count
        
        # 创建多个工作线程
        for i in range(batch_count):
            # 如果指定了seed，每个任务递增seed值
            task_seed = base_seed + i if base_seed is not None else None
            
            worker = TextToImageWorker(
                self.api_client,
                prompt,
                model,
                size,
                negative_prompt,
                prompt_extend,
                task_seed,
                output_folder
            )
            worker.finished.connect(self.on_generation_finished)
            worker.error.connect(self.on_generation_error)
            worker.progress.connect(self.on_generation_progress)
            self.workers.append(worker)
            worker.start()
        
        # 更新状态
        self.status_label.setText(f"正在批量生成 {batch_count} 张图片...")
    
    def on_generation_finished(self, image_url, output_path, prompt_info):
        """生成完成"""
        # 批量任务计数
        self.completed_count += 1
        
        # 添加到画廊（带完整信息）
        self.gallery.add_image(
            output_path,
            prompt_info.get('model', ''),
            prompt_info.get('size', ''),
            prompt_info.get('seed', ''),
            prompt_info.get('orig_prompt', ''),
            prompt_info.get('actual_prompt', ''),
            prompt_info.get('negative_prompt', '')
        )
        
        # 更新进度
        if self.total_count > 1:
            self.generate_btn.setText(f"生成中 ({self.completed_count}/{self.total_count})...")
            self.status_label.setText(f"✅ 已完成 {self.completed_count}/{self.total_count} 张")
        
        # 全部完成
        if self.completed_count >= self.total_count:
            self.generate_btn.setEnabled(True)
            self.generate_btn.setText("生成图片")
            self.status_label.setText(f"✅ 批量生成成功！共 {self.total_count} 张")
            
            # 刷新资源管理器
            main_window = self.window()
            if hasattr(main_window, 'project_explorer'):
                main_window.project_explorer.refresh()
            
            # 只有单张时显示弹窗，批量生成不弹窗避免频繁打扰
            if self.total_count == 1:
                QMessageBox.information(self, "成功", f"图片已生成并保存到:\n{output_path}")
    
    def on_generation_error(self, error_msg):
        """生成错误"""
        # 批量任务计数(错误也算完成)
        self.completed_count += 1
        
        # 更新进度
        if self.total_count > 1:
            self.generate_btn.setText(f"生成中 ({self.completed_count}/{self.total_count})...")
            self.status_label.setText(f"⚠️ {self.completed_count}/{self.total_count} - 部分失败")
        else:
            self.status_label.setText(f"❌ {error_msg}")
        
        # 全部完成
        if self.completed_count >= self.total_count:
            self.generate_btn.setEnabled(True)
            self.generate_btn.setText("生成图片")
            
            # 刷新资源管理器
            main_window = self.window()
            if hasattr(main_window, 'project_explorer'):
                main_window.project_explorer.refresh()
        
        # 只有单张或批量全部失败时显示错误弹窗
        if self.total_count == 1:
            QMessageBox.critical(self, "错误", error_msg)
    
    def on_generation_progress(self, status_msg):
        """生成进度更新"""
        self.status_label.setText(status_msg)
    
    def on_image_clicked(self, image_path):
        """图片点击事件"""
        # 打开图片查看器
        from .image_viewer import ImageViewer
        viewer = ImageViewer(image_path, self)
        viewer.exec_()
    
    def on_project_changed(self):
        """工程变化事件 - 更新画廊上下文"""
        project = self.project_manager.get_current_project()
        self.gallery.set_project_context(project)
