import torch
import logging
import re
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    StaticCache,
    TextIteratorStreamer,
)
from typing import Optional, List, Dict, Any, AsyncGenerator, Tuple
import asyncio
import time
from threading import Thread
from transformers_openai.config import config


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
            self.model_name, use_fast=config.args.tokenizer_use_fast
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
                self.model_name, **model_kwargs
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
        if hasattr(self.tokenizer, "apply_chat_template"):
            try:
                return self.tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
            except Exception as e:
                logger.warning(
                    f"Failed to apply chat template: {e}"
                )  # Fallback formatting
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
        start_time = time.time()

        # Tokenize input
        inputs = self.tokenizer(
            prompt, return_tensors="pt", padding=True, truncation=True
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

        total_time = time.time() - start_time

        # Decode output
        generated_ids = outputs[0][input_length:]
        generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        # Handle stop sequences
        if stop_sequences:
            for stop_seq in stop_sequences:
                if stop_seq in generated_text:
                    generated_text = generated_text.split(stop_seq)[0]
                    break

        # Parse reasoning content if enabled
        clean_text, reasoning_content = self.parse_reasoning_content(generated_text)

        completion_tokens = len(generated_ids)
        tokens_per_second = completion_tokens / total_time if total_time > 0 else 0

        result = {
            "text": clean_text,
            "reasoning_content": reasoning_content,
            "prompt_tokens": input_length,
            "completion_tokens": completion_tokens,
            "total_tokens": input_length + completion_tokens,
            "total_time": total_time,
            "tokens_per_second": tokens_per_second,
        }

        return result

    async def generate_text_stream(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 1.0,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate text completion with streaming using TextIteratorStreamer"""
        start_time = time.time()
        first_token_time = None

        # Tokenize input
        inputs = self.tokenizer(
            prompt, return_tensors="pt", padding=True, truncation=True
        ).to(self.device)

        input_length = inputs.input_ids.shape[1]

        # Create streamer - add special tokens to be able to filter them
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            decode_kwargs={
                "skip_special_tokens": False
            },  # Keep special tokens for filtering
        )

        # Generation parameters
        generation_kwargs = {
            **inputs,
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": temperature > 0,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            "streamer": streamer,
        }

        if self.static_cache:
            generation_kwargs["past_key_values"] = self.static_cache

        # Start generation in a separate thread
        generation_thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        generation_thread.start()

        # Stream tokens as they become available
        generated_text = ""
        completion_tokens = 0
        accumulated_reasoning = ""
        in_thinking_mode = False
        thinking_buffer = ""

        try:
            for new_text in streamer:
                if first_token_time is None:
                    first_token_time = time.time()

                # Filter out unwanted tokens like <|im_end|>
                if "<|im_end|>" in new_text:
                    new_text = new_text.replace("<|im_end|>", "")

                # Skip empty tokens
                if not new_text:
                    continue

                generated_text += new_text
                completion_tokens += (
                    1  # Handle DeepSeek R1 reasoning parsing for streaming
                )
                chunk_text = new_text
                reasoning_delta = None

                if config.args.reasoning_parser == "deepseek_r1":
                    chunk_text, reasoning_delta = self._handle_streaming_reasoning(
                        new_text, generated_text
                    )

                # Check for stop sequences
                finish_reason = None
                if stop_sequences:
                    for stop_seq in stop_sequences:
                        if stop_seq in generated_text:
                            # Truncate at stop sequence
                            truncate_pos = generated_text.find(stop_seq)
                            generated_text = generated_text[:truncate_pos]
                            finish_reason = "stop"
                            break

                # Determine if this is the last chunk
                if not generation_thread.is_alive() and finish_reason is None:
                    finish_reason = "stop"

                # Only yield if we have content to send or it's the final chunk
                if chunk_text or reasoning_delta or finish_reason:
                    current_time = time.time()
                    time_to_first_token = (
                        first_token_time - start_time if first_token_time else None
                    )
                    total_time = current_time - start_time
                    tokens_per_second = (
                        completion_tokens / total_time if total_time > 0 else 0
                    )

                    yield {
                        "text": chunk_text,
                        "reasoning_content": reasoning_delta,
                        "finish_reason": finish_reason,
                        "prompt_tokens": input_length,
                        "completion_tokens": completion_tokens,
                        "total_tokens": input_length + completion_tokens,
                        "time_to_first_token": time_to_first_token,
                        "total_time": total_time,
                        "tokens_per_second": tokens_per_second,
                    }

                # Break if we hit a stop sequence
                if finish_reason == "stop":
                    break

                # Small sleep to allow other coroutines to run
                await asyncio.sleep(config.args.continuous_batching_microsleep)

        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise
        finally:
            # Ensure the generation thread completes
            if generation_thread.is_alive():
                generation_thread.join(timeout=1.0)

    def _handle_streaming_reasoning(
        self, new_text: str, full_text: str
    ) -> Tuple[str, Optional[str]]:
        """Handle reasoning content parsing during streaming"""
        # If reasoning parser is not enabled, just return the new text as-is
        if config.args.reasoning_parser != "deepseek_r1":
            return new_text, None

        # Check if we're currently in a thinking block
        if "<think>" in full_text and "</think>" not in full_text:
            # We're currently in a thinking block, don't output the content
            return "", None
        elif "<think>" in full_text and "</think>" in full_text:
            # Complete thinking block found
            if "</think>" in new_text:
                # This token completes the thinking block, extract reasoning
                clean_text, reasoning = self._parse_deepseek_r1_reasoning(full_text)
                return "", reasoning
            else:
                # Thinking block is complete, this might be content after it
                # For streaming, just return the new text if it doesn't contain think tags
                if "<think>" not in new_text and "</think>" not in new_text:
                    return new_text, None
                return "", None

        # Normal content - no thinking blocks involved
        return new_text, None

    def parse_reasoning_content(self, text: str) -> Tuple[str, Optional[str]]:
        """Parse reasoning content from text based on configured parser"""
        if config.args.reasoning_parser == "deepseek_r1":
            return self._parse_deepseek_r1_reasoning(text)
        return text, None

    def _parse_deepseek_r1_reasoning(self, text: str) -> Tuple[str, Optional[str]]:
        """Parse DeepSeek R1 reasoning content from <think> tags"""
        # More flexible pattern to match <think>...</think> with optional whitespace
        pattern = r"<think>\s*(.*?)\s*</think>\s*"
        match = re.search(pattern, text, re.DOTALL)

        if match:
            reasoning_content = match.group(1).strip()
            # Remove the thinking section from the main content
            clean_content = re.sub(pattern, "", text, flags=re.DOTALL).strip()
            return clean_content, reasoning_content

        return text, None


# Global model manager instance
model_manager = ModelManager()
