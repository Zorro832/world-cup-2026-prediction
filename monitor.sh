#!/bin/bash
# 2026世界杯预测应用 - 自动监控脚本
# 每60秒检查一次应用是否运行，如果停止则自动重启

LOG_FILE="/tmp/monitor.log"
APP_DIR="/workspace"
PORT=5000

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_app() {
    # 检查gunicorn进程是否存在
    if ps aux | grep -v grep | grep -q "gunicorn -w 1 -b 0.0.0.0:$PORT"; then
        return 0
    else
        return 1
    fi
}

start_app() {
    log "应用未运行，正在启动..."
    cd "$APP_DIR"
    nohup gunicorn -w 1 -b 0.0.0.0:$PORT app:app > /tmp/gunicorn.log 2>&1 &
    sleep 3
    
    if check_app; then
        log "✓ 应用启动成功"
        return 0
    else
        log "✗ 应用启动失败"
        return 1
    fi
}

log "===== 监控脚本启动 ====="
log "每60秒检查一次应用状态..."

# 先确保应用运行
if ! check_app; then
    start_app
fi

# 主循环：每60秒检查一次
while true; do
    if ! check_app; then
        log "检测到应用停止，准备重启..."
        start_app
    fi
    sleep 60
done
