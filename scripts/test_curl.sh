#!/bin/bash
# 简单的 cURL API 测试脚本

echo "🧪 Testing Transformers OpenAI API with cURL..."

# 测试健康检查
echo "🔍 Health Check:"
curl -s http://127.0.0.1:8000/health

echo -e "\n\n📋 Models List:"
curl -s http://127.0.0.1:8000/v1/models

echo -e "\n\n💬 Chat Completion:"
curl -s -X POST "http://127.0.0.1:8000/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "Qwen/Qwen3-8B-AWQ",
       "messages": [
         {"role": "user", "content": "Hello! Just say hi back briefly."}
       ],
       "max_tokens": 20,
       "temperature": 0.7
     }'

echo -e "\n\n✅ cURL tests completed!"
