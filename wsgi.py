#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""启动脚本 - 带错误捕获"""
import sys
import traceback

try:
    print("=" * 50)
    print("开始启动2026世界杯竞猜应用...")
    print(f"Python版本: {sys.version}")
    print(f"DATABASE_URL: {'已设置' if __import__('os').environ.get('DATABASE_URL') else '未设置'}")
    print("=" * 50)
    
    from app import app
    
    print("✓ app模块导入成功")
    print("✓ 数据库初始化完成")
    print("正在启动gunicorn...")
    
except Exception as e:
    print(f"❌ 启动失败: {e}")
    traceback.print_exc()
    sys.exit(1)

# 如果到这里说明成功
application = app
