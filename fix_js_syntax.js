const fs = require('fs');
let html = fs.readFileSync('templates/index.html', 'utf8');

// 提取JavaScript代码
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) {
    console.log('❌ 未找到JavaScript代码');
    process.exit(1);
}

let js = scriptMatch[1];

// 修复1: 对象字面量缺少逗号
js = js.replace(/(\d+)\s+(')/g, '$1, $2');
js = js.replace(/(\})\s+(')/g, '$1, $2');

// 修复2: padStart缺少逗号
js = js.replace(/padStart\((\d+)\s+'(.)'\)/g, 'padStart($1, \'$2\')');

// 修复3: classList拼写（确保是正确的）
js = js.replace(/class\s+[Ll]ist/g, 'classList');
js = js.replace(/class[Ll]ist/g, 'classList');

// 修复4: 确保switchTab函数定义正确
if (js.includes('function switchTab(name, event)') && js.includes('event.target')) {
    console.log('✅ switchTab函数定义正确');
}

// 写回文件
html = html.replace(/<script>([\s\S]*?)<\/script>/, `<script>${js}</script>`);
fs.writeFileSync('templates/index.html', html, 'utf8');

console.log('✅ JavaScript语法修复完成');

// 验证语法
try {
    new Function(js);
    console.log('✅ JavaScript语法验证通过');
} catch (e) {
    console.log('❌ 仍有语法错误:', e.message);
}
