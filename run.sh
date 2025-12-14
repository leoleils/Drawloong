#!/bin/bash
# QT 客户端快速启动脚本

echo "图生视频 QT 客户端"
echo "=================="
echo ""

# 检查是否存在 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，正在从 .env.example 复制..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请编辑该文件配置 API 密钥"
    echo ""
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 未找到虚拟环境，正在创建..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
    echo ""
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 检查并安装依赖..."
pip install -q -r requirements.txt

# 运行应用
echo "🚀 启动应用..."
echo ""
python main.py
