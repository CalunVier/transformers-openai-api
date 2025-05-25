#!/usr/bin/env python3
"""
OpenAI API 兼容性测试客户端
"""
from openai import OpenAI

def test_with_openai_client():
    """使用 OpenAI 客户端库测试"""
    print("🧪 Testing with OpenAI client library...")
    
    # 创建客户端，指向我们的本地API
    client = OpenAI(
        base_url="http://127.0.0.1:8000/v1",
        api_key="dummy-key"  # 我们的API不需要真实的key
    )
    
    try:
        # 测试聊天完成
        print("💬 Testing chat completion...")
        response = client.chat.completions.create(
            model="Qwen/Qwen3-8B-AWQ",
            messages=[
                {"role": "user", "content": "你好！请用中文简单介绍一下你自己。"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"✅ Response received:")
        print(f"Model: {response.model}")
        print(f"Content: {response.choices[0].message.content}")
        print(f"Usage: {response.usage}")
        
        # 测试流式响应
        print("\n🌊 Testing streaming...")
        stream = client.chat.completions.create(
            model="Qwen/Qwen3-8B-AWQ",
            messages=[
                {"role": "user", "content": "从1数到5，每个数字一行"}
            ],
            max_tokens=50,
            temperature=0.7,
            stream=True
        )
        
        print("Stream response:")
        for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end='', flush=True)
        print("\n✅ Streaming completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting OpenAI compatibility test...\n")
    test_with_openai_client()
    print("\n✅ Test completed!")
