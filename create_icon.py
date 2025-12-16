#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图标转换脚本
将 PNG 图片转换为 Windows ICO 格式
"""

import os
import sys

def create_ico_from_png(png_path, ico_path):
    """
    将 PNG 图片转换为 ICO 格式
    
    Args:
        png_path: PNG 图片路径
        ico_path: 输出 ICO 文件路径
    """
    try:
        from PIL import Image
        
        # 打开 PNG 图片
        img = Image.open(png_path)
        
        # 转换为 RGBA 模式（如果不是）
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # ICO 文件需要的尺寸列表
        # Windows 推荐包含多种尺寸
        sizes = [
            (16, 16),
            (32, 32),
            (48, 48),
            (64, 64),
            (128, 128),
            (256, 256),
        ]
        
        # 创建不同尺寸的图标
        icons = []
        for size in sizes:
            # 使用高质量缩放
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icons.append(resized)
        
        # 保存为 ICO 文件
        # 使用最大的图标作为基础，包含所有尺寸
        icons[0].save(
            ico_path,
            format='ICO',
            sizes=[(icon.width, icon.height) for icon in icons],
            append_images=icons[1:]
        )
        
        print(f"✅ 图标创建成功: {ico_path}")
        print(f"   包含尺寸: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
        return True
        
    except ImportError:
        print("❌ 需要安装 Pillow 库")
        print("   运行: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ 创建图标失败: {e}")
        return False


def main():
    """主函数"""
    # 默认路径
    png_path = "logo.png"
    ico_path = "logo.ico"
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        png_path = sys.argv[1]
    if len(sys.argv) > 2:
        ico_path = sys.argv[2]
    
    # 检查 PNG 文件是否存在
    if not os.path.exists(png_path):
        print(f"❌ 找不到 PNG 文件: {png_path}")
        return 1
    
    print(f"🔄 正在转换图标...")
    print(f"   输入: {png_path}")
    print(f"   输出: {ico_path}")
    
    # 创建 ICO 文件
    if create_ico_from_png(png_path, ico_path):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
