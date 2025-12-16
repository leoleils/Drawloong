# 参考生视频功能说明

## 功能概述

参考生视频（Reference Video to Video）功能允许用户上传参考视频，通过文本提示词生成新的视频。该功能基于阿里云万相2.6-r2v模型，可以参考视频中的主体和音色来生成新视频。

## 模型信息

- **模型名称**: `wan2.6-r2v`
- **API接口**: `https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
- **调用方式**: 异步调用（需要轮询任务状态）

## 功能特点

### 1. 参考视频支持
- 支持上传1-2个参考视频
- 视频格式：mp4、mov
- 视频时长：2～30秒
- 文件大小：单个视频不超过100MB
- 支持本地文件上传（通过上传接口获取临时URL）

### 2. 角色识别
- 使用 `character1` 指代第一段参考视频中的主体
- 使用 `character2` 指代第二段参考视频中的主体
- 模型仅通过此方式识别多视频中的不同角色

### 3. 视频生成参数

#### 提示词（prompt）
- **必选参数**
- 描述生成视频中期望包含的元素和视觉特点
- 支持中英文
- 长度限制：不超过1500个字符
- 示例：`character1在沙发上开心地看电影`

#### 反向提示词（negative_prompt）
- **可选参数**
- 描述不希望在视频画面中看到的内容
- 支持中英文
- 长度限制：不超过500个字符
- 示例：`低分辨率、错误、最差质量、低质量、残缺、多余的手指、比例不良`

#### 分辨率（size）
- **可选参数**
- 默认值：`1920*1080`（1080P）
- 格式：宽*高（如 `1280*720`）

**720P档位可选分辨率：**
- `1280*720`：16:9
- `720*1280`：9:16
- `960*960`：1:1
- `1088*832`：4:3
- `832*1088`：3:4

**1080P档位可选分辨率：**
- `1920*1080`：16:9
- `1080*1920`：9:16
- `1440*1440`：1:1
- `1632*1248`：4:3
- `1248*1632`：3:4

#### 视频时长（duration）
- **可选参数**
- 可选值：5、10（秒）
- 默认值：5秒

#### 镜头类型（shot_type）
- **可选参数**
- `single`：默认值，输出单镜头视频
- `multi`：输出多镜头视频
- 优先级：shot_type > prompt

#### 音频（audio）
- **可选参数**
- `true`：生成带音频的视频
- `false`：生成无音频的视频
- 默认值：true

#### 随机种子（seed）
- **可选参数**
- 取值范围：[0, 2147483647]
- 用于提升生成结果的可复现性

## API调用示例

### 1. 提交视频生成任务

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
-H 'X-DashScope-Async: enable' \
-H 'X-DashScope-OssResourceResolve: enable' \
-H "Authorization: Bearer $DASHSCOPE_API_KEY" \
-H 'Content-Type: application/json' \
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

**重要**: 当使用 `oss://` 格式的URL时，必须在请求头中添加 `X-DashScope-OssResourceResolve: enable`，否则API无法访问OSS资源。

### 2. 成功响应

```json
{
  "output": {
    "task_status": "PENDING",
    "task_id": "0385dc79-5ff8-4d82-bcb6-xxxxxx"
  },
  "request_id": "4909100c-7b5a-9f92-bfe5-xxxxxx"
}
```

### 3. 查询任务结果

```bash
curl -X GET https://dashscope.aliyuncs.com/api/v1/tasks/86ecf553-d340-4e21-xxxxxxxxx \
--header "Authorization: Bearer $DASHSCOPE_API_KEY"
```

### 4. 任务成功响应

```json
{
  "request_id": "caa62a12-8841-41a6-8af2-xxxxxx",
  "output": {
    "task_id": "eff1443c-ccab-4676-aad3-xxxxxx",
    "task_status": "SUCCEEDED",
    "submit_time": "2025-12-16 00:25:59.869",
    "scheduled_time": "2025-12-16 00:25:59.900",
    "end_time": "2025-12-16 00:30:35.396",
    "orig_prompt": "character1在沙发上开心的看电影",
    "video_url": "https://dashscope-result-sh.oss-accelerate.aliyuncs.com/xxx.mp4?Expires=xxx"
  },
  "usage": {
    "duration": 10.0,
    "size": "1280*720",
    "input_video_duration": 5,
    "output_video_duration": 5,
    "video_count": 1,
    "SR": 720
  }
}
```

### 5. 任务失败响应

```json
{
  "request_id": "e5d70b02-ebd3-98ce-9fe8-759d7d7b107d",
  "output": {
    "task_id": "86ecf553-d340-4e21-af6e-a0c6a421c010",
    "task_status": "FAILED",
    "code": "InvalidParameter",
    "message": "The size is not match xxxxxx"
  }
}
```

## 文件上传接口

如果需要上传本地视频文件，需要先通过上传接口获取临时URL。

### Python示例代码

```python
import os
import requests
from pathlib import Path
from datetime import datetime, timedelta

def get_upload_policy(api_key, model_name):
    """获取文件上传凭证"""
    url = "https://dashscope.aliyuncs.com/api/v1/uploads"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "action": "getPolicy",
        "model": model_name
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to get upload policy: {response.text}")
    return response.json()['data']

def upload_file_to_oss(policy_data, file_path):
    """将文件上传到临时存储OSS"""
    file_name = Path(file_path).name
    key = f"{policy_data['upload_dir']}/{file_name}"
    
    with open(file_path, 'rb') as file:
        files = {
            'OSSAccessKeyId': (None, policy_data['oss_access_key_id']),
            'Signature': (None, policy_data['signature']),
            'policy': (None, policy_data['policy']),
            'x-oss-object-acl': (None, policy_data['x_oss_object_acl']),
            'x-oss-forbid-overwrite': (None, policy_data['x_oss_forbid_overwrite']),
            'key': (None, key),
            'success_action_status': (None, '200'),
            'file': (file_name, file)
        }
        response = requests.post(policy_data['upload_host'], files=files)
        if response.status_code != 200:
            raise Exception(f"Failed to upload file: {response.text}")
    
    return f"oss://{key}"

def upload_file_and_get_url(api_key, model_name, file_path):
    """上传文件并获取URL"""
    # 1. 获取上传凭证
    policy_data = get_upload_policy(api_key, model_name)
    
    # 2. 上传文件到OSS
    oss_url = upload_file_to_oss(policy_data, file_path)
    
    # 3. 返回oss://格式的URL
    # API服务端会使用内部权限访问OSS文件
    # 不需要转换为HTTP URL
    return oss_url

# 使用示例
if __name__ == "__main__":
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise Exception("请设置DASHSCOPE_API_KEY环境变量")
    
    model_name = "wan2.6-r2v"
    file_path = "/path/to/video.mp4"
    
    try:
        public_url = upload_file_and_get_url(api_key, model_name, file_path)
        expire_time = datetime.now() + timedelta(hours=48)
        print(f"文件上传成功，有效期为48小时")
        print(f"过期时间: {expire_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"临时URL: {public_url}")
    except Exception as e:
        print(f"Error: {str(e)}")
```

## 使用流程

1. **准备参考视频**
   - 确保视频格式为mp4或mov
   - 视频时长在2-30秒之间
   - 文件大小不超过100MB

2. **上传视频获取URL**（如果是本地文件）
   - 调用上传接口获取上传凭证
   - 上传文件到OSS
   - 获取临时URL（有效期48小时）

3. **编写提示词**
   - 使用 `character1` 指代第一个参考视频中的主体
   - 使用 `character2` 指代第二个参考视频中的主体（如有）
   - 描述期望的视频内容和效果

4. **配置生成参数**
   - 选择合适的分辨率
   - 设置视频时长（5秒或10秒）
   - 选择镜头类型（单镜头或多镜头）
   - 决定是否包含音频

5. **提交任务**
   - 调用API提交异步任务
   - 获取task_id

6. **轮询任务状态**
   - 每隔几秒查询一次任务状态
   - 等待任务完成（SUCCEEDED）或失败（FAILED）

7. **下载生成的视频**
   - 从响应中获取video_url
   - 下载视频到本地

## 注意事项

1. **参考视频要求**
   - 视频质量会影响生成效果
   - 建议使用清晰、主体明确的视频
   - 避免使用过于复杂的场景

2. **提示词编写**
   - 必须使用 `character1`、`character2` 来指代参考视频中的主体
   - 提示词要清晰、具体
   - 避免过于抽象或模糊的描述

3. **分辨率选择**
   - 必须设置为具体数值（如 `1280*720`）
   - 不能使用比例（如 `1:1`）或档位名称（如 `480P`）

4. **任务轮询**
   - 视频生成通常需要几分钟
   - 建议每5秒查询一次任务状态
   - 设置合理的超时时间（如15分钟）

5. **临时URL有效期**
   - 上传文件获取的临时URL有效期为48小时
   - 生成的视频URL也有过期时间
   - 建议及时下载保存

## 错误处理

### 常见错误码

- `InvalidApiKey`: API密钥无效
- `InvalidParameter`: 参数错误（如分辨率格式不正确）
- `ResourceNotFound`: 资源不存在（如参考视频URL无效）
- `QuotaExceeded`: 配额超限
- `InternalError`: 内部错误

### 错误处理建议

1. 检查API密钥是否正确配置
2. 验证所有参数格式是否符合要求
3. 确认参考视频URL可访问
4. 检查账户配额是否充足
5. 遇到内部错误时可以重试

## 应用场景

1. **角色动画生成**
   - 使用角色视频作为参考
   - 生成不同场景下的角色动画

2. **视频风格迁移**
   - 参考特定风格的视频
   - 生成相似风格的新视频

3. **虚拟主播**
   - 使用主播视频作为参考
   - 生成不同内容的主播视频

4. **产品展示**
   - 参考产品演示视频
   - 生成不同角度或场景的展示视频

## 技术支持

- 阿里云DashScope文档：https://help.aliyun.com/zh/dashscope/
- API密钥获取：https://dashscope.console.aliyun.com/
