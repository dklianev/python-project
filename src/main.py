import os
import customtkinter as ctk
from dotenv import load_dotenv
import datetime
import json
import pyttsx3

# Local imports
from src.components.weather_widget import WeatherWidget
from src.components.notes_widget import NotesWidget
from src.components.todo_widget import TodoWidget
from src.components.calendar_widget import CalendarWidget
from src.components.chat_widget import ChatWidget
from src.components.pomodoro_widget import PomodoroWidget
from src.services.llm_service import LLMService
from src.utils.time_utils import get_greeting
from src.database.db_manager import DatabaseManager

# Load environment variables
load_dotenv()

class AssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure the main window
        self.title("Персонален Асистент")
        self.geometry("1200x800")
        
        # Set theme
        ctk.set_appearance_mode("dark")  # Options: "dark", "light"
        ctk.set_default_color_theme("blue")
        
        # Initialize LLM service
        self.llm = LLMService()
        
        # Setup text-to-speech engine
        self.tts_engine = pyttsx3.init()
        
        # Create sidebar and main content area
        self.create_layout()
        
        # Greet the user
        self.greet_user()
        
    def create_layout(self):
        # Create sidebar frame
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        # App logo/name
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Персонален\nАсистент", 
                                     font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=20)
        
        # Sidebar buttons
        sidebar_options = [
            "Начало", "Чат", "Бележки", "Задачи", "Календар", "Pomodoro", "Настройки"
        ]
        
        self.sidebar_buttons = []
        for option in sidebar_options:
            button = ctk.CTkButton(self.sidebar, text=option, 
                                  command=lambda o=option: self.show_frame(o))
            button.pack(pady=10, padx=20, fill="x")
            self.sidebar_buttons.append(button)
        
        # Theme switch
        self.theme_switch = ctk.CTkSwitch(self.sidebar, text="Тъмна тема", 
                                       command=self.toggle_theme)
        self.theme_switch.pack(pady=10, padx=20, side="bottom")
        self.theme_switch.select()  # Default to dark theme
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(side="right", fill="both", expand=True)
        
        # Create frames for each section
        self.frames = {}
        for option in sidebar_options:
            frame = ctk.CTkFrame(self.main_frame)
            self.frames[option] = frame
            
        # Initialize widgets in each frame
        self.init_home_frame()
        self.init_chat_frame()
        self.init_notes_frame()
        self.init_todo_frame()
        self.init_calendar_frame()
        self.init_pomodoro_frame()
        self.init_settings_frame()
        
        # Show default frame
        self.show_frame("Начало")
        
    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Show selected frame
        self.frames[frame_name].pack(fill="both", expand=True, padx=20, pady=20)
    
    def init_home_frame(self):
        frame = self.frames["Начало"]
        
        # Greeting label
        self.greeting_label = ctk.CTkLabel(frame, 
                                         text=get_greeting(), 
                                         font=ctk.CTkFont(size=28, weight="bold"))
        self.greeting_label.pack(pady=20)
        
        # Date and time
        self.datetime_label = ctk.CTkLabel(frame, 
                                         text=datetime.datetime.now().strftime("%d %B %Y, %H:%M"),
                                         font=ctk.CTkFont(size=16))
        self.datetime_label.pack(pady=10)
        
        # Weather widget
        self.weather_widget = WeatherWidget(frame)
        self.weather_widget.pack(pady=20, fill="x")
        
        # Quote of the day
        self.quote_frame = ctk.CTkFrame(frame)
        self.quote_frame.pack(pady=20, fill="x")
        
        self.quote_label = ctk.CTkLabel(self.quote_frame, 
                                      text="\"Най-добрият начин да предскажеш бъдещето е да го създадеш.\"",
                                      font=ctk.CTkFont(size=14, slant="italic"))
        self.quote_label.pack(pady=10)
        
        self.quote_author = ctk.CTkLabel(self.quote_frame, 
                                       text="- Питър Дракър",
                                       font=ctk.CTkFont(size=12))
        self.quote_author.pack(pady=5)
    
    def init_chat_frame(self):
        frame = self.frames["Чат"]
        self.chat_widget = ChatWidget(frame, self.llm)
        self.chat_widget.pack(fill="both", expand=True)
    
    def init_notes_frame(self):
        frame = self.frames["Бележки"]
        self.notes_widget = NotesWidget(frame)
        self.notes_widget.pack(fill="both", expand=True)
    
    def init_todo_frame(self):
        frame = self.frames["Задачи"]
        self.todo_widget = TodoWidget(frame)
        self.todo_widget.pack(fill="both", expand=True)
    
    def init_calendar_frame(self):
        frame = self.frames["Календар"]
        self.calendar_widget = CalendarWidget(frame)
        self.calendar_widget.pack(fill="both", expand=True)
    
    def init_pomodoro_frame(self):
        frame = self.frames["Pomodoro"]
        self.pomodoro_widget = PomodoroWidget(frame)
        self.pomodoro_widget.pack(fill="both", expand=True)
    
    def init_settings_frame(self):
        frame = self.frames["Настройки"]
        
        settings_label = ctk.CTkLabel(frame, text="Настройки", 
                                    font=ctk.CTkFont(size=24, weight="bold"))
        settings_label.pack(pady=20)
        
        # LLM Model selection
        llm_frame = ctk.CTkFrame(frame)
        llm_frame.pack(fill="x", pady=10)
        
        llm_label = ctk.CTkLabel(llm_frame, text="LLM Модел:")
        llm_label.pack(side="left", padx=10)
        
        llm_options = ["llama3.2", "mistral", "phi3", "openai"]
        self.llm_var = ctk.StringVar(value=os.getenv("LLM_MODEL", "llama3.2"))
        
        llm_dropdown = ctk.CTkOptionMenu(llm_frame, values=llm_options, 
                                       variable=self.llm_var,
                                       command=self.change_llm_model)
        llm_dropdown.pack(side="left", padx=10)
        
        # Weather API key
        api_frame = ctk.CTkFrame(frame)
        api_frame.pack(fill="x", pady=10)
        
        api_label = ctk.CTkLabel(api_frame, text="OpenWeather API ключ:")
        api_label.pack(side="left", padx=10)
        
        self.api_entry = ctk.CTkEntry(api_frame, width=300)
        self.api_entry.pack(side="left", padx=10)
        self.api_entry.insert(0, os.getenv("OPENWEATHER_API_KEY", ""))
        
        api_save = ctk.CTkButton(api_frame, text="Запази", command=self.save_api_key)
        api_save.pack(side="left", padx=10)
        
        # OpenAI API key
        openai_frame = ctk.CTkFrame(frame)
        openai_frame.pack(fill="x", pady=10)
        
        openai_label = ctk.CTkLabel(openai_frame, text="OpenAI API ключ:")
        openai_label.pack(side="left", padx=10)
        
        self.openai_entry = ctk.CTkEntry(openai_frame, width=300, show="*")
        self.openai_entry.pack(side="left", padx=10)
        self.openai_entry.insert(0, os.getenv("OPENAI_API_KEY", ""))
        
        openai_save = ctk.CTkButton(openai_frame, text="Запази", command=self.save_openai_key)
        openai_save.pack(side="left", padx=10)
    
    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
    
    def greet_user(self):
        greeting = get_greeting()
        # TTS greeting
        self.tts_engine.say(greeting)
        self.tts_engine.runAndWait()
    
    def change_llm_model(self, model_name):
        self.llm.change_model(model_name)
        # Update the model display in chat widget if it exists
        if hasattr(self, "chat_widget"):
            self.chat_widget.model_label.configure(text=f"Модел: {model_name}")
    
    def save_api_key(self):
        # In a real app, this would update the .env file or a config file
        api_key = self.api_entry.get()
        os.environ["OPENWEATHER_API_KEY"] = api_key
        
        # Refresh weather data
        self.weather_widget.refresh_weather()
        
    def save_openai_key(self):
        openai_key = self.openai_entry.get()
        os.environ["OPENAI_API_KEY"] = openai_key
        
        # Update the LLM service with the new key
        self.llm.openai_api_key = openai_key

if __name__ == "__main__":
    app = AssistantApp()
    app.mainloop() 