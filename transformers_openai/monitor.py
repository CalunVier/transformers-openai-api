#!/usr/bin/env python3
"""
API 服务器监控工具
"""
import time
import requests
import psutil
from datetime import datetime


def get_server_stats():
    """获取服务器统计信息"""
    try:
        # API 健康检查
        health_response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        api_status = health_response.status_code == 200

        # 系统资源使用
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # GPU 信息（如果有 nvidia-smi）
        gpu_info = "N/A"
        try:
            import subprocess

            gpu_result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if gpu_result.returncode == 0:
                gpu_data = gpu_result.stdout.strip().split("\n")[0].split(", ")
                gpu_util, gpu_mem_used, gpu_mem_total = map(int, gpu_data)
                gpu_info = f"{gpu_util}% GPU, {gpu_mem_used}/{gpu_mem_total}MB"
        except:
            pass

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "api_status": "✅ Online" if api_status else "❌ Offline",
            "cpu_percent": f"{cpu_percent:.1f}%",
            "memory_percent": f"{memory.percent:.1f}%",
            "memory_used": f"{memory.used / 1024**3:.1f}GB",
            "memory_total": f"{memory.total / 1024**3:.1f}GB",
            "disk_percent": f"{disk.percent:.1f}%",
            "gpu_info": gpu_info,
        }
    except Exception as e:
        return {"error": str(e)}


def test_api_latency():
    """测试 API 延迟"""
    try:
        start_time = time.time()
        response = requests.get("http://127.0.0.1:8000/health", timeout=10)
        latency = (time.time() - start_time) * 1000  # 转换为毫秒

        if response.status_code == 200:
            return f"{latency:.1f}ms"
        else:
            return "Error"
    except:
        return "Timeout"


def monitor_loop():
    """监控循环"""
    print("🖥️  API Server Monitor")
    print("=" * 50)

    try:
        while True:
            stats = get_server_stats()
            latency = test_api_latency()

            # 清屏（可选）
            # import os
            # os.system('clear')

            print(f"\n[{stats.get('timestamp', 'N/A')}]")
            print(f"API Status: {stats.get('api_status', 'Unknown')}")
            print(f"API Latency: {latency}")
            print(f"CPU Usage: {stats.get('cpu_percent', 'N/A')}")
            print(
                f"Memory: {stats.get('memory_used', 'N/A')} / {stats.get('memory_total', 'N/A')} ({stats.get('memory_percent', 'N/A')})"
            )
            print(f"Disk Usage: {stats.get('disk_percent', 'N/A')}")
            print(f"GPU: {stats.get('gpu_info', 'N/A')}")
            print("-" * 50)

            time.sleep(5)  # 每5秒更新一次

    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped.")


def single_check():
    """单次检查"""
    print("📊 Server Status Check")
    print("=" * 30)

    stats = get_server_stats()
    latency = test_api_latency()

    for key, value in stats.items():
        if key != "timestamp":
            print(f"{key.replace('_', ' ').title()}: {value}")

    print(f"API Latency: {latency}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        monitor_loop()
    else:
        single_check()
