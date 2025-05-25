# Transformers OpenAI API

本程序用为由 Transformers 运行的模型提供一个 OpenAI 兼容的 API 接口。使用 FastAPI 构建，支持流式和非流式响应，完全兼容 OpenAI Chat Completions API。

## 功能特性

- 🚀 OpenAI Chat Completions API 兼容
- 📡 支持流式和非流式响应
- 🔧 基于 Transformers 库的模型推理
- ⚡ 支持 CUDA 加速和优化
- 🎛️ 可配置的参数（温度、top_p、max_tokens 等）
- 📊 支持批处理和并发限制
- 🐳 Docker 支持
- 🔍 健康检查和监控端点

## 快速开始

### 方法 1: 使用 PowerShell 脚本（推荐）

```powershell
# 直接运行启动脚本
.\start.ps1
```

### 方法 2: 手动安装

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境 (Windows)
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务器
python main.py
```

### 方法 3: 使用 Docker

```bash
# 构建并运行
docker-compose up --build
```

## API 使用示例

### 基本聊天完成

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

### 流式响应

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

### 获取可用模型

```python
import requests

response = requests.get("http://localhost:7088/v1/models")
print(response.json())
```

## 测试客户端

运行包含的测试客户端：

```bash
python example_client.py
```

## API 端点

- `GET /v1/models` - 列出可用模型
- `POST /v1/chat/completions` - 创建聊天完成
- `GET /health` - 健康检查
- `GET /` - 根端点信息

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

## 配置参数

所有配置参数都可以通过命令行参数或环境变量设置：

### 基本配置
- `--host` / `HOSTNAME`: 服务器主机 (默认: 0.0.0.0)
- `--port` / `PORT`: 服务器端口 (默认: 7088)
- `--loglevel` / `LOGLEVEL`: 日志级别 (默认: INFO)

### 模型配置
- `--hf-model` / `HF_MODEL`: Hugging Face 模型名称
- `--model-type` / `MODEL_TYPE`: 模型类型 (默认: AutoModelForCausalLM)
- `--tokenizer-type` / `TOKENIZER_TYPE`: 分词器类型 (默认: AutoTokenizer)
- `--torch-dtype` / `TORCH_DTYPE`: 数据类型 (默认: bfloat16)

### 性能优化
- `--accelerator-type` / `ACCELERATOR_TYPE`: 加速器类型 (默认: cuda)
- `--max-concurrent` / `MAX_CONCURRENT`: 最大并发请求数 (默认: 100)
- `--torch-compile` / `TORCH_COMPILE`: 启用 Torch 编译优化
- `--static-cache` / `STATIC_CACHE`: 预分配 KV 缓存

### 批处理配置
- `--continuous-batching-batch-size`: 连续批处理的最大批次大小 (默认: 20)
- `--continuous-batching-microsleep`: 批处理微睡眠时间 (默认: 0.001)

### 示例启动命令

```bash
python main.py \
    --host 0.0.0.0 \
    --port 7088 \
    --hf-model microsoft/DialoGPT-medium \
    --torch-dtype float16 \
    --max-concurrent 50 \
    --torch-compile True
```

## 项目结构

```
transformers-openai-api/
├── main.py              # 应用入口点
├── app.py               # FastAPI 应用
├── config.py            # 配置管理
├── models.py            # Pydantic 数据模型
├── model_manager.py     # 模型管理器
├── example_client.py    # 测试客户端
├── requirements.txt     # Python 依赖
├── Dockerfile           # Docker 配置
├── docker-compose.yml   # Docker Compose 配置
├── start.ps1           # Windows 启动脚本
└── README.md           # 项目文档
```

## 故障排除

### 常见问题

1. **CUDA 内存不足**
   - 尝试使用较小的模型
   - 设置 `--torch-dtype float16` 或 `--hqq True`
   - 减少 `--max-concurrent` 值

2. **模型加载慢**
   - 确保网络连接稳定
   - 考虑使用本地模型路径

3. **API 响应慢**
   - 启用 `--torch-compile True`
   - 使用 `--static-cache True`
   - 调整 `--continuous-batching-batch-size`

### 日志

启用详细日志：
```bash
python main.py --loglevel DEBUG
```

## 兼容性

本 API 兼容 OpenAI Chat Completions API，可以直接替换 OpenAI 的端点使用。支持的参数：

- `model`: 模型名称
- `messages`: 对话消息列表
- `max_tokens`: 最大生成令牌数
- `temperature`: 采样温度
- `top_p`: Top-p 采样
- `stream`: 是否流式响应
- `stop`: 停止序列

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！