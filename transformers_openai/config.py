import argparse
import os


class Config:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Configuration parser")
        self._add_arguments()
        self.args = self.parser.parse_args()
    
    def _add_arguments(self):
        self.parser.add_argument(
            "--host", 
            type=str, 
            default=os.getenv("HOSTNAME", "0.0.0.0"),
            help="host name to host the app (default: 0.0.0.0, env: HOSTNAME)"
        )
        self.parser.add_argument(
            "--port", 
            type=int, 
            default=int(os.getenv("PORT", 7088)),
            help="port to host the app (default: 7088, env: PORT)"
        )
        self.parser.add_argument(
            "--loglevel", 
            type=str, 
            default=os.getenv("LOGLEVEL", "INFO"),
            help="Logging level (default: INFO, env: LOGLEVEL)"
        )
        self.parser.add_argument(
            "--model-type", 
            type=str, 
            default=os.getenv("MODEL_TYPE", "AutoModelForCausalLM"),
            help="Model type (default: AutoModelForCausalLM, env: MODEL_TYPE)"
        )
        self.parser.add_argument(
            "--tokenizer-type", 
            type=str, 
            default=os.getenv("TOKENIZER_TYPE", "AutoTokenizer"),
            help="Tokenizer type (default: AutoTokenizer, env: TOKENIZER_TYPE)"
        )
        self.parser.add_argument(
            "--tokenizer-use-fast", 
            type=bool, 
            default=os.getenv("TOKENIZER_USE_FAST", "True").lower() == "true",
            help="Use fast tokenizer (default: True, env: TOKENIZER_USE_FAST)"
        )
        self.parser.add_argument(
            "--processor-type", 
            type=str, 
            default=os.getenv("PROCESSOR_TYPE", "AutoTokenizer"),
            help="Processor type (default: AutoTokenizer, env: PROCESSOR_TYPE)"
        )
        self.parser.add_argument(
            "--hf-model", 
            type=str, 
            default=os.getenv("HF_MODEL", "mesolitica/malaysian-llama2-7b-32k-instructions"),
            help="Hugging Face model (default: mesolitica/malaysian-llama2-7b-32k-instructions, env: HF_MODEL)"
        )
        self.parser.add_argument(
            "--torch-dtype", 
            type=str, 
            default=os.getenv("TORCH_DTYPE", "bfloat16"),
            help="Torch data type (default: bfloat16, env: TORCH_DTYPE)"
        )
        self.parser.add_argument(
            "--architecture-type", 
            type=str, 
            choices=["decoder", "encoder-decoder"],
            default=os.getenv("ARCHITECTURE_TYPE", "decoder"),
            help="Architecture type (default: decoder, env: ARCHITECTURE_TYPE)"
        )
        self.parser.add_argument(
            "--serving-type", 
            type=str, 
            choices=["chat", "whisper"],
            default=os.getenv("SERVING_TYPE", "chat"),
            help="Serving type (default: chat, env: SERVING_TYPE)"
        )
        self.parser.add_argument(
            "--continuous-batching-microsleep", 
            type=float, 
            default=float(os.getenv("CONTINUOUS_BATCHING_MICROSLEEP", 0.001)),
            help="microsleep to group continuous batching, 1 / 1e-4 = 10k steps for one second (default: 0.001, env: CONTINUOUS_BATCHING_MICROSLEEP)"
        )
        self.parser.add_argument(
            "--continuous-batching-batch-size", 
            type=int, 
            default=int(os.getenv("CONTINUOUS_BATCHING_BATCH_SIZE", 20)),
            help="maximum of batch size during continuous batching (default: 20, env: CONTINUOUS_BATCHING_BATCH_SIZE)"
        )
        self.parser.add_argument(
            "--static-cache", 
            type=bool, 
            default=os.getenv("STATIC_CACHE", "False").lower() == "true",
            help="Preallocate KV Cache for faster inference (default: False, env: STATIC_CACHE)"
        )
        self.parser.add_argument(
            "--static-cache-encoder-max-length", 
            type=int, 
            default=int(os.getenv("STATIC_CACHE_ENCODER_MAX_LENGTH", 256)),
            help="Maximum concurrent requests (default: 256, env: STATIC_CACHE_ENCODER_MAX_LENGTH)"
        )
        self.parser.add_argument(
            "--static-cache-decoder-max-length", 
            type=int, 
            default=int(os.getenv("STATIC_CACHE_DECODER_MAX_LENGTH", 256)),
            help="Maximum concurrent requests (default: 256, env: STATIC_CACHE_DECODER_MAX_LENGTH)"
        )
        self.parser.add_argument(
            "--accelerator-type", 
            type=str, 
            default=os.getenv("ACCELERATOR_TYPE", "cuda"),
            help="Accelerator type (default: cuda, env: ACCELERATOR_TYPE)"
        )
        self.parser.add_argument(
            "--max-concurrent", 
            type=int, 
            default=int(os.getenv("MAX_CONCURRENT", 100)),
            help="Maximum concurrent requests (default: 100, env: MAX_CONCURRENT)"
        )
        self.parser.add_argument(
            "--torch-profiling", 
            type=bool, 
            default=os.getenv("TORCH_PROFILING", "False").lower() == "true",
            help="Use torch.autograd.profiler.profile() to profile prefill and step (default: False, env: TORCH_PROFILING)"
        )
        self.parser.add_argument(
            "--hqq", 
            type=bool, 
            default=os.getenv("HQQ", "False").lower() == "true",
            help="int4 quantization using HQQ (default: False, env: HQQ)"
        )
        self.parser.add_argument(
            "--torch-compile", 
            type=bool, 
            default=os.getenv("TORCH_COMPILE", "False").lower() == "true",
            help="Torch compile necessary forwards, can speed up at least 1.5X (default: False, env: TORCH_COMPILE)"
        )
        self.parser.add_argument(
            "--torch-compile-mode", 
            type=str, 
            default=os.getenv("TORCH_COMPILE_MODE", "reduce-overhead"),
            help="torch compile type (default: reduce-overhead, env: TORCH_COMPILE_MODE)"
        )
        self.parser.add_argument(
            "--reasoning-parser", 
            type=str, 
            choices=["none", "deepseek_r1"],
            default=os.getenv("REASONING_PARSER", "none"),
            help="Reasoning parser type to extract thinking content (default: none, env: REASONING_PARSER)"
        )


config = Config()
