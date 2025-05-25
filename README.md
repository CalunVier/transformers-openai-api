# Transformers OpenAI API

[English](README.md) | [简体中文](README.zh-CN.md)

This project provides an OpenAI-compatible API interface for models running with Hugging Face Transformers. Built with FastAPI, it supports both streaming and non-streaming responses and is fully compatible with the OpenAI Chat Completions API.

## Features

- 🚀 OpenAI Chat Completions API compatible
- 📡 Supports streaming and non-streaming responses
- 🔧 Model inference based on the Transformers library
- ⚡ CUDA acceleration and optimization
- 🎛️ Configurable parameters (temperature, top_p, max_tokens, etc.)
- 📊 Batch processing and concurrency limits
- 🐳 Docker support
- 🔍 Health check and monitoring endpoints

## Quick Start

### Method 1: Using PowerShell Script (Recommended)

```powershell
# Run the startup script directly
.\start.ps1
```

### Method 2: Manual Installation

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment (Windows)
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
python main.py
```

### Method 3: Using Docker

```bash
# Build and run
docker-compose up --build
```

## API Usage Examples

### Basic Chat Completion

```python
import requests
import json

url = "http://localhost:7088/v1/chat/completions"
payload = {
    "model": "mesolitica/malaysian-llama2-7b-32k-instructions",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! How are you?"}
    ],
    "max_tokens": 100,
    "temperature": 0.7
}

response = requests.post(url, json=payload)
print(response.json())
```

### Streaming Response

```python
import requests
import json

url = "http://localhost:7088/v1/chat/completions"
payload = {
    "model": "mesolitica/malaysian-llama2-7b-32k-instructions",
    "messages": [
        {"role": "user", "content": "Tell me a story"}
    ],
    "max_tokens": 200,
    "temperature": 0.8,
    "stream": True
}

response = requests.post(url, json=payload, stream=True)
for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = line[6:]
            if data.strip() == '[DONE]':
                break
            try:
                chunk = json.loads(data)
                if chunk['choices'][0]['delta'].get('content'):
                    print(chunk['choices'][0]['delta']['content'], end='', flush=True)
            except json.JSONDecodeError:
                continue
```

### List Available Models

```python
import requests

response = requests.get("http://localhost:7088/v1/models")
print(response.json())
```

## Test Client

Run the included test client:

```bash
python example_client.py
```

## API Endpoints

- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Create chat completion
- `GET /health` - Health check
- `GET /` - Root endpoint info

```
usage: main.py [-h] [--host HOST] [--port PORT] [--loglevel LOGLEVEL] [--model-type MODEL_TYPE]
               [--tokenizer-type TOKENIZER_TYPE] [--tokenizer-use-fast TOKENIZER_USE_FAST] [--processor-type PROCESSOR_TYPE]
               [--hf-model HF_MODEL] [--torch-dtype TORCH_DTYPE] [--architecture-type {decoder,encoder-decoder}]
               [--serving-type {chat,whisper}] [--continuous-batching-microsleep CONTINUOUS_BATCHING_MICROSLEEP]
               [--continuous-batching-batch-size CONTINUOUS_BATCHING_BATCH_SIZE] [--static-cache STATIC_CACHE]
               [--static-cache-encoder-max-length STATIC_CACHE_ENCODER_MAX_LENGTH]
               [--static-cache-decoder-max-length STATIC_CACHE_DECODER_MAX_LENGTH] [--accelerator-type ACCELERATOR_TYPE]
               [--max-concurrent MAX_CONCURRENT] [--torch-profiling TORCH_PROFILING] [--hqq HQQ]
               [--torch-compile TORCH_COMPILE] [--torch-compile-mode TORCH_COMPILE_MODE]

Configuration parser

options:
  -h, --help            show this help message and exit
  --host HOST           host name to host the app (default: 0.0.0.0, env: HOSTNAME)
  --port PORT           port to host the app (default: 7088, env: PORT)
  --loglevel LOGLEVEL   Logging level (default: INFO, env: LOGLEVEL)
  --model-type MODEL_TYPE
                        Model type (default: AutoModelForCausalLM, env: MODEL_TYPE)
  --tokenizer-type TOKENIZER_TYPE
                        Tokenizer type (default: AutoTokenizer, env: TOKENIZER_TYPE)
  --tokenizer-use-fast TOKENIZER_USE_FAST
                        Use fast tokenizer (default: True, env: TOKENIZER_USE_FAST)
  --processor-type PROCESSOR_TYPE
                        Processor type (default: AutoTokenizer, env: PROCESSOR_TYPE)
  --hf-model HF_MODEL   Hugging Face model (default: mesolitica/malaysian-llama2-7b-32k-instructions, env: HF_MODEL)
  --torch-dtype TORCH_DTYPE
                        Torch data type (default: bfloat16, env: TORCH_DTYPE)
  --architecture-type {decoder,encoder-decoder}
                        Architecture type (default: decoder, env: ARCHITECTURE_TYPE)
  --serving-type {chat,whisper}
                        Serving type (default: chat, env: SERVING_TYPE)
  --continuous-batching-microsleep CONTINUOUS_BATCHING_MICROSLEEP
                        microsleep to group continuous batching, 1 / 1e-4 = 10k steps for one second (default: 0.001, env:
                        CONTINUOUS_BATCHING_MICROSLEEP)
  --continuous-batching-batch-size CONTINUOUS_BATCHING_BATCH_SIZE
                        maximum of batch size during continuous batching (default: 20, env: CONTINUOUS_BATCHING_BATCH_SIZE)
  --static-cache STATIC_CACHE
                        Preallocate KV Cache for faster inference (default: False, env: STATIC_CACHE)
  --static-cache-encoder-max-length STATIC_CACHE_ENCODER_MAX_LENGTH
                        Maximum concurrent requests (default: 256, env: STATIC_CACHE_ENCODER_MAX_LENGTH)
  --static-cache-decoder-max-length STATIC_CACHE_DECODER_MAX_LENGTH
                        Maximum concurrent requests (default: 256, env: STATIC_CACHE_DECODER_MAX_LENGTH)
  --accelerator-type ACCELERATOR_TYPE
                        Accelerator type (default: cuda, env: ACCELERATOR_TYPE)
  --max-concurrent MAX_CONCURRENT
                        Maximum concurrent requests (default: 100, env: MAX_CONCURRENT)
  --torch-profiling TORCH_PROFILING
                        Use torch.autograd.profiler.profile() to profile prefill and step (default: False, env:
                        TORCH_PROFILING)
  --hqq HQQ             int4 quantization using HQQ (default: False, env: HQQ)
  --torch-compile TORCH_COMPILE
                        Torch compile necessary forwards, can speed up at least 1.5X (default: False, env: TORCH_COMPILE)
  --torch-compile-mode TORCH_COMPILE_MODE
                        torch compile type (default: reduce-overhead, env: TORCH_COMPILE_MODE)
```

## Configuration Parameters

All configuration parameters can be set via command-line arguments or environment variables:

### Basic Configuration
- `--host` / `HOSTNAME`: Server host (default: 0.0.0.0)
- `--port` / `PORT`: Server port (default: 7088)
- `--loglevel` / `LOGLEVEL`: Logging level (default: INFO)

### Model Configuration
- `--hf-model` / `HF_MODEL`: Hugging Face model name
- `--model-type` / `MODEL_TYPE`: Model type (default: AutoModelForCausalLM)
- `--tokenizer-type` / `TOKENIZER_TYPE`: Tokenizer type (default: AutoTokenizer)
- `--torch-dtype` / `TORCH_DTYPE`: Data type (default: bfloat16)

### Performance Optimization
- `--accelerator-type` / `ACCELERATOR_TYPE`: Accelerator type (default: cuda)
- `--max-concurrent` / `MAX_CONCURRENT`: Maximum concurrent requests (default: 100)
- `--torch-compile` / `TORCH_COMPILE`: Enable Torch compile optimization
- `--static-cache` / `STATIC_CACHE`: Preallocate KV cache

### Batch Processing
- `--continuous-batching-batch-size`: Maximum batch size for continuous batching (default: 20)
- `--continuous-batching-microsleep`: Micro sleep time for batching (default: 0.001)

### Example Startup Command

```bash
python main.py \
    --host 0.0.0.0 \
    --port 7088 \
    --hf-model microsoft/DialoGPT-medium \
    --torch-dtype float16 \
    --max-concurrent 50 \
    --torch-compile True
```

## Project Structure

```
transformers-openai-api/
├── main.py              # Application entry point
├── app.py               # FastAPI app
├── config.py            # Configuration management
├── models.py            # Pydantic data models
├── model_manager.py     # Model manager
├── example_client.py    # Test client
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker config
├── docker-compose.yml   # Docker Compose config
├── start.ps1            # Windows startup script
└── README.md            # Project documentation
```

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Try using a smaller model
   - Set `--torch-dtype float16` or `--hqq True`
   - Reduce the value of `--max-concurrent`

2. **Slow Model Loading**
   - Ensure a stable network connection
   - Consider using a local model path

3. **Slow API Response**
   - Enable `--torch-compile True`
   - Use `--static-cache True`
   - Adjust `--continuous-batching-batch-size`

### Logging

Enable detailed logging:
```bash
python main.py --loglevel DEBUG
```

## Compatibility

This API is compatible with the OpenAI Chat Completions API and can be used as a direct replacement for OpenAI endpoints. Supported parameters:

- `model`: Model name
- `messages`: List of conversation messages
- `max_tokens`: Maximum number of generated tokens
- `temperature`: Sampling temperature
- `top_p`: Top-p sampling
- `stream`: Whether to use streaming response
- `stop`: Stop sequences

## License

MIT License

## Contributing

Contributions and pull requests are welcome!