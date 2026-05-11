#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026世界杯预测应用 - Render.com版本
使用PostgreSQL数据库（Render.com免费提供）
"""
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
import os
import json

# 数据库适配：本地用SQLite，生产环境用PostgreSQL
if os.environ.get('DATABASE_URL'):
    # 生产环境：使用PostgreSQL（Render.com提供）
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'world_cup_2026_secret_key')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    def get_db():
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        conn.autocommit = True
        return conn
    
    def init_db():
        conn = get_db()
        c = conn.cursor()
        # 创建表（PostgreSQL语法）
        c.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id SERIAL PRIMARY KEY,
                stage TEXT,
                match_datetime TEXT,
                team_a TEXT,
                team_b TEXT,
                actual_a INTEGER,
                actual_b INTEGER
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                user_name TEXT,
                match_id INTEGER,
                pred_a INTEGER,
                pred_b INTEGER,
                UNIQUE(user_name, match_id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS knockouts (
                id SERIAL PRIMARY KEY,
                user_name TEXT,
                round_name TEXT,
                predicted_teams TEXT,
                UNIQUE(user_name, round_name)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS knockout_actual (
                id SERIAL PRIMARY KEY,
                round_name TEXT UNIQUE,
                actual_teams TEXT
            )
        ''')
        conn.close()
else:
    # 本地环境：使用SQLite
    import sqlite3
    
    app = Flask(__name__)
    app.secret_key = 'world_cup_2026_secret_key'
    ADMIN_PASSWORD = 'admin123'
    
    def get_db():
        conn = sqlite3.connect('world_cup_2026.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db():
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stage TEXT,
                match_datetime TEXT,
                team_a TEXT,
                team_b TEXT,
                actual_a INTEGER,
                actual_b INTEGER
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT,
                match_id INTEGER,
                pred_a INTEGER,
                pred_b INTEGER,
                UNIQUE(user_name, match_id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS knockouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT,
                round_name TEXT,
                predicted_teams TEXT,
                UNIQUE(user_name, round_name)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS knockout_actual (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_name TEXT UNIQUE,
                actual_teams TEXT
            )
        ''')
        conn.commit()
        conn.close()

# ============= 路由定义 =============
@app.route('/')
def index():
    init_db()  # 确保数据库表存在
    return render_template('index.html')

# ... 这里需要复制所有API路由 ...
# 由于代码较长，我先创建一个简化版本

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
