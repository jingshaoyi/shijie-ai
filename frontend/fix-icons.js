const fs = require('fs');
const path = require('path');

// 文件替换映射
const replacements = {
  '&#xe604;': '←',  // 返回
  '&#xe605;': '↑',  // 发送
  '&#xe106;': '📝',  // 历史
  '&#xe107;': '💬',  // 对话历史
  '&#xe108;': '>',   // 箭头
  '&#xe109;': '🗑️', // 清空
  '&#xe110;': '📧', // 反馈
  '&#xe111;': 'ℹ️', // 关于
  '&#xe112;': '📜', // 协议
};

const baseDir = path.join(__dirname, 'pages');

function replaceInFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;
  
  // 替换 HTML 实体为对应字符
  for (const [entity, char] of Object.entries(replacements)) {
    if (content.includes(entity)) {
      content = content.split(entity).join(char);
      modified = true;
    }
  }
  
  // 替换 class 名称
  if (content.includes('iconfont')) {
    content = content.replace(/iconfont/g, 'icon-text');
    modified = true;
  }
  
  if (modified) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log('Updated:', filePath);
  }
}

function walkDir(dir) {
  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      walkDir(filePath);
    } else if (file.endsWith('.vue')) {
      replaceInFile(filePath);
    }
  });
}

walkDir(baseDir);
console.log('All iconfont references replaced!');
