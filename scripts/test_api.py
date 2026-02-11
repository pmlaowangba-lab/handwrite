#!/usr/bin/env python3
"""
自动测试 AI API 连接
"""

import requests
import json
import sys

# API 配置
API_ENDPOINT = "https://gmn.chuangzuoli.com/v1/chat/completions"
API_KEY = "sk-028e8422a037c8b88ce93eb86157bd71d010886aa56a393aea0d51c83ae699c1"
MODEL = "gpt-5.2-codex"

print("=" * 60)
print("🤖 AI API 自动测试")
print("=" * 60)
print(f"📍 Endpoint: {API_ENDPOINT}")
print(f"🔑 API Key: {API_KEY[:20]}...")
print(f"🤖 Model: {MODEL}")
print("=" * 60)

# 测试请求
payload = {
    "model": MODEL,
    "messages": [
        {
            "role": "user",
            "content": "测试连接，请回复 OK"
        }
    ],
    "max_tokens": 100
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

print("\n📤 发送测试请求...")
print(f"Request URL: {API_ENDPOINT}")
print(f"Request Body: {json.dumps(payload, indent=2, ensure_ascii=False)}")

try:
    response = requests.post(
        API_ENDPOINT,
        headers=headers,
        json=payload,
        timeout=30
    )

    print(f"\n📥 响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")

    if response.status_code == 200:
        result = response.json()
        print("\n✅ 连接成功！")
        print(f"完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

        # 提取回复内容
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0].get('message', {}).get('content', '')
            print(f"\n💬 AI 回复: {content}")

        sys.exit(0)
    else:
        print(f"\n❌ 连接失败！")
        print(f"错误响应: {response.text}")
        sys.exit(1)

except requests.exceptions.Timeout:
    print("\n❌ 请求超时！")
    sys.exit(1)
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ 连接错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ 未知错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
