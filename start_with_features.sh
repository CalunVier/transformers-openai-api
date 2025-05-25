#!/bin/bash

echo "🚀 Starting Transformers OpenAI API with New Features"
echo "=================================================="

# Set environment variables for testing
LOGLEVEL="DEBUG"
REASONING_PARSER="deepseek_r1"
HF_MODEL="Qwen/Qwen3-8B-AWQ"
MAX_CONCURRENT="10"
HOST="0.0.0.0"
PORT="8000"

echo "Configuration:"
echo "- Log Level: $LOGLEVEL"
echo "- Reasoning Parser: $REASONING_PARSER"
echo "- Model: $HF_MODEL"
echo "- Host: $HOST:$PORT"
echo ""

echo "Starting server with new features..."
python main.py \
    --loglevel "$LOGLEVEL" \
    --reasoning-parser "$REASONING_PARSER" \
    --hf-model "$HF_MODEL" \
    --max-concurrent "$MAX_CONCURRENT" \
    --host "$HOST" \
    --port "$PORT"
