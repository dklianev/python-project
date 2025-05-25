"""
Configuration file for the Personal Assistant application.
Contains default settings and constants.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application settings
APP_NAME = "Персонален Асистент"
APP_VERSION = "1.0.0"
DEFAULT_WINDOW_SIZE = "1200x800"

# Database settings
DATABASE_PATH = "data/assistant.db"
JSON_DATA_DIR = "data"

# API settings
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# LLM settings
DEFAULT_LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
AVAILABLE_MODELS = ["llama3.2", "mistral", "phi3", "openai"]

# UI settings
DEFAULT_THEME = "dark"
SIDEBAR_WIDTH = 200

# Weather settings
DEFAULT_LOCATION = "София,BG"

# Pomodoro settings
DEFAULT_WORK_TIME = 25  # minutes
DEFAULT_BREAK_TIME = 5  # minutes
DEFAULT_LONG_BREAK_TIME = 15  # minutes

# Request timeouts
API_TIMEOUT = 30
WEATHER_TIMEOUT = 10

# File paths
ASSETS_DIR = "src/assets"
COMPONENTS_DIR = "src/components"
SERVICES_DIR = "src/services"
UTILS_DIR = "src/utils" 