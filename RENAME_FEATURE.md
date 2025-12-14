# 文件重命名功能说明

## 功能概述

现在您可以直接在资源管理器中重命名图片和视频文件，无需打开文件管理器，快速方便！

## 使用方法

### 方法一：右键菜单

1. **定位文件**
   ```
   在资源管理器中找到要重命名的文件
   ```

2. **打开菜单**
   ```
   右键点击文件 → 选择"重命名"
   ```

3. **输入新名称**
   ```
   在对话框中输入新文件名（不含扩展名）
   如：product1 → product_new
   ```

4. **确认重命名**
   ```
   点击"确定" → 完成重命名
   自动保留原文件扩展名
   ```

### 完整操作流程

```
右键文件
  ↓
选择"重命名"
  ↓
输入新名称（自动填充当前名称）
  ↓
点击确定
  ↓
✅ 重命名成功！
```

## 功能特点

### 智能扩展名处理

**自动保留扩展名：**
```
原文件: product.jpg
输入: new_product
结果: new_product.jpg  ✅ 自动添加 .jpg
```

**不需要手动输入扩展名：**
```
输入框只需填写文件名主体部分
系统自动保留原扩展名
```

### 重名检测

**场景：目标文件名已存在**
```
inputs/
  ├─ image1.jpg
  └─ image2.jpg

尝试: image2 → image1
结果: ❌ 提示"文件名已存在，请使用其他名称"
```

### 输入验证

**空白名称：**
```
输入: [空白]
结果: ❌ 取消操作，不执行重命名
```

**相同名称：**
```
原名: product
输入: product
结果: ❌ 取消操作（没有改变）
```

### 即时反馈

**成功提示：**
```
✅ 文件已重命名为: new_name.jpg
自动刷新资源管理器
```

**失败提示：**
```
❌ 重命名失败: [错误原因]
提供详细错误信息
```

## 右键菜单结构

```
右键文件
┌──────────────────────┐
│ 重命名               │ ← 新增功能
├──────────────────────┤
│ 在文件管理器中显示    │
│ 复制路径              │
├──────────────────────┤
│ 删除                  │
└──────────────────────┘
```

## 使用场景

### 场景 1：整理产品图片

```
需求：统一产品图片命名规范

之前：
- IMG_001.jpg
- IMG_002.jpg
- IMG_003.jpg

操作：
1. 右键 IMG_001.jpg → 重命名
2. 输入: product_apple
3. 重复操作...

之后：
- product_apple.jpg
- product_banana.jpg
- product_orange.jpg

效率：比打开文件管理器快 3 倍 ⚡
```

### 场景 2：视频版本管理

```
需求：标记视频生成版本

之前：
- output.mp4
- output.mp4（需要覆盖或手动重命名）

操作：
1. 右键 output.mp4 → 重命名
2. 输入: output_v1
3. 生成新视频
4. 新视频自动命名为 output.mp4

之后：
- output_v1.mp4（旧版本）
- output.mp4（新版本）

优势：版本清晰，便于对比 ✨
```

### 场景 3：图片分类命名

```
需求：按主题重命名图片

操作示例：
- landscape1.jpg → beijing_summer.jpg
- landscape2.jpg → shanghai_night.jpg
- landscape3.jpg → hangzhou_lake.jpg

结果：
- 文件名有意义
- 便于查找
- 提升管理效率
```

## 技术实现

### 核心代码

```python
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
        QMessageBox.warning(
            self,
            "重命名失败",
            f"文件名 '{new_name_with_ext}' 已存在，请使用其他名称。"
        )
        return
    
    # 执行重命名
    try:
        os.rename(file_path, new_path)
        self.refresh()
        QMessageBox.information(self, "成功", f"文件已重命名为:\n{new_name_with_ext}")
    except Exception as e:
        QMessageBox.critical(self, "错误", f"重命名失败: {str(e)}")
```

### 安全保护

1. **重名检测**：防止覆盖已存在的文件
2. **输入验证**：过滤无效输入
3. **异常处理**：捕获并显示错误信息
4. **自动刷新**：重命名后立即更新列表

## 注意事项

### ⚠️ 文件名规范

**推荐命名方式：**
```
✅ product_name
✅ video_2023_12_11
✅ image-final
✅ logo_v2
```

**避免使用：**
```
❌ product/name（包含特殊字符）
❌ video:test（包含非法字符）
❌ <file>（系统保留字符）
```

### ⚠️ 扩展名说明

**系统自动处理扩展名：**
```
原文件: image.jpg
输入: new_image.png  ← 输入 .png 无效
结果: new_image.png.jpg  ← 系统添加 .jpg
```

**建议：**
- 只输入文件名主体
- 不要包含扩展名
- 系统会自动保留原扩展名

### ⚠️ 操作建议

**重命名前：**
- 确认文件没有被其他程序打开
- 检查新名称是否符合规范
- 确保不会与已有文件重名

**重命名后：**
- 检查资源管理器中的新名称
- 如果其他地方引用了该文件，需更新引用

## 快捷操作技巧

### 技巧 1：批量重命名模式

```
为一组文件添加统一前缀：

image1.jpg → product_image1.jpg
image2.jpg → product_image2.jpg
image3.jpg → product_image3.jpg

方法：依次重命名，输入带前缀的新名称
```

### 技巧 2：版本号管理

```
保留历史版本：

final.jpg → final_v1.jpg
（生成新版本后）
final.jpg → final_v2.jpg
（最新版本保持 final.jpg）

方法：新版本生成前，先重命名旧版本
```

### 技巧 3：日期标记

```
添加日期信息：

output.mp4 → output_20231211.mp4
demo.mp4 → demo_20231211.mp4

方法：在文件名中包含日期标识
```

## 与其他功能配合

### 配合缩略图

```
1. 通过缩略图识别图片内容
2. 右键重命名为有意义的名称
3. 提升后续查找效率
```

### 配合版本管理

```
1. 生成视频后预览
2. 如需保留，重命名添加版本号
3. 继续生成新版本
4. 便于对比不同版本
```

### 配合批量导入

```
1. 批量拖入图片
2. 根据内容重命名
3. 分类整理素材
4. 高效管理工程文件
```

## 常见问题

### Q1: 重命名后缩略图会更新吗？

A: 会！系统会自动刷新资源管理器，缩略图会立即显示新的文件名。

### Q2: 可以修改扩展名吗？

A: 当前版本不支持修改扩展名，只能修改文件名主体部分。这是为了防止误操作导致文件无法打开。

### Q3: 重命名失败怎么办？

A: 
1. 检查文件是否被其他程序占用
2. 确认新文件名不包含特殊字符
3. 确保目标名称不与已有文件重复
4. 查看错误提示中的详细信息

### Q4: 可以撤销重命名吗？

A: 当前版本不支持撤销。建议重命名前确认新名称，或手动再次重命名回原来的名字。

### Q5: 重命名会影响文件内容吗？

A: 不会！重命名只修改文件名，不会影响文件内容、大小、质量等任何属性。

---

**版本**: v1.3.3  
**更新日期**: 2025-12-11  
**功能状态**: ✅ 已实现

**享受更便捷的文件管理体验！** 📝✨
