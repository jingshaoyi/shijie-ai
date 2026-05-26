// Node.js script to generate simple PNG icons for tabbar
// Run: node generate-icons.js

const fs = require('fs');
const path = require('path');

// Simple 81x81 PNG with solid color (81x81 is standard tabbar icon size)
function createSimplePNG(color) {
  // This creates a minimal valid PNG with a simple colored square
  // PNG header + IHDR + IDAT + IEND
  const width = 81;
  const height = 81;
  
  // Create raw RGBA data (simple colored square)
  const rawData = [];
  for (let y = 0; y < height; y++) {
    rawData.push(0); // filter byte
    for (let x = 0; x < width; x++) {
      // Create a rounded rectangle effect with simple color fill
      const centerX = width / 2;
      const centerY = height / 2;
      const radius = 30;
      const dx = x - centerX;
      const dy = y - centerY;
      
      if (dx * dx + dy * dy < radius * radius) {
        // Inside circle - use color
        rawData.push(color.r, color.g, color.b, 255);
      } else {
        // Outside - transparent
        rawData.push(0, 0, 0, 0);
      }
    }
  }
  
  // Use zlib to compress (if available) or return uncompressed
  let compressed;
  try {
    const zlib = require('zlib');
    const rawBuffer = Buffer.from(rawData);
    compressed = zlib.deflateSync(rawBuffer);
  } catch (e) {
    // Fallback - create uncompressed
    compressed = Buffer.from(rawData);
  }
  
  // Build PNG file
  const chunks = [];
  
  // PNG signature
  chunks.push(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
  
  // IHDR chunk
  const ihdrData = Buffer.alloc(13);
  ihdrData.writeUInt32BE(width, 0);
  ihdrData.writeUInt32BE(height, 4);
  ihdrData.writeUInt8(8, 8); // bit depth
  ihdrData.writeUInt8(6, 9); // color type (RGBA)
  ihdrData.writeUInt8(0, 10); // compression
  ihdrData.writeUInt8(0, 11); // filter
  ihdrData.writeUInt8(0, 12); // interlace
  chunks.push(createChunk('IHDR', ihdrData));
  
  // IDAT chunk
  chunks.push(createChunk('IDAT', compressed));
  
  // IEND chunk
  chunks.push(createChunk('IEND', Buffer.alloc(0)));
  
  return Buffer.concat(chunks);
}

function createChunk(type, data) {
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length, 0);
  
  const typeBuffer = Buffer.from(type);
  const crcData = Buffer.concat([typeBuffer, data]);
  const crc = crc32(crcData);
  
  const crcBuffer = Buffer.alloc(4);
  crcBuffer.writeUInt32BE(crc >>> 0, 0);
  
  return Buffer.concat([length, typeBuffer, data, crcBuffer]);
}

function crc32(data) {
  let crc = 0xFFFFFFFF;
  const table = [];
  
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
    }
    table[n] = c;
  }
  
  for (let i = 0; i < data.length; i++) {
    crc = table[(crc ^ data[i]) & 0xFF] ^ (crc >>> 8);
  }
  
  return crc ^ 0xFFFFFFFF;
}

// Color definitions (gray for inactive, blue for active)
const inactiveColor = { r: 153, g: 153, b: 153 }; // #999999
const activeColor = { r: 41, g: 121, b: 255 }; // #2979FF

const icons = [
  { name: 'home.png', color: inactiveColor },
  { name: 'home-active.png', color: activeColor },
  { name: 'chat.png', color: inactiveColor },
  { name: 'chat-active.png', color: activeColor },
  { name: 'history.png', color: inactiveColor },
  { name: 'history-active.png', color: activeColor },
  { name: 'user.png', color: inactiveColor },
  { name: 'user-active.png', color: activeColor },
];

const outputDir = path.join(__dirname, 'static', 'tabbar');

// Create icons
icons.forEach(icon => {
  const png = createSimplePNG(icon.color);
  const outputPath = path.join(outputDir, icon.name);
  fs.writeFileSync(outputPath, png);
  console.log(`Created: ${icon.name}`);
});

console.log('All icons created successfully!');
