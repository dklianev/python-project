#!/usr/bin/env python

"""
Персонален Десктоп Асистент - стартиращ скрипт

Този скрипт стартира приложението и извършва предварителна проверка 
на изискванията и зависимостите.
"""

import os
import sys
import platform
import subprocess
import importlib
import time

REQUIRED_PACKAGES = [
    "customtkinter",
    "requests",
    "pytz",
    "pyttsx3",
    "pillow",
    "ollama",
    "python-dotenv",
    "tkcalendar"
]

def check_dependencies():
    """Проверка дали всички необходими пакети са инсталирани"""
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Липсващи зависимости:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        
        # Ask if want to install
        answer = input("Искате ли да инсталирате липсващите пакети? (y/n): ")
        if answer.lower() == 'y':
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
                print("Успешно инсталирани пакети!")
            except subprocess.CalledProcessError:
                print("Грешка при инсталация на пакетите. Моля, инсталирайте ръчно:")
                print(f"pip install {' '.join(missing_packages)}")
                return False
        else:
            print("Моля, инсталирайте липсващите пакети и опитайте отново.")
            return False
    
    return True

def check_ollama():
    """Проверка дали Ollama е инсталиран и работи"""
    try:
        # Try to import the ollama module
        import ollama
        
        print("Проверка на връзката с Ollama сървъра...")
        # Call the Ollama API to check if it's running
        try:
            import requests
            response = requests.get("http://localhost:11434/api/version", timeout=2)
            if response.status_code == 200:
                version = response.json().get("version", "Unknown")
                print(f"Ollama сървър е активен (версия {version}).")
                return True
        except:
            print("Грешка при свързване с Ollama сървъра.")
            print("Моля, уверете се, че Ollama е инсталиран и стартиран:")
            print("1. Изтеглете от https://ollama.ai/")
            print("2. Инсталирайте и стартирайте Ollama")
            print("3. Изпълнете 'ollama pull llama3.2' за да изтеглите необходимия модел")
            return False
    
    except ImportError:
        print("Ollama Python пакет не е инсталиран.")
        return False
    
    return True

def check_env():
    """Проверка за .env файл и създаване ако не съществува"""
    if not os.path.exists(".env"):
        print("Създаване на .env файл с настройки по подразбиране...")
        with open(".env", "w", encoding="utf-8") as f:
            f.write("OPENWEATHER_API_KEY=your_api_key_here\n")
            f.write("OLLAMA_API_URL=http://localhost:11434/api\n")
            f.write("LLM_MODEL=llama3.2\n")
            f.write("OPENAI_API_KEY=\n")
        print("Създаден .env файл. Моля, редактирайте го с вашите настройки.")

def check_directories():
    """Проверка за необходимите директории"""
    dirs = ["data", "src/assets"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def main():
    """Основна функция за стартиране на приложението"""
    print("=" * 60)
    print("Персонален Десктоп Асистент - стартиране")
    print("=" * 60)
    
    # Checks
    print("\n[1/4] Проверка на зависимостите...")
    if not check_dependencies():
        sys.exit(1)
    
    print("\n[2/4] Проверка на Ollama...")
    # Uncomment to enable Ollama check
    # if not check_ollama():
    #     sys.exit(1)
    
    print("\n[3/4] Проверка на конфигурацията...")
    check_env()
    
    print("\n[4/4] Проверка на директориите...")
    check_directories()
    
    print("\nСтартиране на приложението...")
    from src.main import AssistantApp
    
    app = AssistantApp()
    app.mainloop()

if __name__ == "__main__":
    main() 