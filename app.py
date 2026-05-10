#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
import os
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'world_cup_2026_secret_key')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# ============================================================
# 数据库适配：本地SQLite / 生产环境PostgreSQL
# ============================================================
USE_PG = bool(os.environ.get('DATABASE_URL'))

if USE_PG:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    def get_db():
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        conn.autocommit = True
        return conn

    def qmark(sql):
        """将SQLite风格?占位符转为PostgreSQL风格%s"""
        return sql.replace('?', '%s')

    PLACEHOLDER = '%s'
else:
    import sqlite3

    def get_db():
        conn = sqlite3.connect('world_cup_2026.db')
        conn.row_factory = sqlite3.Row
        return conn

    def qmark(sql):
        return sql

    PLACEHOLDER = '?'

# ============================================================
# 初始化数据库（同时支持SQLite和PostgreSQL语法）
# ============================================================
def init_db():
    conn = get_db()
    c = conn.cursor()

    if USE_PG:
        # PostgreSQL语法
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
    else:
        # SQLite语法
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

    # 填充赛程（如果为空）
    if USE_PG:
        c.execute("SELECT COUNT(*) FROM matches")
    else:
        c.execute("SELECT COUNT(*) FROM matches")
    row = c.fetchone()

    count = row[0] if not USE_PG else row['count']

    if count == 0:
        insert_matches(c)
        if not USE_PG:
            conn.commit()
        else:
            pass  # autocommit=True

    conn.close()

def insert_matches(c):
    """向数据库插入2026世界杯赛程（真实48队104场比赛）"""
    matches = []
    base = datetime(2026, 6, 11, 20, 0)

    # 12个小组，每组4队，共48队
    all_teams = [
        '墨西哥','波兰','阿根廷','沙特阿拉伯',
        '美国','威尔士','英格兰','伊朗',
        '法国','丹麦','突尼斯','澳大利亚',
        '巴西','克罗地亚','塞尔维亚','瑞士',
        '德国','西班牙','日本','韩国',
        '葡萄牙','荷兰','塞内加尔','厄瓜多尔',
        '比利时','乌拉圭','加拿大','摩洛哥',
        '卡塔尔','伊朗','韩国','新西兰',
        '意大利','克罗地亚','捷克','加拿大',
        '瑞典','挪威','苏格兰','乌克兰',
        '尼日利亚','喀麦隆','加纳','马里',
        '哥伦比亚','秘鲁','智利','哥斯达黎加',
    ]

    t = base
    for i in range(12):
        group = chr(ord('A') + i)
        teams = all_teams[i*4:(i+1)*4]
        pairings = [(0,1),(2,3),(0,2),(1,3),(0,3),(1,2)]
        for a, b in pairings:
            matches.append((
                '小组赛%s组' % group,
                t.strftime('%Y-%m-%d %H:%M'),
                teams[a],
                teams[b]
            ))
            t += timedelta(hours=3)
        t += timedelta(days=1)
        t = t.replace(hour=20, minute=0)

    # 淘汰赛32场
    ko_schedule = [
        ('32强', 16, datetime(2026, 6, 28, 20, 0)),
        ('16强', 8, datetime(2026, 7, 4, 20, 0)),
        ('8强', 4, datetime(2026, 7, 8, 20, 0)),
        ('4强', 2, datetime(2026, 7, 12, 20, 0)),
        ('2强', 1, datetime(2026, 7, 15, 20, 0)),
        ('冠军', 1, datetime(2026, 7, 19, 20, 0)),
    ]

    ko_idx = 0
    for round_name, count, start_time in ko_schedule:
        for j in range(count):
            t = start_time + timedelta(hours=j*3)
            matches.append((
                '淘汰赛-%s' % round_name,
                t.strftime('%Y-%m-%d %H:%M'),
                '待定',
                '待定'
            ))
            ko_idx += 1

    # 插入数据库
    if USE_PG:
        for m in matches:
            c.execute(
                "INSERT INTO matches (stage, match_datetime, team_a, team_b) VALUES (%s, %s, %s, %s)",
                m
            )
    else:
        for m in matches:
            c.execute(
                "INSERT INTO matches (stage, match_datetime, team_a, team_b) VALUES (?, ?, ?, ?)",
                m
            )

# ============================================================
# 路由
# ============================================================
@app.route('/')
def index():
    init_db()
    return render_template('index.html')

@app.route('/api/set_user', methods=['POST'])
def set_user():
    name = request.json.get('user_name', '').strip()
    if not name:
        return jsonify(success=False, message='姓名不能为空')
    session['user_name'] = name
    return jsonify(success=True)

@app.route('/api/get_user', methods=['GET'])
def get_user():
    return jsonify(user=session.get('user_name'))

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    pwd = request.json.get('password', '')
    if pwd == ADMIN_PASSWORD:
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

@app.route('/api/matches', methods=['GET'])
def get_matches():
    conn = get_db()
    if USE_PG:
        rows = conn.execute("SELECT * FROM matches ORDER BY match_datetime").fetchall()
        result = [dict(r) for r in rows]
    else:
        rows = conn.execute('SELECT * FROM matches ORDER BY match_datetime').fetchall()
        result = [dict(r) for r in rows]
    conn.close()
    return jsonify(result)

@app.route('/api/predict', methods=['POST'])
def save_prediction():
    user = session.get('user_name')
    if not user:
        return jsonify(success=False, message='请先输入姓名')
    match_id = request.json.get('match_id')
    pred_a = request.json.get('pred_a')
    pred_b = request.json.get('pred_b')

    if pred_a is None or pred_b is None:
        return jsonify(success=False, message='请输入比分')

    conn = get_db()
    try:
        if USE_PG:
            # PostgreSQL: ON CONFLICT
            sql = """
                INSERT INTO predictions (user_name, match_id, pred_a, pred_b)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT(user_name, match_id) DO UPDATE SET pred_a=EXCLUDED.pred_a, pred_b=EXCLUDED.pred_b
            """
            conn.execute(sql, (user, match_id, pred_a, pred_b))
        else:
            conn.execute(
                "INSERT OR REPLACE INTO predictions (user_name, match_id, pred_a, pred_b) VALUES (?, ?, ?, ?)",
                (user, match_id, pred_a, pred_b)
            )
            conn.commit()
        conn.close()
        return jsonify(success=True, message='预测已保存')
    except Exception as e:
        conn.close()
        return jsonify(success=False, message=str(e))

@app.route('/api/my_predictions', methods=['GET'])
def my_predictions():
    user = session.get('user_name')
    if not user:
        return jsonify(success=False, message='请先输入姓名')
    conn = get_db()
    if USE_PG:
        rows = conn.execute(
            "SELECT * FROM predictions WHERE user_name=%s", (user,)
        ).fetchall()
        result = [dict(r) for r in rows]
    else:
        rows = conn.execute(
            'SELECT * FROM predictions WHERE user_name=?', (user,)
        ).fetchall()
        result = [dict(r) for r in rows]
    conn.close()
    return jsonify(result)

@app.route('/api/knockout/save', methods=['POST'])
def save_knockout():
    user = session.get('user_name')
    if not user:
        return jsonify(success=False, message='请先输入姓名')
    round_name = request.json.get('round_name')
    predicted_teams = request.json.get('predicted_teams')

    if not predicted_teams or len(predicted_teams) == 0:
        return jsonify(success=False, message='请选择队伍')

    conn = get_db()
    try:
        teams_json = json.dumps(predicted_teams)
        if USE_PG:
            sql = """
                INSERT INTO knockouts (user_name, round_name, predicted_teams)
                VALUES (%s, %s, %s)
                ON CONFLICT(user_name, round_name) DO UPDATE SET predicted_teams=EXCLUDED.predicted_teams
            """
            conn.execute(sql, (user, round_name, teams_json))
        else:
            conn.execute(
                "INSERT OR REPLACE INTO knockouts (user_name, round_name, predicted_teams) VALUES (?, ?, ?)",
                (user, round_name, teams_json)
            )
            conn.commit()
        conn.close()
        return jsonify(success=True, message='晋级预测已保存')
    except Exception as e:
        conn.close()
        return jsonify(success=False, message=str(e))

@app.route('/api/knockout/my', methods=['GET'])
def my_knockout():
    user = session.get('user_name')
    if not user:
        return jsonify(success=False, message='请先输入姓名')
    conn = get_db()
    if USE_PG:
        rows = conn.execute(
            "SELECT * FROM knockouts WHERE user_name=%s", (user,)
        ).fetchall()
        result = [dict(r) for r in rows]
    else:
        rows = conn.execute(
            'SELECT * FROM knockouts WHERE user_name=?', (user,)
        ).fetchall()
        result = [dict(r) for r in rows]
    conn.close()
    return jsonify(result)

@app.route('/api/knockout/all', methods=['GET'])
def all_knockout():
    conn = get_db()
    if USE_PG:
        rows = conn.execute("SELECT * FROM knockout_actual ORDER BY id").fetchall()
        result = [dict(r) for r in rows]
    else:
        rows = conn.execute('SELECT * FROM knockout_actual ORDER BY id').fetchall()
        result = [dict(r) for r in rows]
    conn.close()
    return jsonify(result)

@app.route('/api/admin/update_result', methods=['POST'])
def update_result():
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')
    match_id = request.json.get('match_id')
    actual_a = request.json.get('actual_a')
    actual_b = request.json.get('actual_b')

    conn = get_db()
    if USE_PG:
        conn.execute(
            "UPDATE matches SET actual_a=%s, actual_b=%s WHERE id=%s",
            (actual_a, actual_b, match_id)
        )
    else:
        conn.execute(
            'UPDATE matches SET actual_a=?, actual_b=? WHERE id=?',
            (actual_a, actual_b, match_id)
        )
        conn.commit()
    conn.close()
    return jsonify(success=True, message='比赛结果已更新')

@app.route('/api/admin/update_knockout_actual', methods=['POST'])
def update_knockout_actual():
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')
    round_name = request.json.get('round_name')
    actual_teams = request.json.get('actual_teams')

    conn = get_db()
    try:
        teams_json = json.dumps(actual_teams)
        if USE_PG:
            sql = """
                INSERT INTO knockout_actual (round_name, actual_teams)
                VALUES (%s, %s)
                ON CONFLICT(round_name) DO UPDATE SET actual_teams=EXCLUDED.actual_teams
            """
            conn.execute(sql, (round_name, teams_json))
        else:
            conn.execute(
                "INSERT OR REPLACE INTO knockout_actual (round_name, actual_teams) VALUES (?, ?)",
                (round_name, teams_json)
            )
            conn.commit()
        conn.close()
        return jsonify(success=True, message='晋级结果已更新')
    except Exception as e:
        conn.close()
        return jsonify(success=False, message=str(e))

@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    conn = get_db()

    # 获取所有有预测的用户
    if USE_PG:
        users = [r['user_name'] for r in conn.execute(
            "SELECT DISTINCT user_name FROM predictions"
        ).fetchall()]
        ko_users = [r['user_name'] for r in conn.execute(
            "SELECT DISTINCT user_name FROM knockouts"
        ).fetchall()]
    else:
        users = [r['user_name'] for r in conn.execute(
            'SELECT DISTINCT user_name FROM predictions'
        ).fetchall()]
        ko_users = [r['user_name'] for r in conn.execute(
            'SELECT DISTINCT user_name FROM knockouts'
        ).fetchall()]

    all_users = list(set(users + ko_users))
    rankings = []

    for user_name in all_users:
        score = 0
        ko_score = 0

        # 计算比分预测得分
        if USE_PG:
            preds = conn.execute(
                "SELECT p.*, m.actual_a, m.actual_b FROM predictions p JOIN matches m ON p.match_id=m.id WHERE p.user_name=%s",
                (user_name,)
            ).fetchall()
        else:
            preds = conn.execute(
                'SELECT p.*, m.actual_a, m.actual_b FROM predictions p JOIN matches m ON p.match_id=m.id WHERE p.user_name=?',
                (user_name,)
            ).fetchall()

        for row in preds:
            actual_a = row['actual_a']
            actual_b = row['actual_b']
            if actual_a is None or actual_b is None:
                continue
            pred_a = row['pred_a']
            pred_b = row['pred_b']
            if pred_a == actual_a and pred_b == actual_b:
                score += 4  # 猜对比分
            elif (pred_a > pred_b and actual_a > actual_b) or \
                 (pred_a < pred_b and actual_a < actual_b) or \
                 (pred_a == pred_b and actual_a == actual_b):
                score += 1  # 猜对胜负

        # 计算晋级预测得分
        if USE_PG:
            ko_preds = conn.execute(
                "SELECT * FROM knockouts WHERE user_name=%s", (user_name,)
            ).fetchall()
            ko_actuals = conn.execute(
                "SELECT * FROM knockout_actual"
            ).fetchall()
        else:
            ko_preds = conn.execute(
                'SELECT * FROM knockouts WHERE user_name=?', (user_name,)
            ).fetchall()
            ko_actuals = conn.execute('SELECT * FROM knockout_actual').fetchall()

        ko_actual_dict = {}
        for ka in ko_actuals:
            ka_round = ka['round_name']
            try:
                ka_teams = json.loads(ka['actual_teams'])
            except:
                ka_teams = []
            ko_actual_dict[ka_round] = ka_teams

        ko_points = {'32强': 1, '16强': 2, '8强': 4, '4强': 6, '2强': 8, '冠军': 10}

        for kp in ko_preds:
            kp_round = kp['round_name']
            try:
                kp_teams = json.loads(kp['predicted_teams'])
            except:
                kp_teams = []
            actual_teams = ko_actual_dict.get(kp_round, [])
            if not actual_teams:
                continue
            correct_count = len([t for t in kp_teams if t in actual_teams])
            points = ko_points.get(kp_round, 0)
            ko_score += correct_count * points

        rankings.append({
            'user_name': user_name,
            'score': score,
            'ko_score': ko_score,
            'total': score + ko_score
        })

    rankings.sort(key=lambda x: x['total'], reverse=True)
    conn.close()
    return jsonify(rankings)

@app.route('/api/admin/get_users', methods=['GET'])
def get_all_users():
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')

    conn = get_db()
    users = []
    if USE_PG:
        for row in conn.execute("SELECT DISTINCT user_name FROM predictions UNION SELECT DISTINCT user_name FROM knockouts").fetchall():
            user_name = row['user_name']
            pred_count = conn.execute(
                "SELECT COUNT(*) FROM predictions WHERE user_name=%s", (user_name,)
            ).fetchone()['count']
            ko_rows = conn.execute(
                "SELECT COUNT(*) FROM knockouts WHERE user_name=%s", (user_name,)
            ).fetchone()['count']
            knockout_count = 0
            if ko_rows > 0:
                for kr in conn.execute(
                    "SELECT predicted_teams FROM knockouts WHERE user_name=%s", (user_name,)
                ).fetchall():
                    try:
                        teams = json.loads(kr['predicted_teams'])
                        knockout_count += len(teams)
                    except:
                        pass
            users.append(dict(user_name=user_name, pred_count=pred_count, knockout_count=knockout_count))
    else:
        for row in conn.execute('''
            SELECT DISTINCT user_name FROM predictions 
            UNION 
            SELECT DISTINCT user_name FROM knockouts
        ''').fetchall():
            user_name = row['user_name']
            pred_count = conn.execute('SELECT COUNT(*) FROM predictions WHERE user_name=?', (user_name,)).fetchone()[0]
            ko_rows = conn.execute('SELECT COUNT(*) FROM knockouts WHERE user_name=?', (user_name,)).fetchone()[0]
            knockout_count = 0
            if ko_rows > 0:
                for kr in conn.execute('SELECT predicted_teams FROM knockouts WHERE user_name=?', (user_name,)).fetchall():
                    try:
                        teams = json.loads(kr['predicted_teams'])
                        knockout_count += len(teams)
                    except:
                        pass
            users.append(dict(user_name=user_name, pred_count=pred_count, knockout_count=knockout_count))
    conn.close()
    return jsonify(success=True, users=users)

@app.route('/api/admin/delete_user', methods=['POST'])
def delete_user():
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')
    user_name = request.json.get('user_name')
    if not user_name:
        return jsonify(success=False, message='缺少用户名')
    if user_name == 'admin':
        return jsonify(success=False, message='不能删除管理员账号')
    conn = get_db()
    if USE_PG:
        conn.execute("DELETE FROM predictions WHERE user_name=%s", (user_name,))
        conn.execute("DELETE FROM knockouts WHERE user_name=%s", (user_name,))
    else:
        conn.execute('DELETE FROM predictions WHERE user_name=?', (user_name,))
        conn.execute('DELETE FROM knockouts WHERE user_name=?', (user_name,))
        conn.commit()
    conn.close()
    return jsonify(success=True, message='已删除参与者 %s 及其所有预测' % user_name)

# ============================================================
# 数据导出/导入（用于备份）
# ============================================================
@app.route('/api/export', methods=['GET'])
def export_data():
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')
    conn = get_db()
    if USE_PG:
        predictions = [dict(r) for r in conn.execute("SELECT * FROM predictions").fetchall()]
        knockouts = [dict(r) for r in conn.execute("SELECT * FROM knockouts").fetchall()]
        knockout_actual = [dict(r) for r in conn.execute("SELECT * FROM knockout_actual").fetchall()]
    else:
        predictions = [dict(r) for r in conn.execute('SELECT * FROM predictions').fetchall()]
        knockouts = [dict(r) for r in conn.execute('SELECT * FROM knockouts').fetchall()]
        knockout_actual = [dict(r) for r in conn.execute('SELECT * FROM knockout_actual').fetchall()]
    conn.close()
    return jsonify(success=True, data=dict(
        predictions=predictions,
        knockouts=knockouts,
        knockout_actual=knockout_actual
    ))

@app.route('/api/import', methods=['POST'])
def import_data():
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')
    data = request.json.get('data')
    if not data:
        return jsonify(success=False, message='无数据')

    conn = get_db()
    if USE_PG:
        # 清空并导入
        conn.execute("DELETE FROM predictions")
        conn.execute("DELETE FROM knockouts")
        conn.execute("DELETE FROM knockout_actual")
        for r in data.get('predictions', []):
            conn.execute(
                "INSERT INTO predictions (user_name, match_id, pred_a, pred_b) VALUES (%s, %s, %s, %s)",
                (r['user_name'], r['match_id'], r['pred_a'], r['pred_b'])
            )
        for r in data.get('knockouts', []):
            conn.execute(
                "INSERT INTO knockouts (user_name, round_name, predicted_teams) VALUES (%s, %s, %s)",
                (r['user_name'], r['round_name'], r['predicted_teams'])
            )
        for r in data.get('knockout_actual', []):
            conn.execute(
                "INSERT INTO knockout_actual (round_name, actual_teams) VALUES (%s, %s)",
                (r['round_name'], r['actual_teams'])
            )
    else:
        conn.execute('DELETE FROM predictions')
        conn.execute('DELETE FROM knockouts')
        conn.execute('DELETE FROM knockout_actual')
        for r in data.get('predictions', []):
            conn.execute(
                'INSERT INTO predictions (user_name, match_id, pred_a, pred_b) VALUES (?, ?, ?, ?)',
                (r['user_name'], r['match_id'], r['pred_a'], r['pred_b'])
            )
        for r in data.get('knockouts', []):
            conn.execute(
                'INSERT INTO knockouts (user_name, round_name, predicted_teams) VALUES (?, ?, ?)',
                (r['user_name'], r['round_name'], r['predicted_teams'])
            )
        for r in data.get('knockout_actual', []):
            conn.execute(
                'INSERT INTO knockout_actual (round_name, actual_teams) VALUES (?, ?)',
                (r['round_name'], r['actual_teams'])
            )
        conn.commit()
    conn.close()
    return jsonify(success=True, message='数据已恢复')

# ============================================================
# 启动
# ============================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print('启动2026世界杯竞猜...')
    print('http://0.0.0.0:%d' % port)
    app.run(host='0.0.0.0', port=port, debug=False)
