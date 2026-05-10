#!/usr/bin/env python3
import sqlite3
from datetime import datetime, timedelta
import os

# 删除旧数据库
if os.path.exists('world_cup_2026.db'):
    os.remove('world_cup_2026.db')
    print("✓ 旧数据库已删除")

conn = sqlite3.connect('world_cup_2026.db')
cursor = conn.cursor()

# 创建所有表
cursor.execute('''
    CREATE TABLE matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stage TEXT,
        match_datetime TEXT,
        team_a TEXT,
        team_b TEXT,
        actual_a INTEGER,
        actual_b INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        match_id INTEGER,
        pred_a INTEGER,
        pred_b INTEGER,
        UNIQUE(user_name, match_id)
    )
''')

cursor.execute('''
    CREATE TABLE knockouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        round_name TEXT,
        predicted_teams TEXT,
        UNIQUE(user_name, round_name)
    )
''')

cursor.execute('''
    CREATE TABLE knockout_actual (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_name TEXT UNIQUE,
        actual_teams TEXT
    )
''')

print("✓ 数据库表已创建")

# 2026世界杯48支参赛队伍（真实档位）
all_teams = [
    # 第1档（东道主+世界排名前11）
    '墨西哥', '美国', '加拿大', '阿根廷', '法国', '巴西', '英格兰', '比利时', '葡萄牙', '德国', '西班牙', '意大利',
    # 第2档
    '荷兰', '克罗地亚', '乌拉圭', '哥伦比亚', '摩洛哥', '瑞士', '丹麦', '波兰', '日本', '韩国', '塞内加尔', '奥地利',
    # 第3档
    '乌克兰', '塞尔维亚', '捷克', '匈牙利', '瑞典', '挪威', '苏格兰', '威尔士', '爱尔兰', '斯洛伐克', '罗马尼亚', '希腊',
    # 第4档
    '厄瓜多尔', '秘鲁', '智利', '尼日利亚', '喀麦隆', '加纳', '马里', '突尼斯', '伊朗', '澳大利亚', '沙特阿拉伯', '卡塔尔',
]

print(f"✓ 参赛队伍：{len(all_teams)} 支")

# 生成小组赛（12组，每组4队，共72场）
match_time = datetime(2026, 6, 11, 20, 0)
matches = []

for i in range(12):
    group = chr(ord('A') + i)
    teams = all_teams[i*4:(i+1)*4]
    pairings = [(0,1),(2,3),(0,2),(1,3),(0,3),(1,2)]
    
    for a, b in pairings:
        matches.append((
            f'小组赛{group}组',
            match_time.strftime('%Y-%m-%d %H:%M'),
            teams[a],
            teams[b]
        ))
        match_time += timedelta(hours=3)
    
    match_time += timedelta(days=1)
    match_time = match_time.replace(hour=20, minute=0)

print(f"✓ 已添加 {len(matches)} 场小组赛")

# 淘汰赛（32场）
ko_schedule = [
    ('32强', 16, datetime(2026, 6, 28, 20, 0)),
    ('16强', 8, datetime(2026, 7, 4, 20, 0)),
    ('8强', 4, datetime(2026, 7, 8, 20, 0)),
]

for stage, count, start_time in ko_schedule:
    t = start_time
    for i in range(count):
        matches.append((
            stage,
            t.strftime('%Y-%m-%d %H:%M'),
            f'{stage}-{i*2+1}',
            f'{stage}-{i*2+2}'
        ))
        t += timedelta(hours=3)
        if (i+1) % 2 == 0:
            t += timedelta(days=1)
            t = t.replace(hour=20, minute=0)

# 半决赛
matches.append(('半决赛', '2026-07-12 20:00', '半决赛-1', '半决赛-2'))
matches.append(('半决赛', '2026-07-13 20:00', '半决赛-3', '半决赛-4'))

# 季军赛
matches.append(('季军赛', '2026-07-17 20:00', '季军赛-1', '季军赛-2'))

# 决赛
matches.append(('决赛', '2026-07-19 20:00', '决赛-1', '决赛-2'))

print(f"✓ 已添加 32 场淘汰赛")

# 插入所有比赛
for match in matches:
    cursor.execute('''
        INSERT INTO matches (stage, match_datetime, team_a, team_b, actual_a, actual_b)
        VALUES (?, ?, ?, ?, NULL, NULL)
    ''', match)

conn.commit()
conn.close()

print(f"\n✅ 总共添加 {len(matches)} 场比赛")
print("✅ 数据库重建完成，ID从1开始！")
print(f"\n参赛队伍（48支）：")
for i in range(0, 48, 4):
    print(f"  {all_teams[i]}, {all_teams[i+1]}, {all_teams[i+2]}, {all_teams[i+3]}")
