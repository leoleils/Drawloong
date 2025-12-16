# OSS URL格式说明

## 为什么使用 oss:// 格式？

在参考生视频功能中，我们使用 `oss://` 格式的URL而不是HTTP URL，原因如下：

### 1. 权限管理

**oss:// 格式的优势**:
- ✅ API服务端使用内部权限访问OSS
- ✅ 无需设置文件公开访问权限
- ✅ 更安全，避免文件被公开访问
- ✅ 避免403 Forbidden错误

**HTTP URL的问题**:
- ❌ 需要文件有公开读权限
- ❌ 可能遇到403 Forbidden错误
- ❌ 安全性较低
- ❌ 需要额外配置ACL权限

### 2. URL格式对比

#### oss:// 格式
```
oss://dashscope-instant/f5489a0a93fd726480c44067ac773413/2025-12-16/xxx.mp4
```

**特点**:
- 内部格式，仅供API服务端使用
- 服务端有完整的OSS访问权限
- 无需担心权限问题

#### HTTP URL格式
```
https://dashscope-file-mgr.oss-cn-beijing.aliyuncs.com/dashscope-instant/f5489a0a93fd726480c44067ac773413/2025-12-16/xxx.mp4
```

**特点**:
- 公开访问格式
- 需要文件有公开读权限
- 可能遇到403错误

### 3. 阿里云最佳实践

根据阿里云DashScope的文档和最佳实践：

1. **文件上传流程**:
   ```
   本地文件 → 上传到OSS → 返回oss://格式 → 提交给API
   ```

2. **API处理流程**:
   ```
   接收oss://URL → 使用内部权限访问 → 处理文件 → 返回结果
   ```

3. **为什么这样设计**:
   - 安全性：避免文件公开暴露
   - 简单性：无需管理复杂的权限
   - 可靠性：避免权限相关的错误

### 4. 常见误区

#### 误区1：认为API需要HTTP URL
**错误**: 将oss://转换为HTTP URL
**正确**: 直接使用oss://格式

#### 误区2：认为oss://格式不被支持
**错误**: "No connection adapters were found for 'oss://...'"
**原因**: 这是客户端代码尝试访问oss://URL导致的，应该直接传递给API
**正确**: 不要在客户端尝试访问oss://URL，直接传递给API

#### 误区3：尝试设置公开访问权限
**错误**: 修改OSS文件的ACL为public-read
**问题**: 安全风险，且不必要
**正确**: 使用oss://格式，让API服务端处理

### 5. 实现细节

#### 上传代码
```python
def upload_video_and_get_url(self, video_path: str, model_name: str) -> str:
    # 1. 获取上传凭证
    policy_data = get_upload_policy(api_key, model_name)
    
    # 2. 上传文件到OSS
    key = f"{policy_data['upload_dir']}/{file_name}"
    upload_file_to_oss(policy_data, video_path, key)
    
    # 3. 返回oss://格式（重要！）
    oss_url = f"oss://{key}"
    return oss_url  # 不要转换为HTTP URL
```

#### 提交任务代码
```python
def submit_reference_video_to_video(self, reference_video_urls: list, ...):
    payload = {
        "model": "wan2.6-r2v",
        "input": {
            "prompt": prompt,
            "reference_video_urls": reference_video_urls  # 直接使用oss://格式
        },
        ...
    }
    
    # 重要：使用oss://格式时，必须添加特殊请求头
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'X-DashScope-Async': 'enable',
        'X-DashScope-OssResourceResolve': 'enable'  # 启用OSS资源解析
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
```

### 6. 关键要点：OSS资源解析请求头

**最重要的一点**: 使用 `oss://` 格式时，必须在请求头中添加：
```
X-DashScope-OssResourceResolve: enable
```

**示例**:
```bash
curl -X POST https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -H 'X-DashScope-Async: enable' \
  -H 'X-DashScope-OssResourceResolve: enable' \
  -d '{ ... }'
```

**为什么需要这个请求头？**
- 告诉API服务端需要解析OSS资源
- 启用内部OSS访问权限
- 没有这个请求头，API无法访问oss://格式的URL

### 7. 错误排查

#### 如果遇到 "No connection adapters" 错误
**原因**: 客户端代码尝试访问oss://URL
**检查**: 
- 是否在客户端代码中尝试下载或访问oss://URL？
- 是否正确地将URL传递给API而不是自己处理？

**解决**:
- 确保oss://URL直接传递给API
- 不要在客户端使用requests访问oss://URL
- 确保添加了 `X-DashScope-OssResourceResolve: enable` 请求头

#### 如果遇到 403 Forbidden 错误
**原因**: 使用了HTTP URL但文件没有公开权限，或者缺少OSS资源解析请求头
**解决**: 
- 改用oss://格式
- 添加 `X-DashScope-OssResourceResolve: enable` 请求头
- 不要转换为HTTP URL

### 7. 测试验证

#### 正确的测试流程
1. 上传视频文件
2. 获取oss://格式的URL
3. 直接将oss://URL传递给API
4. 验证任务提交成功

#### 验证URL格式
```python
# 正确的URL格式
assert url.startswith('oss://'), "URL应该以oss://开头"

# 错误的URL格式
assert not url.startswith('https://'), "不应该使用HTTP URL"
```

### 8. 总结

| 方面 | oss:// 格式 | HTTP URL |
|------|------------|----------|
| **权限管理** | ✅ 简单 | ❌ 复杂 |
| **安全性** | ✅ 高 | ❌ 低 |
| **可靠性** | ✅ 高 | ❌ 可能403 |
| **推荐度** | ✅ 推荐 | ❌ 不推荐 |

**结论**: 始终使用 `oss://` 格式，让API服务端处理文件访问。

---

## 参考资料

- [阿里云OSS文档](https://help.aliyun.com/product/31815.html)
- [DashScope API文档](https://help.aliyun.com/zh/dashscope/)
- [文件上传最佳实践](https://help.aliyun.com/zh/dashscope/developer-reference/file-upload)

---

**更新日期**: 2025年12月16日
