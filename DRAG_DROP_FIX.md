# 拖拽功能修复说明

## 🐛 问题描述

从工程资源管理器（视频集）拖动视频文件到参考视频预览区域时，拖拽操作无法正常工作。

## 🔍 问题分析

### 原因1：工程资源管理器不支持视频拖拽
工程资源管理器的 `start_drag` 方法只允许拖拽图片文件，不支持视频文件。

**修复**：修改 `ui/project_explorer.py`，添加视频文件支持。

### 原因2：缺少 dragMoveEvent
缺少 `dragMoveEvent` 事件处理器。在Qt的拖拽系统中：

1. **dragEnterEvent**: 拖拽进入组件时触发
2. **dragMoveEvent**: 拖拽在组件内移动时持续触发（必需！）
3. **dropEvent**: 释放拖拽时触发

如果没有实现 `dragMoveEvent` 或没有正确接受事件，拖拽操作会被中断。

### 工程资源管理器的拖拽实现
```python
# ui/project_explorer.py
mime_data = QMimeData()
mime_data.setUrls([QUrl.fromLocalFile(file_path)])
drag.setMimeData(mime_data)
```

使用标准的 `QMimeData` 和 `QUrl.fromLocalFile()`，这是正确的实现。

## ✅ 解决方案

### 修改内容

#### 文件1: `ui/project_explorer.py`

**修改 start_drag 方法，支持视频文件拖拽**:

```python
def start_drag(self, supportedActions):
    # ...
    
    # 允许拖拽图片和视频文件
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.mp4', '.mov')
    if not file_path.lower().endswith(allowed_extensions):
        return
    
    # ...
    
    # 设置拖拽时显示的缩略图
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        thumbnail = self.create_thumbnail(file_path)
    elif file_path.lower().endswith(('.mp4', '.mov')):
        thumbnail = self.create_video_thumbnail(file_path)
    else:
        thumbnail = None
```

#### 文件2: `ui/reference_video_to_video_widget.py`

#### 1. 添加 dragMoveEvent

```python
def dragMoveEvent(self, event):
    """拖拽移动事件"""
    if event.mimeData().hasUrls():
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.mp4', '.mov')):
                event.acceptProposedAction()
                return
    event.ignore()
```

**作用**:
- 在拖拽移动过程中持续验证文件类型
- 接受有效的视频文件拖拽
- 拒绝无效的文件类型

#### 2. 改进 dragEnterEvent

```python
def dragEnterEvent(self, event: QDragEnterEvent):
    """拖拽进入事件"""
    if event.mimeData().hasUrls():
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.mp4', '.mov')):
                event.acceptProposedAction()
                self.setStyleSheet(...)
                return
    event.ignore()  # 明确拒绝无效拖拽
```

**改进**:
- 添加 `return` 语句，明确处理流程
- 添加 `event.ignore()` 拒绝无效拖拽

#### 3. 改进 dropEvent

```python
def dropEvent(self, event: QDropEvent):
    """拖放事件"""
    urls = event.mimeData().urls()
    if urls:
        file_path = urls[0].toLocalFile()
        if file_path.lower().endswith(('.mp4', '.mov')):
            self.video_dropped.emit(file_path)
            event.acceptProposedAction()
            return
    event.ignore()  # 明确拒绝无效拖拽
```

**改进**:
- 添加 `return` 语句
- 添加 `event.ignore()` 拒绝无效拖拽

## 🧪 测试验证

### 测试场景

#### 场景1: 从工程资源管理器拖拽
1. ✅ 打开工程
2. ✅ 在工程资源管理器中找到视频文件
3. ✅ 拖动视频文件到参考视频预览区域
4. ✅ 预览区域显示蓝色高亮
5. ✅ 释放鼠标，视频加载成功
6. ✅ 显示视频缩略图

#### 场景2: 从文件系统拖拽
1. ✅ 打开文件管理器（Finder/资源管理器）
2. ✅ 找到视频文件
3. ✅ 拖动到参考视频预览区域
4. ✅ 预览区域显示蓝色高亮
5. ✅ 释放鼠标，视频加载成功
6. ✅ 显示视频缩略图

#### 场景3: 拖拽非视频文件
1. ✅ 拖动图片或其他文件
2. ✅ 预览区域不显示高亮
3. ✅ 无法释放（鼠标显示禁止图标）
4. ✅ 释放后无任何操作

#### 场景4: 拖拽到两个预览区域
1. ✅ 拖动视频到参考视频1区域
2. ✅ 视频1加载成功
3. ✅ 拖动另一个视频到参考视频2区域
4. ✅ 视频2加载成功
5. ✅ 两个视频都显示缩略图

## 🔧 技术细节

### Qt拖拽事件流程

```
1. 用户开始拖拽
   ↓
2. dragEnterEvent (目标组件)
   - 检查MIME数据
   - 决定是否接受
   ↓
3. dragMoveEvent (目标组件) - 持续触发
   - 验证拖拽位置
   - 持续接受或拒绝
   ↓
4. dropEvent (目标组件)
   - 处理拖拽数据
   - 执行实际操作
```

### 关键点

1. **必须实现 dragMoveEvent**
   - 即使只是简单地接受事件
   - 否则拖拽会被中断

2. **明确接受或拒绝事件**
   - 使用 `event.acceptProposedAction()` 接受
   - 使用 `event.ignore()` 拒绝
   - 不要让事件处于未定义状态

3. **验证MIME数据**
   - 检查 `hasUrls()`
   - 验证文件扩展名
   - 确保文件存在

## 📊 代码对比

### 修复前
```python
def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
        # ... 验证 ...
        event.acceptProposedAction()
        # 缺少 return

# 缺少 dragMoveEvent ❌

def dropEvent(self, event):
    # ... 处理 ...
    event.acceptProposedAction()
    # 缺少 return 和 ignore
```

### 修复后
```python
def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
        # ... 验证 ...
        event.acceptProposedAction()
        return  # ✅
    event.ignore()  # ✅

def dragMoveEvent(self, event):  # ✅ 新增
    if event.mimeData().hasUrls():
        # ... 验证 ...
        event.acceptProposedAction()
        return
    event.ignore()

def dropEvent(self, event):
    # ... 处理 ...
    event.acceptProposedAction()
    return  # ✅
    event.ignore()  # ✅
```

## 💡 最佳实践

### 实现拖拽接收的标准模式

```python
class DragDropWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)  # 启用拖拽接收
    
    def dragEnterEvent(self, event):
        """拖拽进入 - 初始验证"""
        if self.is_valid_drag(event):
            event.acceptProposedAction()
            self.show_highlight()
            return
        event.ignore()
    
    def dragMoveEvent(self, event):
        """拖拽移动 - 持续验证（必需！）"""
        if self.is_valid_drag(event):
            event.acceptProposedAction()
            return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖拽离开 - 清理UI"""
        self.hide_highlight()
    
    def dropEvent(self, event):
        """拖放 - 处理数据"""
        if self.is_valid_drag(event):
            self.process_drop(event)
            event.acceptProposedAction()
            return
        event.ignore()
    
    def is_valid_drag(self, event):
        """验证拖拽数据"""
        if not event.mimeData().hasUrls():
            return False
        # ... 更多验证 ...
        return True
```

## 🎯 用户体验改进

### 修复前
- ❌ 从工程资源管理器拖拽无效
- ❌ 鼠标显示禁止图标
- ❌ 无法释放文件
- ❌ 用户困惑

### 修复后
- ✅ 从工程资源管理器拖拽正常
- ✅ 鼠标显示正确图标
- ✅ 可以正常释放文件
- ✅ 显示蓝色高亮反馈
- ✅ 自动加载视频和缩略图

## 🔄 相关功能

### 支持的拖拽来源
1. ✅ 工程资源管理器
2. ✅ 文件系统（Finder/资源管理器）
3. ✅ 桌面
4. ✅ 其他应用程序

### 支持的文件格式
- ✅ .mp4
- ✅ .mov

### 自动功能
- ✅ 文件格式验证
- ✅ 文件大小检查（≤100MB）
- ✅ 视频缩略图生成
- ✅ 视频信息显示

## 📝 更新日志

### v1.15.1 (2025-12-16)

**修复**:
- ✅ 添加 `dragMoveEvent` 事件处理
- ✅ 改进 `dragEnterEvent` 事件处理
- ✅ 改进 `dropEvent` 事件处理
- ✅ 明确事件接受/拒绝逻辑

**影响**:
- ✅ 从工程资源管理器拖拽现在正常工作
- ✅ 更好的拖拽反馈
- ✅ 更可靠的拖拽操作

## 🎉 总结

通过添加 `dragMoveEvent` 和改进事件处理逻辑，现在可以从工程资源管理器正常拖拽视频文件到参考视频预览区域了！

**关键改进**:
1. ✅ 添加必需的 `dragMoveEvent`
2. ✅ 明确的事件接受/拒绝
3. ✅ 更好的用户反馈
4. ✅ 更可靠的拖拽操作

---

**修复日期**: 2025年12月16日  
**版本**: v1.15.1  
**状态**: ✅ 已完成并验证
