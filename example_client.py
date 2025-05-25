#!/usr/bin/env python3
"""
Example client for testing the Transformers OpenAI API
"""

import requests
import json
import time


def test_chat_completion(base_url="http://localhost:7088", stream=False):
    """Test chat completion endpoint"""
    
    url = f"{base_url}/v1/chat/completions"
    
    payload = {
        "model": "mesolitica/malaysian-llama2-7b-32k-instructions",  # Use your actual model name
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! Can you tell me a short joke?"}
        ],
        "max_tokens": 100,
        "temperature": 0.7,
        "stream": stream
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Testing {'streaming' if stream else 'non-streaming'} chat completion...")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    if stream:
        # Streaming request
        response = requests.post(url, json=payload, headers=headers, stream=True)
        
        if response.status_code == 200:
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data.strip() == '[DONE]':
                            print("\nStream completed.")
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk['choices'][0]['delta'].get('content'):
                                print(chunk['choices'][0]['delta']['content'], end='', flush=True)
                        except json.JSONDecodeError:
                            continue
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    else:
        # Non-streaming request
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("Response:")
            print(json.dumps(result, indent=2))
            print(f"\nGenerated text: {result['choices'][0]['message']['content']}")
            print(f"Usage: {result['usage']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


def test_models_list(base_url="http://localhost:7088"):
    """Test models list endpoint"""
    
    url = f"{base_url}/v1/models"
    
    print("Testing models list...")
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        print("Available models:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def test_health_check(base_url="http://localhost:7088"):
    """Test health check endpoint"""
    
    url = f"{base_url}/health"
    
    print("Testing health check...")
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        print("Health check:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def main():
    """Main function"""
    base_url = "http://localhost:7088"
    
    print("=" * 60)
    print("Transformers OpenAI API Client Test")
    print("=" * 60)
    
    # Test health check
    test_health_check(base_url)
    print("\n" + "=" * 60)
    
    # Test models list
    test_models_list(base_url)
    print("\n" + "=" * 60)
    
    # Test non-streaming chat completion
    test_chat_completion(base_url, stream=False)
    print("\n" + "=" * 60)
    
    # Test streaming chat completion
    test_chat_completion(base_url, stream=True)
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
