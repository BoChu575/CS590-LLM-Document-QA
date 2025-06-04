import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
   # API configuration
   TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')

   # Model configuration - using Together AI available models
   DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
   AVAILABLE_MODELS = [
       "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
       "meta-llama/Llama-3.3-70B-Instruct-Turbo",
       "mistralai/Mixtral-8x7B-Instruct-v0.1",
       "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
       "Qwen/Qwen2.5-72B-Instruct-Turbo",
       "google/gemma-2b-it"
   ]

   # Text processing configuration
   MAX_TOKENS = 4000
   TEMPERATURE = 0.1

   # Application configuration
   APP_TITLE = "LLM Document Summarization and Q&A System"
   MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

   # Supported file types
   SUPPORTED_FILE_TYPES = ['pdf', 'txt', 'docx']