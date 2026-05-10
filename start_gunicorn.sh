#!/bin/bash
# 2026世界杯竞猜应用 - 持久化启动脚本
# 使用gunicorn确保持续运行

cd /workspace

# 停止旧进程
pkill -f "gunicorn" 2>/dev/null
pkill -f "python3 app.py" 2>/dev/null
sleep 2

# 使用gunicorn启动（生产级WSGI服务器）
# -w 4: 4个工作进程
# --timeout 120: 超时120秒
# --log-file: 日志文件
# --access-logfile: 访问日志
nohup gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --log-file gunicorn.log --access-logfile access.log app:app > gunicorn.out 2>&1 &

sleep 3

# 检查是否启动成功
if lsof -i:5000 >/dev/null 2>&1; then
    echo "✅ 应用启动成功！"
    echo "📱 访问地址："
    echo "   https://webview.e2b.bj5.sandbox.cloudstudio.club/?x-cs-sandbox-id=a104cef90d0d46eeac20c498614b7237&x-cs-sandbox-port=5000"
    echo ""
    echo "📊 进程信息："
    ps aux | grep gunicorn | grep -v grep | head -5
    echo ""
    echo "📝 日志文件："
    echo "   主日志：gunicorn.log"
    echo "   访问日志：access.log"
    echo "   输出日志：gunicorn.out"
else
    echo "❌ 应用启动失败！"
    echo "检查日志："
    tail -20 gunicorn.log 2>/dev/null || tail -20 gunicorn.out 2>/dev/null
fi
