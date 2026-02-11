#!/usr/bin/env python3
"""
手写体生成器 — 本地服务器 + AI 代理
Text to Handwriting Generator with AI Proxy

用法：
    python generate.py                    # 启动本地服务器（默认端口 8765）
    python generate.py --port 9000        # 指定端口
    python generate.py "你的文本内容"      # 启动并预填文本
    python generate.py --file text.txt    # 启动并从文件读取文本

启动后会自动打开浏览器访问 http://localhost:8765
"""

import os
import sys
import json
import subprocess
import threading
import webbrowser
import urllib.parse
import urllib.request
import ssl
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial

DEFAULT_FRONTEND_TEMPLATE = 'handwriting-new.html'


# ==================== API 代理逻辑 ====================

def get_api_type(endpoint):
    """判断 API 类型"""
    if 'anthropic.com' in endpoint or '/v1/messages' in endpoint:
        return 'claude'
    return 'openai'


def build_api_url(base_endpoint):
    """智能补全 API URL"""
    url = base_endpoint.strip().rstrip('/')

    # 已经包含完整路径
    if '/v1/chat/completions' in url or '/v1/messages' in url:
        return url

    # 以 /openai 结尾
    if url.endswith('/openai'):
        return url + '/v1/chat/completions'

    # 只是域名
    import re
    if re.match(r'^https?://[^/]+$', url):
        return url + '/v1/chat/completions'

    # 默认补全 OpenAI 格式
    return url + '/v1/chat/completions'


def proxy_chat_request(request_data):
    """代理 AI 聊天请求"""
    endpoint = request_data.get('endpoint', '')
    api_key = request_data.get('apiKey', '')
    model = request_data.get('model', '')
    messages = request_data.get('messages', [])
    max_tokens = request_data.get('maxTokens', 4096)

    if not endpoint or not api_key:
        return {'error': '请配置 API Endpoint 和 API Key'}, 400

    # 构建目标 URL
    api_url = build_api_url(endpoint)
    api_type = get_api_type(api_url)

    # 构建请求头
    if api_type == 'claude':
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
    else:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

    # 构建请求体
    body = {
        'model': model,
        'max_tokens': max_tokens,
        'messages': messages
    }

    body_bytes = json.dumps(body).encode('utf-8')

    # 创建请求
    req = urllib.request.Request(
        api_url,
        data=body_bytes,
        headers=headers,
        method='POST'
    )

    # 发送请求（忽略 SSL 证书验证以兼容各种中转服务）
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result, 200
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace')
        try:
            error_json = json.loads(error_body)
            return {'error': f'API 返回错误 ({e.code})', 'detail': error_json}, e.code
        except json.JSONDecodeError:
            return {'error': f'API 返回错误 ({e.code})', 'detail': error_body[:500]}, e.code
    except urllib.error.URLError as e:
        return {'error': f'无法连接到 API: {str(e.reason)}'}, 502
    except Exception as e:
        return {'error': f'请求失败: {str(e)}'}, 500


# ==================== HTTP 服务器 ====================

class HandwritingHandler(SimpleHTTPRequestHandler):
    """自定义 HTTP 请求处理器"""

    def __init__(self, *args, root_dir=None, **kwargs):
        self.root_dir = root_dir
        super().__init__(*args, directory=root_dir, **kwargs)

    def do_POST(self):
        """处理 POST 请求（API 代理）"""
        if self.path == '/api/chat':
            self.handle_chat_proxy()
        else:
            self.send_error(404, 'Not Found')

    def handle_chat_proxy(self):
        """处理 AI 聊天代理请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode('utf-8'))

            # 调用代理
            result, status_code = proxy_chat_request(request_data)

            # 返回响应
            response_body = json.dumps(result, ensure_ascii=False).encode('utf-8')
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(response_body)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_body)

        except json.JSONDecodeError:
            self.send_json_error(400, '请求体 JSON 解析失败')
        except Exception as e:
            self.send_json_error(500, f'服务器内部错误: {str(e)}')

    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_json_error(self, code, message):
        """发送 JSON 格式的错误响应"""
        body = json.dumps({'error': message}, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        """处理 GET 请求"""
        # 忽略 favicon 请求
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, format, *args):
        """自定义日志格式"""
        try:
            msg = str(args[0]) if args else ''
            if '/api/' in msg:
                print(f"  🤖 API: {msg}")
            elif '200' not in msg and '304' not in msg and '204' not in msg:
                print(f"  📄 {msg}")
        except Exception:
            pass

    def translate_path(self, path):
        """重写路径映射，支持 /templates/ 和 /assets/ 路由"""
        # URL 解码并去掉查询参数
        path = urllib.parse.unquote(path.split('?')[0].split('#')[0])

        # 默认根路径指向 templates/handwriting-new.html
        if path == '/' or path == '':
            return os.path.join(self.root_dir, 'templates', DEFAULT_FRONTEND_TEMPLATE)

        # 直接拼接到项目根目录（处理 /assets/、/templates/ 等所有路径）
        clean = path.lstrip('/')
        full_path = os.path.join(self.root_dir, clean)
        return full_path


def start_server(root_dir, port=8765, text=None):
    """启动本地服务器"""
    handler = partial(HandwritingHandler, root_dir=root_dir)
    server = HTTPServer(('127.0.0.1', port), handler)

    url = f'http://localhost:{port}'
    if text:
        url += f'#text={urllib.parse.quote(text)}'

    print(f"\n✍️  手写体生成器 v3.1 — 本地服务模式")
    print(f"{'=' * 50}")
    print(f"🌐 服务地址: http://localhost:{port}")
    print(f"🤖 AI 代理:  http://localhost:{port}/api/chat")
    print(f"{'=' * 50}")
    print(f"💡 提示：在网页中配置 AI API 即可使用润色功能")
    print(f"🛑 按 Ctrl+C 停止服务器\n")

    # 延迟打开浏览器
    def open_browser():
        import time
        time.sleep(0.8)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 服务器已停止")
        server.server_close()


def main():
    """主函数"""
    # 项目根目录（scripts/ 的上级）
    root_dir = str(Path(__file__).parent.parent)
    port = 8765
    text = None

    # 解析参数
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--port' and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        elif args[i] == '--file' and i + 1 < len(args):
            file_path = Path(args[i + 1])
            if not file_path.exists():
                print(f"❌ 错误：文件不存在 {file_path}")
                sys.exit(1)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"📖 已从文件读取文本: {file_path}")
            i += 2
        elif args[i] in ['-h', '--help']:
            print(__doc__)
            sys.exit(0)
        else:
            text = args[i]
            print(f"📝 使用自定义文本: {text[:50]}...")
            i += 1

    start_server(root_dir, port, text)


if __name__ == "__main__":
    main()
