#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工程资源管理器
类似 VSCode 的文件浏览器
使用 QFluentWidgets 组件美化
"""

import os
import shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidgetItem, QFileIconProvider, QInputDialog, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QUrl, QSize
from PyQt5.QtGui import QDrag, QPixmap

# 尝试导入 QFluentWidgets 组件
try:
    from qfluentwidgets import (
        TreeWidget, RoundMenu, Action, FluentIcon,
        ToolButton, SubtitleLabel, BodyLabel, MessageBox
    )
    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    from PyQt5.QtWidgets import QTreeWidget as TreeWidget, QMenu, QPushButton, QLabel, QMessageBox
    print("警告: QFluentWidgets 未安装，将使用原生 PyQt5 组件")


class ProjectExplorer(QWidget):
    """工程资源管理器"""
    
    # 定义信号
    file_selected = pyqtSignal(str)  # 文件路径
    refresh_requested = pyqtSignal()
    file_drag_started = pyqtSignal(str)  # 文件拖拽开始
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_project = None
        self.icon_provider = QFileIconProvider()
        
        # 启用整个 widget 的拖拽接收
        self.setAcceptDrops(True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题栏
        header = QWidget()
        header_layout = QHBoxLayout(header)
        # 统一标题栏内边距：10px 水平，5px 垂直
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        if FLUENT_AVAILABLE:
            title_label = SubtitleLabel("资源管理器")
        else:
            title_label = QLabel("资源管理器")
            title_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 刷新按钮
        if FLUENT_AVAILABLE:
            refresh_btn = ToolButton(FluentIcon.SYNC)
            refresh_btn.setFixedSize(28, 28)
            refresh_btn.setToolTip("刷新")
            refresh_btn.clicked.connect(self.refresh)
        else:
            refresh_btn = QPushButton("⟳")
            refresh_btn.setFixedSize(24, 24)
            refresh_btn.setToolTip("刷新")
            refresh_btn.clicked.connect(self.refresh)
            refresh_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #666;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: #e9ecef;
                    border-radius: 4px;
                    color: #333;
                }
            """)
        header_layout.addWidget(refresh_btn)
        
        layout.addWidget(header)
        
        # 树形视图
        self.tree = TreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # 设置图标大小 - 使用较小的图标以节省空间
        self.tree.setIconSize(QSize(24, 24))
        
        # 树形视图启用拖拽
        self.tree.setDragEnabled(True)
        if FLUENT_AVAILABLE:
            from PyQt5.QtWidgets import QAbstractItemView
            self.tree.setDragDropMode(QAbstractItemView.DragOnly)
        else:
            self.tree.setDragDropMode(TreeWidget.DragOnly)
        
        # 连接拖拽开始信号
        self.tree.startDrag = self.start_drag
        
        layout.addWidget(self.tree)
        
        # 空状态提示
        if FLUENT_AVAILABLE:
            self.empty_label = BodyLabel("未打开工程\n\n请创建或打开工程")
            self.empty_label.setAlignment(Qt.AlignCenter)
        else:
            self.empty_label = QLabel("未打开工程\n\n请创建或打开工程")
            self.empty_label.setAlignment(Qt.AlignCenter)
            self.empty_label.setStyleSheet("""
                QLabel {
                    color: #999;
                    font-size: 14px;
                    padding: 20px;
                }
            """)
        layout.addWidget(self.empty_label)
        
        # 默认显示空状态
        self.show_empty_state()
    
    def set_project(self, project):
        """设置当前工程"""
        self.current_project = project
        if project:
            self.load_project()
        else:
            self.show_empty_state()
    
    def show_empty_state(self):
        """显示空状态"""
        self.tree.hide()
        self.empty_label.show()
    
    def load_project(self):
        """加载工程文件结构"""
        self.tree.clear()
        self.empty_label.hide()
        self.tree.show()
        
        if not self.current_project:
            return
        
        # 添加根节点
        root = QTreeWidgetItem(self.tree)
        root.setText(0, self.current_project.name)
        root.setData(0, Qt.UserRole, self.current_project.path)
        if FLUENT_AVAILABLE:
            root.setIcon(0, FluentIcon.FOLDER.icon())
        root.setExpanded(True)
        
        # 添加 inputs 文件夹 (显示为图集)
        inputs_item = QTreeWidgetItem(root)
        if FLUENT_AVAILABLE:
            inputs_item.setText(0, "图集")
            inputs_item.setIcon(0, FluentIcon.PHOTO.icon())
        else:
            inputs_item.setText(0, "📁 图集")
        inputs_item.setData(0, Qt.UserRole, self.current_project.inputs_folder)
        inputs_item.setExpanded(True)  # 默认展开
        self.load_folder(inputs_item, self.current_project.inputs_folder)
        
        # 添加 outputs 文件夹 (显示为视频集)
        outputs_item = QTreeWidgetItem(root)
        if FLUENT_AVAILABLE:
            outputs_item.setText(0, "视频集")
            outputs_item.setIcon(0, FluentIcon.VIDEO.icon())
        else:
            outputs_item.setText(0, "📁 视频集")
        outputs_item.setData(0, Qt.UserRole, self.current_project.outputs_folder)
        outputs_item.setExpanded(True)  # 默认展开
        self.load_folder(outputs_item, self.current_project.outputs_folder)
    
    def load_folder(self, parent_item, folder_path):
        """加载文件夹内容"""
        if not os.path.exists(folder_path):
            return
        
        try:
            items = os.listdir(folder_path)
            items.sort()
            
            # 判断是图集还是视频集
            folder_name = parent_item.text(0)
            is_image_folder = "图集" in folder_name
            is_video_folder = "视频集" in folder_name
            
            # 定义支持的文件类型
            image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
            video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
            
            for item_name in items:
                item_path = os.path.join(folder_path, item_name)
                
                if os.path.isfile(item_path):
                    ext_lower = item_path.lower()
                    
                    # 图集只显示图片文件
                    if is_image_folder:
                        if ext_lower.endswith(image_extensions):
                            file_item = QTreeWidgetItem(parent_item)
                            # 使用缩略图
                            thumbnail = self.create_thumbnail(item_path)
                            if thumbnail:
                                from PyQt5.QtGui import QIcon
                                file_item.setIcon(0, QIcon(thumbnail))
                            elif FLUENT_AVAILABLE:
                                file_item.setIcon(0, FluentIcon.PHOTO.icon())
                            file_item.setText(0, item_name)
                            file_item.setData(0, Qt.UserRole, item_path)
                        # 跳过所有非图片文件
                        
                    # 视频集只显示视频文件
                    elif is_video_folder:
                        if ext_lower.endswith(video_extensions):
                            file_item = QTreeWidgetItem(parent_item)
                            # 使用视频预览图
                            thumbnail = self.create_video_thumbnail(item_path)
                            if thumbnail:
                                from PyQt5.QtGui import QIcon
                                file_item.setIcon(0, QIcon(thumbnail))
                                file_item.setText(0, item_name)
                            elif FLUENT_AVAILABLE:
                                file_item.setIcon(0, FluentIcon.VIDEO.icon())
                                file_item.setText(0, item_name)
                            else:
                                # 没有缩略图时显示视频emoji
                                file_item.setText(0, f"🎬 {item_name}")
                            file_item.setData(0, Qt.UserRole, item_path)
                        # 跳过所有非视频文件
                        
        except Exception as e:
            print(f"加载文件夹失败: {e}")
    
    def create_thumbnail(self, image_path):
        """
        创建图片缩略图
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            QPixmap: 缩略图，失败返回 None
        """
        try:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                return None
            
            # 创建 24x24 的缩略图（更紧凑的显示）
            thumbnail = pixmap.scaled(
                24, 24,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            return thumbnail
        except Exception as e:
            print(f"创建缩略图失败: {e}")
            return None
    
    def create_video_thumbnail(self, video_path):
        """
        创建视频预览图（提取第一帧）
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            QPixmap: 预览图，失败返回 None
        """
        try:
            import cv2
            import numpy as np
            from PyQt5.QtGui import QImage
            
            # 打开视频文件
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return None
            
            # 读取第一帧
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                return None
            
            # 转换BGR到RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 转换为QImage
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # 转换为QPixmap并缩放（更紧凑的显示）
            pixmap = QPixmap.fromImage(q_image)
            thumbnail = pixmap.scaled(
                24, 24,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            return thumbnail
            
        except ImportError:
            # 如果没有安装cv2，返回None
            return None
        except Exception as e:
            # 静默失败，不打印错误信息
            return None
    
    def refresh(self):
        """刷新"""
        if self.current_project:
            self.load_project()
        self.refresh_requested.emit()
    
    def on_item_double_clicked(self, item, column):
        """双击项目"""
        file_path = item.data(0, Qt.UserRole)
        if file_path and os.path.isfile(file_path):
            self.file_selected.emit(file_path)
    
    def get_dragged_file_path(self):
        """获取正在拖拽的文件路径"""
        item = self.tree.currentItem()
        if item:
            file_path = item.data(0, Qt.UserRole)
            if file_path and os.path.isfile(file_path):
                return file_path
        return None
    
    def start_drag(self, supportedActions):
        """开始拖拽操作"""
        item = self.tree.currentItem()
        if not item:
            return
        
        file_path = item.data(0, Qt.UserRole)
        if not file_path or not os.path.isfile(file_path):
            return
        
        # 允许拖拽图片和视频文件
        allowed_extensions = ('.png', '.jpg', '.jpeg', '.mp4', '.mov')
        if not file_path.lower().endswith(allowed_extensions):
            return
        
        # 创建拖拽对象
        drag = QDrag(self.tree)
        
        # 设置MIME数据
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(file_path)])
        drag.setMimeData(mime_data)
        
        # 设置拖拽时显示的缩略图
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            thumbnail = self.create_thumbnail(file_path)
        elif file_path.lower().endswith(('.mp4', '.mov')):
            thumbnail = self.create_video_thumbnail(file_path)
        else:
            thumbnail = None
        
        if thumbnail:
            drag.setPixmap(thumbnail)
            drag.setHotSpot(thumbnail.rect().center())
        
        # 发送拖拽开始信号
        self.file_drag_started.emit(file_path)
        
        # 执行拖拽
        drag.exec_(Qt.CopyAction)
    
    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        pass
    
    def dropEvent(self, event):
        """放置事件 - 接收外部文件"""
        if not self.current_project:
            self._show_warning("提示", "请先打开工程")
            return
        
        urls = event.mimeData().urls()
        if not urls:
            return
        
        # 判断是单文件还是批量导入
        is_batch = len(urls) > 1
        
        # 统计导入结果
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        # 处理拖放的文件
        for url in urls:
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                # 批量导入时不显示单个文件的提示
                result = self.import_file(file_path, show_message=not is_batch)
                if result == 'success':
                    success_count += 1
                elif result == 'skipped':
                    skipped_count += 1
                else:
                    failed_count += 1
        
        event.acceptProposedAction()
        self.refresh()
        
        # 批量导入时显示总结
        if is_batch:
            message = f"成功: {success_count} 个"
            if skipped_count > 0:
                message += f"\n跳过: {skipped_count} 个"
            if failed_count > 0:
                message += f"\n失败: {failed_count} 个"
            self._show_info("导入完成", message)
    
    def _show_info(self, title, content):
        """显示信息提示"""
        if FLUENT_AVAILABLE:
            from utils.message_helper import MessageHelper
            MessageHelper.info(self.window(), title, content)
        else:
            QMessageBox.information(self, title, content)
    
    def _show_warning(self, title, content):
        """显示警告提示"""
        if FLUENT_AVAILABLE:
            from utils.message_helper import MessageHelper
            MessageHelper.warning(self.window(), title, content)
        else:
            QMessageBox.warning(self, title, content)
    
    def _show_error(self, title, content):
        """显示错误提示"""
        if FLUENT_AVAILABLE:
            from utils.message_helper import MessageHelper
            MessageHelper.error(self.window(), title, content)
        else:
            QMessageBox.critical(self, title, content)
    
    def _show_success(self, title, content):
        """显示成功提示"""
        if FLUENT_AVAILABLE:
            from utils.message_helper import MessageHelper
            MessageHelper.success(self.window(), title, content)
        else:
            QMessageBox.information(self, title, content)
    
    def _confirm(self, title, content):
        """显示确认对话框"""
        if FLUENT_AVAILABLE:
            dialog = MessageBox(title, content, self.window())
            return dialog.exec_() == 1
        else:
            result = QMessageBox.question(
                self, title, content,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return result == QMessageBox.Yes
    
    def import_file(self, file_path, show_message=True):
        """
        导入文件到工程
        
        Args:
            file_path: 文件路径
            show_message: 是否显示消息提示
            
        Returns:
            'success': 导入成功
            'skipped': 用户跳过
            'failed': 导入失败
        """
        if not self.current_project:
            return 'failed'
        
        # 判断文件类型
        ext = os.path.splitext(file_path)[1].lower()
        
        # 定义支持的文件类型
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        
        if ext in image_extensions:
            # 图片文件只能复制到 inputs 文件夹（图集）
            dest_folder = self.current_project.inputs_folder
            file_type = "图片"
        elif ext in video_extensions:
            # 视频文件只能复制到 outputs 文件夹（视频集）
            dest_folder = self.current_project.outputs_folder
            file_type = "视频"
        else:
            if show_message:
                self._show_warning(
                    "不支持的文件类型", 
                    f"文件类型 {ext} 不支持\n\n"
                    f"支持的图片格式: {', '.join(image_extensions)}\n"
                    f"支持的视频格式: {', '.join(video_extensions)}"
                )
            return 'failed'
        
        try:
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(dest_folder, file_name)
            
            # 检查是否已存在
            if os.path.exists(dest_path):
                if not self._confirm("确认覆盖", f"文件 '{file_name}' 已存在，是否覆盖？"):
                    return 'skipped'
            
            # 复制文件
            shutil.copy2(file_path, dest_path)
            
            if show_message:
                folder_name = "图集" if ext in image_extensions else "视频集"
                self._show_success("导入成功", f"{file_type}文件已导入到 {folder_name}")
            
            return 'success'
            
        except Exception as e:
            if show_message:
                self._show_error("导入失败", f"无法导入文件: {str(e)}")
            return 'failed'
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.tree.itemAt(position)
        if not item:
            return
        
        file_path = item.data(0, Qt.UserRole)
        if not file_path or not os.path.isfile(file_path):
            return
        
        if FLUENT_AVAILABLE:
            # 使用 Fluent 风格的 RoundMenu
            menu = RoundMenu(parent=self)
            
            # 重命名
            rename_action = Action(FluentIcon.EDIT, "重命名", self)
            rename_action.triggered.connect(lambda: self.rename_file(file_path))
            menu.addAction(rename_action)
            
            menu.addSeparator()
            
            # 在系统中显示
            show_action = Action(FluentIcon.FOLDER, "在文件管理器中显示", self)
            show_action.triggered.connect(lambda: self.show_in_finder(file_path))
            menu.addAction(show_action)
            
            # 复制路径
            copy_action = Action(FluentIcon.COPY, "复制路径", self)
            copy_action.triggered.connect(lambda: self.copy_path(file_path))
            menu.addAction(copy_action)
            
            menu.addSeparator()
            
            # 删除文件
            delete_action = Action(FluentIcon.DELETE, "删除", self)
            delete_action.triggered.connect(lambda: self.delete_file(file_path))
            menu.addAction(delete_action)
        else:
            # 使用原生 QMenu
            menu = QMenu(self)
            
            # 重命名
            rename_action = menu.addAction("重命名")
            rename_action.triggered.connect(lambda: self.rename_file(file_path))
            
            menu.addSeparator()
            
            # 在系统中显示
            show_action = menu.addAction("在文件管理器中显示")
            show_action.triggered.connect(lambda: self.show_in_finder(file_path))
            
            # 复制路径
            copy_action = menu.addAction("复制路径")
            copy_action.triggered.connect(lambda: self.copy_path(file_path))
            
            menu.addSeparator()
            
            # 删除文件
            delete_action = menu.addAction("删除")
            delete_action.triggered.connect(lambda: self.delete_file(file_path))
        
        menu.exec_(self.tree.viewport().mapToGlobal(position))
    
    def show_in_finder(self, file_path):
        """在文件管理器中显示"""
        import subprocess
        import platform
        
        system = platform.system()
        try:
            if system == 'Darwin':  # macOS
                subprocess.run(['open', '-R', file_path])
            elif system == 'Windows':
                subprocess.run(['explorer', '/select,', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', os.path.dirname(file_path)])
        except Exception as e:
            self._show_error("错误", f"无法打开文件管理器: {str(e)}")
    
    def copy_path(self, file_path):
        """复制路径到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(file_path)
        self._show_success("已复制", "文件路径已复制到剪贴板")
    
    def rename_file(self, file_path):
        """重命名文件"""
        old_name = os.path.basename(file_path)
        name_without_ext, ext = os.path.splitext(old_name)
        
        # 弹出输入对话框
        new_name, ok = QInputDialog.getText(
            self,
            "重命名文件",
            "请输入新的文件名（不含扩展名）:",
            text=name_without_ext
        )
        
        if not ok or not new_name or new_name == name_without_ext:
            return
        
        # 添加原扩展名
        new_name_with_ext = new_name + ext
        new_path = os.path.join(os.path.dirname(file_path), new_name_with_ext)
        
        # 检查新文件名是否已存在
        if os.path.exists(new_path):
            self._show_warning(
                "重命名失败",
                f"文件名 '{new_name_with_ext}' 已存在，请使用其他名称。"
            )
            return
        
        # 执行重命名
        try:
            os.rename(file_path, new_path)
            self.refresh()
            self._show_success("成功", f"文件已重命名为:\n{new_name_with_ext}")
        except Exception as e:
            self._show_error("错误", f"重命名失败: {str(e)}")
    
    def delete_file(self, file_path):
        """删除文件"""
        if self._confirm("确认删除", f"确定要删除文件吗？\n\n{os.path.basename(file_path)}"):
            try:
                os.remove(file_path)
                self.refresh()
                self._show_success("成功", "文件已删除")
            except Exception as e:
                self._show_error("错误", f"删除失败: {str(e)}")
