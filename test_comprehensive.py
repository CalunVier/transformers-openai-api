#!/usr/bin/env python3
"""
全面的 API 性能和功能测试
"""
import asyncio
import time
import json
from concurrent.futures import ThreadPoolExecutor
import requests
from openai import OpenAI

# API 配置
BASE_URL = "http://127.0.0.1:8000"
MODEL_NAME = "Qwen/Qwen3-8B-AWQ"

def test_basic_functionality():
    """测试基本功能"""
    print("🔧 Testing basic functionality...")
    
    # 健康检查
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    health_data = response.json()
    print(f"✅ Health check: {health_data}")
    
    # 模型列表
    response = requests.get(f"{BASE_URL}/v1/models")
    assert response.status_code == 200
    models_data = response.json()
    print(f"✅ Models: {len(models_data['data'])} models available")

def test_chat_completion():
    """测试聊天完成"""
    print("\n💬 Testing chat completion...")
    
    client = OpenAI(base_url=f"{BASE_URL}/v1", api_key="dummy")
    
    # 简单对话
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "What is 2+2?"}],
        max_tokens=50,
        temperature=0.1
    )
    
    print(f"✅ Math question: {response.choices[0].message.content.strip()}")
    
    # 多轮对话
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": "My name is Alice"},
            {"role": "assistant", "content": "Nice to meet you, Alice!"},
            {"role": "user", "content": "What's my name?"}
        ],
        max_tokens=30,
        temperature=0.1
    )
    
    print(f"✅ Multi-turn: {response.choices[0].message.content.strip()}")

def test_streaming():
    """测试流式响应"""
    print("\n🌊 Testing streaming...")
    
    client = OpenAI(base_url=f"{BASE_URL}/v1", api_key="dummy")
    
    start_time = time.time()
    content = ""
    
    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "Count from 1 to 3"}],
        max_tokens=50,
        temperature=0.1,
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content += chunk.choices[0].delta.content
    
    duration = time.time() - start_time
    print(f"✅ Streaming response: {content.strip()}")
    print(f"⏱️ Streaming duration: {duration:.2f}s")

def test_concurrent_requests():
    """测试并发请求"""
    print("\n🚀 Testing concurrent requests...")
    
    def make_request(i):
        client = OpenAI(base_url=f"{BASE_URL}/v1", api_key="dummy")
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": f"Generate a random number for request {i}"}],
                max_tokens=20,
                temperature=0.8
            )
            return {"success": True, "request_id": i, "response": response.choices[0].message.content.strip()}
        except Exception as e:
            return {"success": False, "request_id": i, "error": str(e)}
    
    start_time = time.time()
    
    # 并发 5 个请求
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(5)]
        results = [future.result() for future in futures]
    
    duration = time.time() - start_time
    successful = sum(1 for r in results if r["success"])
    
    print(f"✅ Concurrent requests: {successful}/5 successful")
    print(f"⏱️ Total duration: {duration:.2f}s")
    
    for result in results:
        if result["success"]:
            print(f"  Request {result['request_id']}: {result['response']}")
        else:
            print(f"  Request {result['request_id']}: ERROR - {result['error']}")

def test_parameter_variations():
    """测试不同参数设置"""
    print("\n🎛️ Testing parameter variations...")
    
    client = OpenAI(base_url=f"{BASE_URL}/v1", api_key="dummy")
    
    # 测试不同温度
    for temp in [0.1, 0.5, 0.9]:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Say hello creatively"}],
            max_tokens=30,
            temperature=temp
        )
        print(f"✅ Temperature {temp}: {response.choices[0].message.content.strip()}")
    
    # 测试不同 max_tokens
    for max_tokens in [10, 50, 100]:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Tell me about artificial intelligence"}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        print(f"✅ Max tokens {max_tokens}: {len(response.choices[0].message.content)} chars")

def benchmark_performance():
    """性能基准测试"""
    print("\n📊 Performance benchmark...")
    
    client = OpenAI(base_url=f"{BASE_URL}/v1", api_key="dummy")
    
    # 单个请求性能
    start_time = time.time()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "Write a short poem about technology"}],
        max_tokens=100,
        temperature=0.7
    )
    duration = time.time() - start_time
    
    tokens = response.usage.total_tokens
    tokens_per_second = tokens / duration
    
    print(f"✅ Single request performance:")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Total tokens: {tokens}")
    print(f"  Tokens/second: {tokens_per_second:.2f}")
    print(f"  Response: {response.choices[0].message.content.strip()[:100]}...")

def main():
    """主测试函数"""
    print("🧪 Starting comprehensive API testing...\n")
    
    try:
        test_basic_functionality()
        test_chat_completion()
        test_streaming()
        test_concurrent_requests()
        test_parameter_variations()
        benchmark_performance()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
