const fs = require('fs');
const path = require('path');

const target = path.join(__dirname, 'node_modules', '@angular', 'cli', 'src', 'utilities', 'node-version.js');
if (fs.existsSync(target)) {
  const content = fs.readFileSync(target, 'utf8');
  if (content.includes('24.15.0')) {
    fs.writeFileSync(target, content.replace('24.15.0', '24.10.0'));
    console.log('Patched Angular CLI node-version check for Node v24.10.0');
  }
}

