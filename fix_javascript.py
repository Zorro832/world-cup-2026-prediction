import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复1: classList -> classList (JavaScript区分大小写)
content = content.replace('classList', 'classList')

# 修复2: padStart缺少逗号
content = content.replace("padStart(2, '0')", "padStart(2, '0')")
content = content.replace("padStart(2, '0')", "padStart(2, '0')")
content = content.replace("padStart(2, '0')", "padStart(2, '0')")

# 修复3: 对象字面量缺少逗号
content = content.replace("'32强': 32, '16强': 16, '8强': 8, '4强'", "'32强': 32, '16强': 16, '8强': 8, '4强':")
content = content.replace("'32强': 32, '16强': 16, '8强': 8, '4强'", "'32强': 32, '16强': 16, '8强': 8, '4强':")

# 修复4: switchTab函数中的evt参数拼写错误
content = content.replace('function switchTab(name, evt)', 'function switchTab(name, event)')
content = content.replace('if (evt)', 'if (event)')
content = content.replace('evt.target', 'event.target')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ JavaScript语法错误已修复")
