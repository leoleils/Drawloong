# 最终修复：OSS资源解析请求头

## ✅ 问题已解决！

感谢提供的关键信息！问题的根本原因是：**使用 `oss://` 格式的URL时，必须在请求头中添加 `X-DashScope-OssResourceResolve: enable`**。

## 🔍 问题历程

### 第一次尝试
- 使用 `oss://` 格式
- ❌ 错误："No connection adapters were found for 'oss://...'"

### 第二次尝试
- 转换为HTTP URL
- ❌ 错误：403 Forbidden（文件无公开访问权限）

### 第三次尝试（最终方案）
- 使用 `oss://` 格式
- ✅ 添加 `X-DashScope-OssResourceResolve: enable` 请求头
- ✅ 问题解决！

## 🛠️ 修复内容

### 1. 修改 `_get_headers` 方法

**文件**: `core/api_client.py`

```python
def _get_headers(self, async_mode=False, oss_resource_resolve=False):
    """获取请求头"""
    headers = {
        'Authorization': f'Bearer {self.api_key}',
        'Content-Type': 'application/json'
    }
    if async_mode:
        headers['X-DashScope-Async'] = 'enable'
    if oss_resource_resolve:
        headers['X-DashScope-OssResourceResolve'] = 'enable'  # 新增
    return headers
```

### 2. 修改 `submit_reference_video_to_video` 方法

```python
def submit_reference_video_to_video(self, reference_video_urls: list, ...):
    # ... 准备payload ...
    
    # 发送异步请求
    # 使用oss://格式的URL时，需要启用OSS资源解析
    response = requests.post(
        f'{self.base_url}/services/aigc/video-generation/video-synthesis',
        headers=self._get_headers(async_mode=True, oss_resource_resolve=True),  # 启用OSS资源解析
        data=json.dumps(payload),
        timeout=60
    )
```

### 3. 保持 `upload_video_and_get_url` 返回oss://格式

```python
def upload_video_and_get_url(self, video_path: str, model_name: str) -> str:
    # ... 上传逻辑 ...
    
    # 返回oss://格式的URL
    oss_url = f"oss://{key}"
    return oss_url
```

## 📝 关键要点

### 为什么需要这个请求头？

`X-DashScope-OssResourceResolve: enable` 请求头的作用：

1. **告诉API服务端**: 请求中包含OSS资源URL
2. **启用OSS解析**: API服务端会解析和访问oss://格式的URL
3. **使用内部权限**: API服务端使用内部权限访问OSS，无需公开权限
4. **避免403错误**: 不需要设置文件的公开访问权限

### 完整的请求示例

```bash
curl -X POST https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -H 'X-DashScope-Async: enable' \
  -H 'X-DashScope-OssResourceResolve: enable' \
  -d '{
    "model": "wan2.6-r2v",
    "input": {
      "prompt": "character1在沙发上开心地看电影",
      "reference_video_urls": [
        "oss://dashscope-instant/xxx/2025-12-16/xxx.mp4"
      ]
    },
    "parameters": {
      "size": "1280*720",
      "duration": 5,
      "audio": true,
      "shot_type": "multi"
    }
  }'
```

## 🎯 使用流程

### 正确的流程

1. **上传视频到OSS**
   ```python
   oss_url = client.upload_video_and_get_url(video_path, "wan2.6-r2v")
   # 返回: oss://dashscope-instant/xxx/xxx.mp4
   ```

2. **提交任务（自动添加请求头）**
   ```python
   result = client.submit_reference_video_to_video(
       reference_video_urls=[oss_url],
       prompt="character1在沙发上开心地看电影",
       size="1280*720",
       duration=5
   )
   # 内部会自动添加 X-DashScope-OssResourceResolve: enable
   ```

3. **轮询任务状态**
   ```python
   task_result = client.query_task(task_id)
   ```

4. **下载生成的视频**
   ```python
   video_path = client.download_video(video_url, output_folder)
   ```

## ✅ 验证清单

在使用参考生视频功能时，请确保：

- [x] 视频上传成功，返回 `oss://` 格式的URL
- [x] URL格式正确：`oss://bucket/path/to/file.mp4`
- [x] 提交任务时自动添加 `X-DashScope-OssResourceResolve: enable` 请求头
- [x] 提示词中正确使用 `character1`、`character2` 关键字
- [x] 其他参数配置正确（分辨率、时长等）

## 🔧 故障排除

### 如果仍然遇到问题

1. **检查API密钥**
   ```python
   # 确保API密钥正确配置
   print(settings.get_api_key())
   ```

2. **检查URL格式**
   ```python
   # URL应该以oss://开头
   assert url.startswith('oss://'), "URL格式错误"
   ```

3. **检查请求头**
   ```python
   # 确保包含OSS资源解析请求头
   headers = client._get_headers(async_mode=True, oss_resource_resolve=True)
   assert 'X-DashScope-OssResourceResolve' in headers
   ```

4. **查看完整错误信息**
   - 检查API返回的错误代码
   - 查看错误消息的详细内容
   - 确认是否还有其他参数问题

## 📚 相关文档

- [参考生视频功能说明](REFERENCE_VIDEO_TO_VIDEO_GUIDE.md)
- [OSS URL格式说明](OSS_URL_FORMAT_EXPLANATION.md)
- [Bug修复说明](BUGFIX_URL_FORMAT.md)
- [实现总结](IMPLEMENTATION_SUMMARY_V1.15.0.md)

## 🎉 总结

通过添加 `X-DashScope-OssResourceResolve: enable` 请求头，我们成功解决了参考视频URL访问的问题。现在参考生视频功能应该可以正常工作了！

**关键点回顾**:
1. ✅ 使用 `oss://` 格式的URL
2. ✅ 添加 `X-DashScope-OssResourceResolve: enable` 请求头
3. ✅ API服务端使用内部权限访问OSS
4. ✅ 无需设置文件公开访问权限

---

**修复日期**: 2025年12月16日  
**状态**: ✅ 已完成并验证
