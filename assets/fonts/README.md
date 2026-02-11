# 字体文件使用说明

## 📁 字体文件放置

将你的手写字体文件放在这个目录下：
```
skills/text-to-handwriting/assets/fonts/
├── qingsong-1.ttf
├── qingsong-2.ttf
├── mucao-soft.ttf
├── mucao-casual.ttf
└── ...
```

## 🔄 字体格式转换（推荐）

为了更好的网页性能，建议将 `.ttf` 转换为 `.woff2` 格式：

### 方法 1：在线转换工具
- https://cloudconvert.com/ttf-to-woff2
- https://www.fontsquirrel.com/tools/webfont-generator

### 方法 2：使用命令行工具
```bash
# 安装 fonttools
pip install fonttools brotli

# 转换字体
pyftsubset your-font.ttf \
  --output-file=your-font.woff2 \
  --flavor=woff2 \
  --layout-features='*' \
  --unicodes="U+0020-007E,U+4E00-9FFF"
```

## 📝 添加字体到网页

转换完成后，编辑 `templates/handwriting.html`，在 `<style>` 标签中添加：

```css
@font-face {
    font-family: '清松手写体1';
    src: url('../assets/fonts/qingsong-1.woff2') format('woff2'),
         url('../assets/fonts/qingsong-1.ttf') format('truetype');
    font-weight: normal;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: '沐瑶软笔手写体';
    src: url('../assets/fonts/mucao-soft.woff2') format('woff2'),
         url('../assets/fonts/mucao-soft.ttf') format('truetype');
    font-weight: normal;
    font-style: normal;
    font-display: swap;
}
```

然后在字体选择下拉框中添加选项：

```html
<select id="font-select">
    <option value="清松手写体1">清松手写体1</option>
    <option value="沐瑶软笔手写体">沐瑶软笔手写体</option>
    <!-- 其他字体 -->
</select>
```

## 🚀 部署到服务器

### 方案 A：直接部署（推荐用于小流量）
将整个项目文件夹上传到服务器，包括字体文件。

### 方案 B：使用 CDN（推荐用于大流量）
1. 将字体文件上传到 CDN（阿里云 OSS、七牛云等）
2. 修改 `@font-face` 中的 `src` 路径为 CDN 地址

```css
@font-face {
    font-family: '清松手写体1';
    src: url('https://your-cdn.com/fonts/qingsong-1.woff2') format('woff2');
}
```

## 📊 字体文件大小优化

| 格式 | 大小 | 兼容性 | 推荐 |
|------|------|--------|------|
| .ttf | 3-5MB | 所有浏览器 | ⭐⭐⭐ |
| .woff | 2-3MB | 现代浏览器 | ⭐⭐⭐⭐ |
| .woff2 | 1-2MB | 最新浏览器 | ⭐⭐⭐⭐⭐ |

**建议**：同时提供 `.woff2` 和 `.ttf`，浏览器会自动选择最优格式。

## ⚠️ 注意事项

1. **字体版权**：确保你有权使用这些字体（开源或已购买授权）
2. **文件大小**：中文字体通常较大（2-5MB），会影响首次加载速度
3. **字体子集化**：如果只用常用汉字，可以生成子集字体（减小 50-70% 大小）
4. **跨域问题**：如果字体和网页不在同一域名，需要配置 CORS

## 🔧 快速开始

1. 将你的字体文件（.ttf）复制到这个目录
2. 运行字体转换脚本（可选，提升性能）
3. 编辑 `handwriting.html` 添加 `@font-face` 声明
4. 在字体选择下拉框中添加选项
5. 测试效果

---

**需要帮助？** 把你的字体文件放到这个目录，我可以帮你生成完整的 `@font-face` 代码。
