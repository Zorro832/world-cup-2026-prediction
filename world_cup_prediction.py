#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026年世界杯竞猜桌面应用
使用Tkinter制作图形界面，SQLite保存数据
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import json
import sqlite3
import os

class WorldCupPredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("2026年世界杯竞猜")
        self.root.geometry("900x700")
        
        # 初始化数据库
        self.init_db()
        
        # 当前用户
        self.current_user = ""
        
        # 创建界面
        self.create_widgets()
        
        # 加载数据
        self.load_matches()
        self.update_rankings()
    
    def init_db(self):
        """初始化数据库"""
        self.conn = sqlite3.connect('world_cup_2026.db')
        self.cursor = self.conn.cursor()
        
        # 创建比赛表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                stage TEXT,
                match_date TEXT,
                match_time TEXT,
                team_a TEXT,
                team_b TEXT,
                actual_a INTEGER,
                actual_b INTEGER
            )
        ''')
        
        # 创建预测表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT,
                match_id INTEGER,
                pred_a INTEGER,
                pred_b INTEGER,
                UNIQUE(user_name, match_id)
            )
        ''')
        
        self.conn.commit()
        
        # 如果没有比赛数据，插入初始数据
        self.cursor.execute("SELECT COUNT(*) FROM matches")
        if self.cursor.fetchone()[0] == 0:
            self.insert_sample_matches()
    
    def insert_sample_matches(self):
        """插入示例比赛数据"""
        matches = [
            (1, "小组赛A组", "2026-06-11", "20:00", "墨西哥", "波兰", None, None),
            (2, "小组赛A组", "2026-06-11", "23:00", "阿根廷", "沙特阿拉伯", None, None),
            (3, "小组赛A组", "2026-06-16", "20:00", "墨西哥", "沙特阿拉伯", None, None),
            (4, "小组赛A组", "2026-06-16", "23:00", "阿根廷", "波兰", None, None),
            (5, "小组赛A组", "2026-06-21", "20:00", "墨西哥", "阿根廷", None, None),
            (6, "小组赛A组", "2026-06-21", "20:00", "波兰", "沙特阿拉伯", None, None),
            (7, "小组赛B组", "2026-06-12", "20:00", "美国", "威尔士", None, None),
            (8, "小组赛B组", "2026-06-12", "23:00", "英格兰", "伊朗", None, None),
            (9, "小组赛B组", "2026-06-17", "20:00", "美国", "英格兰", None, None),
            (10, "小组赛B组", "2026-06-17", "23:00", "威尔士", "伊朗", None, None),
        ]
        
        self.cursor.executemany('''
            INSERT OR REPLACE INTO matches 
            (id, stage, match_date, match_time, team_a, team_b, actual_a, actual_b)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', matches)
        self.conn.commit()
    
    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill='x')
        
        title_label = ttk.Label(
            title_frame, 
            text="⚽ 2026年世界杯竞猜", 
            font=('Arial', 20, 'bold')
        )
        title_label.pack()
        
        rule_label = ttk.Label(
            title_frame,
            text="积分规则：准确比分 4分 | 猜中胜负 1分 | 未猜中 0分",
            font=('Arial', 11),
            foreground='#d00'
        )
        rule_label.pack()
        
        # 用户名输入
        user_frame = ttk.Frame(self.root, padding="10")
        user_frame.pack(fill='x')
        
        ttk.Label(user_frame, text="姓名：", font=('Arial', 11)).pack(side='left')
        self.user_entry = ttk.Entry(user_frame, width=20, font=('Arial', 11))
        self.user_entry.pack(side='left', padx=(0, 10))
        
        ttk.Button(user_frame, text="确认", command=self.set_user).pack(side='left')
        self.user_status = ttk.Label(user_frame, text="未登录", foreground='red')
        self.user_status.pack(side='left', padx=10)
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # 预测标签页
        self.predict_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.predict_frame, text="📝 填写预测")
        self.create_predict_tab()
        
        # 排名标签页
        self.ranking_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ranking_frame, text="🏆 实时排名")
        self.create_ranking_tab()
        
        # 管理员标签页
        self.admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.admin_frame, text="⚙️ 管理员")
        self.create_admin_tab()
    
    def create_predict_tab(self):
        """创建预测标签页"""
        # 提示信息
        info = ttk.Label(
            self.predict_frame,
            text="💡 提示：比赛开始前5分钟将锁定该场比赛的预测",
            font=('Arial', 10)
        )
        info.pack(pady=5)
        
        # 创建表格
        columns = ('ID', '阶段', '日期', '时间', '队伍A', '队伍B', '预测A', '预测B', '状态')
        self.predict_tree = ttk.Treeview(
            self.predict_frame,
            columns=columns,
            show='headings',
            height=20
        )
        
        # 设置列标题和宽度
        col_widths = [40, 100, 80, 60, 100, 100, 60, 60, 80]
        for col, width in zip(columns, col_widths):
            self.predict_tree.heading(col, text=col)
            self.predict_tree.column(col, width=width, anchor='center')
        
        self.predict_tree.pack(pady=10, padx=10, fill='both', expand=True)
        
        # 预测输入框
        input_frame = ttk.Frame(self.predict_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="比赛ID：").grid(row=0, column=0, padx=5)
        self.match_id_entry = ttk.Entry(input_frame, width=10)
        self.match_id_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="预测A：").grid(row=0, column=2, padx=5)
        self.pred_a_entry = ttk.Entry(input_frame, width=10)
        self.pred_a_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="预测B：").grid(row=0, column=4, padx=5)
        self.pred_b_entry = ttk.Entry(input_frame, width=10)
        self.pred_b_entry.grid(row=0, column=5, padx=5)
        
        ttk.Button(input_frame, text="保存预测", command=self.save_prediction).grid(row=0, column=6, padx=10)
        
        # 绑定双击事件
        self.predict_tree.bind('<Double-1>', self.on_tree_double_click)
    
    def create_ranking_tab(self):
        """创建排名标签页"""
        # 统计信息
        stats_frame = ttk.Frame(self.ranking_frame)
        stats_frame.pack(pady=10)
        
        self.stat_users = ttk.Label(stats_frame, text="参与人数：0", font=('Arial', 11))
        self.stat_users.grid(row=0, column=0, padx=20)
        
        self.stat_matches = ttk.Label(stats_frame, text="已完成：0", font=('Arial', 11))
        self.stat_matches.grid(row=0, column=1, padx=20)
        
        self.stat_avg = ttk.Label(stats_frame, text="平均得分：0", font=('Arial', 11))
        self.stat_avg.grid(row=0, column=2, padx=20)
        
        # 排名表格
        columns = ('排名', '姓名', '总积分', '准确比分', '猜中胜负')
        self.ranking_tree = ttk.Treeview(
            self.ranking_frame,
            columns=columns,
            show='headings',
            height=20
        )
        
        for col in columns:
            self.ranking_tree.heading(col, text=col)
            self.ranking_tree.column(col, width=120, anchor='center')
        
        self.ranking_tree.pack(pady=10, padx=10, fill='both', expand=True)
        
        ttk.Button(self.ranking_frame, text="刷新排名", command=self.update_rankings).pack(pady=10)
    
    def create_admin_tab(self):
        """创建管理员标签页"""
        info = ttk.Label(
            self.admin_frame,
            text="⚙️ 管理员专区：填写实际比赛结果",
            font=('Arial', 11)
        )
        info.pack(pady=10)
        
        # 实际结果输入
        input_frame = ttk.Frame(self.admin_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="比赛ID：").grid(row=0, column=0, padx=5)
        self.admin_match_id = ttk.Entry(input_frame, width=10)
        self.admin_match_id.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="实际A：").grid(row=0, column=2, padx=5)
        self.actual_a_entry = ttk.Entry(input_frame, width=10)
        self.actual_a_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="实际B：").grid(row=0, column=4, padx=5)
        self.actual_b_entry = ttk.Entry(input_frame, width=10)
        self.actual_b_entry.grid(row=0, column=5, padx=5)
        
        ttk.Button(input_frame, text="保存结果", command=self.save_actual_result).grid(row=0, column=6, padx=10)
        
        # 比赛列表
        columns = ('ID', '阶段', '日期', '时间', '队伍A', '队伍B', '实际A', '实际B')
        self.admin_tree = ttk.Treeview(
            self.admin_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        col_widths = [40, 100, 80, 60, 100, 100, 60, 60]
        for col, width in zip(columns, col_widths):
            self.admin_tree.heading(col, text=col)
            self.admin_tree.column(col, width=width, anchor='center')
        
        self.admin_tree.pack(pady=10, padx=10, fill='both', expand=True)
        
        ttk.Button(self.admin_frame, text="刷新列表", command=self.load_matches).pack(pady=10)
    
    def set_user(self):
        """设置当前用户"""
        username = self.user_entry.get().strip()
        if not username:
            messagebox.showerror("错误", "请输入姓名！")
            return
        
        self.current_user = username
        self.user_status.config(text=f"当前用户：{username}", foreground='green')
        messagebox.showinfo("成功", f"欢迎，{username}！")
        
        # 重新加载预测数据
        self.load_predictions()
    
    def load_matches(self):
        """加载比赛数据"""
        # 清空表格
        for item in self.predict_tree.get_children():
            self.predict_tree.delete(item)
        for item in self.admin_tree.get_children():
            self.admin_tree.delete(item)
        
        # 从数据库加载
        self.cursor.execute('SELECT * FROM matches ORDER BY id')
        matches = self.cursor.fetchall()
        
        for match in matches:
            id, stage, date, time, team_a, team_b, actual_a, actual_b = match
            
            # 检查是否锁定
            status = self.get_match_status(date, time)
            
            # 添加到预测表格
            self.predict_tree.insert('', 'end', values=(
                id, stage, date, time, team_a, team_b, '', '', status
            ))
            
            # 添加到管理员表格
            self.admin_tree.insert('', 'end', values=(
                id, stage, date, time, team_a, team_b, 
                actual_a if actual_a is not None else '',
                actual_b if actual_b is not None else ''
            ))
    
    def get_match_status(self, date_str, time_str):
        """获取比赛状态"""
        try:
            match_datetime = datetime.strptime(f"{date_str} {time_str}:00", "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            diff_minutes = (match_datetime - now).total_seconds() / 60
            
            if diff_minutes <= 5:
                return "已锁定"
            elif diff_minutes <= 0:
                return "已结束"
            else:
                return "可预测"
        except:
            return "未知"
    
    def load_predictions(self):
        """加载用户的预测"""
        if not self.current_user:
            return
        
        # 获取用户的预测
        self.cursor.execute('''
            SELECT match_id, pred_a, pred_b 
            FROM predictions 
            WHERE user_name = ?
        ''', (self.current_user,))
        
        predictions = {row[0]: (row[1], row[2]) for row in self.cursor.fetchall()}
        
        # 更新表格
        for item in self.predict_tree.get_children():
            values = list(self.predict_tree.item(item)['values'])
            match_id = values[0]
            
            if match_id in predictions:
                values[6] = predictions[match_id][0]
                values[7] = predictions[match_id][1]
                self.predict_tree.item(item, values=values)
    
    def save_prediction(self):
        """保存预测"""
        if not self.current_user:
            messagebox.showerror("错误", "请先输入姓名并确认！")
            return
        
        try:
            match_id = int(self.match_id_entry.get())
            pred_a = int(self.pred_a_entry.get())
            pred_b = int(self.pred_b_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数据！")
            return
        
        # 检查比赛是否存在和是否锁定
        self.cursor.execute('SELECT match_date, match_time FROM matches WHERE id = ?', (match_id,))
        result = self.cursor.fetchone()
        
        if not result:
            messagebox.showerror("错误", "比赛ID不存在！")
            return
        
        date_str, time_str = result
        status = self.get_match_status(date_str, time_str)
        
        if status == "已锁定":
            messagebox.showerror("错误", "比赛开始前5分钟不能修改预测！")
            return
        
        # 保存预测
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO predictions (user_name, match_id, pred_a, pred_b)
                VALUES (?, ?, ?, ?)
            ''', (self.current_user, match_id, pred_a, pred_b))
            self.conn.commit()
            
            messagebox.showinfo("成功", "预测已保存！")
            
            # 清空输入框
            self.match_id_entry.delete(0, 'end')
            self.pred_a_entry.delete(0, 'end')
            self.pred_b_entry.delete(0, 'end')
            
            # 重新加载
            self.load_predictions()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{e}")
    
    def on_tree_double_click(self, event):
        """双击表格行"""
        selection = self.predict_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.predict_tree.item(item)['values']
        
        # 填充输入框
        self.match_id_entry.delete(0, 'end')
        self.match_id_entry.insert(0, str(values[0]))
    
    def save_actual_result(self):
        """保存实际比赛结果"""
        try:
            match_id = int(self.admin_match_id.get())
            actual_a = int(self.actual_a_entry.get())
            actual_b = int(self.actual_b_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数据！")
            return
        
        # 更新数据库
        try:
            self.cursor.execute('''
                UPDATE matches 
                SET actual_a = ?, actual_b = ?
                WHERE id = ?
            ''', (actual_a, actual_b, match_id))
            self.conn.commit()
            
            messagebox.showinfo("成功", "实际结果已保存！系统将自动计算得分。")
            
            # 清空输入框
            self.admin_match_id.delete(0, 'end')
            self.actual_a_entry.delete(0, 'end')
            self.actual_b_entry.delete(0, 'end')
            
            # 重新加载
            self.load_matches()
            self.update_rankings()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{e}")
    
    def update_rankings(self):
        """更新排名"""
        # 获取所有用户
        self.cursor.execute('SELECT DISTINCT user_name FROM predictions')
        users = [row[0] for row in self.cursor.fetchall()]
        
        rankings = []
        
        for user in users:
            score = 0
            exact = 0
            correct = 0
            
            # 获取该用户的所有预测
            self.cursor.execute('''
                SELECT p.match_id, p.pred_a, p.pred_b, m.actual_a, m.actual_b
                FROM predictions p
                JOIN matches m ON p.match_id = m.id
                WHERE p.user_name = ? AND m.actual_a IS NOT NULL AND m.actual_b IS NOT NULL
            ''', (user,))
            
            for row in self.cursor.fetchall():
                _, pred_a, pred_b, actual_a, actual_b = row
                
                # 准确比分
                if pred_a == actual_a and pred_b == actual_b:
                    score += 4
                    exact += 1
                # 猜中胜负
                elif (pred_a - pred_b) * (actual_a - actual_b) > 0:
                    score += 1
                    correct += 1
                # 平局也猜中
                elif pred_a == pred_b and actual_a == actual_b:
                    score += 1
                    correct += 1
            
            rankings.append({
                'user': user,
                'score': score,
                'exact': exact,
                'correct': correct
            })
        
        # 排序
        rankings.sort(key=lambda x: x['score'], reverse=True)
        
        # 更新表格
        for item in self.ranking_tree.get_children():
            self.ranking_tree.delete(item)
        
        for idx, r in enumerate(rankings, 1):
            self.ranking_tree.insert('', 'end', values=(
                idx, r['user'], r['score'], r['exact'], r['correct']
            ))
        
        # 更新统计
        self.stat_users.config(text=f"参与人数：{len(users)}")
        
        self.cursor.execute('SELECT COUNT(*) FROM matches WHERE actual_a IS NOT NULL')
        finished = self.cursor.fetchone()[0]
        self.stat_matches.config(text=f"已完成：{finished}")
        
        if rankings:
            avg_score = sum(r['score'] for r in rankings) / len(rankings)
            self.stat_avg.config(text=f"平均得分：{avg_score:.1f}")
        else:
            self.stat_avg.config(text="平均得分：0")
    
    def __del__(self):
        """关闭数据库连接"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    root = tk.Tk()
    app = WorldCupPredictionApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
