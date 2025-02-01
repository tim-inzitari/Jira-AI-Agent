import os
import ollama
import openai

class BaseLLMProvider:
    def chat(self, messages: list) -> dict:
        raise NotImplementedError("chat method not implemented")

class OllamaProvider(BaseLLMProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = ollama.Client(host=os.getenv('OLLAMA_HOST'))
        models = self.client.list()
        available_models = [m["model"].lower() for m in models["models"]]
        if self.model_name.lower() not in available_models:
            raise ValueError(f"Model {model_name} not available in Ollama")
    
    def chat(self, messages: list) -> dict:
        return self.client.chat(
            model=self.model_name,
            messages=messages
        )

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY must be set for OpenAI API")
    
    def chat(self, messages: list) -> dict:
        completion = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=messages,
            temperature=0
        )
        content = completion.choices[0].message.content
        # Wrap response so parsing logic remains unchanged
        wrapped_content = f"<answer>{content}</answer>"
        return {'message': {'content': wrapped_content}}