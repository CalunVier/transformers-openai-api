#!/usr/bin/env python3
"""
Transformers OpenAI API

本程序用为由 Transformers 运行的模型提供一个 OpenAI 兼容的 API 接口
"""

import uvicorn
import logging
from config import config


def main():
    """Main entry point"""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.args.loglevel.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Transformers OpenAI API server...")
    
    # Log configuration
    logger.info(f"Host: {config.args.host}")
    logger.info(f"Port: {config.args.port}")
    logger.info(f"Model: {config.args.hf_model}")
    logger.info(f"Max concurrent requests: {config.args.max_concurrent}")
    
    # Start the server
    uvicorn.run(
        "app:app",
        host=config.args.host,
        port=config.args.port,
        log_level=config.args.loglevel.lower(),
        reload=False
    )


if __name__ == "__main__":
    main()