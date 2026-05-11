# 2026世界杯预测应用 - 部署教程

## 方法1：通过GitHub部署（推荐）

### 步骤1：创建GitHub仓库
1. 访问 https://github.com 并登录（没有账号需要先注册）
2. 点击右上角 "+" → "New repository"
3. 仓库名填写：`world-cup-2026-prediction`
4. 选择 "Public"
5. 点击 "Create repository"

### 步骤2：上传代码到GitHub
在本地电脑的终端（或Git Bash）执行：

```bash
# 克隆仓库（把 YOUR_USERNAME 换成你的GitHub用户名）
git clone https://github.com/YOUR_USERNAME/world-cup-2026-prediction.git
cd world-cup-2026-prediction

# 复制所有文件到这个目录
# （把 /workspace/* 的所有文件复制到这里）

# 提交并推送
git add .
git commit -m "初始提交：2026世界杯预测应用"
git push origin main
```

### 步骤3：部署到Render.com
1. 访问 https://render.com 并注册/登录
2. 点击 "New +" → "Web Service"
3. 连接你的GitHub账号
4. 选择 `world-cup-2026-prediction` 仓库
5. 配置：
   - **Name**: world-cup-2026（随便填）
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 1 app:app`
6. 点击 "Create Web Service"
7. 等待5-10分钟部署完成
8. 你会得到一个永久链接，例如：`https://world-cup-2026.onrender.com`

---

## 方法2：直接上传ZIP到Render.com（不需要GitHub）

### 步骤1：下载代码包
从AI助手这里下载以下文件（打包成ZIP）：
- app.py
- requirements.txt
- render.yaml
- templates/index.html
- world_cup_2026.db

### 步骤2：部署到Render
1. 访问 https://render.com
2. 注册/登录
3. 点击 "New +" → "Web Service"
4. 选择 "Upload Files"
5. 上传ZIP包
6. 配置同上
7. 部署

---

## 重要提示

### 数据库问题
**当前应用使用SQLite数据库（world_cup_2026.db）**，但Render.com的免费tier是**临时文件系统**，每次部署都会重置数据库！

### 解决方案
需要修改为使用PostgreSQL数据库（Render.com提供免费PostgreSQL）。

如果你需要，我可以修改代码以支持PostgreSQL。

---

## 需要帮助？

告诉我你卡在哪一步，我会详细指导你！
