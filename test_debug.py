#!/usr/bin/env python3
"""
调试和测试修复后的 API
"""
import json
import requests
import time
from openai import OpenAI

def test_with_curl():
    """使用 requests 测试流式响应"""
    print("🧪 Testing streaming with requests...")
    
    payload = {
        "model": "Qwen/Qwen3-8B-AWQ",
        "messages": [
            {"role": "user", "content": "Hello! Please respond briefly."}
        ],
        "max_tokens": 30,
        "temperature": 0.7,
        "stream": True
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            stream=True,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\nStreaming response:")
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    print(f"Raw line: {repr(line_str)}")
                    
                    if line_str.startswith('data: '):
                        data = line_str[6:]  # Remove 'data: ' prefix
                        if data.strip() == '[DONE]':
                            print("✅ Stream completed")
                            break
                        try:
                            chunk = json.loads(data)
                            print(f"Parsed chunk: {chunk}")
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    print(f"Content: {delta['content']}")
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}")
                            print(f"Data: {repr(data)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_non_streaming():
    """测试非流式响应"""
    print("\n💬 Testing non-streaming...")
    
    payload = {
        "model": "Qwen/Qwen3-8B-AWQ",
        "messages": [
            {"role": "user", "content": "What is 1+1?"}
        ],
        "max_tokens": 20,
        "temperature": 0.1,
        "stream": False
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_with_openai_client():
    """使用 OpenAI 客户端测试"""
    print("\n🔧 Testing with OpenAI client...")
    
    client = OpenAI(
        base_url="http://127.0.0.1:8000/v1",
        api_key="dummy"
    )
    
    try:
        # 非流式
        print("Non-streaming:")
        response = client.chat.completions.create(
            model="Qwen/Qwen3-8B-AWQ",
            messages=[{"role": "user", "content": "Say hello in one word"}],
            max_tokens=10,
            temperature=0.1
        )
        print(f"Response: {response.choices[0].message.content}")
        
        # 流式
        print("\nStreaming:")
        stream = client.chat.completions.create(
            model="Qwen/Qwen3-8B-AWQ",
            messages=[{"role": "user", "content": "Count to 3"}],
            max_tokens=20,
            temperature=0.1,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end='', flush=True)
        print("\n✅ OpenAI client test completed")
        
    except Exception as e:
        print(f"❌ OpenAI client error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🚀 Testing fixed API...\n")
    
    # 测试健康检查
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    test_non_streaming()
    test_with_curl()
    test_with_openai_client()
    
    print("\n✅ All debug tests completed!")

if __name__ == "__main__":
    main()
