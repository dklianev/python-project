import os
import requests
import json
import customtkinter as ctk
from PIL import Image, ImageTk
import datetime


class WeatherWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(corner_radius=10)
        
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.location = "София,BG"  # Default location
        
        # Weather display
        self.location_frame = ctk.CTkFrame(self)
        self.location_frame.pack(pady=10, padx=10, fill="x")
        
        self.location_label = ctk.CTkLabel(self.location_frame, text="Местоположение:", 
                                         font=ctk.CTkFont(size=14))
        self.location_label.pack(side="left", padx=5)
        
        self.location_entry = ctk.CTkEntry(self.location_frame, width=200)
        self.location_entry.pack(side="left", padx=5)
        self.location_entry.insert(0, self.location)
        
        self.search_button = ctk.CTkButton(self.location_frame, text="Търси", 
                                         command=self.refresh_weather)
        self.search_button.pack(side="left", padx=5)
        
        # Weather info display
        self.weather_frame = ctk.CTkFrame(self)
        self.weather_frame.pack(pady=10, padx=10, fill="x")
        
        # Temperature and condition
        self.temp_label = ctk.CTkLabel(self.weather_frame, text="--°C", 
                                     font=ctk.CTkFont(size=36, weight="bold"))
        self.temp_label.pack(side="left", padx=20)
        
        self.condition_label = ctk.CTkLabel(self.weather_frame, text="--", 
                                          font=ctk.CTkFont(size=14))
        self.condition_label.pack(side="left", padx=10)
        
        # Additional info
        self.details_frame = ctk.CTkFrame(self)
        self.details_frame.pack(pady=5, padx=10, fill="x")
        
        # Humidity
        self.humidity_label = ctk.CTkLabel(self.details_frame, text="Влажност: --%", 
                                         font=ctk.CTkFont(size=12))
        self.humidity_label.pack(side="left", padx=10)
        
        # Wind
        self.wind_label = ctk.CTkLabel(self.details_frame, text="Вятър: -- м/с", 
                                     font=ctk.CTkFont(size=12))
        self.wind_label.pack(side="left", padx=10)
        
        # Fetch weather if API key is available
        if self.api_key:
            self.refresh_weather()
        else:
            self.show_api_missing()
    
    def refresh_weather(self):
        self.location = self.location_entry.get()
        
        if not self.api_key:
            self.show_api_missing()
            return
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={self.location}&appid={self.api_key}&units=metric&lang=bg"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                # Update temperature
                temp = round(data['main']['temp'])
                self.temp_label.configure(text=f"{temp}°C")
                
                # Update condition
                condition = data['weather'][0]['description'].capitalize()
                self.condition_label.configure(text=condition)
                
                # Update humidity
                humidity = data['main']['humidity']
                self.humidity_label.configure(text=f"Влажност: {humidity}%")
                
                # Update wind
                wind = data['wind']['speed']
                self.wind_label.configure(text=f"Вятър: {wind} м/с")
            else:
                self.show_error(f"Грешка: {data.get('message', 'Unknown error')}")
        
        except Exception as e:
            self.show_error(f"Грешка при извличане на данни за времето: {str(e)}")
    
    def show_api_missing(self):
        self.temp_label.configure(text="--°C")
        self.condition_label.configure(text="API ключ не е намерен")
        self.humidity_label.configure(text="Влажност: --%")
        self.wind_label.configure(text="Вятър: -- м/с")
    
    def show_error(self, message):
        self.temp_label.configure(text="--°C")
        self.condition_label.configure(text=message)
        self.humidity_label.configure(text="Влажност: --%")
        self.wind_label.configure(text="Вятър: -- м/с") 