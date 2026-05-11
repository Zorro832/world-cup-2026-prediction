#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
import os
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'world_cup_2026_secret_key')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

DATABASE_URL = os.environ.get('DATABASE_URL')
print(f'[启动] DATABASE_URL: {"已设置" if DATABASE_URL else "未设置(使用SQLite)"}')

if DATABASE_URL:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        print('[启动] psycopg2 导入成功')
    except ImportError as e:
        print(f'[启动] psycopg2 导入失败: {e}，尝试pg8000...')
        try:
            import pg8000
            print('[启动] pg8000 导入成功')
        except ImportError as e2:
            print(f'[启动] pg8000 也导入失败: {e2}，回退SQLite')
            DATABASE_URL = None

    if DATABASE_URL:
        def get_db():
            conn = psycopg2.connect(DATABASE_URL)
            conn.autocommit = True
            return conn

        PH = '%s'

        def upsert_predictions(cur, user, match_id, pred_a, pred_b):
            cur.execute('''INSERT INTO predictions (user_name, match_id, pred_a, pred_b) VALUES (%s, %s, %s, %s) ON CONFLICT (user_name, match_id) DO UPDATE SET pred_a=EXCLUDED.pred_a, pred_b=EXCLUDED.pred_b''', (user, match_id, pred_a, pred_b))

        def upsert_knockouts(cur, user, rnd, teams_json):
            cur.execute('''INSERT INTO knockouts (user_name, round_name, predicted_teams) VALUES (%s, %s, %s) ON CONFLICT (user_name, round_name) DO UPDATE SET predicted_teams=EXCLUDED.predicted_teams''', (user, rnd, teams_json))

        def upsert_knockout_actual(cur, rnd, teams_json):
            cur.execute('''INSERT INTO knockout_actual (round_name, actual_teams) VALUES (%s, %s) ON CONFLICT (round_name) DO UPDATE SET actual_teams=EXCLUDED.actual_teams''', (rnd, teams_json))
        print('[启动] PostgreSQL模式已配置')

if not DATABASE_URL:
    import sqlite3

    def get_db():
        conn = sqlite3.connect('world_cup_2026.db')
        conn.row_factory = sqlite3.Row
        return conn

    PH = '?'

    def upsert_predictions(cur, user, match_id, pred_a, pred_b):
        cur.execute('INSERT OR REPLACE INTO predictions (user_name, match_id, pred_a, pred_b) VALUES (?, ?, ?, ?)', (user, match_id, pred_a, pred_b))

    def upsert_knockouts(cur, user, rnd, teams_json):
        cur.execute('INSERT OR REPLACE INTO knockouts (user_name, round_name, predicted_teams) VALUES (?, ?, ?)', (user, rnd, teams_json))

    def upsert_knockout_actual(cur, rnd, teams_json):
        cur.execute('INSERT OR REPLACE INTO knockout_actual (round_name, actual_teams) VALUES (?, ?)', (rnd, teams_json))
    print('[启动] SQLite模式已配置')

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
    
    # 填充赛程（如果为空）
    c.execute("SELECT COUNT(*) FROM matches")
    if c.fetchone()[0] == 0:
        matches = []
        base = datetime(2026, 6, 11, 20, 0)
        
        # 小组赛 72场 - 48支不重复队伍
        all_teams = [
            '墨西哥', '波兰', '阿根廷', '沙特阿拉伯',
            '美国', '威尔士', '英格兰', '伊朗',
            '法国', '丹麦', '突尼斯', '澳大利亚',
            '巴西', '克罗地亚', '塞尔维亚', '瑞士',
            '德国', '西班牙', '日本', '韩国',
            '葡萄牙', '荷兰', '塞内加尔', '厄瓜多尔',
            '比利时', '乌拉圭', '加拿大', '摩洛哥',
            '卡塔尔', '厄瓜多尔', '塞内加尔', '荷兰',
            '意大利', '奥地利', '捷克', '匈牙利',
            '瑞典', '挪威', '苏格兰', '乌克兰',
            '尼日利亚', '喀麦隆', '加纳', '马里',
            '哥伦比亚', '秘鲁', '智利', '厄瓜多尔',
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
        
        # 淘汰赛 32场
        ko_schedule = [
            ('32强', 16, datetime(2026, 6, 28, 20, 0)),
            ('16强', 8, datetime(2026, 7, 4, 20, 0)),
            ('8强', 4, datetime(2026, 7, 8, 20, 0)),
        ]
        
        for stage, count, start_time in ko_schedule:
            t2 = start_time
            for i in range(count):
                matches.append((
                    stage,
                    t2.strftime('%Y-%m-%d %H:%M'),
                    '%s-%d' % (stage, i*2+1),
                    '%s-%d' % (stage, i*2+2)
                ))
                t2 += timedelta(hours=3)
                if (i+1) % 2 == 0:
                    t2 += timedelta(days=1)
                    t2 = t2.replace(hour=20, minute=0)
        
        # 半决赛
        matches.append(('半决赛', '2026-07-12 20:00', '半决赛-1', '半决赛-2'))
        matches.append(('半决赛', '2026-07-13 20:00', '半决赛-3', '半决赛-4'))
        
        # 季军赛
        matches.append(('季军赛', '2026-07-17 20:00', '季军赛-1', '季军赛-2'))
        
        # 决赛
        matches.append(('决赛', '2026-07-19 20:00', '决赛-1', '决赛-2'))
        
        # 插入数据库
        for m in matches:
            c.execute('''
                INSERT INTO matches (stage, match_datetime, team_a, team_b, actual_a, actual_b)
                VALUES (?, ?, ?, ?, NULL, NULL)
            ''', m)
        conn.commit()
        print("已添加 %d 场比赛，48支参赛队伍" % len(matches))
    
    conn.close()

init_db()

def is_locked(match_datetime_str):
    mt = datetime.strptime(match_datetime_str, '%Y-%m-%d %H:%M')
    return (mt - datetime.now()).total_seconds() < 300

def is_knocked():
    conn = get_db()
    row = conn.execute('SELECT MIN(match_datetime) FROM matches').fetchone()
    conn.close()
    if not row or not row[0]:
        return False
    first = datetime.strptime(row[0], '%Y-%m-%d %H:%M')
    return (first - datetime.now()).total_seconds() < 3600

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/set_user', methods=['POST'])
def set_user():
    data = request.json
    name = data.get('user', '').strip()
    if not name:
        return jsonify(success=False, message='请输入姓名')
    session['user'] = name
    return jsonify(success=True, user=name)

@app.route('/api/get_user', methods=['GET'])
def get_user():
    return jsonify(user=session.get('user', ''))

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

@app.route('/api/save_prediction', methods=['POST'])
def save_prediction():
    d = request.json
    user = d.get('user', '')
    match_id = d.get('match_id')
    pred_a = d.get('pred_a')
    pred_b = d.get('pred_b')
    
    if not user or pred_a is None or pred_b is None:
        return jsonify(success=False, message='请填写完整')
    
    conn = get_db()
    row = conn.execute('SELECT match_datetime FROM matches WHERE id=?', (match_id,)).fetchone()
    if row:
        if is_locked(row[0]):
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
    user = request.args.get('user', '')
    conn = get_db()
    rows = conn.execute('SELECT match_id, pred_a, pred_b FROM predictions WHERE user_name=?', (user,)).fetchall()
    conn.close()
    r = {}
    for row in rows:
        r[row[0]] = {'pred_a': row[1], 'pred_b': row[2]}
    return jsonify(r)

@app.route('/api/match_predictions', methods=['GET'])
def get_match_preds():
    match_id = request.args.get('match_id', '')
    if not match_id:
        return jsonify(success=False, message='缺少match_id')
    conn = get_db()
    rows = conn.execute('''
        SELECT user_name, pred_a, pred_b 
        FROM predictions 
        WHERE match_id=?
    ''', (match_id,)).fetchall()
    conn.close()
    preds = [{'user': r[0], 'pred_a': r[1], 'pred_b': r[2]} for r in rows]
    return jsonify(success=True, predictions=preds)

@app.route('/api/knockout/save', methods=['POST'])
def save_knockout():
    if is_knocked():
        return jsonify(success=False, message='已锁定（第一场比赛前1小时）')
    d = request.json
    user = d.get('user', '')
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
    user = request.args.get('user', '')
    conn = get_db()
    rows = conn.execute('SELECT round_name, predicted_teams FROM knockouts WHERE user_name=?', (user,)).fetchall()
    conn.close()
    preds = {r[0]: json.loads(r[1]) for r in rows}
    return jsonify(success=True, predictions=preds, locked=is_knocked())

@app.route('/api/knockout/teams', methods=['GET'])
def get_teams():
    conn = get_db()
    rows = conn.execute('SELECT team_a FROM matches UNION ALL SELECT team_b FROM matches').fetchall()
    conn.close()
    # 过滤掉淘汰赛的占位符（如"32强-1"、"决赛-2"等）
    valid_teams = []
    for r in rows:
        t = r[0]
        if not t:
            continue
        # 过滤：不包含数字、不包含"强"、"决赛"、"季军赛"
        if any(char.isdigit() for char in t):
            continue
        if '强' in t or '决赛' in t or '季军赛' in t:
            continue
        valid_teams.append(t)
    teams = sorted(set(valid_teams))
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

@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    conn = get_db()
    users = [r[0] for r in conn.execute('SELECT DISTINCT user_name FROM predictions').fetchall()]
    KO_SCORES = {'32强': 1, '16强': 2, '8强': 4, '4强': 6, '2强': 8, '冠军': 10}
    actual = {}
    for r in conn.execute('SELECT round_name, actual_teams FROM knockout_actual').fetchall():
        actual[r[0]] = json.loads(r[1])
    rankings = []
    for user in users:
        score = 0
        exact = 0
        correct = 0
        ko_score = 0
        for row in conn.execute('''
            SELECT p.pred_a, p.pred_b, m.actual_a, m.actual_b
            FROM predictions p JOIN matches m ON p.match_id=m.id
            WHERE p.user_name=? AND m.actual_a IS NOT NULL
        ''', (user,)):
            pa, pb, aa, ab = row
            if pa == aa and pb == ab:
                score += 4
                exact += 1
            elif (pa > pb and aa > ab) or (pa < pb and aa < ab) or (pa == pb and aa == ab):
                score += 1
                correct += 1
        for r in conn.execute('SELECT round_name, predicted_teams FROM knockouts WHERE user_name=?', (user,)):
            rnd = r[0]
            pred = json.loads(r[1])
            real = actual.get(rnd, [])
            hits = len(set(pred) & set(real))
            ko_score += hits * KO_SCORES.get(rnd, 0)
            score += hits * KO_SCORES.get(rnd, 0)
        rankings.append(dict(user=user, score=score, exact=exact, correct=correct, ko_score=ko_score))
    rankings.sort(key=lambda x: -x['score'])
    finished = conn.execute('SELECT COUNT(*) FROM matches WHERE actual_a IS NOT NULL').fetchone()[0]
    conn.close()
    avg = sum(r['score'] for r in rankings) / len(rankings) if rankings else 0
    return jsonify(users=len(rankings), finished=finished, 
                   avg_score=round(avg, 1), rankings=rankings)

@app.route('/api/user_detail', methods=['GET'])
def get_user_detail():
    user = request.args.get('user', '')
    if not user:
        return jsonify(success=False, message='缺少用户名')
    conn = get_db()
    score = 0
    exact = 0
    correct = 0
    KO_SCORES = {'32强': 1, '16强': 2, '8强': 4, '4强': 6, '2强': 8, '冠军': 10}
    for row in conn.execute('''
        SELECT p.pred_a, p.pred_b, m.actual_a, m.actual_b
        FROM predictions p JOIN matches m ON p.match_id=m.id
        WHERE p.user_name=? AND m.actual_a IS NOT NULL
    ''', (user,)):
        pa, pb, aa, ab = row
        if pa == aa and pb == ab:
            score += 4
            exact += 1
        elif (pa > pb and aa > ab) or (pa < pb and aa < ab) or (pa == pb and aa == ab):
            score += 1
            correct += 1
    actual = {}
    for r in conn.execute('SELECT round_name, actual_teams FROM knockout_actual').fetchall():
        actual[r[0]] = json.loads(r[1])
    for r in conn.execute('SELECT round_name, predicted_teams FROM knockouts WHERE user_name=?', (user,)):
        rnd = r[0]
        pred = json.loads(r[1])
        real = actual.get(rnd, [])
        hits = len(set(pred) & set(real))
        score += hits * KO_SCORES.get(rnd, 0)
    predictions = []
    for row in conn.execute('''
        SELECT p.match_id, p.pred_a, p.pred_b, m.stage, m.team_a, m.team_b, m.actual_a, m.actual_b
        FROM predictions p JOIN matches m ON p.match_id=m.id
        WHERE p.user_name=?
        ORDER BY m.match_datetime
    ''', (user,)):
        match_id, pred_a, pred_b, stage, team_a, team_b, actual_a, actual_b = row
        s = 0
        if actual_a is not None:
            if pred_a == actual_a and pred_b == actual_b:
                s = 4
            elif (pred_a > pred_b and actual_a > actual_b) or (pred_a < pred_b and actual_a < actual_b) or (pred_a == pred_b and actual_a == actual_b):
                s = 1
        predictions.append(dict(
            match_id=match_id, stage=stage, team_a=team_a, team_b=team_b,
            pred_a=pred_a, pred_b=pred_b, actual_a=actual_a, actual_b=actual_b, score=s
        ))
    # 添加晋级预测详情
    knockout_predictions = []
    for r in conn.execute('SELECT round_name, predicted_teams FROM knockouts WHERE user_name=?', (user,)):
        rnd = r[0]
        pred = json.loads(r[1])
        real = actual.get(rnd, [])
        for i, team in enumerate(pred):
            score_val = 0
            actual_team = None
            if team in real:
                score_val = KO_SCORES.get(rnd, 0)
                actual_team = team
            knockout_predictions.append(dict(
                round=rnd,
                team=team,
                actual_team=actual_team,
                score=score_val
            ))
    conn.close()
    return jsonify(success=True, user=user, total_score=score, exact_count=exact, correct_count=correct, predictions=predictions, knockout_predictions=knockout_predictions)

# ============= 数据导出/导入（备份功能） =============
@app.route('/api/export', methods=['GET'])
def export_data():
    """导出所有数据为JSON格式，用于备份"""
    conn = get_db()
    data = {}
    
    # 导出matches表
    data['matches'] = [dict(row) for row in conn.execute('SELECT * FROM matches').fetchall()]
    
    # 导出predictions表
    data['predictions'] = [dict(row) for row in conn.execute('SELECT * FROM predictions').fetchall()]
    
    # 导出knockouts表
    data['knockouts'] = [dict(row) for row in conn.execute('SELECT * FROM knockouts').fetchall()]
    
    # 导出knockout_actual表
    data['knockout_actual'] = [dict(row) for row in conn.execute('SELECT * FROM knockout_actual').fetchall()]
    
    conn.close()
    return jsonify(success=True, data=data)

# ============= 管理员删除参与者 =============
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
    try:
        # 删除该用户的所有预测
        conn.execute('DELETE FROM predictions WHERE user_name=?', (user_name,))
        # 删除该用户的晋级预测
        conn.execute('DELETE FROM knockouts WHERE user_name=?', (user_name,))
        conn.commit()
        conn.close()
        return jsonify(success=True, message=f'已删除参与者 {user_name} 及其所有预测')
    except Exception as e:
        conn.close()
        return jsonify(success=False, message=str(e))

@app.route('/api/import', methods=['POST'])
def import_data():
    """从JSON备份导入数据"""
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')
    
    backup = request.json
    conn = get_db()
    c = conn.cursor()
    
    try:
        # 清空现有数据（可选，这里选择追加模式）
        # 如果您想清空后再导入，取消下面的注释
        # c.execute('DELETE FROM matches')
        # c.execute('DELETE FROM predictions')
        # c.execute('DELETE FROM knockouts')
        # c.execute('DELETE FROM knockout_actual')
        
        # 导入matches
        for row in backup.get('matches', []):
            c.execute('''
                INSERT OR IGNORE INTO matches (id, stage, match_datetime, team_a, team_b, actual_a, actual_b)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (row['id'], row['stage'], row['match_datetime'], 
                 row['team_a'], row['team_b'], row['actual_a'], row['actual_b']))
        
        # 导入predictions
        for row in backup.get('predictions', []):
            c.execute('''
                INSERT OR IGNORE INTO predictions (id, user_name, match_id, pred_a, pred_b)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['id'], row['user_name'], row['match_id'], row['pred_a'], row['pred_b']))
        
        # 导入knockouts
        for row in backup.get('knockouts', []):
            c.execute('''
                INSERT OR IGNORE INTO knockouts (id, user_name, round_name, predicted_teams)
                VALUES (?, ?, ?, ?)
            ''', (row['id'], row['user_name'], row['round_name'], row['predicted_teams']))
        
        # 导入knockout_actual
        for row in backup.get('knockout_actual', []):
            c.execute('''
                INSERT OR IGNORE INTO knockout_actual (id, round_name, actual_teams)
                VALUES (?, ?, ?)
            ''', (row['id'], row['round_name'], row['actual_teams']))
        
        conn.commit()
        conn.close()
        return jsonify(success=True, message='数据导入成功！')
    except Exception as e:
        conn.close()
        return jsonify(success=False, message=str(e))

# ============= 获取所有参与者 =============
@app.route('/api/admin/get_users', methods=['GET'])
def get_all_users():
    if not session.get('is_admin'):
        return jsonify(success=False, message='需要管理员权限')
    
    conn = get_db()
    users = []
    # 使用 UNION 获取所有有预测或晋级预测的用户
    for row in conn.execute('''
        SELECT DISTINCT user_name FROM predictions 
        UNION 
        SELECT DISTINCT user_name FROM knockouts
    ''').fetchall():
        user_name = row['user_name']
        # 统计该用户的比分预测数
        pred_count = conn.execute('SELECT COUNT(*) FROM predictions WHERE user_name=?', (user_name,)).fetchone()[0]
        # 统计该用户的晋级预测项数
        knockout_count = 0
        ko_rows = conn.execute('SELECT COUNT(*) FROM knockouts WHERE user_name=?', (user_name,)).fetchone()[0]
        if ko_rows > 0:
            # 如果有晋级预测记录，统计总项数
            for kr in conn.execute('SELECT predicted_teams FROM knockouts WHERE user_name=?', (user_name,)).fetchall():
                import json
                teams = json.loads(kr['predicted_teams'])
                knockout_count += len(teams)
        users.append(dict(
            user_name=user_name,
            pred_count=pred_count,
            knockout_count=knockout_count
        ))
    conn.close()
    return jsonify(success=True, users=users)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print('启动2026世界杯竞猜...')
    print('http://0.0.0.0:%d' % port)
    app.run(host='0.0.0.0', port=port, debug=False)
