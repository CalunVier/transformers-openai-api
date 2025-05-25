#!/usr/bin/env python3
"""
Test script for new features:
1. DeepSeek R1 reasoning parser
2. Fixed streaming responses (no <|im_end|> tokens)
3. Enhanced usage statistics with speed information
4. DEBUG level request logging
"""

import requests
import json
import time


def test_debug_logging():
    """Test DEBUG level logging"""
    print("=== Testing DEBUG Level Logging ===")
    
    url = "http://localhost:8000/v1/chat/completions"
    payload = {
        "model": "Qwen/Qwen3-8B-AWQ",
        "messages": [
            {"role": "user", "content": "Hello, this is a test for debug logging"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    print("Sending request (check server console for DEBUG logs)...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Request successful - check server console for DEBUG output")
        print(f"Response: {result['choices'][0]['message']['content'][:100]}...")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)


def test_enhanced_usage_stats():
    """Test enhanced usage statistics"""
    print("\n=== Testing Enhanced Usage Statistics ===")
    
    url = "http://localhost:8000/v1/chat/completions"
    payload = {
        "model": "Qwen/Qwen3-8B-AWQ",
        "messages": [
            {"role": "user", "content": "Write a short poem about programming"}
        ],
        "max_tokens": 100,
        "temperature": 0.8
    }
    
    start_time = time.time()
    response = requests.post(url, json=payload)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        usage = result.get('usage', {})
        
        print("✅ Enhanced usage statistics:")
        print(f"  Prompt tokens: {usage.get('prompt_tokens')}")
        print(f"  Completion tokens: {usage.get('completion_tokens')}")
        print(f"  Total tokens: {usage.get('total_tokens')}")
        print(f"  Total time: {usage.get('total_time'):.3f}s" if usage.get('total_time') else "  Total time: N/A")
        print(f"  Tokens per second: {usage.get('tokens_per_second'):.2f}" if usage.get('tokens_per_second') else "  Tokens per second: N/A")
        print(f"  Client-side time: {end_time - start_time:.3f}s")
        
        # Check if new fields are present
        if usage.get('total_time') is not None and usage.get('tokens_per_second') is not None:
            print("✅ New timing fields are present")
        else:
            print("❌ New timing fields are missing")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)


def test_streaming_token_filtering():
    """Test streaming responses don't show <|im_end|> tokens"""
    print("\n=== Testing Streaming Token Filtering ===")
    
    url = "http://localhost:8000/v1/chat/completions"
    payload = {
        "model": "Qwen/Qwen3-8B-AWQ",
        "messages": [
            {"role": "user", "content": "Count from 1 to 10"}
        ],
        "max_tokens": 50,
        "temperature": 0.5,
        "stream": True
    }
    
    response = requests.post(url, json=payload, stream=True)
    
    if response.status_code == 200:
        print("✅ Streaming response received")
        full_content = ""
        unwanted_tokens_found = False
        usage_found = False
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data.strip() == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk['choices'][0]['delta']
                        if 'content' in delta:
                            content = delta['content']
                            full_content += content
                            print(content, end='', flush=True)
                            
                            # Check for unwanted tokens
                            if '<|im_end|>' in content:
                                unwanted_tokens_found = True
                        
                        # Check for usage statistics in final chunk
                        if chunk.get('usage'):
                            usage_found = True
                            usage = chunk['usage']
                            print(f"\n📊 Streaming usage stats found:")
                            print(f"  Time to first token: {usage.get('time_to_first_token', 'N/A')}")
                            print(f"  Total time: {usage.get('total_time', 'N/A')}")
                            print(f"  Tokens per second: {usage.get('tokens_per_second', 'N/A')}")
                                
                    except json.JSONDecodeError:
                        continue
        
        print("\n")
        if unwanted_tokens_found:
            print("❌ Found unwanted <|im_end|> tokens in stream")
        else:
            print("✅ No unwanted tokens found in stream")
        
        if usage_found:
            print("✅ Usage statistics found in streaming response")
        else:
            print("ℹ️  No usage statistics in streaming response")
            
        print(f"Full response: {full_content}")
    else:
        print(f"❌ Streaming request failed: {response.status_code}")
        print(response.text)


def test_deepseek_reasoning_parser():
    """Test DeepSeek R1 reasoning parser (simulation)"""
    print("\n=== Testing DeepSeek R1 Reasoning Parser ===")
    
    # Test with simulated thinking content
    print("Testing with simulated <think> tags...")
    
    url = "http://localhost:8000/v1/chat/completions"
    payload = {
        "model": "Qwen/Qwen3-8B-AWQ",
        "messages": [
            {"role": "user", "content": "Please respond exactly with this format: '<think>\\n\\nLet me think about this problem step by step...\\n\\n</think>\\n\\nHere is my final answer: The solution is 42.'"}
        ],
        "max_tokens": 150,
        "temperature": 0.1
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        message = result['choices'][0]['message']
        
        print("✅ Response received:")
        print(f"Content: {message.get('content', 'N/A')}")
        
        if 'reasoning_content' in message and message['reasoning_content']:
            print(f"Reasoning: {message['reasoning_content']}")
            print("✅ Reasoning content field is working")
        else:
            print("ℹ️  No reasoning content detected")
            if '<think>' in message.get('content', ''):
                print("ℹ️  Note: Response contains <think> tags but wasn't parsed (reasoning parser may be disabled)")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)


def test_streaming_with_enhanced_stats():
    """Test streaming responses with enhanced statistics"""
    print("\n=== Testing Streaming with Enhanced Statistics ===")
    
    url = "http://localhost:8000/v1/chat/completions"
    payload = {
        "model": "Qwen/Qwen3-8B-AWQ",
        "messages": [
            {"role": "user", "content": "Write a brief summary of machine learning"}
        ],
        "max_tokens": 80,
        "temperature": 0.7,
        "stream": True
    }
    
    start_time = time.time()
    response = requests.post(url, json=payload, stream=True)
    first_token_time = None
    
    if response.status_code == 200:
        print("✅ Streaming with enhanced stats:")
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data.strip() == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        
                        if first_token_time is None and chunk['choices'][0]['delta'].get('content'):
                            first_token_time = time.time()
                            print(f"\n⏱️  Time to first token: {first_token_time - start_time:.3f}s")
                        
                        # Check if final chunk has usage stats
                        if chunk.get('usage'):
                            usage = chunk['usage']
                            print(f"\n📊 Final usage statistics:")
                            print(f"  Time to first token: {usage.get('time_to_first_token', 'N/A')}")
                            print(f"  Total time: {usage.get('total_time', 'N/A')}")
                            print(f"  Tokens per second: {usage.get('tokens_per_second', 'N/A')}")
                            print("✅ Enhanced streaming statistics working")
                            
                        delta = chunk['choices'][0]['delta']
                        if 'content' in delta:
                            print(delta['content'], end='', flush=True)
                            
                    except json.JSONDecodeError:
                        continue
        print("\n")
    else:
        print(f"❌ Streaming request failed: {response.status_code}")
        print(response.text)


def test_configuration_check():
    """Check if server is running with the expected configuration"""
    print("\n=== Testing Configuration ===")
    
    try:
        # Check health endpoint
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ Server is healthy")
            print(f"  Model: {health_data.get('model', 'Unknown')}")
        
        # Check models endpoint
        models_response = requests.get("http://localhost:8000/v1/models")
        if models_response.status_code == 200:
            models_data = models_response.json()
            print("✅ Models endpoint working")
            if models_data.get('data'):
                print(f"  Available model: {models_data['data'][0].get('id', 'Unknown')}")
    
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")


def main():
    """Run all tests"""
    print("🧪 Testing New Features Implementation")
    print("=" * 50)
    
    # First check if server is running
    test_configuration_check()
    
    # Test all new features
    test_debug_logging()
    test_enhanced_usage_stats()
    test_streaming_token_filtering()
    test_deepseek_reasoning_parser()
    test_streaming_with_enhanced_stats()
    
    print("\n" + "=" * 50)
    print("🏁 All tests completed!")
    print("\nNotes:")
    print("- For DEBUG logging, check the server console output")
    print("- DeepSeek R1 reasoning parser can be enabled with --reasoning-parser deepseek_r1")
    print("- Enhanced statistics should show timing information")
    print("- Streaming should not contain <|im_end|> tokens")
    print("- Usage statistics should appear in both regular and streaming responses")


if __name__ == "__main__":
    main()
