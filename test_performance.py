#!/usr/bin/env python3
"""
性能测试和对比
"""
import time
import requests
import json
from openai import OpenAI

def test_streaming_performance():
    """测试流式响应的性能"""
    print("🚀 流式响应性能测试...\n")
    
    client = OpenAI(
        base_url="http://127.0.0.1:8000/v1",
        api_key="dummy"
    )
    
    test_cases = [
        {
            "name": "短响应 (20 tokens)",
            "messages": [{"role": "user", "content": "Count from 1 to 5"}],
            "max_tokens": 20
        },
        {
            "name": "中等响应 (50 tokens)", 
            "messages": [{"role": "user", "content": "Explain what is machine learning in simple terms"}],
            "max_tokens": 50
        },
        {
            "name": "长响应 (100 tokens)",
            "messages": [{"role": "user", "content": "Write a short story about a robot learning to cook"}],
            "max_tokens": 100
        }
    ]
    
    for test_case in test_cases:
        print(f"📊 测试: {test_case['name']}")
        
        # 测试流式响应
        start_time = time.time()
        first_token_time = None
        tokens_received = 0
        
        try:
            stream = client.chat.completions.create(
                model="Qwen/Qwen3-8B-AWQ",
                messages=test_case["messages"],
                max_tokens=test_case["max_tokens"],
                temperature=0.7,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    if first_token_time is None:
                        first_token_time = time.time()
                    tokens_received += 1
            
            end_time = time.time()
            
            total_time = end_time - start_time
            first_token_latency = first_token_time - start_time if first_token_time else 0
            tokens_per_second = tokens_received / total_time if total_time > 0 else 0
            
            print(f"  ✅ 总时间: {total_time:.2f}s")
            print(f"  ⚡ 首Token延迟: {first_token_latency:.2f}s")
            print(f"  📈 接收tokens: {tokens_received}")
            print(f"  🔥 生成速度: {tokens_per_second:.2f} tokens/s")
            
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        
        print()

def test_non_streaming_performance():
    """测试非流式响应的性能"""
    print("📦 非流式响应性能测试...\n")
    
    client = OpenAI(
        base_url="http://127.0.0.1:8000/v1",
        api_key="dummy"
    )
    
    test_cases = [
        {
            "name": "短响应 (20 tokens)",
            "messages": [{"role": "user", "content": "What is 2+2?"}],
            "max_tokens": 20
        },
        {
            "name": "中等响应 (50 tokens)",
            "messages": [{"role": "user", "content": "Explain what is Python programming"}],
            "max_tokens": 50
        }
    ]
    
    for test_case in test_cases:
        print(f"📊 测试: {test_case['name']}")
        
        start_time = time.time()
        
        try:
            response = client.chat.completions.create(
                model="Qwen/Qwen3-8B-AWQ",
                messages=test_case["messages"],
                max_tokens=test_case["max_tokens"],
                temperature=0.7
            )
            
            end_time = time.time()
            total_time = end_time - start_time
            
            completion_tokens = response.usage.completion_tokens
            tokens_per_second = completion_tokens / total_time if total_time > 0 else 0
            
            print(f"  ✅ 总时间: {total_time:.2f}s")
            print(f"  📈 生成tokens: {completion_tokens}")
            print(f"  🔥 生成速度: {tokens_per_second:.2f} tokens/s")
            print(f"  📝 响应: {response.choices[0].message.content[:100]}...")
            
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        
        print()

def test_concurrent_requests():
    """测试并发请求性能"""
    print("🔀 并发请求测试...\n")
    
    import concurrent.futures
    import threading
    
    def make_request(request_id):
        """发起单个请求"""
        client = OpenAI(
            base_url="http://127.0.0.1:8000/v1",
            api_key="dummy"
        )
        
        start_time = time.time()
        try:
            response = client.chat.completions.create(
                model="Qwen/Qwen3-8B-AWQ",
                messages=[{"role": "user", "content": f"Hello, this is request {request_id}"}],
                max_tokens=30,
                temperature=0.5
            )
            end_time = time.time()
            return {
                "id": request_id,
                "success": True,
                "time": end_time - start_time,
                "tokens": response.usage.completion_tokens
            }
        except Exception as e:
            end_time = time.time()
            return {
                "id": request_id,
                "success": False,
                "time": end_time - start_time,
                "error": str(e)
            }
    
    # 测试不同的并发级别
    for concurrent_requests in [2, 3, 5]:
        print(f"📊 测试 {concurrent_requests} 个并发请求:")
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_request, i) for i in range(concurrent_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        if successful:
            avg_time = sum(r["time"] for r in successful) / len(successful)
            total_tokens = sum(r["tokens"] for r in successful)
            throughput = total_tokens / total_time
            
            print(f"  ✅ 成功: {len(successful)}/{concurrent_requests}")
            print(f"  ⏱️  总时间: {total_time:.2f}s")
            print(f"  📊 平均延迟: {avg_time:.2f}s")
            print(f"  🔥 总吞吐量: {throughput:.2f} tokens/s")
        
        if failed:
            print(f"  ❌ 失败: {len(failed)} 个请求")
        
        print()

def main():
    print("🧪 TransformersOpenAI API 性能测试")
    print("=" * 50)
    
    # 确保服务器正在运行
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        print(f"✅ 服务器状态: {response.json()}\n")
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return
    
    # 运行性能测试
    test_non_streaming_performance()
    test_streaming_performance() 
    test_concurrent_requests()
    
    print("✅ 所有性能测试完成!")

if __name__ == "__main__":
    main()
