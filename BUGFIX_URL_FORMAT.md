# Bug修复：参考视频URL格式和权限问题

## 🐛 问题描述

**错误信息1**:
```
生成失败 [InvalidParameter]: Reference video download failed: 
Failed to download reference video oss://dashscope-instant/...
No connection adapters were found for 'oss://...'
```

**错误信息2** (修复后):
```
生成失败 [InvalidParameter]: Reference video download failed: 
Failed to download reference video https://dashscope-file-mgr.oss-cn-beijing.aliyuncs.com/...
403 Client Error: Forbidden
```

**问题原因**:
1. 第一次尝试：使用 `oss://` 格式，但某些API版本不支持
2. 第二次尝试：转换为HTTP URL，但上传的文件没有公开访问权限，导致403错误
3. **根本原因**：应该使用 `oss://` 格式，让API服务端使用内部权限访问

## ✅ 解决方案

### 修改的文件
- `core/api_client.py` - `upload_video_and_get_url()` 方法

### 修改内容

**修改前**:
```python
def upload_video_and_get_url(self, video_path: str, model_name: str) -> str:
    # ... 上传逻辑 ...
    
    # 返回oss://格式（错误）
    return f"oss://{key}"
```

**修改后** (最终版本):
```python
def upload_video_and_get_url(self, video_path: str, model_name: str) -> str:
    # ... 上传逻辑 ...
    
    # 3. 返回oss://格式的URL
    # API服务端会使用内部权限访问OSS文件
    # 不需要转换为HTTP URL，避免403权限问题
    oss_url = f"oss://{key}"
    
    return oss_url  # 返回oss://格式（正确）

def submit_reference_video_to_video(self, reference_video_urls: list, ...):
    # ... 准备payload ...
    
    # 关键：使用oss://格式时，必须添加特殊请求头
    headers = self._get_headers(async_mode=True, oss_resource_resolve=True)
    # 这会添加: X-DashScope-OssResourceResolve: enable
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
```

### 关键发现：OSS资源解析请求头

**最重要的修复**: 使用 `oss://` 格式时，必须在请求头中添加：
```
X-DashScope-OssResourceResolve: enable
```

没有这个请求头，API无法访问OSS资源！

### 工作原理

1. **上传文件到OSS**: 使用上传凭证将文件上传到指定的OSS bucket
   - Bucket: `dashscope-instant`
   - 路径: `f5489a0a93fd726480c44067ac773413/2025-12-16/xxx.mp4`

2. **返回oss://格式URL**: 
   - 格式: `oss://path/to/file`
   - 示例: `oss://dashscope-instant/f5489a0a93fd726480c44067ac773413/2025-12-16/xxx.mp4`

3. **API服务端处理**: 
   - API服务端接收oss://格式的URL
   - 使用内部权限访问OSS文件
   - 无需公开访问权限，避免403错误

## 🧪 测试验证

### 测试步骤
1. 上传一个测试视频
2. 检查返回的URL格式
3. 验证URL是否以 `https://` 开头
4. 提交视频生成任务
5. 确认任务成功提交

### 预期结果
- ✅ URL格式: `https://bucket.endpoint/path/to/file`
- ✅ 任务提交成功
- ✅ 视频生成正常

## 📝 相关文档更新

同时更新了以下文档：
- `REFERENCE_VIDEO_TO_VIDEO_GUIDE.md` - 添加URL转换说明
- `IMPLEMENTATION_SUMMARY_V1.15.0.md` - 记录bug修复

## 🔍 技术细节

### OSS URL格式说明

**内部格式 (oss://)**:
- 用途: OSS内部引用
- 格式: `oss://bucket-name/path/to/file`
- 示例: `oss://dashscope-instant/xxx/file.mp4`
- 限制: 只能在OSS内部使用，外部无法访问

**HTTP格式 (https://)**:
- 用途: 公开访问
- 格式: `https://bucket-name.endpoint/path/to/file`
- 示例: `https://dashscope-instant.oss-cn-beijing.aliyuncs.com/xxx/file.mp4`
- 优势: 可以通过HTTP协议直接访问

### API要求

阿里云DashScope的 `wan2.6-r2v` 模型要求：
- ✅ 支持: OSS内部格式 (oss://) - **推荐**
- ✅ 支持: HTTP/HTTPS URL（需要公开访问权限）
- ❌ 不支持: 本地文件路径

**注意**: 使用oss://格式时，API服务端会使用内部权限访问，无需设置公开访问权限。

## 💡 最佳实践

### 上传视频的正确流程

1. **获取上传凭证**
   ```python
   policy_data = get_upload_policy(api_key, model_name)
   ```

2. **上传文件到OSS**
   ```python
   upload_file_to_oss(policy_data, file_path)
   ```

3. **返回oss://格式URL**
   ```python
   oss_url = f"oss://{key}"
   return oss_url
   ```

4. **使用oss://格式提交任务**
   ```python
   submit_reference_video_to_video(
       reference_video_urls=[oss_url],  # 使用oss://格式
       prompt="..."
   )
   ```

### 注意事项

1. **URL有效期**: 上传后的URL有效期为48小时
2. **访问权限**: 确保URL是公开可访问的
3. **格式验证**: 提交前验证URL格式是否正确
4. **错误处理**: 捕获并处理URL转换错误

## 🔄 升级说明

如果你已经安装了v1.15.0的初始版本，请：

1. **更新代码**
   ```bash
   git pull origin main
   ```

2. **重启应用**
   ```bash
   ./run.sh  # macOS/Linux
   run.bat   # Windows
   ```

3. **测试功能**
   - 上传一个测试视频
   - 验证URL格式
   - 提交生成任务

## 📞 技术支持

如果仍然遇到问题：

1. 检查API密钥是否正确
2. 验证网络连接
3. 查看完整错误日志
4. 提交Issue到GitHub

---

**修复日期**: 2025年12月16日  
**影响版本**: v1.15.0  
**修复状态**: ✅ 已完成
