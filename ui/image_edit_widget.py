#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像编辑组件
支持单图编辑和多图融合
"""

import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QComboBox, QPushButton, QGroupBox,
    QSplitter, QScrollArea, QMessageBox, QGridLayout,
    QSpinBox, QListWidget, QListWidgetItem, QFileDialog, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent

try:
    from qfluentwidgets import (
        PushButton, PrimaryPushButton, FluentIcon,
        ComboBox, SwitchButton, BodyLabel, SpinBox,
        TextEdit, TransparentToolButton, ToolButton
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False


class ImageEditWorker(QThread):
    """图像编辑工作线程"""
    
    finished = pyqtSignal(list, dict)  # image_urls, edit_info
    error = pyqtSignal(str)  # error_message
    progress = pyqtSignal(str)  # status_message
    
    def __init__(self, api_client, images, prompt, model, n, negative_prompt, prompt_extend, output_folder, size="", enable_interleave=False, max_images=5):
        super().__init__()
        self.api_client = api_client
        self.images = images
        self.prompt = prompt
        self.model = model
        self.n = n
        self.negative_prompt = negative_prompt
        self.prompt_extend = prompt_extend
        self.output_folder = output_folder
        self.size = size  # 输出尺寸
        self.enable_interleave = enable_interleave  # 图文混合模式
        self.max_images = max_images  # 最大图片数量
    
    def run(self):
        """执行图像编辑任务"""
        try:
            import requests
            import time
            
            # 判断是否为万相模型（异步模式）
            is_wanxiang = self.model.startswith('wan2.') or self.model == 'wan2.6-image'
            
            if is_wanxiang:
                # 万相2.5/2.6：异步模式
                self._run_async_mode()
            else:
                # 其他模型：同步模式
                self._run_sync_mode()
            
        except Exception as e:
            self.error.emit(f"编辑失败: {str(e)}")
    
    def _run_sync_mode(self):
        """同步模式：通义千问模型"""
        import requests
        
        # 1. 提交编辑任务
        self.progress.emit("正在提交编辑任务...")
        result = self.api_client.submit_image_edit(
            images=self.images,
            prompt=self.prompt,
            model=self.model,
            n=self.n,
            negative_prompt=self.negative_prompt,
            prompt_extend=self.prompt_extend,
            size=self.size,
            enable_interleave=self.enable_interleave,
            max_images=self.max_images
        )
        
        # 2. 检查响应
        if 'code' in result:
            error_msg = result.get('message', 'Unknown error')
            self.error.emit(f"编辑失败: {error_msg}")
            return
        
        if 'output' not in result or 'choices' not in result['output']:
            self.error.emit("API响应格式错误")
            return
        
        # 3. 获取生成的图片URL
        choices = result['output']['choices']
        if not choices or not choices[0].get('message', {}).get('content'):
            self.error.emit("未获取到生成的图片")
            return
        
        content = choices[0]['message']['content']
        image_urls = [item['image'] for item in content if 'image' in item]
        
        if not image_urls:
            self.error.emit("未获取到生成的图片")
            return
        
        # 4. 下载图片
        self._download_images(image_urls)
    
    def _run_async_mode(self):
        """异步模式：万相2.5模型"""
        import requests
        import time
        
        # 1. 提交异步任务
        self.progress.emit("正在提交编辑任务...")
        result = self.api_client.submit_image_edit(
            images=self.images,
            prompt=self.prompt,
            model=self.model,
            n=self.n,
            negative_prompt=self.negative_prompt,
            prompt_extend=self.prompt_extend,
            size=self.size,
            enable_interleave=self.enable_interleave,
            max_images=self.max_images
        )
        
        # 2. 检查响应
        if 'code' in result:
            error_msg = result.get('message', 'Unknown error')
            self.error.emit(f"提交任务失败: {error_msg}")
            return
        
        if 'output' not in result or 'task_id' not in result['output']:
            self.error.emit("未能获取任务ID")
            return
        
        task_id = result['output']['task_id']
        self.progress.emit(f"任务已提交，ID: {task_id}\n正在处理...")
        
        # 3. 轮询任务状态
        max_retries = 60  # 最多等待60次（约2分钟）
        retry_count = 0
        
        while retry_count < max_retries:
            time.sleep(2)  # 等待2秒
            
            try:
                task_result = self.api_client.query_image_edit_task(task_id)
                
                if 'code' in task_result:
                    error_msg = task_result.get('message', 'Unknown error')
                    self.error.emit(f"查询任务失败: {error_msg}")
                    return
                
                if 'output' not in task_result:
                    self.error.emit("查询响应格式错误")
                    return
                
                task_status = task_result['output'].get('task_status', '')
                
                if task_status == 'SUCCEEDED':
                    # 任务成功，提取图片URL
                    image_urls = []
                    
                    # 尝试从choices中提取（万相2.6格式）
                    if 'choices' in task_result['output']:
                        choices = task_result['output']['choices']
                        for choice in choices:
                            if 'message' in choice and 'content' in choice['message']:
                                content = choice['message']['content']
                                for item in content:
                                    if 'image' in item:
                                        image_urls.append(item['image'])
                    
                    # 尝试从results中提取（旧格式）
                    elif 'results' in task_result['output']:
                        results = task_result['output']['results']
                        for r in results:
                            if 'url' in r:
                                image_urls.append(r['url'])
                    
                    if image_urls:
                        self._download_images(image_urls)
                        return
                    else:
                        self.error.emit("任务成功但未获取到图片")
                        return
                
                elif task_status == 'FAILED':
                    error_code = task_result['output'].get('code', '')
                    error_msg = task_result['output'].get('message', '未知错误')
                    self.error.emit(f"任务失败: [{error_code}] {error_msg}")
                    return
                
                elif task_status in ['PENDING', 'RUNNING']:
                    retry_count += 1
                    continue
                
                else:
                    self.error.emit(f"未知任务状态: {task_status}")
                    return
                    
            except Exception as e:
                self.error.emit(f"查询任务异常: {str(e)}")
                return
        
        # 超时
        self.error.emit("任务超时，请稍后重试")
    
    def _download_images(self, image_urls):
        """下载图片"""
        import requests
        from datetime import datetime
        
        self.progress.emit(f"正在下载{len(image_urls)}张图片...")
        downloaded_paths = []
        errors = []
        
        for i, url in enumerate(image_urls):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"image_edit_{timestamp}_{i+1}.png"
            output_path = os.path.join(self.output_folder, filename)
            
            try:
                self.progress.emit(f"下载图片 {i+1}/{len(image_urls)}...")
                print(f"正在下载图片: {url}")
                
                img_response = requests.get(url, timeout=30)
                img_response.raise_for_status()  # 检查HTTP错误
                
                with open(output_path, 'wb') as f:
                    f.write(img_response.content)
                
                downloaded_paths.append(output_path)
                print(f"图片{i+1}下载成功: {output_path}")
                
            except Exception as e:
                error_msg = f"图片{i+1}下载失败: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
        
        if not downloaded_paths:
            error_detail = "\n".join(errors) if errors else "未知错误"
            self.error.emit(f"所有图片下载失败:\n{error_detail}")
            return
        
        if errors:
            # 部分成功
            self.progress.emit(f"成功下载{len(downloaded_paths)}/{len(image_urls)}张图片")
        
        # 构建编辑信息
        edit_info = {
            'model': self.model,
            'prompt': self.prompt,
            'negative_prompt': self.negative_prompt,
            'image_count': len(self.images),
            'output_count': len(downloaded_paths)
        }
        
        self.finished.emit(downloaded_paths, edit_info)


class ImageGalleryWidget(QWidget):
    """图片画廊组件"""
    
    image_clicked = pyqtSignal(str)  # image_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.images = []
        self.setup_ui()
    
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
        self.empty_label = QLabel("暂无编辑结果")
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
    
    def add_images(self, image_paths, prompt='', model=''):
        """批量添加图片到画廊"""
        for image_path in image_paths:
            if os.path.exists(image_path):
                image_info = {
                    'path': image_path,
                    'prompt': prompt,
                    'model': model
                }
                self.images.insert(0, image_info)
        self.refresh_gallery()
    
    def refresh_gallery(self):
        """刷新画廊显示"""
        # 清空现有布局
        while self.gallery_layout.count():
            item = self.gallery_layout.takeAt(0)
            widget = item.widget()
            if widget and widget != self.empty_label:
                widget.deleteLater()
        
        if not self.images:
            self.empty_label.show()
            self.gallery_layout.addWidget(self.empty_label, 0, 0, Qt.AlignCenter)
            return
        
        self.empty_label.hide()
        
        # 每行3张图片
        columns = 3
        for i, image_info in enumerate(self.images):
            row = i // columns
            col = i % columns
            
            card = self.create_image_card(
                image_info['path'],
                image_info.get('prompt', ''),
                image_info.get('model', '')
            )
            self.gallery_layout.addWidget(card, row, col)
    
    def create_image_card(self, image_path, prompt='', model=''):
        """创建图片卡片"""
        card = QWidget()
        card.setObjectName("galleryCard")
        card.setStyleSheet("""
            QWidget#galleryCard {
                background: transparent;
                border-radius: 6px;
                border: 1px solid #dee2e6;
            }
            QWidget#galleryCard:hover {
                border: 1px solid #007bff;
            }
        """)
        card.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # 图片标签
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("background: transparent; border: none;")
        
        layout.addWidget(image_label)
        
        # 文件名
        filename = os.path.basename(image_path)
        name_label = QLabel(filename)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("""
            color: #666; 
            font-size: 10px;
            background: transparent;
            border: none;
        """)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # 点击事件
        card.mousePressEvent = lambda e: self.image_clicked.emit(image_path)
        
        return card
    
    def clear(self):
        """清空画廊"""
        self.images.clear()
        self.refresh_gallery()


class ImageEditWidget(QWidget):
    """图像编辑主组件"""
    
    def __init__(self, api_client, project_manager, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.project_manager = project_manager
        self.worker = None
        self.selected_images = []
        self.setup_ui()
        
        # 启用拖拽
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 主分割器 - 左右分割
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：配置面板（窄）
        config_widget = self.create_config_panel()
        main_splitter.addWidget(config_widget)
        
        # 右侧：上下分割（选择图片 + 编辑结果）
        right_splitter = QSplitter(Qt.Vertical)
        
        # 右上：选择的图片预览
        preview_widget = self.create_preview_panel()
        right_splitter.addWidget(preview_widget)
        
        # 右下：生成结果画廊
        self.gallery = ImageGalleryWidget()
        self.gallery.image_clicked.connect(self.on_image_clicked)
        right_splitter.addWidget(self.gallery)
        
        right_splitter.setStretchFactor(0, 2)  # 选择图片占2份
        right_splitter.setStretchFactor(1, 2)  # 编辑结果占2份
        
        main_splitter.addWidget(right_splitter)
        
        # 设置左右比例：配置面板窄，右侧宽
        main_splitter.setStretchFactor(0, 1)  # 配置面板占1份
        main_splitter.setStretchFactor(1, 3)  # 右侧占3份
        
        layout.addWidget(main_splitter)
    
    def create_preview_panel(self):
        """创建图片预览面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        group_box = QGroupBox()
        group_layout = QVBoxLayout(group_box)
        
        # 图片预览区域
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
        """)
        
        self.preview_widget = QWidget()
        self.preview_layout = QGridLayout(self.preview_widget)
        self.preview_layout.setSpacing(8)
        self.preview_layout.setContentsMargins(8, 8, 8, 8)
        
        # 空状态提示
        if FLUENT_AVAILABLE:
            self.empty_preview_label = BodyLabel("暂无选择图片")
        else:
            self.empty_preview_label = QLabel("暂无选择图片")
        self.empty_preview_label.setAlignment(Qt.AlignCenter)
        self.empty_preview_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 14px;
                padding: 30px;
            }
        """)
        self.preview_layout.addWidget(self.empty_preview_label, 0, 0, Qt.AlignCenter)
        
        self.preview_scroll.setWidget(self.preview_widget)
        group_layout.addWidget(self.preview_scroll)
        
        # 图片操作按钮
        btn_layout = QHBoxLayout()
        
        if FLUENT_AVAILABLE:
            self.add_image_btn = PushButton(FluentIcon.ADD, "添加图片")
            self.add_image_btn.setMinimumHeight(36)
        else:
            self.add_image_btn = QPushButton("添加图片")
            self.add_image_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
        self.add_image_btn.clicked.connect(self.add_images)
        btn_layout.addWidget(self.add_image_btn)
        
        if FLUENT_AVAILABLE:
            self.clear_images_btn = PushButton(FluentIcon.DELETE, "清空")
            self.clear_images_btn.setMinimumHeight(36)
        else:
            self.clear_images_btn = QPushButton("清空")
            self.clear_images_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
        self.clear_images_btn.clicked.connect(self.clear_images)
        btn_layout.addWidget(self.clear_images_btn)
        
        group_layout.addLayout(btn_layout)
        
        # 提示信息
        if FLUENT_AVAILABLE:
            self.mode_hint = BodyLabel("单图编辑：选择1张图片")
        else:
            self.mode_hint = QLabel("单图编辑：选择1张图片")
        self.mode_hint.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                padding: 5px;
                background: #f8f9fa;
                border-radius: 3px;
            }
        """)
        self.mode_hint.setWordWrap(True)
        group_layout.addWidget(self.mode_hint)
        
        layout.addWidget(group_box)
        return widget
    
    def create_config_panel(self):
        """创建配置面板 - Fluent风格"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(5, 5, 15, 5)
        
        # 模式选择
        if FLUENT_AVAILABLE:
            mode_label = BodyLabel("编辑模式")
        else:
            mode_label = QLabel("编辑模式:")
            mode_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        scroll_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.setMinimumHeight(36)
        self.mode_combo.addItem("单图编辑", "single")
        self.mode_combo.addItem("多图融合", "multi")
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        scroll_layout.addWidget(self.mode_combo)
        
        # 编辑提示词
        scroll_layout.addSpacing(8)
        if FLUENT_AVAILABLE:
            prompt_label = BodyLabel("编辑描述")
        else:
            prompt_label = QLabel("编辑描述:")
            prompt_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        scroll_layout.addWidget(prompt_label)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("描述想要的编辑效果...\n例如：生成一张符合深度图的图像，一辆红色的破旧的自行车停在一条泥泞的小路上，背景是茂密的原始森林")
        self.prompt_edit.setMinimumHeight(100)
        scroll_layout.addWidget(self.prompt_edit)
        
        # 反向提示词
        scroll_layout.addSpacing(8)
        if FLUENT_AVAILABLE:
            neg_prompt_label = BodyLabel("反向提示词")
        else:
            neg_prompt_label = QLabel("反向提示词:")
            neg_prompt_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        scroll_layout.addWidget(neg_prompt_label)
        
        self.neg_prompt_edit = QTextEdit()
        self.neg_prompt_edit.setPlaceholderText("描述不希望出现的内容...")
        self.neg_prompt_edit.setMaximumHeight(60)
        scroll_layout.addWidget(self.neg_prompt_edit)
        
        # 模型选择
        scroll_layout.addSpacing(15)
        if FLUENT_AVAILABLE:
            model_label = BodyLabel("模型")
        else:
            model_label = QLabel("模型:")
            model_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        scroll_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.setMinimumHeight(36)
        # 万相2.6模型（最新，异步）
        self.model_combo.addItem("万相2.6（最新）", "wan2.6-image")
        # 万相2.5模型（异步）
        self.model_combo.addItem("万相2.5 Preview", "wan2.5-i2i-preview")
        # 通义千问模型（同步）- 推荐新模型
        self.model_combo.addItem("通义千问 Edit Plus（推荐）", "qwen-image-edit-plus")
        self.model_combo.addItem("通义千问 Edit Plus 2025", "qwen-image-edit-plus-2025-10-30")
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        scroll_layout.addWidget(self.model_combo)
        
        # 模型说明
        self.model_desc_label = QLabel("支持单图编辑和多图融合，异步处理")
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
        scroll_layout.addWidget(self.model_desc_label)
        
        # 生成数量
        scroll_layout.addSpacing(8)
        if FLUENT_AVAILABLE:
            n_label = BodyLabel("生成数量")
        else:
            n_label = QLabel("生成数量:")
            n_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        scroll_layout.addWidget(n_label)
        
        if FLUENT_AVAILABLE:
            self.n_spinbox = SpinBox()
        else:
            self.n_spinbox = QSpinBox()
        self.n_spinbox.setMinimum(1)
        self.n_spinbox.setMaximum(6)
        self.n_spinbox.setValue(2)
        self.n_spinbox.setMinimumHeight(36)
        scroll_layout.addWidget(self.n_spinbox)
        
        # 输出尺寸（仅万相2.5/2.6显示）
        scroll_layout.addSpacing(8)
        if FLUENT_AVAILABLE:
            size_label = BodyLabel("输出尺寸")
        else:
            size_label = QLabel("输出尺寸:")
            size_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.size_label = size_label
        scroll_layout.addWidget(size_label)
        
        self.size_combo = QComboBox()
        self.size_combo.setMinimumHeight(36)
        self.size_combo.addItem("默认（不指定）", "")
        self.size_combo.addItem("1:1 (1280×1280)", "1280*1280")
        self.size_combo.addItem("1:1 (1024×1024)", "1024*1024")
        self.size_combo.addItem("2:3 (800×1200)", "800*1200")
        self.size_combo.addItem("3:2 (1200×800)", "1200*800")
        self.size_combo.addItem("3:4 (960×1280)", "960*1280")
        self.size_combo.addItem("4:3 (1280×960)", "1280*960")
        self.size_combo.addItem("9:16 (720×1280)", "720*1280")
        self.size_combo.addItem("16:9 (1280×720)", "1280*720")
        self.size_combo.addItem("21:9 (1344×576)", "1344*576")
        scroll_layout.addWidget(self.size_combo)
        
        # 默认隐藏尺寸选择（仅万相模型显示）
        self.size_label.hide()
        self.size_combo.hide()
        
        # 图文混合输出（仅万相2.6显示）
        scroll_layout.addSpacing(8)
        interleave_layout = QHBoxLayout()
        interleave_layout.setSpacing(12)
        
        if FLUENT_AVAILABLE:
            interleave_label = BodyLabel("启用图文混合输出")
            interleave_layout.addWidget(interleave_label, 1)
            self.interleave_checkbox = SwitchButton()
            self.interleave_checkbox.setChecked(False)
            self.interleave_checkbox.checkedChanged.connect(self.on_interleave_changed)
            interleave_layout.addWidget(self.interleave_checkbox)
        else:
            self.interleave_checkbox = QCheckBox("启用图文混合输出")
            self.interleave_checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 12px;
                    padding: 5px;
                }
            """)
            self.interleave_checkbox.stateChanged.connect(self.on_interleave_changed)
            interleave_layout.addWidget(self.interleave_checkbox)
        
        self.interleave_layout_widget = QWidget()
        self.interleave_layout_widget.setLayout(interleave_layout)
        self.interleave_layout_widget.setToolTip("生成包含文字说明和图片的教程式内容")
        scroll_layout.addWidget(self.interleave_layout_widget)
        
        # 最大图片数量（仅图文混合模式显示）
        if FLUENT_AVAILABLE:
            max_images_label = BodyLabel("最多生成图片数")
        else:
            max_images_label = QLabel("最多生成图片数:")
            max_images_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.max_images_label = max_images_label
        scroll_layout.addWidget(self.max_images_label)
        
        if FLUENT_AVAILABLE:
            self.max_images_spinbox = SpinBox()
        else:
            self.max_images_spinbox = QSpinBox()
        self.max_images_spinbox.setMinimum(1)
        self.max_images_spinbox.setMaximum(5)
        self.max_images_spinbox.setValue(3)
        self.max_images_spinbox.setToolTip("实际生成数量可能少于设定值")
        self.max_images_spinbox.setMinimumHeight(36)
        scroll_layout.addWidget(self.max_images_spinbox)
        
        # 默认隐藏图文混合选项（仅万相2.6显示）
        self.interleave_layout_widget.hide()
        self.max_images_label.hide()
        self.max_images_spinbox.hide()
        
        # 生成按钮
        scroll_layout.addSpacing(12)
        if FLUENT_AVAILABLE:
            self.generate_btn = PrimaryPushButton(FluentIcon.EDIT, "开始编辑")
        else:
            self.generate_btn = QPushButton("开始编辑")
            self.generate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:disabled {
                    background-color: #ccc;
                }
            """)
        self.generate_btn.clicked.connect(self.on_generate_clicked)
        self.generate_btn.setMinimumHeight(48)
        scroll_layout.addWidget(self.generate_btn)
        
        # 状态标签
        if FLUENT_AVAILABLE:
            self.status_label = BodyLabel("")
            self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        else:
            self.status_label = QLabel("")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 11px;
                    padding: 8px;
                    background: #f8f9fa;
                    border-radius: 4px;
                }
            """)
        self.status_label.setMinimumHeight(40)
        self.status_label.setWordWrap(True)
        scroll_layout.addWidget(self.status_label)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # 初始化模型状态（触发一次on_model_changed）
        self.on_model_changed(0)
        
        return widget
    
    def on_mode_changed(self, index):
        """模式改变事件"""
        mode = self.mode_combo.itemData(index)
        if mode == "single":
            self.mode_hint.setText("单图编辑：选择1张图片进行编辑处理")
        else:
            self.mode_hint.setText("多图融合：选择2-3张图片进行融合处理")
    
    def on_interleave_changed(self, state):
        """图文混合模式切换"""
        # 兼容 SwitchButton (bool) 和 QCheckBox (int)
        if isinstance(state, bool):
            is_enabled = state
        else:
            is_enabled = state == 2  # Qt.Checked
        
        if is_enabled:
            # 启用图文混合模式
            self.max_images_label.show()
            self.max_images_spinbox.show()
            # 图文混合模式下n固定为1
            self.n_spinbox.setValue(1)
            self.n_spinbox.setEnabled(False)
        else:
            # 禁用图文混合模式
            self.max_images_label.hide()
            self.max_images_spinbox.hide()
            # 恢复n的设置
            self.n_spinbox.setEnabled(True)
    
    def on_model_changed(self, index):
        """模型改变事件"""
        model = self.model_combo.itemData(index)
        
        # 判断是否为万相模型
        is_wanxiang = model and (model.startswith('wan2.') or model == 'wan2.6-image')
        
        # 获取图文混合状态（兼容 SwitchButton 和 QCheckBox）
        interleave_checked = self.interleave_checkbox.isChecked() if hasattr(self.interleave_checkbox, 'isChecked') else False
        
        if model == 'wan2.6-image':
            self.model_desc_label.setText("万相2.6模型：最新模型，支持参考图生图、图文混合输出，异步处理")
            # 显示尺寸选择
            self.size_label.show()
            self.size_combo.show()
            # 显示图文混合选项
            self.interleave_layout_widget.show()
            # 根据图文混合状态显示max_images
            if interleave_checked:
                self.max_images_label.show()
                self.max_images_spinbox.show()
            # 万相2.6不支持反向提示词
            self.neg_prompt_edit.setEnabled(False)
            self.neg_prompt_edit.setPlaceholderText("此模型不支持反向提示词")
        elif model and model.startswith('wan2.5'):
            self.model_desc_label.setText("万相2.5模型：支持单图编辑和多图融合，异步处理，效果更优")
            # 显示尺寸选择
            self.size_label.show()
            self.size_combo.show()
            # 隐藏图文混合选项（2.5不支持）
            self.interleave_layout_widget.hide()
            self.max_images_label.hide()
            self.max_images_spinbox.hide()
            # 万相2.5不支持反向提示词
            self.neg_prompt_edit.setEnabled(False)
            self.neg_prompt_edit.setPlaceholderText("此模型不支持反向提示词")
        else:
            # 通义千问模型
            if model == "qwen-image-edit-plus":
                self.model_desc_label.setText("通义千问 Edit Plus（推荐）：支持单图编辑和多图融合，可输出1-6张图片，支持自定义分辨率，同步处理")
                # 显示尺寸选择（新模型支持自定义分辨率）
                self.size_label.show()
                self.size_combo.show()
            else:
                self.model_desc_label.setText("通义千问模型：支持单图编辑和多图融合，同步处理")
                # 隐藏尺寸选择
                self.size_label.hide()
                self.size_combo.hide()
            # 隐藏图文混合选项
            self.interleave_layout_widget.hide()
            self.max_images_label.hide()
            self.max_images_spinbox.hide()
            # 通义千问支持反向提示词
            self.neg_prompt_edit.setEnabled(True)
            self.neg_prompt_edit.setPlaceholderText("描述不希望出现的内容...")
    
    def add_images(self):
        """添加图片"""
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "提示", "请先创建或打开工程")
            return
        
        project = self.project_manager.get_current_project()
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片",
            project.inputs_folder,
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff *.webp *.gif)"
        )
        
        if file_paths:
            mode = self.mode_combo.currentData()
            max_images = 1 if mode == "single" else 3
            
            for file_path in file_paths:
                if len(self.selected_images) >= max_images:
                    QMessageBox.warning(
                        self,
                        "提示",
                        f"{'单图编辑' if mode == 'single' else '多图融合'}模式最多选择{max_images}张图片"
                    )
                    break
                
                if file_path not in self.selected_images:
                    self.selected_images.append(file_path)
            
            # 刷新预览
            self.refresh_image_preview()
    
    def clear_images(self):
        """清空图片列表"""
        self.selected_images.clear()
        self.refresh_image_preview()
    
    def refresh_image_preview(self):
        """刷新图片预览"""
        # 清空现有布局
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            widget = item.widget()
            if widget and widget != self.empty_preview_label:
                widget.deleteLater()
        
        if not self.selected_images:
            # 显示空状态
            self.empty_preview_label.show()
            self.preview_layout.addWidget(self.empty_preview_label, 0, 0, Qt.AlignCenter)
            return
        
        # 隐藏空状态
        self.empty_preview_label.hide()
        
        # 根据图片数量决定列数：1张图片时单列显示更大，多张时2列
        columns = 1 if len(self.selected_images) == 1 else 2
        for i, image_path in enumerate(self.selected_images):
            row = i // columns
            col = i % columns
            
            # 创建图片卡片
            card = self.create_preview_card(image_path, i)
            self.preview_layout.addWidget(card, row, col)
    
    def create_preview_card(self, image_path, index):
        """创建图片预览卡片"""
        card = QWidget()
        card.setObjectName("previewCard")  # 设置对象名
        card.setStyleSheet("""
            QWidget#previewCard {
                background: transparent;
                border: 2px solid #dee2e6;
                border-radius: 6px;
            }
            QWidget#previewCard:hover {
                border: 2px solid #007bff;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # 图片缩略图
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(image_label)
        
        # 文件名和序号
        info_layout = QHBoxLayout()
        info_layout.setSpacing(4)
        
        # 序号标签
        index_label = QLabel(f"图{index + 1}")
        index_label.setStyleSheet("""
            QLabel {
                color: white;
                background: #007bff;
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: bold;
            }
        """)
        info_layout.addWidget(index_label)
        
        # 文件名
        filename = os.path.basename(image_path)
        if len(filename) > 12:
            filename = filename[:10] + '...'
        name_label = QLabel(filename)
        name_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 10px;
            }
        """)
        name_label.setToolTip(os.path.basename(image_path))  # 完整文件名
        info_layout.addWidget(name_label)
        info_layout.addStretch()
        
        # 删除按钮
        if FLUENT_AVAILABLE:
            remove_btn = TransparentToolButton(FluentIcon.CLOSE)
            remove_btn.setFixedSize(24, 24)
        else:
            remove_btn = QPushButton("×")
            remove_btn.setFixedSize(20, 20)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #c82333;
                }
            """)
        remove_btn.clicked.connect(lambda: self.remove_image(image_path))
        info_layout.addWidget(remove_btn)
        
        layout.addLayout(info_layout)
        
        return card
    
    def remove_image(self, image_path):
        """删除单张图片"""
        if image_path in self.selected_images:
            self.selected_images.remove(image_path)
            self.refresh_image_preview()
    
    def on_generate_clicked(self):
        """生成按钮点击"""
        # 验证图片
        if not self.selected_images:
            QMessageBox.warning(self, "提示", "请先选择图片")
            return
        
        mode = self.mode_combo.currentData()
        if mode == "single" and len(self.selected_images) != 1:
            QMessageBox.warning(self, "提示", "单图编辑模式需要选择1张图片")
            return
        elif mode == "multi" and len(self.selected_images) < 2:
            QMessageBox.warning(self, "提示", "多图融合模式至少需要2张图片")
            return
        
        # 验证提示词
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "提示", "请输入编辑描述")
            return
        
        # 检查是否有工程
        if not self.project_manager.has_project():
            QMessageBox.warning(self, "提示", "请先创建或打开工程")
            return
        
        # 获取配置
        model = self.model_combo.currentData()
        n = self.n_spinbox.value()
        negative_prompt = self.neg_prompt_edit.toPlainText().strip()
        size = self.size_combo.currentData()  # 获取输出尺寸
        enable_interleave = self.interleave_checkbox.isChecked()  # 图文混合模式
        max_images = self.max_images_spinbox.value()  # 最大图片数量
        
        # 获取输出文件夹
        project = self.project_manager.get_current_project()
        output_folder = project.inputs_folder
        
        # 禁用按钮
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("编辑中...")
        
        # 创建工作线程
        self.worker = ImageEditWorker(
            self.api_client,
            self.selected_images,
            prompt,
            model,
            n,
            negative_prompt,
            True,  # prompt_extend
            output_folder,
            size,  # 输出尺寸
            enable_interleave,  # 图文混合模式
            max_images  # 最大图片数量
        )
        self.worker.finished.connect(self.on_edit_finished)
        self.worker.error.connect(self.on_edit_error)
        self.worker.progress.connect(self.on_edit_progress)
        self.worker.start()
    
    def on_edit_finished(self, image_paths, edit_info):
        """编辑完成"""
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("开始编辑")
        self.status_label.setText(f"✅ 编辑成功！生成了{len(image_paths)}张图片")
        
        # 添加到画廊
        self.gallery.add_images(
            image_paths,
            edit_info.get('prompt', ''),
            edit_info.get('model', '')
        )
        
        # 刷新资源管理器
        main_window = self.window()
        if hasattr(main_window, 'project_explorer'):
            main_window.project_explorer.refresh()
        
        QMessageBox.information(
            self,
            "成功",
            f"图片编辑完成！\n已生成{len(image_paths)}张图片"
        )
    
    def on_edit_error(self, error_msg):
        """编辑错误"""
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("开始编辑")
        self.status_label.setText(f"❌ {error_msg}")
        
        QMessageBox.critical(self, "错误", error_msg)
    
    def on_edit_progress(self, status_msg):
        """编辑进度更新"""
        self.status_label.setText(status_msg)
    
    def on_image_clicked(self, image_path):
        """图片点击事件"""
        from .image_viewer import ImageViewer
        viewer = ImageViewer(image_path, self)
        viewer.exec_()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否有图片文件
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.gif')):
                    event.acceptProposedAction()
                    return
    
    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        urls = event.mimeData().urls()
        if not urls:
            return
        
        mode = self.mode_combo.currentData()
        max_images = 1 if mode == "single" else 3
        
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.gif')):
                if len(self.selected_images) >= max_images:
                    QMessageBox.warning(
                        self,
                        "提示",
                        f"{'单图编辑' if mode == 'single' else '多图融合'}模式最多选择{max_images}张图片"
                    )
                    break
                
                if file_path not in self.selected_images:
                    self.selected_images.append(file_path)
        
        # 刷新预览
        self.refresh_image_preview()
        event.acceptProposedAction()
