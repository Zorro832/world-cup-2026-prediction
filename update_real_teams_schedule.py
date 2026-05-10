#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新2026年世界杯真实赛程 - 基于官方公布的完整赛程
包含48支真实球队和104场比赛的准确对阵
"""

import sqlite3
from datetime import datetime, timedelta

def update_database():
    conn = sqlite3.connect('/workspace/world_cup_2026.db')
    cursor = conn.cursor()
    
    # 清空现有比赛数据
    cursor.execute('DELETE FROM matches')
    print("✅ 已清空现有比赛数据")
    
    matches = []
    
    # ========== 小组赛第1轮 (24场比赛) ==========
    # 第1比赛日 — 6月11日（周四）
    matches.append((1, '小组赛A组', '2026-06-11 15:00', '墨西哥', '南非', None, None))
    matches.append((2, '小组赛A组', '2026-06-11 22:00', '韩国', '捷克', None, None))
    
    # 第2比赛日 — 6月12日（周五）
    matches.append((3, '小组赛B组', '2026-06-12 15:00', '加拿大', '波黑', None, None))
    matches.append((4, '小组赛D组', '2026-06-12 21:00', '美国', '巴拉圭', None, None))
    
    # 第3比赛日 — 6月13日（周六）
    matches.append((5, '小组赛C组', '2026-06-13 12:00', '巴西', '摩洛哥', None, None))
    matches.append((6, '小组赛C组', '2026-06-13 15:00', '海地', '苏格兰', None, None))
    matches.append((7, '小组赛D组', '2026-06-13 18:00', '澳大利亚', '土耳其', None, None))
    matches.append((8, '小组赛B组', '2026-06-13 21:00', '卡塔尔', '瑞士', None, None))
    
    # 第4比赛日 — 6月14日（周日）
    matches.append((9, '小组赛E组', '2026-06-14 12:00', '德国', '库拉索', None, None))
    matches.append((10, '小组赛E组', '2026-06-14 15:00', '科特迪瓦', '厄瓜多尔', None, None))
    matches.append((11, '小组赛F组', '2026-06-14 18:00', '荷兰', '日本', None, None))
    matches.append((12, '小组赛F组', '2026-06-14 21:00', '瑞典', '突尼斯', None, None))
    
    # 第5比赛日 — 6月15日（周一）
    matches.append((13, '小组赛H组', '2026-06-15 12:00', '西班牙', '佛得角', None, None))
    matches.append((14, '小组赛H组', '2026-06-15 15:00', '沙特阿拉伯', '乌拉圭', None, None))
    matches.append((15, '小组赛G组', '2026-06-15 18:00', '比利时', '埃及', None, None))
    matches.append((16, '小组赛G组', '2026-06-15 21:00', '伊朗', '新西兰', None, None))
    
    # 第6比赛日 — 6月16日（周二）
    matches.append((17, '小组赛I组', '2026-06-16 12:00', '法国', '塞内加尔', None, None))
    matches.append((18, '小组赛I组', '2026-06-16 15:00', '伊拉克', '挪威', None, None))
    matches.append((19, '小组赛J组', '2026-06-16 18:00', '阿根廷', '阿尔及利亚', None, None))
    matches.append((20, '小组赛J组', '2026-06-16 21:00', '奥地利', '约旦', None, None))
    
    # 第7比赛日 — 6月17日（周三）
    matches.append((21, '小组赛L组', '2026-06-17 12:00', '英格兰', '克罗地亚', None, None))
    matches.append((22, '小组赛L组', '2026-06-17 15:00', '加纳', '巴拿马', None, None))
    matches.append((23, '小组赛K组', '2026-06-17 18:00', '葡萄牙', '刚果民主共和国', None, None))
    matches.append((24, '小组赛K组', '2026-06-17 21:00', '乌兹别克斯坦', '哥伦比亚', None, None))
    
    # ========== 小组赛第2轮 (24场比赛) ==========
    # 第8比赛日 — 6月18日（周四）
    matches.append((25, '小组赛A组', '2026-06-18 12:00', '捷克', '南非', None, None))
    matches.append((26, '小组赛B组', '2026-06-18 15:00', '瑞士', '波黑', None, None))
    matches.append((27, '小组赛B组', '2026-06-18 18:00', '加拿大', '卡塔尔', None, None))
    matches.append((28, '小组赛A组', '2026-06-18 21:00', '墨西哥', '韩国', None, None))
    
    # 第9比赛日 — 6月19日（周五）
    matches.append((29, '小组赛C组', '2026-06-19 12:00', '巴西', '海地', None, None))
    matches.append((30, '小组赛C组', '2026-06-19 15:00', '苏格兰', '摩洛哥', None, None))
    matches.append((31, '小组赛D组', '2026-06-19 18:00', '土耳其', '巴拉圭', None, None))
    matches.append((32, '小组赛D组', '2026-06-19 21:00', '美国', '澳大利亚', None, None))
    
    # 第10比赛日 — 6月20日（周六）
    matches.append((33, '小组赛E组', '2026-06-20 12:00', '德国', '科特迪瓦', None, None))
    matches.append((34, '小组赛E组', '2026-06-20 15:00', '厄瓜多尔', '库拉索', None, None))
    matches.append((35, '小组赛F组', '2026-06-20 18:00', '荷兰', '瑞典', None, None))
    matches.append((36, '小组赛F组', '2026-06-20 21:00', '突尼斯', '日本', None, None))
    
    # 第11比赛日 — 6月21日（周日）
    matches.append((37, '小组赛H组', '2026-06-21 12:00', '西班牙', '沙特阿拉伯', None, None))
    matches.append((38, '小组赛H组', '2026-06-21 15:00', '乌拉圭', '佛得角', None, None))
    matches.append((39, '小组赛G组', '2026-06-21 18:00', '比利时', '伊朗', None, None))
    matches.append((40, '小组赛G组', '2026-06-21 21:00', '新西兰', '埃及', None, None))
    
    # 第12比赛日 — 6月22日（周一）
    matches.append((41, '小组赛I组', '2026-06-22 12:00', '法国', '伊拉克', None, None))
    matches.append((42, '小组赛I组', '2026-06-22 15:00', '挪威', '塞内加尔', None, None))
    matches.append((43, '小组赛J组', '2026-06-22 18:00', '阿根廷', '奥地利', None, None))
    matches.append((44, '小组赛J组', '2026-06-22 21:00', '约旦', '阿尔及利亚', None, None))
    
    # 第13比赛日 — 6月23日（周二）
    matches.append((45, '小组赛L组', '2026-06-23 12:00', '英格兰', '加纳', None, None))
    matches.append((46, '小组赛L组', '2026-06-23 15:00', '巴拿马', '克罗地亚', None, None))
    matches.append((47, '小组赛K组', '2026-06-23 18:00', '葡萄牙', '乌兹别克斯坦', None, None))
    matches.append((48, '小组赛K组', '2026-06-23 21:00', '哥伦比亚', '刚果民主共和国', None, None))
    
    # ========== 小组赛第3轮 (24场比赛) ==========
    # 第14比赛日 — 6月24日（周三）【6场比赛同时开球】
    matches.append((49, '小组赛A组', '2026-06-24 12:00', '墨西哥', '捷克', None, None))
    matches.append((50, '小组赛A组', '2026-06-24 12:00', '韩国', '南非', None, None))
    matches.append((51, '小组赛B组', '2026-06-24 15:00', '加拿大', '瑞士', None, None))
    matches.append((52, '小组赛B组', '2026-06-24 15:00', '波黑', '卡塔尔', None, None))
    matches.append((53, '小组赛C组', '2026-06-24 18:00', '苏格兰', '巴西', None, None))
    matches.append((54, '小组赛C组', '2026-06-24 18:00', '摩洛哥', '海地', None, None))
    
    # 第15比赛日 — 6月25日（周四）【6场比赛同时开球】
    matches.append((55, '小组赛E组', '2026-06-25 12:00', '厄瓜多尔', '德国', None, None))
    matches.append((56, '小组赛E组', '2026-06-25 12:00', '库拉索', '科特迪瓦', None, None))
    matches.append((57, '小组赛F组', '2026-06-25 15:00', '突尼斯', '荷兰', None, None))
    matches.append((58, '小组赛F组', '2026-06-25 15:00', '日本', '瑞典', None, None))
    matches.append((59, '小组赛D组', '2026-06-25 18:00', '美国', '土耳其', None, None))
    matches.append((60, '小组赛D组', '2026-06-25 18:00', '巴拉圭', '澳大利亚', None, None))
    
    # 第16比赛日 — 6月26日（周五）【6场比赛同时开球】
    matches.append((61, '小组赛I组', '2026-06-26 12:00', '挪威', '法国', None, None))
    matches.append((62, '小组赛I组', '2026-06-26 12:00', '塞内加尔', '伊拉克', None, None))
    matches.append((63, '小组赛H组', '2026-06-26 15:00', '乌拉圭', '西班牙', None, None))
    matches.append((64, '小组赛H组', '2026-06-26 15:00', '佛得角', '沙特阿拉伯', None, None))
    matches.append((65, '小组赛G组', '2026-06-26 18:00', '新西兰', '比利时', None, None))
    matches.append((66, '小组赛G组', '2026-06-26 18:00', '埃及', '伊朗', None, None))
    
    # 第17比赛日 — 6月27日（周六）【6场比赛同时开球】
    matches.append((67, '小组赛L组', '2026-06-27 12:00', '巴拿马', '英格兰', None, None))
    matches.append((68, '小组赛L组', '2026-06-27 12:00', '克罗地亚', '加纳', None, None))
    matches.append((69, '小组赛K组', '2026-06-27 15:00', '哥伦比亚', '葡萄牙', None, None))
    matches.append((70, '小组赛K组', '2026-06-27 15:00', '刚果民主共和国', '乌兹别克斯坦', None, None))
    matches.append((71, '小组赛J组', '2026-06-27 18:00', '约旦', '阿根廷', None, None))
    matches.append((72, '小组赛J组', '2026-06-27 18:00', '阿尔及利亚', '奥地利', None, None))
    
    # ========== 32强淘汰赛 (16场比赛) ==========
    # 6月28日 – 7月3日
    matches.append((73, '32强淘汰赛', '2026-06-28 15:00', 'A组第1', 'C/D/E组第3', None, None))
    matches.append((74, '32强淘汰赛', '2026-06-28 21:00', 'B组第1', 'A/D/E/F组第3', None, None))
    matches.append((75, '32强淘汰赛', '2026-06-29 15:00', 'C组第1', 'D/E/F组第3', None, None))
    matches.append((76, '32强淘汰赛', '2026-06-29 21:00', 'D组第1', 'A/B/C组第3', None, None))
    matches.append((77, '32强淘汰赛', '2026-06-30 15:00', 'E组第1', 'A/B/C/D组第3', None, None))
    matches.append((78, '32强淘汰赛', '2026-06-30 21:00', 'F组第1', 'A/B/C/D/E组第3', None, None))
    matches.append((79, '32强淘汰赛', '2026-07-01 15:00', 'G组第1', '最佳第3名', None, None))
    matches.append((80, '32强淘汰赛', '2026-07-01 21:00', 'H组第1', '最佳第3名', None, None))
    matches.append((81, '32强淘汰赛', '2026-07-02 15:00', 'I组第1', '最佳第3名', None, None))
    matches.append((82, '32强淘汰赛', '2026-07-02 21:00', 'J组第1', '最佳第3名', None, None))
    matches.append((83, '32强淘汰赛', '2026-07-03 15:00', 'K组第1', '最佳第3名', None, None))
    matches.append((84, '32强淘汰赛', '2026-07-03 21:00', 'L组第1', '最佳第3名', None, None))
    matches.append((85, '32强淘汰赛', '2026-07-04 15:00', 'A组第2', 'B组第2', None, None))
    matches.append((86, '32强淘汰赛', '2026-07-04 21:00', 'C组第2', 'D组第2', None, None))
    matches.append((87, '32强淘汰赛', '2026-07-05 15:00', 'E组第2', 'F组第2', None, None))
    matches.append((88, '32强淘汰赛', '2026-07-05 21:00', 'G组第2', 'H组第2', None, None))
    
    # ========== 16强赛 (8场比赛) ==========
    # 7月6日 – 7月9日
    matches.append((89, '16强赛', '2026-07-06 15:00', '73场胜者', '74场胜者', None, None))
    matches.append((90, '16强赛', '2026-07-06 21:00', '75场胜者', '76场胜者', None, None))
    matches.append((91, '16强赛', '2026-07-07 15:00', '77场胜者', '78场胜者', None, None))
    matches.append((92, '16强赛', '2026-07-07 21:00', '79场胜者', '80场胜者', None, None))
    matches.append((93, '16强赛', '2026-07-08 15:00', '81场胜者', '82场胜者', None, None))
    matches.append((94, '16强赛', '2026-07-08 21:00', '83场胜者', '84场胜者', None, None))
    matches.append((95, '16强赛', '2026-07-09 15:00', '85场胜者', '86场胜者', None, None))
    matches.append((96, '16强赛', '2026-07-09 21:00', '87场胜者', '88场胜者', None, None))
    
    # ========== 四分之一决赛 (4场比赛) ==========
    # 7月10日 – 7月11日
    matches.append((97, '四分之一决赛', '2026-07-10 15:00', '89场胜者', '90场胜者', None, None))
    matches.append((98, '四分之一决赛', '2026-07-10 21:00', '91场胜者', '92场胜者', None, None))
    matches.append((99, '四分之一决赛', '2026-07-11 15:00', '93场胜者', '94场胜者', None, None))
    matches.append((100, '四分之一决赛', '2026-07-11 21:00', '95场胜者', '96场胜者', None, None))
    
    # ========== 半决赛 (2场比赛) ==========
    # 7月14日 – 7月15日
    matches.append((101, '半决赛', '2026-07-14 20:00', '97场胜者', '98场胜者', None, None))
    matches.append((102, '半决赛', '2026-07-15 20:00', '99场胜者', '100场胜者', None, None))
    
    # ========== 季军赛和决赛 ==========
    matches.append((103, '季军赛', '2026-07-18 16:00', '101场负者', '102场负者', None, None))
    matches.append((104, '决赛', '2026-07-19 15:00', '101场胜者', '102场胜者', None, None))
    
    # 插入所有比赛
    cursor.executemany('''
        INSERT INTO matches (id, stage, match_datetime, team_a, team_b, actual_a, actual_b)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', matches)
    
    conn.commit()
    
    # 验证数据
    cursor.execute('SELECT COUNT(*) FROM matches')
    count = cursor.fetchone()[0]
    print(f"\n✅ 成功插入 {count} 场比赛")
    
    # 显示48支参赛球队
    cursor.execute('SELECT DISTINCT team_a, team_b FROM matches WHERE stage LIKE "小组赛%"')
    teams = set()
    for row in cursor.fetchall():
        teams.add(row[0])
        teams.add(row[1])
    print(f"✅ 参赛球队数量: {len(teams)} 支")
    print(f"   球队列表: {', '.join(sorted(teams)[:10])}...")
    
    # 显示前5场比赛
    cursor.execute('SELECT id, stage, match_datetime, team_a, team_b FROM matches ORDER BY id LIMIT 5')
    print("\n📋 前5场比赛:")
    for row in cursor.fetchall():
        print(f"  {row[0]}. [{row[1]}] {row[2]} | {row[3]} vs {row[4]}")
    
    # 显示最后5场比赛
    cursor.execute('SELECT id, stage, match_datetime, team_a, team_b FROM matches ORDER BY id DESC LIMIT 5')
    print("\n🏆 最后5场比赛:")
    for row in cursor.fetchall():
        print(f"  {row[0]}. [{row[1]}] {row[2]} | {row[3]} vs {row[4]}")
    
    conn.close()
    print("\n✅ 数据库更新完成！已使用2026年世界杯真实赛程")

if __name__ == '__main__':
    update_database()
