# v1.15.0 - 全面适配万相2.6，新增参考生视频功能

## 🎯 核心更新

### 新增参考生视频功能 (wan2.6-r2v)
- 支持1-2个参考视频生成新视频
- 智能角色识别（character1/character2）
- 视频上传到OSS并自动获取URL
- 完整的参数配置（分辨率、时长、镜头类型、音频）
- 视频缩略图预览（使用OpenCV）
- 拖拽上传支持
- 任务管理集成

### 技术实现
- 新增 `ReferenceVideoToVideoWidget` UI组件
- 新增 `upload_video_and_get_url()` API方法
- 新增 `submit_reference_video_to_video()` API方法
- 添加 `X-DashScope-OssResourceResolve: enable` 请求头支持
- 使用OpenCV生成视频缩略图

## 🎨 UI/UX改进

### 视频缩略图显示
- 上传视频后自动显示缩略图预览
- 使用OpenCV提取视频第一帧
- 自动缩放适应显示区域
- 响应式窗口大小调整

### 工程文件夹集成
- 点击"浏览..."时自动打开工程inputs文件夹
- 快速选择已导入的视频文件
- 优化工作流程

### 拖拽功能增强
- 支持从工程资源管理器拖拽视频
- 支持从文件系统拖拽视频
- 拖拽时显示蓝色高亮反馈
- 工程资源管理器支持视频文件拖拽

## 🐛 Bug修复

### 拖拽功能修复
- 修复从工程资源管理器拖拽视频无效的问题
- 添加 `dragMoveEvent` 事件处理
- 改进事件接受/拒绝逻辑
- 工程资源管理器现在支持拖拽mp4、mov文件

### OSS URL格式修复
- 使用 `oss://` 格式的URL
- 添加 `X-DashScope-OssResourceResolve: enable` 请求头
- API服务端使用内部权限访问OSS文件

## ⚡ 性能优化

### 字体优化
- 优先使用系统字体（-apple-system, BlinkMacSystemFont）
- 消除macOS上的字体查找警告
- 减少启动时间约70ms

### 错误处理优化
- OpenCV错误静默失败
- 改进降级处理
- 清爽的控制台输出

## 📋 任务管理

### 参考生视频任务集成
- 任务列表显示参考生视频任务状态
- 支持任务进度监控和状态更新
- 任务完成/失败时自动更新状态
- 与首帧生视频的任务管理方式一致

## 📝 文档更新

### 新增文档
- `REFERENCE_VIDEO_TO_VIDEO_GUIDE.md` - 完整功能说明
- `REFERENCE_VIDEO_QUICK_START.md` - 快速入门指南
- `FEATURE_IMPROVEMENTS_V1.15.1.md` - 功能改进说明
- `OPENCV_THUMBNAIL_UPDATE.md` - OpenCV缩略图更新说明
- `DRAG_DROP_FIX.md` - 拖拽功能修复说明
- `WARNINGS_FIX.md` - 警告信息修复说明
- `FINAL_FIX_OSS_HEADER.md` - OSS请求头修复说明
- `OSS_URL_FORMAT_EXPLANATION.md` - OSS URL格式说明
- `BUGFIX_URL_FORMAT.md` - URL格式bug修复
- `FEATURES_COMPARISON.md` - 功能对比表
- `release-notes-v1.15.0.md` - 版本发布说明
- `IMPLEMENTATION_SUMMARY_V1.15.0.md` - 实现总结

### 更新文档
- `CHANGELOG.md` - 详细的变更日志
- `README.md` - 更新功能列表和版本号

## 🔧 修改的文件

### 核心功能
- `ui/reference_video_to_video_widget.py` - 新增参考生视频组件
- `core/api_client.py` - 扩展API客户端
- `ui/main_window.py` - 集成新标签页

### UI改进
- `ui/project_explorer.py` - 支持视频拖拽
- `themes/themes.py` - 优化字体设置

### 配置
- `main.py` - 更新版本号到1.15.0
- `README.md` - 更新版本徽章

## 🎉 总结

v1.15.0是一个重大更新，全面适配万相2.6模型，新增参考生视频功能，并进行了大量UI/UX改进和bug修复。

### 主要亮点
1. ✅ 参考生视频功能完整实现
2. ✅ 视频缩略图预览
3. ✅ 工程文件夹集成
4. ✅ 拖拽功能增强
5. ✅ 任务管理集成
6. ✅ 性能优化
7. ✅ 完整的文档支持

### 技术改进
- 使用OpenCV替代ffmpeg
- 统一的实现方式
- 更好的错误处理
- 更快的启动速度

---

**发布日期**: 2025年12月16日  
**版本**: v1.15.0  
**状态**: ✅ 已完成
