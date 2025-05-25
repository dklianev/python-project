import customtkinter as ctk
import time
import threading
import json
import os
from datetime import datetime, timedelta


class PomodoroWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Default settings
        self.pomodoro_length = 25 * 60  # 25 minutes in seconds
        self.short_break_length = 5 * 60  # 5 minutes
        self.long_break_length = 15 * 60  # 15 minutes
        self.pomodoros_until_long_break = 4
        
        # State variables
        self.timer_running = False
        self.timer_paused = False
        self.current_mode = "pomodoro"  # pomodoro, short_break, long_break
        self.current_count = 0
        self.completed_pomodoros = 0
        self.remaining_seconds = self.pomodoro_length
        self.timer_thread = None
        
        # Stats file
        self.stats_file = "data/pomodoro_stats.json"
        self.stats = {"completed_pomodoros": 0, "total_focus_time": 0, "sessions": []}
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
        
        # Load stats
        self.load_stats()
        
        # Create header
        self.header_label = ctk.CTkLabel(self, text="Pomodoro Таймер", 
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(pady=10)
        
        # Timer display
        self.timer_frame = ctk.CTkFrame(self)
        self.timer_frame.pack(pady=20, padx=20, fill="x")
        
        self.timer_label = ctk.CTkLabel(self.timer_frame, text="25:00", 
                                      font=ctk.CTkFont(size=64, weight="bold"))
        self.timer_label.pack(pady=20)
        
        # Progress frame with labels for completed pomodoros
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, 
                                        text=f"Завършени pomodoros: {self.completed_pomodoros}/{self.pomodoros_until_long_break}")
        self.progress_label.pack(side="left", padx=10)
        
        # Mode buttons
        self.mode_frame = ctk.CTkFrame(self)
        self.mode_frame.pack(fill="x", padx=20, pady=10)
        
        self.pomodoro_button = ctk.CTkButton(self.mode_frame, text="Pomodoro",
                                          command=lambda: self.change_mode("pomodoro"))
        self.pomodoro_button.pack(side="left", expand=True, fill="x", padx=5)
        
        self.short_break_button = ctk.CTkButton(self.mode_frame, text="Кратка почивка",
                                            command=lambda: self.change_mode("short_break"))
        self.short_break_button.pack(side="left", expand=True, fill="x", padx=5)
        
        self.long_break_button = ctk.CTkButton(self.mode_frame, text="Дълга почивка",
                                           command=lambda: self.change_mode("long_break"))
        self.long_break_button.pack(side="left", expand=True, fill="x", padx=5)
        
        # Control buttons
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(fill="x", padx=20, pady=20)
        
        self.start_button = ctk.CTkButton(self.control_frame, text="Старт", 
                                        command=self.start_timer,
                                        fg_color="#4CAF50", hover_color="#388E3C")
        self.start_button.pack(side="left", expand=True, fill="x", padx=5)
        
        self.pause_button = ctk.CTkButton(self.control_frame, text="Пауза", 
                                        command=self.pause_timer,
                                        state="disabled", 
                                        fg_color="#FF9800", hover_color="#F57C00")
        self.pause_button.pack(side="left", expand=True, fill="x", padx=5)
        
        self.reset_button = ctk.CTkButton(self.control_frame, text="Нулиране", 
                                       command=self.reset_timer,
                                       fg_color="#F44336", hover_color="#D32F2F")
        self.reset_button.pack(side="left", expand=True, fill="x", padx=5)
        
        # Settings
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(fill="x", padx=20, pady=10)
        
        self.settings_label = ctk.CTkLabel(self.settings_frame, text="Настройки", 
                                        font=ctk.CTkFont(weight="bold"))
        self.settings_label.pack(pady=5)
        
        # Time settings
        self.time_settings_frame = ctk.CTkFrame(self.settings_frame)
        self.time_settings_frame.pack(fill="x", padx=10, pady=5)
        
        # Pomodoro length
        self.pomodoro_length_frame = ctk.CTkFrame(self.time_settings_frame)
        self.pomodoro_length_frame.pack(fill="x", pady=5)
        
        self.pomodoro_length_label = ctk.CTkLabel(self.pomodoro_length_frame, text="Фокус време (минути):")
        self.pomodoro_length_label.pack(side="left", padx=5)
        
        self.pomodoro_length_var = ctk.StringVar(value="25")
        self.pomodoro_length_entry = ctk.CTkEntry(self.pomodoro_length_frame, width=50, 
                                              textvariable=self.pomodoro_length_var)
        self.pomodoro_length_entry.pack(side="right", padx=5)
        
        # Short break length
        self.short_break_frame = ctk.CTkFrame(self.time_settings_frame)
        self.short_break_frame.pack(fill="x", pady=5)
        
        self.short_break_label = ctk.CTkLabel(self.short_break_frame, text="Кратка почивка (минути):")
        self.short_break_label.pack(side="left", padx=5)
        
        self.short_break_var = ctk.StringVar(value="5")
        self.short_break_entry = ctk.CTkEntry(self.short_break_frame, width=50, 
                                           textvariable=self.short_break_var)
        self.short_break_entry.pack(side="right", padx=5)
        
        # Long break length
        self.long_break_frame = ctk.CTkFrame(self.time_settings_frame)
        self.long_break_frame.pack(fill="x", pady=5)
        
        self.long_break_label = ctk.CTkLabel(self.long_break_frame, text="Дълга почивка (минути):")
        self.long_break_label.pack(side="left", padx=5)
        
        self.long_break_var = ctk.StringVar(value="15")
        self.long_break_entry = ctk.CTkEntry(self.long_break_frame, width=50, 
                                          textvariable=self.long_break_var)
        self.long_break_entry.pack(side="right", padx=5)
        
        # Pomodoros until long break
        self.pomodoros_frame = ctk.CTkFrame(self.time_settings_frame)
        self.pomodoros_frame.pack(fill="x", pady=5)
        
        self.pomodoros_label = ctk.CTkLabel(self.pomodoros_frame, text="Pomodoros до дълга почивка:")
        self.pomodoros_label.pack(side="left", padx=5)
        
        self.pomodoros_var = ctk.StringVar(value="4")
        self.pomodoros_entry = ctk.CTkEntry(self.pomodoros_frame, width=50, 
                                         textvariable=self.pomodoros_var)
        self.pomodoros_entry.pack(side="right", padx=5)
        
        # Apply settings button
        self.apply_button = ctk.CTkButton(self.settings_frame, text="Приложи настройките", 
                                       command=self.apply_settings)
        self.apply_button.pack(pady=10)
        
        # Stats section
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.stats_label = ctk.CTkLabel(self.stats_frame, text="Статистика", 
                                     font=ctk.CTkFont(weight="bold"))
        self.stats_label.pack(pady=5)
        
        self.total_pomodoros_label = ctk.CTkLabel(self.stats_frame, 
                                             text=f"Общо завършени pomodoros: {self.stats['completed_pomodoros']}")
        self.total_pomodoros_label.pack(fill="x", padx=5)
        
        hours = self.stats['total_focus_time'] // 3600
        minutes = (self.stats['total_focus_time'] % 3600) // 60
        self.total_time_label = ctk.CTkLabel(self.stats_frame, 
                                          text=f"Общо фокус време: {hours}ч {minutes}м")
        self.total_time_label.pack(fill="x", padx=5)
        
        # Listen to window close event
        self.bind("<Destroy>", self.on_close)
        
        # Update the timer display
        self.update_timer_display()
        self.highlight_active_mode()
    
    def load_stats(self):
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            else:
                self.stats = {"completed_pomodoros": 0, "total_focus_time": 0, "sessions": []}
        except Exception as e:
            print(f"Грешка при зареждане на pomodoro статистика: {e}")
            self.stats = {"completed_pomodoros": 0, "total_focus_time": 0, "sessions": []}
    
    def save_stats(self):
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Грешка при запазване на pomodoro статистика: {e}")
    
    def start_timer(self):
        if self.timer_paused:
            # Resume timer
            self.timer_paused = False
            self.start_button.configure(state="disabled")
            self.pause_button.configure(state="normal")
        elif not self.timer_running:
            # Start new timer
            self.timer_running = True
            self.start_button.configure(state="disabled")
            self.pause_button.configure(state="normal")
            
            # Start timer thread
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
            self.timer_thread.start()
    
    def pause_timer(self):
        if self.timer_running:
            self.timer_paused = True
            self.pause_button.configure(state="disabled")
            self.start_button.configure(state="normal", text="Продължи")
    
    def reset_timer(self):
        # Stop any running timer
        self.timer_running = False
        self.timer_paused = False
        
        # Reset to current mode's default time
        self.set_time_for_current_mode()
        
        # Reset UI
        self.start_button.configure(state="normal", text="Старт")
        self.pause_button.configure(state="disabled")
        self.update_timer_display()
    
    def run_timer(self):
        start_time = datetime.now()
        last_second = self.remaining_seconds
        
        while self.timer_running and self.remaining_seconds > 0:
            if not self.timer_paused:
                # Calculate elapsed time
                elapsed = (datetime.now() - start_time).total_seconds()
                self.remaining_seconds = max(0, last_second - int(elapsed))
                
                # Update UI from the main thread
                self.after(0, self.update_timer_display)
            
            # Sleep briefly to avoid high CPU usage
            time.sleep(0.1)
        
        # Only proceed if timer completed (not reset)
        if self.timer_running and self.remaining_seconds == 0:
            # Update UI from the main thread
            self.after(0, self.timer_completed)
    
    def timer_completed(self):
        # Play notification sound (could be implemented with pygame or other libraries)
        print("Timer completed!")
        
        # Update stats for completed pomodoro
        if self.current_mode == "pomodoro":
            self.completed_pomodoros += 1
            self.stats['completed_pomodoros'] += 1
            self.stats['total_focus_time'] += self.pomodoro_length
            
            # Add session record
            session = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "duration": self.pomodoro_length
            }
            self.stats['sessions'].append(session)
            
            # Save stats
            self.save_stats()
            
            # Update stats display
            self.update_stats_display()
        
        # Update UI
        self.update_progress_display()
        
        # Automatically switch to the next mode
        if self.current_mode == "pomodoro":
            # Check if it's time for a long break
            if self.completed_pomodoros % self.pomodoros_until_long_break == 0:
                self.change_mode("long_break")
            else:
                self.change_mode("short_break")
        else:
            # After a break, start next pomodoro
            self.change_mode("pomodoro")
        
        # Reset timer state
        self.timer_running = False
        self.start_button.configure(state="normal", text="Старт")
        self.pause_button.configure(state="disabled")
    
    def change_mode(self, mode):
        self.current_mode = mode
        self.reset_timer()
        self.highlight_active_mode()
    
    def set_time_for_current_mode(self):
        if self.current_mode == "pomodoro":
            self.remaining_seconds = self.pomodoro_length
        elif self.current_mode == "short_break":
            self.remaining_seconds = self.short_break_length
        else:  # long_break
            self.remaining_seconds = self.long_break_length
    
    def update_timer_display(self):
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")
    
    def update_progress_display(self):
        self.progress_label.configure(
            text=f"Завършени pomodoros: {self.completed_pomodoros}/{self.pomodoros_until_long_break}"
        )
    
    def update_stats_display(self):
        self.total_pomodoros_label.configure(
            text=f"Общо завършени pomodoros: {self.stats['completed_pomodoros']}"
        )
        
        hours = self.stats['total_focus_time'] // 3600
        minutes = (self.stats['total_focus_time'] % 3600) // 60
        self.total_time_label.configure(
            text=f"Общо фокус време: {hours}ч {minutes}м"
        )
    
    def highlight_active_mode(self):
        default_color = "#1f538d"  # Default button color
        active_color = "#14375e"   # Darker color for active button
        
        self.pomodoro_button.configure(fg_color=active_color if self.current_mode == "pomodoro" else default_color)
        self.short_break_button.configure(fg_color=active_color if self.current_mode == "short_break" else default_color)
        self.long_break_button.configure(fg_color=active_color if self.current_mode == "long_break" else default_color)
    
    def apply_settings(self):
        try:
            # Get values from entries and convert to seconds
            self.pomodoro_length = int(self.pomodoro_length_var.get()) * 60
            self.short_break_length = int(self.short_break_var.get()) * 60
            self.long_break_length = int(self.long_break_var.get()) * 60
            self.pomodoros_until_long_break = int(self.pomodoros_var.get())
            
            # Update timer if not running
            if not self.timer_running:
                self.set_time_for_current_mode()
                self.update_timer_display()
                self.update_progress_display()
        except ValueError as e:
            print(f"Грешка при прилагане на настройките: {e}")
            # Handle invalid input (could show error dialog)
            pass
    
    def on_close(self, event):
        # Save stats when closing
        self.save_stats() 