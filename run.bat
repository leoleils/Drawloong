@echo off
REM QT 客户端快速启动脚本 (Windows)

echo 图生视频 QT 客户端
echo ==================
echo.

REM 检查是否存在 .env 文件
if not exist ".env" (
    echo 未找到 .env 文件，正在从 .env.example 复制...
    copy .env.example .env
    echo 已创建 .env 文件，请编辑该文件配置 API 密钥
    echo.
)

REM 检查虚拟环境
if not exist "venv" (
    echo 未找到虚拟环境，正在创建...
    python -m venv venv
    echo 虚拟环境创建完成
    echo.
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 检查并安装依赖...
pip install -q -r requirements.txt

REM 运行应用
echo 启动应用...
echo.
python main.py

pause
