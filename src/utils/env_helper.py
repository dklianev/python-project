"""
Environment configuration helper for the Personal Assistant.
"""

import os
from typing import Dict, List, Tuple
from dotenv import load_dotenv


def load_and_validate_env() -> Tuple[bool, List[str]]:
    """
    Load environment variables and validate them.
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    load_dotenv()
    
    issues = []
    
    # Check OpenWeather API key
    openweather_key = os.getenv("OPENWEATHER_API_KEY", "")
    if not openweather_key or openweather_key == "your_openweather_api_key_here":
        issues.append("⚠️  OpenWeather API ключ не е конфигуриран")
    
    # Check OpenAI API key (optional)
    openai_key = os.getenv("OPENAI_API_KEY", "")
    llm_model = os.getenv("LLM_MODEL", "llama3.2")
    if llm_model == "openai" and (not openai_key or openai_key == "your_openai_api_key_here"):
        issues.append("⚠️  OpenAI API ключ е нужен за избрания модел")
    
    # Check Ollama URL
    ollama_url = os.getenv("OLLAMA_API_URL", "")
    if not ollama_url:
        issues.append("⚠️  Ollama API URL не е конфигуриран")
    
    return len(issues) == 0, issues


def get_api_status() -> Dict[str, str]:
    """
    Get the status of API keys.
    
    Returns:
        Dictionary with API status information
    """
    load_dotenv()
    
    status = {}
    
    # OpenWeather
    openweather_key = os.getenv("OPENWEATHER_API_KEY", "")
    if not openweather_key or openweather_key == "your_openweather_api_key_here":
        status["openweather"] = "❌ Не е конфигуриран"
    else:
        status["openweather"] = "✅ Конфигуриран"
    
    # OpenAI
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key or openai_key == "your_openai_api_key_here":
        status["openai"] = "❌ Не е конфигуриран"
    else:
        status["openai"] = "✅ Конфигуриран"
    
    # LLM Model
    llm_model = os.getenv("LLM_MODEL", "llama3.2")
    status["llm_model"] = f"🤖 {llm_model}"
    
    return status


def create_env_instructions() -> str:
    """
    Create instructions for setting up environment variables.
    
    Returns:
        Formatted instructions string
    """
    instructions = """
📋 Инструкции за настройка на API ключове:

1. 🌤️  OpenWeather API (за информация за времето):
   • Отидете на: https://openweathermap.org/api
   • Регистрирайте се безплатно
   • Получете вашия API ключ
   • Заменете 'your_openweather_api_key_here' в .env файла

2. 🤖 OpenAI API (ако искате да използвате ChatGPT):
   • Отидете на: https://platform.openai.com/api-keys
   • Влезте с вашия акаунт
   • Създайте нов API ключ
   • Заменете 'your_openai_api_key_here' в .env файла

3. 🦙 Ollama (за локални модели):
   • Инсталирайте Ollama от: https://ollama.ai
   • Стартирайте Ollama сървъра
   • Изтеглете модел: ollama pull llama3.2

📝 След промените рестартирайте приложението.
"""
    return instructions


def check_env_file() -> bool:
    """
    Check if .env file exists.
    
    Returns:
        True if .env file exists, False otherwise
    """
    return os.path.exists(".env")


def print_env_status():
    """Print current environment status to console."""
    if not check_env_file():
        print("❌ .env файлът не съществува")
        print("💡 Стартирайте приложението с 'python run.py' за автоматично създаване")
        return
    
    is_valid, issues = load_and_validate_env()
    status = get_api_status()
    
    print("\n📊 Статус на API конфигурацията:")
    print("=" * 40)
    
    for service, stat in status.items():
        print(f"{service.capitalize()}: {stat}")
    
    if issues:
        print("\n⚠️  Проблеми:")
        for issue in issues:
            print(f"  {issue}")
        
        print(create_env_instructions())
    else:
        print("\n✅ Всички API ключове са конфигурирани правилно!") 