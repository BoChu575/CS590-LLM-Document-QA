# utils/llm_client.py
import requests
import json
from config import Config
import logging


class LLMClient:
    """Together AI client wrapper class"""

    def __init__(self, api_key=None):
        """Initialize LLM client"""
        self.api_key = api_key or Config.TOGETHER_API_KEY
        if not self.api_key:
            print("⚠️ Warning: Together AI API key not found. Please set TOGETHER_API_KEY in .env file")
            self.client = None
        else:
            try:
                # Set up API endpoint and headers
                self.api_url = "https://api.together.xyz/v1/chat/completions"
                self.headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                self.default_model = Config.DEFAULT_MODEL
                print("✅ Together AI client initialized successfully")
                self.client = True
            except Exception as e:
                print(f"❌ LLM client initialization failed: {str(e)}")
                self.client = None

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def generate_response(self, prompt, model=None, temperature=None, max_tokens=None):
        """Generate LLM response"""
        if not self.client:
            return "❌ API client not initialized, please check API key configuration"

        try:
            model = model or self.default_model
            temperature = temperature or Config.TEMPERATURE
            max_tokens = max_tokens or Config.MAX_TOKENS

            self.logger.info(f"Sending request to model: {model}")

            # Prepare request payload
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            # Make API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result_data = response.json()
                result = result_data['choices'][0]['message']['content']
                self.logger.info(f"Successfully got response, length: {len(result)} characters")
                return result
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                self.logger.error(error_msg)
                return f"❌ {error_msg}"

        except Exception as e:
            error_msg = f"API call failed: {str(e)}"
            self.logger.error(error_msg)
            return f"❌ {error_msg}"

    def summarize_text(self, text, max_length=200):
        """Text summarization function"""
        if not self.client:
            return "❌ Cannot generate summary: API client not initialized"

        prompt = f"""
Please generate a concise summary of the following text, no more than {max_length} words:

Text content:
{text}

Summary:
"""

        return self.generate_response(prompt, max_tokens=max_length + 50)

    def answer_question(self, context, question):
        """Answer questions based on context"""
        if not self.client:
            return "❌ Cannot answer question: API client not initialized"

        prompt = f"""
Based on the following document content, please answer the user's question. If the document doesn't contain relevant information, please state "No relevant information found in the document."

Document content:
{context}

User question: {question}

Answer:
"""

        return self.generate_response(prompt)

    def test_connection(self):
        """Test API connection"""
        if not self.client:
            return False, "API client not initialized"

        try:
            response = self.generate_response(
                "Please reply 'Connection test successful' to confirm the API is working.",
                max_tokens=50
            )
            if "❌" not in response:
                return True, response
            else:
                return False, response
        except Exception as e:
            return False, str(e)


# Test code
if __name__ == "__main__":
    print("🚀 Initializing Together AI client...")
    llm = LLMClient()

    if llm.client:
        print("🔗 Testing API connection...")
        success, response = llm.test_connection()

        if success:
            print(f"✅ Connection successful! Response: {response}")
        else:
            print(f"❌ Connection failed: {response}")
    else:
        print("⚠️ Client not initialized, please check API key configuration")