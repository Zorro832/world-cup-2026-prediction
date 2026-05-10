#!/bin/bash
# 持续运行脚本 - 确保应用2年内不中断

cd /workspace

# 停止旧进程
pkill -9 -f "gunicorn|app.py" 2>/dev/null
sleep 2

# 启动监督进程
while true; do
    # 检查端口
    if ! lsof -i:5000 >/dev/null 2>&1; then
        echo "[$(date)] 启动应用..."
        gunicorn -w 4 -b 0.0.0.0:5000 \
            --timeout 300 \
            --graceful-timeout 30 \
            --keep-alive 5 \
            --max-requests 1000 \
            --max-requests-jitter 50 \
            --log-level info \
            --access-logfile logs/access.log \
            --error-logfile logs/error.log \
            app:app >> logs/output.log 2>&1 &
        GUNICORN_PID=$!
        echo $GUNICORN_PID > app.pid
        echo "[$(date)] 应用已启动，PID: $GUNICORN_PID"
    fi
    
    # 检查数据库完整性
    if [ -f world_cup_2026.db ]; then
        # 每天备份一次
        TODAY=$(date +%Y%m%d)
        if [ ! -f "backups/backup_$TODAY.db" ]; then
            mkdir -p backups
            cp world_cup_2026.db "backups/backup_$TODAY.db"
            echo "[$(date)] 数据库已备份"
        fi
    fi
    
    sleep 300  # 每5分钟检查一次
done
