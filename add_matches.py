#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补充完整的2026世界杯赛程（104场比赛）"""
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('world_cup_2026.db')
cursor = conn.cursor()

# 清空现有比赛数据（重新生成完整赛程）
cursor.execute('DELETE FROM matches')
cursor.execute('DELETE FROM predictions')  # 同时清空预测（因为比赛ID会变化）

# 2026世界杯比赛时间：2026年6月11日 - 7月19日
# 48支球队，12个小组，104场比赛

base_date = datetime(2026, 6, 11, 20, 0)  # 开幕式 + 揭幕战

matches = []

# ========== 小组赛 (72场) ==========
# 12个小组 (A-L)，每组4队，每组6场比赛

groups = {
    'A': ['墨西哥', '波兰', '阿根廷', '沙特阿拉伯'],
    'B': ['美国', '威尔士', '英格兰', '伊朗'],
    'C': ['法国', '丹麦', '突尼斯', '澳大利亚'],
    'D': ['巴西', '克罗地亚', '塞尔维亚', '瑞士'],
    'E': ['德国', '西班牙', '日本', '韩国'],
    'F': ['葡萄牙', '荷兰', '塞内加尔', '厄瓜多尔'],
    'G': ['比利时', '乌拉圭', '加拿大', '摩洛哥'],
    'H': ['阿根廷', '墨西哥', '波兰', '沙特'],  # 实际抽签后调整
    'I': ['法国', '丹麦', '突尼斯', '澳大利亚'],
    'J': ['巴西', '克罗地亚', '塞尔维亚', '瑞士'],
    'K': ['德国', '西班牙', '日本', '韩国'],
    'L': ['葡萄牙', '荷兰', '塞内加尔', '厄瓜多尔'],
}

match_time = base_date

for group, teams in groups.items():
    # 每组6场比赛
    # 第1轮
    for i in range(0, 4, 2):
        matches.append((f'小组赛{group}组', match_time.strftime('%Y-%m-%d %H:%M'), teams[i], teams[i+1]))
        match_time += timedelta(hours=3)
    
    # 第2轮
    for i in range(1, 4, 2):
        matches.append((f'小组赛{group}组', match_time.strftime('%Y-%m-%d %H:%M'), teams[i], teams[i-1]))
        match_time += timedelta(hours=3)
    
    # 第3轮
    matches.append((f'小组赛{group}组', match_time.strftime('%Y-%m-%d %H:%M'), teams[0], teams[2]))
    matches.append((f'小组赛{group}组', match_time.strftime('%Y-%m-%d %H:%M'), teams[1], teams[3]))
    match_time += timedelta(hours=3)
    
    # 第4轮
    matches.append((f'小组赛{group}组', match_time.strftime('%Y-%m-%d %H:%M'), teams[2], teams[3]))
    matches.append((f'小组赛{group}组', match_time.strftime('%Y-%m-%d %H:%M'), teams[0], teams[1]))
    match_time += timedelta(hours=3)
    
    # 第5轮
    matches.append((f'小组赛{group}组', match_time.strftime('%Y-%m-%d %H:%M'), teams[0], teams[3]))
    matches.append((f'小组赛{group}组', match_time.strftime('%Y-%m-%d %H:%M'), teams[1], teams[2]))
    match_time += timedelta(hours=3)
    
    # 第6轮
    matches.append((f'小组赛{group}组', match_time.strftime('%Y-%m-%d %H:%M'), teams[2], teams[0]))
    matches.append((f'小组赛{group}组', match_time.strftime('%Y-%m-%d %H:%M'), teams[3], teams[1]))
    match_time += timedelta(hours=3)
    
    # 小组赛间隔一天
    match_time += timedelta(days=1)

# 插入小组赛
for match in matches:
    cursor.execute('''
        INSERT INTO matches (stage, match_datetime, team_a, team_b, actual_a, actual_b)
        VALUES (?, ?, ?, ?, NULL, NULL)
    ''', match)

print(f'✅ 已插入 {len(matches)} 场小组赛')

# ========== 淘汰赛 (32场) ==========
knockout_matches = []

# 32强 (16场) - 2026年6月28日开始
match_time = datetime(2026, 6, 28, 20, 0)
for i in range(16):
    knockout_matches.append(('32强', match_time.strftime('%Y-%m-%d %H:%M'), f'32强-胜者{i*2+1}', f'32强-胜者{i*2+2}'))
    match_time += timedelta(hours=3)

# 16强 (8场) - 2026年7月3日开始
match_time = datetime(2026, 7, 3, 20, 0)
for i in range(8):
    knockout_matches.append(('16强', match_time.strftime('%Y-%m-%d %H:%M'), f'16强-胜者{i*2+1}', f'16强-胜者{i*2+2}'))
    match_time += timedelta(hours=3)

# 8强 (4场) - 2026年7月7日开始
match_time = datetime(2026, 7, 7, 20, 0)
for i in range(4):
    knockout_matches.append(('8强', match_time.strftime('%Y-%m-%d %H:%M'), f'8强-胜者{i*2+1}', f'8强-胜者{i*2+2}'))
    match_time += timedelta(hours=3)

# 半决赛 (2场) - 2026年7月11日
knockout_matches.append(('半决赛', '2026-07-11 20:00', '半决赛-胜者1', '半决赛-胜者2'))
knockout_matches.append(('半决赛', '2026-07-12 20:00', '半决赛-胜者3', '半决赛-胜者4'))

# 季军赛 - 2026年7月17日
knockout_matches.append(('季军赛', '2026-07-17 20:00', '半决赛-负者1', '半决赛-负者2'))

# 决赛 - 2026年7月19日
knockout_matches.append(('决赛', '2026-07-19 20:00', '决赛-胜者1', '决赛-胜者2'))

# 插入淘汰赛
for match in knockout_matches:
    cursor.execute('''
        INSERT INTO matches (stage, match_datetime, team_a, team_b, actual_a, actual_b)
        VALUES (?, ?, ?, ?, NULL, NULL)
    ''', match)

print(f'✅ 已插入 {len(knockout_matches)} 场淘汰赛')

total = len(matches) + len(knockout_matches)
print(f'✅ 总共插入 {total} 场比赛')

conn.commit()
conn.close()

print('✅ 赛程补充完成！')
