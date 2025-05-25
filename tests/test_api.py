#!/usr/bin/env python3
"""
简单的 API 测试脚本
"""
import requests
import json
import time

def test_health():
    """测试健康检查端点"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat_completion():
    """测试聊天完成端点"""
    print("\n💬 Testing chat completion endpoint...")
    
    payload = {
        "model": "Qwen/Qwen3-8B-AWQ",
        "messages": [
            {"role": "user", "content": "Hello! Can you tell me a short joke?"}
        ],
        "max_tokens": 150,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        print("Sending request...")
        response = requests.post(
            "http://127.0.0.1:8000/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Model: {result.get('model', 'N/A')}")
            print(f"Usage: {result.get('usage', {})}")
            
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']
                print(f"Response: {message['content']}")
                return True
            else:
                print("❌ No choices in response")
                return False
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat completion failed: {e}")
        return False

def test_streaming():
    """测试流式响应"""
    print("\n🌊 Testing streaming endpoint...")
    
    payload = {
        "model": "Qwen/Qwen3-8B-AWQ",
        "messages": [
            {"role": "user", "content": "Count from 1 to 5"}
        ],
        "max_tokens": 50,
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
        
        if response.status_code == 200:
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data = line_str[6:]  # Remove 'data: ' prefix
                        if data.strip() == '[DONE]':
                            print("\n✅ Stream completed")
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    print(delta['content'], end='', flush=True)
                        except json.JSONDecodeError:
                            continue
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Streaming failed: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Starting API tests...\n")
    
    # 测试健康检查
    if not test_health():
        print("❌ Health check failed, exiting...")
        return
    
    # 等待一下确保模型完全加载
    print("\n⏳ Waiting for model to be ready...")
    time.sleep(2)
    
    # 测试聊天完成
    test_chat_completion()
    
    # 测试流式响应
    test_streaming()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
