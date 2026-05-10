#!/bin/bash
# 2026世界杯预测应用 - 启动脚本

echo "===== 启动2026世界杯预测应用 ====="

# 停止旧进程
echo "停止旧进程..."
pkill -f "gunicorn -w 1 -b 0.0.0.0:5000" 2>/dev/null
sleep 1

# 检查端口是否被占用
if netstat -tlnp 2>/dev/null | grep -q ":5000 "; then
    echo "端口5000被占用，清理..."
    lsof -ti:5000 | xargs kill -9 2>/dev/null
    sleep 1
fi

# 启动应用
echo "启动应用..."
cd /workspace
nohup gunicorn -w 1 -b 0.0.0.0:5000 app:app > /tmp/gunicorn.log 2>&1 &
sleep 3

# 检查是否启动成功
if ps aux | grep -v grep | grep -q gunicorn; then
    echo "✓ 应用启动成功！"
    echo "✓ 进程运行中"
    netstat -tlnp 2>/dev/null | grep 5000 || ss -tlnp 2>/dev/null | grep 5000
    echo ""
    echo "预览链接："
    /root/.codebuddy/skills/preview/notify 5000
else
    echo "✗ 应用启动失败！"
    echo "查看日志："
    tail -20 /tmp/gunicorn.log
fi
