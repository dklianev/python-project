import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMService:
    def __init__(self):
        self.api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")
        self.model = os.getenv("LLM_MODEL", "llama3.2")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
    
    def get_response(self, user_message, chat_history=None):
        """
        Get a response from the LLM model via Ollama or OpenAI API
        
        Args:
            user_message: The user's message
            chat_history: Optional chat history for context
            
        Returns:
            The model's response
        """
        try:
            if self.model == "openai":
                # Use OpenAI API
                if not self.openai_api_key:
                    return "OpenAI API ключ не е намерен. Моля, добавете го в настройките."
                
                messages = self._format_messages_openai(user_message, chat_history)
                response = self._call_openai_api(messages)
            else:
                # Use Ollama API
                messages = self._format_messages_ollama(user_message, chat_history)
                response = self._call_ollama_api(messages)
            
            return response
        
        except Exception as e:
            print(f"Error calling LLM: {str(e)}")
            return f"Извинявам се, но възникна грешка при комуникацията с езиковия модел. Моля, опитайте отново по-късно. Грешка: {str(e)}"
    
    def _format_messages_ollama(self, user_message, chat_history=None):
        """Format the message history for Ollama API"""
        messages = []
        
        # If chat history is provided, include relevant context
        if chat_history:
            # Only include the last few messages to avoid token limits
            recent_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
            
            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                # Skip empty messages
                if not content.strip():
                    continue
                
                # Map roles to Ollama format
                if role == "user":
                    messages.append({"role": "user", "content": content})
                elif role == "assistant":
                    messages.append({"role": "assistant", "content": content})
        
        # Add the current message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _format_messages_openai(self, user_message, chat_history=None):
        """Format the message history for OpenAI API"""
        messages = []
        
        # System message
        messages.append({"role": "system", "content": "Ти си полезен български асистент."})
        
        # If chat history is provided, include relevant context
        if chat_history:
            # Only include the last few messages to avoid token limits
            recent_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
            
            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                # Skip empty messages
                if not content.strip():
                    continue
                
                # Add messages with appropriate roles
                if role in ["user", "assistant"]:
                    messages.append({"role": role, "content": content})
        
        # Add the current message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _call_ollama_api(self, messages):
        """Call the Ollama API with the formatted messages"""
        url = f"{self.api_url}/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1024,
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("message", {}).get("content", "")
        else:
            # Handle error
            error_msg = f"API Error: Status code {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail.get('error', '')}"
            except:
                pass
            
            raise Exception(error_msg)
    
    def _call_openai_api(self, messages):
        """Call the OpenAI API with the formatted messages"""
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            # Handle error
            error_msg = f"OpenAI API Error: Status code {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail.get('error', {}).get('message', '')}"
            except:
                pass
            
            raise Exception(error_msg)
    
    def change_model(self, model_name):
        """Change the LLM model"""
        self.model = model_name
        return True 