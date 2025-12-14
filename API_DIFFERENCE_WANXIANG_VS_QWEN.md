# 万相 vs 通义千问 API差异说明

## 概述

万相（Wanxiang）模型和通义千问（Qwen）模型虽然都使用相同的API端点，但在请求参数结构上存在关键差异，主要体现在 `negative_prompt` 的位置和是否需要 `prompt_extend`、`watermark` 等参数。

## API端点（相同）

```
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis
```

## 核心差异对比

### 1. 请求参数结构

#### 万相模型（wan2.5/wan2.2系列）

```json
{
    "model": "wan2.2-t2i-flash",
    "input": {
        "prompt": "雪地，白色小教堂，极光，冬日场景，柔和的光线。",
        "negative_prompt": "人物"  // ✅ 在 input 中
    },
    "parameters": {
        "size": "1024*1024",
        "n": 1
        // ❌ 不需要 prompt_extend 和 watermark
    }
}
```

#### 通义千问模型（qwen-image系列）

```json
{
    "model": "qwen-image-plus",
    "input": {
        "prompt": "雪地，白色小教堂，极光，冬日场景，柔和的光线。"
        // ❌ negative_prompt 不在这里
    },
    "parameters": {
        "size": "1328*1328",
        "n": 1,
        "negative_prompt": "人物",  // ✅ 在 parameters 中
        "prompt_extend": true,      // ✅ 需要这个参数
        "watermark": false          // ✅ 需要这个参数
    }
}
```

### 2. 参数位置对比表

| 参数 | 万相模型 | 通义千问模型 |
|------|---------|-------------|
| **prompt** | input 中 | input 中 |
| **negative_prompt** | input 中 ✅ | parameters 中 ✅ |
| **size** | parameters 中 | parameters 中 |
| **n** | parameters 中 | parameters 中 |
| **prompt_extend** | ❌ 不需要 | ✅ 需要（parameters中） |
| **watermark** | ❌ 不需要 | ✅ 需要（parameters中） |

## 详细对比

### 万相模型API

#### 请求示例

```bash
curl -X POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis \
    -H 'X-DashScope-Async: enable' \
    -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
    -H 'Content-Type: application/json' \
    -d '{
    "model": "wan2.2-t2i-flash",
    "input": {
        "prompt": "雪地，白色小教堂，极光，冬日场景，柔和的光线。",
        "negative_prompt": "人物"
    },
    "parameters": {
        "size": "1024*1024",
        "n": 1
    }
}'
```

#### 成功响应

```json
{
    "output": {
        "task_status": "PENDING",
        "task_id": "0385dc79-5ff8-4d82-bcb6-xxxxxx"
    },
    "request_id": "4909100c-7b5a-9f92-bfe5-xxxxxx"
}
```

#### 任务成功结果

```json
{
    "request_id": "f767d108-7d50-908b-a6d9-xxxxxx",
    "output": {
        "task_id": "d492bffd-10b5-4169-b639-xxxxxx",
        "task_status": "SUCCEEDED",
        "submit_time": "2025-01-08 16:03:59.840",
        "scheduled_time": "2025-01-08 16:03:59.863",
        "end_time": "2025-01-08 16:04:10.660",
        "results": [
            {
                "orig_prompt": "原始提示词",
                "actual_prompt": "优化后的提示词",
                "url": "https://dashscope-result-wlcb.oss-cn-wulanchabu.aliyuncs.com/1.png"
            }
        ],
        "task_metrics": {
            "TOTAL": 1,
            "SUCCEEDED": 1,
            "FAILED": 0
        }
    },
    "usage": {
        "image_count": 1
    }
}
```

### 通义千问模型API

#### 请求示例

```bash
curl -X POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis \
    -H 'X-DashScope-Async: enable' \
    -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
    -H 'Content-Type: application/json' \
    -d '{
    "model": "qwen-image-plus",
    "input": {
        "prompt": "雪地，白色小教堂，极光，冬日场景，柔和的光线。"
    },
    "parameters": {
        "size": "1328*1328",
        "n": 1,
        "negative_prompt": "人物",
        "prompt_extend": true,
        "watermark": false
    }
}'
```

#### 响应格式

与万相模型相同，都是异步任务模式。

## 代码实现

### 智能判断模型类型

```python
def submit_task(self):
    """提交异步生成任务"""
    # 判断是否为万相模型（以wan开头）
    is_wanxiang = self.model.startswith('wan')
    
    if is_wanxiang:
        # 万相模型的API格式
        data = {
            "model": self.model,
            "input": {
                "prompt": self.prompt
            },
            "parameters": {
                "size": self.size,
                "n": 1
            }
        }
        
        # 万相模型：negative_prompt 在 input 中
        if self.negative_prompt:
            data["input"]["negative_prompt"] = self.negative_prompt
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
```

### 模型识别逻辑

```python
# 万相模型
is_wanxiang = model_id.startswith('wan')

# 万相模型示例
'wan2.5-t2i-preview'  → is_wanxiang = True
'wan2.2-t2i-flash'    → is_wanxiang = True
'wan2.2-t2i-plus'     → is_wanxiang = True

# 通义千问模型示例
'qwen-image-plus'     → is_wanxiang = False
'qwen-image'          → is_wanxiang = False
```

## 参数说明

### 共同参数

| 参数 | 类型 | 位置 | 说明 |
|------|------|------|------|
| model | string | 顶层 | 模型ID |
| prompt | string | input | 用户描述文本 |
| size | string | parameters | 图片分辨率（宽*高） |
| n | integer | parameters | 生成图片数量（通常为1） |

### 万相模型特有

| 参数 | 类型 | 位置 | 说明 |
|------|------|------|------|
| negative_prompt | string | input | 反向提示词（在input中） |

### 通义千问模型特有

| 参数 | 类型 | 位置 | 说明 |
|------|------|------|------|
| negative_prompt | string | parameters | 反向提示词（在parameters中） |
| prompt_extend | boolean | parameters | 是否启用提示词智能改写 |
| watermark | boolean | parameters | 是否添加水印 |

## 错误处理

### 异常响应（相同）

```json
{
    "code": "InvalidApiKey",
    "message": "Invalid API-key provided.",
    "request_id": "fb53c4ec-1c12-4fc4-a580-xxxxxx"
}
```

### 任务失败（相同）

```json
{
    "request_id": "e5d70b02-ebd3-98ce-9fe8-759d7d7b107d",
    "output": {
        "task_id": "86ecf553-d340-4e21-af6e-xxxxxx",
        "task_status": "FAILED",
        "code": "InvalidParameter",
        "message": "错误详细信息",
        "task_metrics": {
            "TOTAL": 4,
            "SUCCEEDED": 0,
            "FAILED": 4
        }
    }
}
```

### 部分失败（万相模型支持）

```json
{
    "request_id": "85eaba38-0185-99d7-8d16-xxxxxx",
    "output": {
        "task_id": "86ecf553-d340-4e21-af6e-xxxxxx",
        "task_status": "SUCCEEDED",
        "results": [
            {
                "url": "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/123/a1.png"
            },
            {
                "code": "InternalError.Timeout",
                "message": "An internal timeout error has occurred..."
            }
        ],
        "task_metrics": {
            "TOTAL": 2,
            "SUCCEEDED": 1,
            "FAILED": 1
        }
    },
    "usage": {
        "image_count": 1
    }
}
```

### 查询过期

```json
{
    "request_id": "a4de7c32-7057-9f82-8581-xxxxxx",
    "output": {
        "task_id": "502a00b1-19d9-4839-a82f-xxxxxx",
        "task_status": "UNKNOWN"
    }
}
```

## 最佳实践

### 1. 参数构建顺序

```python
# 步骤1：构建基础结构
data = {
    "model": model_id,
    "input": {"prompt": prompt},
    "parameters": {"size": size, "n": 1}
}

# 步骤2：根据模型类型添加特定参数
if is_wanxiang:
    # 万相模型
    if negative_prompt:
        data["input"]["negative_prompt"] = negative_prompt
else:
    # 通义千问模型
    data["parameters"]["prompt_extend"] = True
    data["parameters"]["watermark"] = False
    if negative_prompt:
        data["parameters"]["negative_prompt"] = negative_prompt
```

### 2. 模型类型判断

```python
def is_wanxiang_model(model_id):
    """判断是否为万相模型"""
    return model_id.startswith('wan')

# 使用示例
if is_wanxiang_model('wan2.5-t2i-preview'):
    # 使用万相API格式
    pass
else:
    # 使用通义千问API格式
    pass
```

### 3. 错误处理

```python
# 提交任务错误
if 'code' in result:
    error_code = result.get('code')
    error_msg = result.get('message')
    # InvalidApiKey, InvalidParameter, etc.
    handle_error(error_code, error_msg)

# 任务失败
if task_status == 'FAILED':
    error_code = result['output'].get('code')
    error_msg = result['output'].get('message')
    handle_task_failure(error_code, error_msg)

# 任务过期
if task_status == 'UNKNOWN':
    handle_task_expired()
```

## 常见问题

### Q1: 为什么两个模型的参数位置不同？

**A:** API设计演进导致：
- 万相模型是较新的API设计，将 `negative_prompt` 作为输入的一部分
- 通义千问模型沿用旧版设计，将 `negative_prompt` 作为生成参数

### Q2: 如果用错了参数位置会怎样？

**A:** 可能的结果：
```
1. API返回错误：InvalidParameter
2. 参数被忽略：不报错但不生效
3. 默认行为：使用默认值
```

### Q3: 是否可以混用参数？

**A:** 不建议：
```
❌ 万相模型 + parameters中的negative_prompt → 可能被忽略
❌ 通义千问 + input中的negative_prompt → 可能报错
✅ 严格按照模型类型使用对应格式
```

### Q4: 如何快速区分两种模型？

**A:** 通过模型ID前缀：
```
wan*  → 万相模型
qwen* → 通义千问模型
```

## 技术要点

### 兼容性设计

```python
class TextToImageAPI:
    """文生图API适配器"""
    
    def build_request(self, model, prompt, size, negative_prompt, **kwargs):
        """构建请求参数"""
        is_wanxiang = model.startswith('wan')
        
        # 基础结构
        request = {
            "model": model,
            "input": {"prompt": prompt},
            "parameters": {"size": size, "n": 1}
        }
        
        # 模型特定参数
        if is_wanxiang:
            self._apply_wanxiang_params(request, negative_prompt)
        else:
            self._apply_qwen_params(request, negative_prompt, **kwargs)
        
        return request
    
    def _apply_wanxiang_params(self, request, negative_prompt):
        """应用万相模型参数"""
        if negative_prompt:
            request["input"]["negative_prompt"] = negative_prompt
    
    def _apply_qwen_params(self, request, negative_prompt, prompt_extend=True, watermark=False):
        """应用通义千问模型参数"""
        request["parameters"]["prompt_extend"] = prompt_extend
        request["parameters"]["watermark"] = watermark
        if negative_prompt:
            request["parameters"]["negative_prompt"] = negative_prompt
```

### 单元测试

```python
def test_wanxiang_request_format():
    """测试万相模型请求格式"""
    api = TextToImageAPI()
    request = api.build_request(
        model="wan2.5-t2i-preview",
        prompt="测试",
        size="1280*1280",
        negative_prompt="人物"
    )
    
    # 断言
    assert "negative_prompt" in request["input"]
    assert "negative_prompt" not in request["parameters"]
    assert "prompt_extend" not in request["parameters"]

def test_qwen_request_format():
    """测试通义千问模型请求格式"""
    api = TextToImageAPI()
    request = api.build_request(
        model="qwen-image-plus",
        prompt="测试",
        size="1328*1328",
        negative_prompt="人物"
    )
    
    # 断言
    assert "negative_prompt" in request["parameters"]
    assert "negative_prompt" not in request["input"]
    assert "prompt_extend" in request["parameters"]
    assert "watermark" in request["parameters"]
```

## 升级总结

### ✅ 核心改进

1. **智能识别模型类型** - 通过模型ID前缀判断
2. **动态构建请求参数** - 根据模型类型使用不同格式
3. **向后兼容** - 同时支持两种模型
4. **代码简洁** - 统一的API调用接口

### 📊 对比总结

| 特性 | 万相模型 | 通义千问模型 |
|------|---------|-------------|
| **API端点** | 相同 | 相同 |
| **异步模式** | 相同 | 相同 |
| **negative_prompt位置** | input ✅ | parameters ✅ |
| **prompt_extend** | ❌ 不需要 | ✅ 需要 |
| **watermark** | ❌ 不需要 | ✅ 需要 |
| **识别方式** | model.startswith('wan') | model.startswith('qwen') |

### 🎯 开发建议

1. **统一封装** - 使用适配器模式封装API差异
2. **类型判断** - 明确的模型类型识别逻辑
3. **参数验证** - 确保参数位置正确
4. **错误处理** - 详细的错误信息提示
5. **单元测试** - 覆盖两种模型的调用场景

---

**版本**: v1.9.0  
**更新日期**: 2025-12-12  
**兼容性**: ✅ 万相模型 + 通义千问模型

**智能适配，无缝切换！** 🔄✨
