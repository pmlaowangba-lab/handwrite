# 纸张背景图片资源

## 📁 图片放置

将纸张背景图片放在这个目录下：
```
skills/text-to-handwriting/assets/papers/
├── red-grid-real.jpg       # 红格子稿纸（实拍）
├── red-grid-print.jpg      # 红格子稿纸（打印版）
├── black-grid-real.jpg     # 黑格子稿纸（实拍）
├── single-line-real.jpg    # 单红线信稿纸（实拍）
├── draft-paper.jpg         # 草稿纸（实拍）
├── a4-portrait.jpg         # A4 纸（纵向）
├── a4-landscape.jpg        # A4 纸（横向）
└── ...
```

## 🌐 免费纸张图片资源

### 推荐网站

1. **Unsplash** (https://unsplash.com/)
   - 搜索关键词：`paper texture`, `notebook paper`, `lined paper`, `grid paper`
   - 完全免费，可商用
   - 高质量图片

2. **Pexels** (https://www.pexels.com/)
   - 搜索关键词：`paper background`, `notebook`, `writing paper`
   - 免费商用
   - 多种纸张纹理

3. **Pixabay** (https://pixabay.com/)
   - 搜索关键词：`paper`, `notebook`, `lined paper`
   - 免费商用
   - 大量纸张纹理

4. **Freepik** (https://www.freepik.com/)
   - 搜索关键词：`paper texture`, `notebook paper`
   - 部分免费（需注明出处）
   - 矢量图和位图都有

### 搜索关键词（中英文）

| 纸张类型 | 英文关键词 | 中文关键词 |
|---------|-----------|-----------|
| 红格子稿纸 | red grid paper, chinese writing paper | 红格子纸、作文纸 |
| 黑格子稿纸 | black grid paper, graph paper | 黑格子纸、方格纸 |
| 单红线信稿纸 | lined paper, ruled paper | 横线纸、信纸 |
| 草稿纸 | draft paper, scratch paper | 草稿纸、演算纸 |
| A4 白纸 | white paper texture, blank paper | 白纸、A4 纸 |

## 📐 图片规格要求

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| **分辨率** | 2000x3000px 以上 | 确保清晰度 |
| **DPI** | 300 dpi | 适合打印 |
| **格式** | JPG 或 PNG | JPG 文件更小 |
| **文件大小** | 500KB - 2MB | 平衡质量和加载速度 |
| **比例** | 2:3 (A4 比例) | 适配 Canvas 尺寸 |

## 🎨 自己拍摄纸张

如果你想要最真实的效果，可以自己拍摄：

### 拍摄设备
- 手机相机（1200万像素以上）
- 单反相机（更佳）

### 拍摄技巧
1. **光线**：自然光或柔和的室内光，避免强烈阴影
2. **角度**：正上方垂直拍摄，避免透视变形
3. **背景**：纯色背景，避免杂物
4. **对焦**：对准纸张中心，确保清晰
5. **后期**：调整亮度、对比度，裁剪为 A4 比例

### 推荐拍摄的纸张
- 红格子作文纸（文具店购买）
- 黑格子方格纸
- 单红线信纸
- 草稿纸（用过的，有真实感）
- 米黄色复古纸

## 🔧 图片优化

拍摄或下载后，建议进行优化：

### 在线工具
- **TinyPNG** (https://tinypng.com/) - 压缩图片，减小文件大小
- **Squoosh** (https://squoosh.app/) - Google 出品的图片压缩工具

### 命令行工具
```bash
# 使用 ImageMagick 调整大小和压缩
convert input.jpg -resize 2000x3000 -quality 85 output.jpg
```

## 📝 添加纸张到网页

图片准备好后，编辑 `templates/handwriting.html`：

### 1. 更新纸张配置
```javascript
const paperImages = {
    'red-grid-real': '../assets/papers/red-grid-real.jpg',
    'red-grid-print': '../assets/papers/red-grid-print.jpg',
    'black-grid': '../assets/papers/black-grid-real.jpg',
    'single-line': '../assets/papers/single-line-real.jpg',
    'draft': '../assets/papers/draft-paper.jpg',
    'a4-portrait': '../assets/papers/a4-portrait.jpg'
};
```

### 2. 更新下拉框选项
```html
<select id="paper-select">
    <option value="white">白纸</option>
    <option value="red-grid-real">红格子稿纸（实拍）</option>
    <option value="red-grid-print">红格子稿纸（打印版）</option>
    <option value="black-grid">黑格子稿纸</option>
    <option value="single-line">单红线信稿纸</option>
    <option value="draft">草稿纸</option>
    <option value="a4-portrait">A4 纸（纵向）</option>
</select>
```

### 3. 修改渲染逻辑
```javascript
// 如果选择了图片背景
if (paperImages[paperType]) {
    const img = new Image();
    img.src = paperImages[paperType];
    img.onload = function() {
        ctx.drawImage(img, 0, 0, displayWidth, displayHeight);
        // 继续渲染文字...
    };
} else {
    // 使用纯色背景
    ctx.fillStyle = paperColors[paperType];
    ctx.fillRect(0, 0, displayWidth, displayHeight);
}
```

## 🚀 快速开始

1. 从推荐网站下载纸张图片
2. 放到这个目录
3. 按照上面的说明修改 HTML 文件
4. 测试效果

---

**需要帮助？** 把图片放到这个目录，我可以帮你生成完整的代码。

## 📦 我已经为你找到的免费资源

### 推荐下载（直接可用）

1. **红格子稿纸**
   - Unsplash: https://unsplash.com/s/photos/chinese-writing-paper
   - 搜索 "grid paper red"

2. **横线本**
   - Unsplash: https://unsplash.com/s/photos/lined-paper
   - 搜索 "ruled paper"

3. **方格纸**
   - Unsplash: https://unsplash.com/s/photos/graph-paper
   - 搜索 "grid paper"

4. **草稿纸**
   - Unsplash: https://unsplash.com/s/photos/notebook-paper
   - 搜索 "draft paper texture"

5. **A4 白纸**
   - Unsplash: https://unsplash.com/s/photos/white-paper-texture
   - 搜索 "paper texture white"

**或者，我可以用 CSS 先绘制这些纸张样式，效果也不错，不需要图片！**
