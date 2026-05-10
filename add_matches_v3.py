#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026年世界杯完整赛程（48队，104场比赛）"""
from datetime import datetime, timedelta
import sqlite3

conn = sqlite3.connect('world_cup_2026.db')
cursor = conn.cursor()

# 删除现有数据
cursor.execute('DELETE FROM matches')
cursor.execute('DELETE FROM predictions')
conn.commit()

match_time = datetime(2026, 6, 11, 20, 0)  # 揭幕战：2026年6月11日 20:00
matches = []

# ========== 小组赛 (72场) ==========
# 2026世界杯扩军至48队，12个小组，每组4队
# 12 × 6 = 72场

groups = {
    'A': ['墨西哥', '波兰', '阿根廷', '沙特阿拉伯'],
    'B': ['美国', '威尔士', '英格兰', '伊朗'],
    'C': ['法国', '丹麦', '突尼斯', '澳大利亚'],
    'D': ['巴西', '克罗地亚', '塞尔维亚', '瑞士'],
    'E': ['德国', '西班牙', '日本', '韩国'],
    'F': ['葡萄牙', '荷兰', '塞内加尔', '厄瓜多尔'],
    'G': ['比利时', '乌拉圭', '加拿大', '摩洛哥'],
    'H': ['卡塔尔', '厄瓜多尔', '塞内加尔', '荷兰'],
    'I': ['阿根廷', '沙特阿拉伯', '墨西哥', '波兰'],
    'J': ['法国', '澳大利亚', '丹麦', '突尼斯'],
    'K': ['巴西', '塞尔维亚', '瑞士', '克罗地亚'],
    'L': ['德国', '韩国', '西班牙', '日本'],
}

for group, teams in groups.items():
    # 每组6场比赛
    pairings = [
        (0, 1), (2, 3),  # 第1轮
        (0, 2), (1, 3),  # 第2轮
        (0, 3), (1, 2),  # 第3轮
    ]
    
    for i, (a, b) in enumerate(pairings):
        matches.append((
            f'小组赛{group}组',
            match_time.strftime('%Y-%m-%d %H:%M'),
            teams[a],
            teams[b]
        ))
        match_time += timedelta(hours=3)
    
    # 每个小组赛间隔1天
    match_time += timedelta(days=1)
    match_time = match_time.replace(hour=20, minute=0)

print(f'✅ 已添加 {len(matches)} 场小组赛')

# ========== 淘汰赛 (32场) ==========
# 32强：16场
match_time = datetime(2026, 6, 28, 20, 0)
for i in range(16):
    matches.append((
        '32强',
        match_time.strftime('%Y-%m-%d %H:%M'),
        f'32强-{i*2+1}',
        f'32强-{i*2+2}'
    ))
    match_time += timedelta(hours=3)
    if (i+1) % 2 == 0:
        match_time += timedelta(days=1)
        match_time = match_time.replace(hour=20, minute=0)

# 16强：8场
match_time = datetime(2026, 7, 4, 20, 0)
for i in range(8):
    matches.append((
        '16强',
        match_time.strftime('%Y-%m-%d %H:%M'),
        f'16强-{i*2+1}',
        f'16强-{i*2+2}'
    ))
    match_time += timedelta(hours=3)
    if (i+1) % 2 == 0:
        match_time += timedelta(days=1)
        match_time = match_time.replace(hour=20, minute=0)

# 8强：4场
match_time = datetime(2026, 7, 8, 20, 0)
for i in range(4):
    matches.append((
        '8强',
        match_time.strftime('%Y-%m-%d %H:%M'),
        f'8强-{i*2+1}',
        f'8强-{i*2+2}'
    ))
    match_time += timedelta(hours=3)
    if (i+1) % 2 == 0:
        match_time += timedelta(days=1)
        match_time = match_time.replace(hour=20, minute=0)

# 半决赛：2场
matches.append(('半决赛', '2026-07-12 20:00', '半决赛-1', '半决赛-2'))
matches.append(('半决赛', '2026-07-13 20:00', '半决赛-3', '半决赛-4'))

# 季军赛：1场
matches.append(('季军赛', '2026-07-17 20:00', '季军赛-1', '季军赛-2'))

# 决赛：1场
matches.append(('决赛', '2026-07-19 20:00', '决赛-1', '决赛-2'))

print(f'✅ 已添加 32 场淘汰赛')

# 插入所有比赛
for match in matches:
    cursor.execute('''
        INSERT INTO matches (stage, match_datetime, team_a, team_b, actual_a, actual_b)
        VALUES (?, ?, ?, ?, NULL, NULL)
    ''', match)

conn.commit()
conn.close()

print(f'✅ 总共添加 {len(matches)} 场比赛')
print('✅ 赛程已重置，ID从1开始！')
