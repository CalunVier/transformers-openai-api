import torch
import logging
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    AutoProcessor,
    StaticCache
)
from typing import Optional, List, Dict, Any, AsyncGenerator
import asyncio
import time
from config import config


logger = logging.getLogger(__name__)


class ModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.processor = None
        self.device = None
        self.static_cache = None
        self.model_name = config.args.hf_model
        
    async def initialize(self):
        """Initialize the model and tokenizer"""
        logger.info(f"Initializing model: {self.model_name}")
        
        # Set device
        if config.args.accelerator_type == "cuda" and torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")
        
        logger.info(f"Using device: {self.device}")
        
        # Load tokenizer
        logger.info("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            use_fast=config.args.tokenizer_use_fast
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        logger.info("Loading model...")
        torch_dtype = getattr(torch, config.args.torch_dtype)
        
        model_kwargs = {
            "torch_dtype": torch_dtype,
            "device_map": "auto" if self.device.type == "cuda" else None,
        }
        
        if config.args.model_type == "AutoModelForCausalLM":
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
        else:
            raise ValueError(f"Unsupported model type: {config.args.model_type}")
        
        # Move model to device if not using device_map
        if model_kwargs["device_map"] is None:
            self.model = self.model.to(self.device)
        
        # Apply optimizations
        if config.args.torch_compile:
            logger.info("Applying torch.compile...")
            self.model = torch.compile(self.model, mode=config.args.torch_compile_mode)
        
        # Initialize static cache if enabled
        if config.args.static_cache:
            logger.info("Initializing static cache...")
            self.static_cache = StaticCache(
                config=self.model.config,
                max_batch_size=config.args.continuous_batching_batch_size,
                max_cache_len=config.args.static_cache_decoder_max_length,
                device=self.device,
                dtype=torch_dtype,
            )
        
        logger.info("Model initialization completed")
    
    def format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages into a prompt"""
        if hasattr(self.tokenizer, 'apply_chat_template'):
            try:
                return self.tokenizer.apply_chat_template(
                    messages, 
                    tokenize=False, 
                    add_generation_prompt=True
                )
            except Exception as e:
                logger.warning(f"Failed to apply chat template: {e}")
        
        # Fallback formatting
        prompt = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            if role == "system":
                prompt += f"System: {content}\n"
            elif role == "user":
                prompt += f"Human: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"
        
        prompt += "Assistant: "
        return prompt
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 1.0,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate text completion"""
        # Tokenize input
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            padding=True, 
            truncation=True
        ).to(self.device)
        
        input_length = inputs.input_ids.shape[1]
        
        # Generation parameters
        generation_kwargs = {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": temperature > 0,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }
        
        if self.static_cache:
            generation_kwargs["past_key_values"] = self.static_cache
        
        # Generate
        with torch.no_grad():
            if config.args.torch_profiling:
                with torch.autograd.profiler.profile() as prof:
                    outputs = self.model.generate(**inputs, **generation_kwargs)
                logger.info(f"Generation profiling: {prof.key_averages()}")
            else:
                outputs = self.model.generate(**inputs, **generation_kwargs)
        
        # Decode output
        generated_ids = outputs[0][input_length:]
        generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        # Handle stop sequences
        if stop_sequences:
            for stop_seq in stop_sequences:
                if stop_seq in generated_text:
                    generated_text = generated_text.split(stop_seq)[0]
                    break
        
        return {
            "text": generated_text,
            "prompt_tokens": input_length,
            "completion_tokens": len(generated_ids),
            "total_tokens": input_length + len(generated_ids)
        }
    
    async def generate_text_stream(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 1.0,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate text completion with streaming"""
        # Tokenize input
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            padding=True, 
            truncation=True
        ).to(self.device)
        
        input_length = inputs.input_ids.shape[1]
        
        # Generation parameters
        generation_kwargs = {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": temperature > 0,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }
        
        if self.static_cache:
            generation_kwargs["past_key_values"] = self.static_cache
        
        # Generate token by token
        generated_tokens = []
        current_input = inputs.input_ids
        
        for _ in range(max_tokens):
            with torch.no_grad():
                outputs = self.model(current_input)
                logits = outputs.logits[0, -1, :]
                
                # Apply temperature and top_p sampling
                if temperature > 0:
                    logits = logits / temperature
                    if top_p < 1.0:
                        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                        cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                        sorted_indices_to_remove = cumulative_probs > top_p
                        sorted_indices_to_remove[1:] = sorted_indices_to_remove[:-1].clone()
                        sorted_indices_to_remove[0] = 0
                        indices_to_remove = sorted_indices_to_remove.scatter(0, sorted_indices, sorted_indices_to_remove)
                        logits[indices_to_remove] = float('-inf')
                    
                    probs = torch.softmax(logits, dim=-1)
                    next_token = torch.multinomial(probs, 1)
                else:
                    next_token = torch.argmax(logits, dim=-1, keepdim=True)
            
            generated_tokens.append(next_token.item())
            
            # Decode the new token
            new_text = self.tokenizer.decode([next_token.item()], skip_special_tokens=True)
            
            # Check for stop sequences
            full_generated = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
            finish_reason = None
            
            if stop_sequences:
                for stop_seq in stop_sequences:
                    if stop_seq in full_generated:
                        finish_reason = "stop"
                        break
            
            if next_token.item() == self.tokenizer.eos_token_id:
                finish_reason = "stop"
            
            yield {
                "text": new_text,
                "finish_reason": finish_reason,
                "prompt_tokens": input_length,
                "completion_tokens": len(generated_tokens),
                "total_tokens": input_length + len(generated_tokens)
            }
            
            if finish_reason:
                break
            
            # Update input for next iteration
            current_input = torch.cat([current_input, next_token.unsqueeze(0)], dim=1)
            
            # Small sleep to allow other coroutines to run
            await asyncio.sleep(config.args.continuous_batching_microsleep)


# Global model manager instance
model_manager = ModelManager()
