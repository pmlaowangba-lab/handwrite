#!/usr/bin/env python3
"""
真实纸张照片预处理脚本
功能：
1. 调整亮度（让纸张更白）
2. 增强对比度（让线条更清晰）
3. 统一尺寸（A4 比例：210x297mm，600dpi = 4961x7016px）
4. 优化文件大小
"""

import os
from PIL import Image, ImageEnhance
from pathlib import Path

# 配置
INPUT_DIR = Path(__file__).parent.parent / 'assets' / 'papers' / 'real'
OUTPUT_DIR = Path(__file__).parent.parent / 'assets' / 'papers' / 'processed'
TARGET_WIDTH = 2480  # A4 宽度 @ 300dpi (适合网页显示)
TARGET_HEIGHT = 3508  # A4 高度 @ 300dpi
BRIGHTNESS_FACTOR = 1.15  # 亮度增强系数（1.0 = 原始）
CONTRAST_FACTOR = 1.1  # 对比度增强系数（1.0 = 原始）
QUALITY = 90  # JPEG 质量（1-100）

def process_image(input_path, output_path):
    """处理单张图片"""
    print(f"处理: {input_path.name}")

    # 打开图片
    img = Image.open(input_path)

    # 转换为 RGB（如果是 RGBA）
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # 1. 调整亮度
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(BRIGHTNESS_FACTOR)

    # 2. 增强对比度
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(CONTRAST_FACTOR)

    # 3. 调整尺寸（保持宽高比）
    img.thumbnail((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

    # 4. 保存为 JPEG（优化文件大小）
    output_path_jpg = output_path.with_suffix('.jpg')
    img.save(output_path_jpg, 'JPEG', quality=QUALITY, optimize=True)

    # 输出文件信息
    input_size = input_path.stat().st_size / 1024 / 1024  # MB
    output_size = output_path_jpg.stat().st_size / 1024 / 1024  # MB
    print(f"  原始: {img.size} ({input_size:.2f} MB)")
    print(f"  输出: {img.size} ({output_size:.2f} MB)")
    print(f"  压缩率: {(1 - output_size/input_size)*100:.1f}%\n")

def main():
    """批量处理所有图片"""
    print("=" * 60)
    print("📸 真实纸张照片预处理")
    print("=" * 60)
    print(f"输入目录: {INPUT_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"目标尺寸: {TARGET_WIDTH}x{TARGET_HEIGHT}px (A4 @ 300dpi)")
    print(f"亮度增强: {BRIGHTNESS_FACTOR}x")
    print(f"对比度增强: {CONTRAST_FACTOR}x")
    print("=" * 60)
    print()

    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 处理所有 PNG 图片
    image_files = list(INPUT_DIR.glob('*.png'))

    if not image_files:
        print("❌ 未找到任何 PNG 图片")
        return

    print(f"找到 {len(image_files)} 张图片\n")

    for input_path in sorted(image_files):
        output_path = OUTPUT_DIR / input_path.name
        try:
            process_image(input_path, output_path)
        except Exception as e:
            print(f"❌ 处理失败: {input_path.name}")
            print(f"   错误: {e}\n")

    print("=" * 60)
    print("✅ 处理完成！")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == '__main__':
    main()
