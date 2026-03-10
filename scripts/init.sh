#!/bin/bash

# 闲鱼自动售货机器人 - 初始化脚本

echo "🚀 开始初始化闲鱼自动售货机器人..."

# 1. 创建必要目录
echo "📁 创建目录结构..."
mkdir -p data logs config

# 2. 检查 Python 版本
echo "🐍 检查 Python 版本..."
python3 --version

# 3. 安装依赖
echo "📦 安装 Python 依赖..."
pip3 install -r requirements.txt

# 4. 安装 Playwright
echo "🎭 安装 Playwright..."
playwright install

# 5. 创建环境配置文件
if [ ! -f .env ]; then
    echo "⚙️ 创建环境配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置闲鱼 Cookie 和其他设置"
else
    echo "✅ 环境配置文件已存在"
fi

# 6. 初始化数据库
echo "💾 初始化数据库..."
python3 -c "from app.utils import init_db; init_db()"

echo ""
echo "✅ 初始化完成！"
echo ""
echo "下一步："
echo "1. 编辑 .env 文件，配置闲鱼 Cookie"
echo "2. 运行：python3 app/main.py"
echo "3. 访问：http://localhost:8080/docs"
echo ""
