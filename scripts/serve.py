#!/usr/bin/env python3
"""
Flask 后端服务器
功能：
1. 提供静态文件服务（HTML、CSS、JS、字体、图片）
2. 提供 /api/polish 接口，在后端调用 AI API
3. 从环境变量读取 API Key（安全）
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv()

# 获取项目根目录
BASE_DIR = Path(__file__).parent.parent

# 创建 Flask 应用
app = Flask(__name__,
            static_folder=str(BASE_DIR / 'templates'),
            static_url_path='')
CORS(app)

# 配置
PORT = 8000
AI_API_ENDPOINT = os.getenv('AI_API_ENDPOINT', 'https://api.openai.com/v1/chat/completions')
AI_API_KEY = os.getenv('AI_API_KEY', '')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
DEFAULT_FRONTEND_TEMPLATE = 'handwriting-new.html'

# ==================== 路由 ====================

@app.route('/')
def index():
    """首页"""
    return send_from_directory(app.static_folder, DEFAULT_FRONTEND_TEMPLATE)

@app.route('/handwriting.html')
def handwriting():
    """兼容旧路径：重定向到最新前端模板"""
    return send_from_directory(app.static_folder, DEFAULT_FRONTEND_TEMPLATE)

@app.route('/handwriting-new.html')
def handwriting_new():
    """最新手写体生成器页面"""
    return send_from_directory(app.static_folder, DEFAULT_FRONTEND_TEMPLATE)

@app.route('/assets/<path:path>')
def serve_assets(path):
    """提供静态资源（字体、图片等）"""
    assets_dir = BASE_DIR / 'assets'
    return send_from_directory(assets_dir, path)

@app.route('/api/polish', methods=['POST'])
def polish_text():
    """
    AI 文案润色接口
    请求体：
    {
        "text": "原始文本"
    }
    响应：
    {
        "success": true,
        "polished_text": "润色后的文本"
    }
    """
    try:
        # 检查 API Key
        if not AI_API_KEY:
            return jsonify({
                'success': False,
                'error': '服务器未配置 AI API Key，请联系管理员'
            }), 500

        # 获取请求数据
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': '请求参数错误：缺少 text 字段'
            }), 400

        original_text = data['text'].strip()
        if not original_text:
            return jsonify({
                'success': False,
                'error': '文本内容不能为空'
            }), 400

        # 构建 AI 提示词
        system_prompt = """你是一个专业的文案润色助手。你的任务是将用户提供的简短文案扩展为 500 字以上的专业内容。

要求：
1. 🚫 严禁使用任何 Emoji 表情
2. 使用简洁、高密度的专业语言
3. 深度扩展内容（每个概念至少 2-3 个支撑点）
4. 多层级展开（标题→要点→详细说明）
5. 内容量至少 500 字，确保充实
6. 层级清晰，适合手写展示
7. 不要有过多空白内容
8. 保持专业、学术的风格"""

        user_prompt = f"请将以下文案扩展为 500 字以上的专业内容：\n\n{original_text}"

        # 调用 AI API
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {AI_API_KEY}'
        }

        payload = {
            'model': AI_MODEL,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'max_tokens': 4096,
            'temperature': 0.7
        }

        response = requests.post(AI_API_ENDPOINT, headers=headers, json=payload, timeout=60)

        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'AI API 调用失败：{response.status_code} {response.text}'
            }), 500

        result = response.json()
        polished_text = result['choices'][0]['message']['content'].strip()

        return jsonify({
            'success': True,
            'polished_text': polished_text
        })

    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'AI API 请求超时，请稍后重试'
        }), 504

    except Exception as e:
        print(f"Error in polish_text: {e}", file=sys.stderr)
        return jsonify({
            'success': False,
            'error': f'服务器内部错误：{str(e)}'
        }), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    """测试 API 连接"""
    if not AI_API_KEY:
        return jsonify({
            'success': False,
            'message': '服务器未配置 AI API Key'
        }), 500

    return jsonify({
        'success': True,
        'message': 'API 配置正常',
        'endpoint': AI_API_ENDPOINT,
        'model': AI_MODEL
    })

# ==================== 启动服务器 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("✍️  手写体生成器服务器 (Flask)")
    print("=" * 60)
    print(f"🌐 服务器地址: http://localhost:{PORT}")
    print(f"📂 项目目录: {BASE_DIR}")
    print(f"💡 在浏览器中打开: http://localhost:{PORT}/handwriting-new.html")
    print(f"🔑 AI API 配置: {'已配置' if AI_API_KEY else '未配置（需要配置 .env 文件）'}")
    print(f"⏹️  按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()

    app.run(host='0.0.0.0', port=PORT, debug=True)
