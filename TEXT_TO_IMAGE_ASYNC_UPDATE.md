# 文生图异步调用升级说明

## 升级概述

文生图功能已从同步调用升级为异步调用模式，提升了系统稳定性和用户体验。

## 核心改进

### 🔄 调用模式对比

#### 之前（同步模式）
```
提交请求 → 等待生成 → 返回结果
  ↓         (阻塞60秒)     ↓
用户等待    界面无响应    获得图片
```

**问题：**
- ❌ 长时间阻塞（最多60秒）
- ❌ 界面无响应
- ❌ 容易超时失败
- ❌ 无法获取进度

#### 现在（异步模式）
```
提交任务 → 获取task_id → 轮询状态 → 下载图片
  ↓           ↓              ↓           ↓
即时响应    立即返回      实时更新    获得结果
```

**优势：**
- ✅ 快速响应（1-2秒）
- ✅ 实时进度反馈
- ✅ 不易超时
- ✅ 更加稳定

## API调用变化

### 1. 提交任务（新增）

**请求：**
```bash
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis
Headers:
  X-DashScope-Async: enable  # 启用异步模式
  Authorization: Bearer $DASHSCOPE_API_KEY
  Content-Type: application/json

Body:
{
    "model": "qwen-image-plus",
    "input": {
        "prompt": "用户描述文本"
    },
    "parameters": {
        "size": "1328*1328",
        "n": 1,
        "prompt_extend": true,
        "watermark": false
    }
}
```

**成功响应：**
```json
{
    "output": {
        "task_status": "PENDING",
        "task_id": "0385dc79-5ff8-4d82-bcb6-xxxxxx"
    },
    "request_id": "4909100c-7b5a-9f92-bfe5-xxxxxx"
}
```

**异常响应：**
```json
{
    "code": "InvalidApiKey",
    "message": "Invalid API-key provided.",
    "request_id": "fb53c4ec-1c12-4fc4-a580-xxxxxx"
}
```

### 2. 查询任务状态（新增）

**请求：**
```bash
GET https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}
Headers:
  Authorization: Bearer $DASHSCOPE_API_KEY
```

**任务成功响应：**
```json
{
    "request_id": "cf4a3304-fa4d-97b6-bc72-xxxxxx",
    "output": {
        "task_id": "18e7cde0-8c17-42aa-afc5-xxxxxx",
        "task_status": "SUCCEEDED",
        "submit_time": "2025-09-05 11:33:20.542",
        "scheduled_time": "2025-09-05 11:33:20.581",
        "end_time": "2025-09-05 11:33:40.807",
        "results": [
            {
                "orig_prompt": "原始提示词",
                "actual_prompt": "优化后的提示词",
                "url": "https://dashscope-result-sz.oss-cn-shenzhen.aliyuncs.com/7d/xxx.png"
            }
        ]
    },
    "usage": {
        "image_count": 1
    }
}
```

**任务失败响应：**
```json
{
    "request_id": "c61fe158-c0de-40f0-b4d9-964625119ba4",
    "output": {
        "task_id": "86ecf553-d340-4e21-xxxxxxxxx",
        "task_status": "FAILED",
        "submit_time": "2025-11-11 11:46:28.116",
        "scheduled_time": "2025-11-11 11:46:28.154",
        "end_time": "2025-11-11 11:46:28.255",
        "code": "InvalidParameter",
        "message": "错误详细信息"
    }
}
```

### 3. 下载图片（保持）

**请求：**
```python
GET {results[0].url}
# 图片URL有效期限制，需及时下载
```

## 代码实现

### 工作线程升级

```python
class TextToImageWorker(QThread):
    """文生图工作线程（异步模式）"""
    
    finished = pyqtSignal(str, str)   # image_url, output_path
    error = pyqtSignal(str)           # error_message
    progress = pyqtSignal(str)        # 新增：进度信息
    
    def run(self):
        """执行文生图任务（异步）"""
        # 1. 提交异步任务
        task_id = self.submit_task()
        
        # 2. 轮询任务状态
        image_url = self.poll_task_status(task_id)
        
        # 3. 下载图片
        output_path = self.download_image(image_url)
        
        # 4. 发送完成信号
        self.finished.emit(image_url, output_path)
```

### 提交任务方法

```python
def submit_task(self):
    """提交异步生成任务"""
    url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {self.api_client.api_key}',
        'X-DashScope-Async': 'enable'  # 关键：启用异步
    }
    
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
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    return result['output']['task_id']
```

### 轮询任务状态

```python
def poll_task_status(self, task_id):
    """轮询任务状态直到完成"""
    url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}'
    
    max_retries = 60  # 最多等待60次（约2分钟）
    retry_count = 0
    
    while retry_count < max_retries:
        response = requests.get(url, headers=headers)
        result = response.json()
        
        task_status = result['output']['task_status']
        
        if task_status == 'SUCCEEDED':
            # 任务成功，返回图片URL
            return result['output']['results'][0]['url']
        
        elif task_status == 'FAILED':
            # 任务失败
            raise Exception(result['output']['message'])
        
        elif task_status in ['PENDING', 'RUNNING']:
            # 任务进行中，继续等待
            retry_count += 1
            time.sleep(2)  # 等待2秒后重试
        
        else:
            raise Exception(f"未知任务状态: {task_status}")
    
    raise Exception("任务超时")
```

### 进度反馈（新增）

```python
def on_generation_progress(self, status_msg):
    """生成进度更新"""
    self.status_label.setText(status_msg)

# 在worker中发送进度
self.progress.emit("正在提交生成任务...")
self.progress.emit("任务已提交，正在生成图片...")
self.progress.emit("正在下载图片...")
```

## UI改进

### 新增状态标签

```python
# 状态标签
self.status_label = QLabel("")
self.status_label.setStyleSheet("""
    QLabel {
        color: #666;
        font-size: 12px;
        padding: 5px;
    }
""")
self.status_label.setWordWrap(True)
group_layout.addWidget(self.status_label)
```

### 状态显示示例

```
正在提交生成任务...
  ↓
任务已提交，ID: 0385dc79-5ff8-4d82-bcb6-xxxxxx
正在生成图片...
  ↓
正在下载图片...
  ↓
✅ 生成成功！
```

## 任务状态流转

```
PENDING（待处理）
    ↓
RUNNING（生成中）
    ↓
  ┌─────┴─────┐
  ↓           ↓
SUCCEEDED   FAILED
（成功）    （失败）
```

### 状态说明

| 状态 | 说明 | 处理 |
|------|------|------|
| PENDING | 任务已提交，等待处理 | 继续轮询 |
| RUNNING | 任务正在生成中 | 继续轮询 |
| SUCCEEDED | 任务成功完成 | 获取图片URL |
| FAILED | 任务失败 | 显示错误信息 |

## 轮询策略

### 参数配置

```python
max_retries = 60      # 最多轮询60次
retry_interval = 2    # 每次间隔2秒
max_wait_time = 120秒 # 最长等待2分钟
```

### 轮询流程

```
提交任务 → 获取task_id
    ↓
第1次查询（0秒）→ PENDING → 等待2秒
    ↓
第2次查询（2秒）→ RUNNING → 等待2秒
    ↓
第3次查询（4秒）→ RUNNING → 等待2秒
    ↓
...（持续轮询）
    ↓
第N次查询 → SUCCEEDED → 获取图片
```

### 超时处理

```python
if retry_count >= max_retries:
    self.error.emit("任务超时，请稍后重试")
    return None
```

## 错误处理

### 1. 提交任务错误

**场景：**
- API密钥无效
- 请求参数错误
- 网络连接失败

**处理：**
```python
if 'code' in result:
    error_msg = result.get('message', 'Unknown error')
    self.error.emit(f"提交任务失败: {error_msg}")
    return None
```

### 2. 任务失败

**场景：**
- 提示词违规
- 参数不合法
- 系统内部错误

**处理：**
```python
if task_status == 'FAILED':
    error_code = result['output'].get('code', '')
    error_msg = result['output'].get('message', '未知错误')
    self.error.emit(f"生成失败: [{error_code}] {error_msg}")
```

### 3. 超时错误

**场景：**
- 任务长时间未完成
- 网络不稳定

**处理：**
```python
if retry_count >= max_retries:
    self.error.emit("任务超时，请稍后重试")
```

## 性能优化

### 异步优势

**响应时间：**
```
同步模式：10-60秒
异步模式：1-2秒（提交任务）
```

**稳定性：**
```
同步模式：容易超时
异步模式：可靠轮询，不易失败
```

**用户体验：**
```
同步模式：界面阻塞，无反馈
异步模式：实时进度，可感知
```

### 资源占用

**网络请求：**
```
同步模式：1次请求（60秒）
异步模式：1次提交 + N次查询（每次2秒）
```

**平均轮询次数：**
```
快速场景：5-10次（10-20秒）
正常场景：10-20次（20-40秒）
慢速场景：20-40次（40-80秒）
```

## 使用体验

### 用户视角

**之前：**
```
点击"生成图片" 
    ↓
按钮变灰，显示"生成中..."
    ↓
（等待30-60秒，无任何反馈）
    ↓
弹窗显示成功/失败
```

**现在：**
```
点击"生成图片"
    ↓
按钮变灰，显示"生成中..."
    ↓
状态：正在提交生成任务...（1秒）
    ↓
状态：任务已提交，ID: xxx
      正在生成图片...（实时更新）
    ↓
状态：正在下载图片...（2秒）
    ↓
状态：✅ 生成成功！
    ↓
弹窗显示成功，图片显示在画廊
```

## 兼容性说明

### API版本

```
旧版API（同步）：
https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation

新版API（异步）：
https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis
```

### 参数变化

**旧版：**
```json
{
    "model": "qwen-image-plus",
    "input": {
        "messages": [{
            "role": "user",
            "content": [{"text": "提示词"}]
        }]
    },
    "parameters": {
        "negative_prompt": "",
        "prompt_extend": true,
        "watermark": false,
        "size": "1328*1328"
    }
}
```

**新版：**
```json
{
    "model": "qwen-image-plus",
    "input": {
        "prompt": "提示词"  // 简化了结构
    },
    "parameters": {
        "size": "1328*1328",
        "n": 1,  // 新增：生成数量
        "prompt_extend": true,
        "watermark": false,
        "negative_prompt": ""  // 可选参数
    }
}
```

## 最佳实践

### 1. 合理设置轮询间隔

```python
# ✅ 推荐：2秒间隔
time.sleep(2)

# ❌ 不推荐：太频繁
time.sleep(0.5)  # 浪费资源

# ❌ 不推荐：太慢
time.sleep(5)    # 响应慢
```

### 2. 设置合理超时

```python
# ✅ 推荐：60次 * 2秒 = 120秒
max_retries = 60

# ❌ 不推荐：过短
max_retries = 10  # 20秒就超时，太短

# ❌ 不推荐：过长
max_retries = 200  # 400秒太长
```

### 3. 提供进度反馈

```python
# ✅ 推荐：详细的进度信息
self.progress.emit("任务已提交，ID: xxx")
self.progress.emit("正在生成图片...")

# ❌ 不推荐：无反馈
# 静默等待
```

## 常见问题

### Q1: 为什么要改为异步？

**A:** 异步模式的优势：
```
1. 快速响应 - 1-2秒即可提交任务
2. 实时反馈 - 显示任务进度
3. 更稳定 - 不易超时失败
4. 用户体验好 - 有进度感知
```

### Q2: 轮询会不会浪费资源？

**A:** 不会，理由：
```
1. 间隔合理 - 每2秒查询一次
2. 请求轻量 - 只是状态查询
3. 有超时限制 - 最多120秒
4. 比同步阻塞更省资源
```

### Q3: 任务超时怎么办？

**A:** 处理方案：
```
1. 检查网络连接
2. 检查API密钥
3. 稍后重试
4. 联系技术支持（如果持续失败）
```

### Q4: 如何调整等待时间？

**A:** 修改轮询参数：
```python
# 调整最大重试次数
max_retries = 60  # 增大/减小此值

# 调整轮询间隔
time.sleep(2)     # 调整间隔时间
```

## 技术细节

### 信号连接

```python
# 新增progress信号
self.worker.progress.connect(self.on_generation_progress)

# 接收进度更新
def on_generation_progress(self, status_msg):
    self.status_label.setText(status_msg)
```

### 异常处理链

```
提交任务异常 → error信号 → 显示错误
    ↓
查询状态异常 → error信号 → 显示错误
    ↓
下载图片异常 → error信号 → 显示错误
    ↓
任务失败 → error信号 → 显示错误
```

### 并发控制

```python
# 禁用按钮防止重复提交
self.generate_btn.setEnabled(False)
self.generate_btn.setText("生成中...")

# 完成后恢复
self.generate_btn.setEnabled(True)
self.generate_btn.setText("生成图片")
```

## 升级总结

### ✅ 核心改进

1. **调用模式** - 从同步改为异步
2. **API接口** - 使用新版text2image接口
3. **轮询机制** - 实现任务状态轮询
4. **进度反馈** - 新增实时状态显示
5. **错误处理** - 更详细的错误信息

### 📊 效果对比

| 指标 | 同步模式 | 异步模式 |
|------|---------|---------|
| 响应时间 | 10-60秒 | 1-2秒 |
| 稳定性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 用户体验 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 进度反馈 | ❌ 无 | ✅ 有 |
| 超时风险 | ⭐⭐⭐⭐ | ⭐ |

### 🎯 用户价值

- ✅ **更快响应** - 任务提交1-2秒完成
- ✅ **实时反馈** - 知道任务进度
- ✅ **更稳定** - 不易超时失败
- ✅ **体验更好** - 有进度感知，不焦虑

---

**版本**: v1.7.0  
**更新日期**: 2025-12-12  
**升级内容**: 文生图异步调用模式  
**向后兼容**: ✅ 完全兼容

**异步调用，稳定高效！** 🚀✨
