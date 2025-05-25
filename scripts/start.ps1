# Transformers OpenAI API 启动脚本

Write-Host "正在启动 Transformers OpenAI API..." -ForegroundColor Green

# 检查 Python 是否安装
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "错误: 未找到 Python。请先安装 Python 3.8+" -ForegroundColor Red
    exit 1
}

# 检查并创建虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# 安装依赖
Write-Host "安装依赖..." -ForegroundColor Yellow
pip install -r requirements.txt

# 设置环境变量（如果需要）
$env:HF_MODEL = "mesolitica/malaysian-llama2-7b-32k-instructions"
$env:TORCH_DTYPE = "bfloat16"
$env:ACCELERATOR_TYPE = "cuda"
$env:MAX_CONCURRENT = "10"
$env:LOGLEVEL = "INFO"

# 启动服务器
Write-Host "启动服务器..." -ForegroundColor Green
Write-Host "API 将在 http://localhost:7088 上运行" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow

python main.py
