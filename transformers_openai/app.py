from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import json
import logging
from typing import AsyncGenerator
import asyncio

from transformers_openai.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatCompletionUsage,
    ChatCompletionStreamResponse,
    ChatCompletionStreamChoice,
    ChatMessage,
    ModelListResponse,
    ModelInfo,
    ErrorResponse
)
from transformers_openai.model_manager import model_manager
from transformers_openai.config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.args.loglevel.upper()))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Transformers OpenAI API",
    description="OpenAI compatible API for Transformers models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request limiter
class RequestLimiter:
    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent
        self.current_requests = 0
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        async with self.lock:
            if self.current_requests >= self.max_concurrent:
                raise HTTPException(status_code=429, detail="Too many concurrent requests")
            self.current_requests += 1
    
    async def release(self):
        async with self.lock:
            self.current_requests = max(0, self.current_requests - 1)

request_limiter = RequestLimiter(config.args.max_concurrent)


@app.on_event("startup")
async def startup_event():
    """Initialize the model on startup"""
    logger.info("Starting up the application...")
    await model_manager.initialize()
    logger.info("Application startup completed")


@app.get("/v1/models")
async def list_models() -> ModelListResponse:
    """List available models"""
    return ModelListResponse(
        data=[
            ModelInfo(
                id=model_manager.model_name,
                owned_by="transformers-openai-api"
            )
        ]
    )


@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    """Create a chat completion"""
    try:
        # DEBUG level logging - print incoming request
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("=== Incoming Chat Completion Request ===")
            logger.debug(f"Request data: {request.model_dump_json(indent=2)}")
            logger.debug("=" * 45)
        
        await request_limiter.acquire()
        
        # DEBUG level logging for incoming requests
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Incoming request: {request.model_dump_json()}")
        
        # Validate model
        if request.model != model_manager.model_name:
            raise HTTPException(
                status_code=400, 
                detail=f"Model {request.model} not found. Available: {model_manager.model_name}"
            )
        
        # Format prompt
        prompt = model_manager.format_chat_prompt([msg.model_dump() for msg in request.messages])
          # Prepare generation parameters
        max_tokens = request.max_tokens or 100
        temperature = request.temperature or 1.0
        top_p = request.top_p or 1.0
        
        stop_sequences = None
        if request.stop:
            if isinstance(request.stop, str):
                stop_sequences = [request.stop]
            else:
                stop_sequences = request.stop
        
        if request.stream:
            # Streaming response
            async def generate_stream() -> AsyncGenerator[str, None]:
                try:
                    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
                    
                    async for chunk in model_manager.generate_text_stream(
                        prompt=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        stop_sequences=stop_sequences
                    ):
                        # Create delta content
                        delta = {}
                        if chunk.get("text"):
                            delta["content"] = chunk["text"]
                        
                        # Add reasoning content if available
                        if chunk.get("reasoning_content"):
                            delta["reasoning_content"] = chunk["reasoning_content"]
                        
                        # Create choice
                        choice = ChatCompletionStreamChoice(
                            index=0,
                            delta=delta,
                            finish_reason=chunk.get("finish_reason")
                        )
                        
                        # Create stream response with usage info
                        stream_response = ChatCompletionStreamResponse(
                            id=completion_id,
                            model=request.model,
                            choices=[choice]
                        )
                        
                        # Add usage information if available
                        if chunk.get("finish_reason"):
                            stream_response.usage = ChatCompletionUsage(
                                prompt_tokens=chunk.get("prompt_tokens", 0),
                                completion_tokens=chunk.get("completion_tokens", 0),
                                total_tokens=chunk.get("total_tokens", 0),
                                time_to_first_token=chunk.get("time_to_first_token"),
                                total_time=chunk.get("total_time"),
                                tokens_per_second=chunk.get("tokens_per_second")
                            )
                        
                        # Send the chunk
                        data = stream_response.model_dump_json()
                        yield f"data: {data}\n\n"
                        
                        # Break if finished
                        if chunk.get("finish_reason"):
                            break
                      # Send final done message
                    yield "data: [DONE]\n\n"
                
                except Exception as e:
                    logger.error(f"Error in streaming generation: {str(e)}")
                    # Send error in stream format
                    error_response = {
                        "error": {
                            "message": str(e),
                            "type": "server_error"
                        }
                    }
                    yield f"data: {json.dumps(error_response)}\n\n"
                    yield "data: [DONE]\n\n"
                
                finally:
                    await request_limiter.release()
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache", 
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        
        else:
            # Non-streaming response
            try:
                result = model_manager.generate_text(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    stop_sequences=stop_sequences
                )
                
                completion_id = f"chatcmpl-{uuid.uuid4().hex}"
                
                # Create message with reasoning content if available
                message = ChatMessage(
                    role="assistant", 
                    content=result["text"],
                    reasoning_content=result.get("reasoning_content")
                )
                
                response = ChatCompletionResponse(
                    id=completion_id,
                    model=request.model,
                    choices=[
                        ChatCompletionChoice(
                            index=0,
                            message=message,
                            finish_reason="stop"
                        )
                    ],                    
                    usage=ChatCompletionUsage(
                        prompt_tokens=result["prompt_tokens"],
                        completion_tokens=result["completion_tokens"],
                        total_tokens=result["total_tokens"],
                        total_time=result.get("total_time"),
                        tokens_per_second=result.get("tokens_per_second")
                    )                
                )
                
                await request_limiter.release()
                return response
            
            except Exception as e:
                await request_limiter.release()
                raise
    
    except Exception as e:
        await request_limiter.release()
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": model_manager.model_name}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Transformers OpenAI API", 
        "model": model_manager.model_name,
        "version": "1.0.0"
    }
