#!/bin/bash

# 闲鱼自动售货机器人 - 启动脚本

echo "🚀 启动闲鱼自动售货机器人..."

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "❌ 错误：.env 文件不存在"
    echo "请先运行：./scripts/init.sh"
    exit 1
fi

# 检查闲鱼 Cookie
XIANFU_COOKIE=$(grep XIANFU_COOKIE .env | cut -d '=' -f2)
if [ "$XIANFU_COOKIE" = "your_cookie_here" ] || [ -z "$XIANFU_COOKIE" ]; then
    echo "⚠️  警告：请先在 .env 文件中配置闲鱼 Cookie"
    echo "继续启动可能无法正常工作..."
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 启动服务
echo "🌐 启动 Web 服务..."
python3 app/main.py
