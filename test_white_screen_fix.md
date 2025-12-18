# 白屏问题修复说明

## 问题描述
打开工程后自动切换到首帧生成视频界面时出现白屏。

## 问题原因
1. **QSplitter 子组件可能被折叠**：QSplitter 默认允许子组件被折叠到0宽度/高度
2. **界面切换时布局未刷新**：切换界面时，组件的几何信息可能未及时更新
3. **组件最小尺寸未设置**：左右两侧的widget没有设置最小宽度，可能被压缩为0

## 修复方案

### 1. 在 `ui/fluent_main_window.py` 中的修复

#### 修复1：防止 QSplitter 子组件被折叠
```python
main_splitter.setChildrenCollapsible(False)  # 防止子组件被折叠
```

#### 修复2：设置左右widget的最小宽度
```python
left_widget.setMinimumWidth(400)  # 左侧最小宽度
right_widget.setMinimumWidth(350)  # 右侧最小宽度
```

#### 修复3：界面切换时强制刷新布局
```python
def on_interface_changed(self, index):
    # ... 原有代码 ...
    
    # 强制刷新当前界面的布局，避免白屏
    if current_widget:
        current_widget.updateGeometry()
        current_widget.update()
```

#### 修复4：打开工程后延迟刷新界面
```python
def switch_to_project(self, project):
    # ... 原有代码 ...
    
    # 切换到首帧生视频界面
    if FLUENT_AVAILABLE:
        self.stackedWidget.setCurrentWidget(self.first_frame_interface)
        # 强制刷新界面布局，避免白屏
        self.first_frame_interface.updateGeometry()
        self.first_frame_interface.update()
        # 使用 QTimer 延迟刷新，确保界面完全加载
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.first_frame_interface.updateGeometry())
```

### 2. 在 `ui/keyframe_to_video_widget.py` 中的修复

#### 修复1：防止 QSplitter 子组件被折叠
```python
main_splitter.setChildrenCollapsible(False)  # 主分割器
right_splitter.setChildrenCollapsible(False)  # 右侧分割器
```

#### 修复2：设置配置面板和右侧widget的最小宽度
```python
widget.setMinimumWidth(320)  # 配置面板最小宽度
right_widget.setMinimumWidth(600)  # 右侧预览区最小宽度
```

## 测试步骤

1. 启动应用程序
2. 创建或打开一个工程
3. 观察是否自动切换到首帧生成视频界面
4. 检查界面是否正常显示（不应该出现白屏）
5. 尝试手动切换到其他功能标签页，再切换回来
6. 检查界面是否仍然正常显示

## 预期结果

- 打开工程后，首帧生成视频界面应该正常显示
- 左侧显示上传区域和视频预览
- 右侧显示配置面板
- 所有组件都应该可见，没有白屏现象
- 界面切换流畅，无延迟或闪烁

## 技术细节

### QSplitter.setChildrenCollapsible(False)
- 防止用户或程序将分割器的子组件拖动到0宽度/高度
- 确保所有子组件始终可见

### updateGeometry() 和 update()
- `updateGeometry()`: 通知布局系统重新计算组件的几何信息
- `update()`: 触发组件的重绘

### QTimer.singleShot()
- 延迟执行刷新操作，确保界面完全加载后再刷新
- 100ms 的延迟足够让 Qt 完成界面的初始化

## 相关文件

- `ui/fluent_main_window.py` - 主窗口
- `ui/keyframe_to_video_widget.py` - 首尾帧生成视频组件
- `ui/config_panel.py` - 配置面板
- `ui/video_viewer.py` - 视频查看器
