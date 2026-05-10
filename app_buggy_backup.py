#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026年世界杯竞猜 Web应用（完整版）
功能：用户竞猜、晋级竞猜、管理员管理、自动锁定、积分排名
"""
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'world_cup_2026_secret_key'

# 管理员密码
ADMIN_PASSWORD = 'admin123'

# ============== 数据库初始化 ==============

def get_db():
    conn = sqlite3.connect('world_cup_2026.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # 比赛表
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
    
    # 预测表（比分竞猜）
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
    
    # 晋级竞猜表
    c.execute('''
        CREATE TABLE IF NOT EXISTS knockouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            round_name TEXT,
            predicted_teams TEXT,
            UNIQUE(user_name, round_name)
        )
    ''')
    
    # 实际晋级队伍表（管理员设置）
    c.execute('''
        CREATE TABLE IF NOT EXISTS knockout_actual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_name TEXT UNIQUE,
            actual_teams TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

    # 注意：赛程数据通过 add_matches_v2.py 脚本填充，不在代码中硬编码

init_db()

# ============== 路由 ==============

@app.route('/')
def index():
    return render_template('index.html')

# ============== 用户 API ==============

@app.route('/api/set_user', methods=['POST'])
def set_user():
    data = request.json
    name = data.get('user','').strip()
    if not name:
        return jsonify(success=False, message='请输入姓名')
    session['user'] = name
    return jsonify(success=True, user=name)

@app.route('/api/get_user', methods=['GET'])
def get_user():
    return jsonify(user=session.get('user',''))

# ============== 管理员 API ==============

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if data.get('password') == ADMIN_PASSWORD:
        session['is_admin'] = True
        return jsonify(success=True)
    return jsonify(success=False, message='密码错误')

@app.route('/api/admin/check', methods=['GET'])
def admin_check():
    return jsonify(is_admin=session.get('is_admin', False))

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('is_admin', None)
    return jsonify(success=True)

# ============== 比赛 API ==============

@app.route('/api/matches', methods=['GET'])
def get_matches():
    conn = get_db()
    rows = conn.execute('SELECT * FROM matches ORDER BY match_datetime').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/admin/add_match', methods=['POST'])
def add_match():
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')
    d = request.json
    conn = get_db()
    conn.execute('''
        INSERT INTO matches (stage, match_datetime, team_a, team_b, actual_a, actual_b)
        VALUES (?, ?, ?, ?, NULL, NULL)
    ''', (d['stage'], d['match_datetime'], d['team_a'], d['team_b']))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/api/admin/save_result', methods=['POST'])
def save_result():
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')
    d = request.json
    conn = get_db()
    conn.execute('UPDATE matches SET actual_a=?, actual_b=? WHERE id=?', 
                   (d['actual_a'], d['actual_b'], d['match_id']))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/api/admin/delete_result', methods=['POST'])
def delete_result():
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')
    d = request.json
    conn = get_db()
    conn.execute('UPDATE matches SET actual_a=NULL, actual_b=NULL WHERE id=?', (d['match_id'],))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/api/admin/delete_match', methods=['POST'])
def delete_match():
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')
    d = request.json
    conn = get_db()
    conn.execute('DELETE FROM predictions WHERE match_id=?', (d['id'],))
    conn.execute('DELETE FROM matches WHERE id=?', (d['id'],))
    conn.commit()
    conn.close()
    return jsonify(success=True)

# ============== 预测 API ==============

@app.route('/api/save_prediction', methods=['POST'])
def save_prediction():
    d = request.json
    user = d.get('user','')
    match_id = d.get('match_id')
    pred_a = d.get('pred_a')
    pred_b = d.get('pred_b')
    
    if not user or pred_a is None or pred_b is None:
        return jsonify(success=False, message='请填写完整')
    
    # 锁定检查：比赛前5分钟
    conn = get_db()
    row = conn.execute('SELECT match_datetime FROM matches WHERE id=?', (match_id,)).fetchone()
    if row:
        mt = datetime.strptime(row[0], '%Y-%m-%d %H:%M')
        if (mt - datetime.now()).total_seconds() < 300:
            conn.close()
            return jsonify(success=False, message='比赛前5分钟不能修改！')
    
    conn.execute('''
        INSERT OR REPLACE INTO predictions (user_name, match_id, pred_a, pred_b)
        VALUES (?, ?, ?, ?)
    ''', (user, match_id, pred_a, pred_b))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/api/user_predictions', methods=['GET'])
def get_user_preds():
    user = request.args.get('user','')
    conn = get_db()
    rows = conn.execute('SELECT match_id, pred_a, pred_b FROM predictions WHERE user_name=?', (user,)).fetchall()
    conn.close()
    r = {}
    for row in rows:
        r[row[0]] = {'pred_a':row[1],'pred_b':row[2]}
    return jsonify(r)

# ============== 晋级竞猜 API ==============

def is_knocked():
    """第一场比赛前1小时锁定"""
    conn = get_db()
    row = conn.execute('SELECT MIN(match_datetime) FROM matches').fetchone()
    conn.close()
    if not row or not row[0]:
        return False
    first = datetime.strptime(row[0], '%Y-%m-%d %H:%M')
    return (first - datetime.now()).total_seconds() < 3600

@app.route('/api/knockout/save', methods=['POST'])
def save_knockout():
    if is_knocked():
        return jsonify(success=False, message='已锁定（第一场比赛前1小时）')
    d = request.json
    user = d.get('user','')
    preds = d.get('predictions', {})
    conn = get_db()
    for rnd, teams in preds.items():
        conn.execute('''
            INSERT OR REPLACE INTO knockouts (user_name, round_name, predicted_teams)
            VALUES (?, ?, ?)
        ''', (user, rnd, json.dumps(teams, ensure_ascii=False)))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/api/knockout/load', methods=['GET'])
def load_knockout():
    user = request.args.get('user','')
    conn = get_db()
    rows = conn.execute('SELECT round_name, predicted_teams FROM knockouts WHERE user_name=?', (user,)).fetchall()
    conn.close()
    preds = {r[0]: json.loads(r[1]) for r in rows}
    return jsonify(success=True, predictions=preds, locked=is_knocked())

@app.route('/api/knockout/teams', methods=['GET'])
def get_teams():
    """获取所有参赛队伍"""
    conn = get_db()
    rows = conn.execute('SELECT team_a FROM matches UNION SELECT team_b FROM matches').fetchall()
    conn.close()
    teams = sorted(set(r[0] for r in rows if r[0] not in ('待定','%s-%d'%('冠军',1))))
    return jsonify(success=True, teams=teams)

@app.route('/api/admin/knockout_actual_save', methods=['POST'])
def save_actual():
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')
    d = request.json
    conn = get_db()
    conn.execute('''
        INSERT OR REPLACE INTO knockout_actual (round_name, actual_teams)
        VALUES (?, ?)
    ''', (d['round'], json.dumps(d['teams'], ensure_ascii=False)))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/api/knockout/actual_load', methods=['GET'])
def load_actual():
    conn = get_db()
    rows = conn.execute('SELECT round_name, actual_teams FROM knockout_actual').fetchall()
    conn.close()
    return jsonify(success=True, data={r[0]: json.loads(r[1]) for r in rows})

# ============== 排名 API ==============

@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    conn = get_db()
    
    # 获取所有有预测的用户
    users = [r[0] for r in conn.execute('SELECT DISTINCT user_name FROM predictions').fetchall()]
    
    # 晋级积分规则
    KO_SCORES = {'32强':1, '16强':2, '8强':4, '4强':6, '2强':8, '冠军':10}
    
    # 实际晋级队伍
    actual = {}
    for r in conn.execute('SELECT round_name, actual_teams FROM knockout_actual').fetchall():
        actual[r[0]] = json.loads(r[1])
    
    rankings = []
    for user in users:
        score = 0
        exact = 0
        correct = 0
        
        # 比分竞猜积分
        for row in conn.execute('''
            SELECT p.pred_a, p.pred_b, m.actual_a, m.actual_b
            FROM predictions p JOIN matches m ON p.match_id=m.id
            WHERE p.user_name=? AND m.actual_a IS NOT NULL
        ''', (user,)):
            pa, pb, aa, ab = row
            if pa == aa and pb == ab:
                score += 4; exact += 1
            elif (pa>pb and aa>ab) or (pa<pb and aa<ab) or (pa==pb and aa==ab):
                score += 1; correct += 1
        
        # 晋级竞猜积分
        for r in conn.execute('SELECT round_name, predicted_teams FROM knockouts WHERE user_name=?', (user,)):
            rnd = r[0]
            pred = json.loads(r[1])
            real = actual.get(rnd, [])
            hits = len(set(pred) & set(real))
            score += hits * KO_SCORES.get(rnd, 0)
        
        rankings.append(dict(user=user, score=score, exact=exact, correct=correct))
    
    rankings.sort(key=lambda x:-x['score'])
    
    # 统计
    finished = conn.execute('SELECT COUNT(*) FROM matches WHERE actual_a IS NOT NULL').fetchone()[0]
    conn.close()
    
    avg = sum(r['score'] for r in rankings) / len(rankings) if rankings else 0
    
    return jsonify(users=len(rankings), finished=finished, 
                   avg_score=round(avg,1), rankings=rankings)

if __name__ == '__main__':
    print('🚀 启动2026世界杯竞猜...')
    print('🔗 http://0.0.0.0:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)
