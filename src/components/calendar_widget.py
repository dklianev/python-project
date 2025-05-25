import customtkinter as ctk
from tkcalendar import Calendar
import json
import os
import datetime
from datetime import datetime as dt


class CalendarWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.events_file = "data/events.json"
        self.events = []
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.events_file), exist_ok=True)
        
        # Load existing events
        self.load_events()
        
        # Create main layout
        self.create_layout()
        
        # Initialize variables
        self.current_event_id = None
    
    def create_layout(self):
        # Header
        self.header_label = ctk.CTkLabel(self, text="Календар", 
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(pady=10)
        
        # Main content split
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left frame - Calendar
        self.calendar_frame = ctk.CTkFrame(self.main_frame)
        self.calendar_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        current_date = dt.now()
        
        # Create the calendar
        self.calendar = Calendar(self.calendar_frame, 
                               selectmode="day",
                               year=current_date.year, 
                               month=current_date.month,
                               day=current_date.day,
                               locale="bg_BG",  # Bulgarian locale
                               background="#333333",
                               foreground="white",
                               selectbackground="#1f538d",
                               selectforeground="white",
                               normalbackground="#2b2b2b",
                               normalforeground="white",
                               weekendbackground="#3b3b3b",
                               weekendforeground="white",
                               othermonthbackground="#222222",
                               othermonthforeground="gray")
        
        self.calendar.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bind selection event
        self.calendar.bind("<<CalendarSelected>>", self.on_date_selected)
        
        # Today button
        self.today_button = ctk.CTkButton(self.calendar_frame, text="Днес", 
                                        command=self.go_to_today)
        self.today_button.pack(pady=10)
        
        # Right frame - Events
        self.events_frame = ctk.CTkFrame(self.main_frame)
        self.events_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Selected date label
        self.date_label = ctk.CTkLabel(self.events_frame, 
                                     text=current_date.strftime("%d %B %Y"),
                                     font=ctk.CTkFont(size=16, weight="bold"))
        self.date_label.pack(pady=(10, 5))
        
        # Events for selected date
        self.events_list_frame = ctk.CTkScrollableFrame(self.events_frame)
        self.events_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add event section
        self.add_event_frame = ctk.CTkFrame(self.events_frame)
        self.add_event_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.event_title_entry = ctk.CTkEntry(self.add_event_frame, 
                                           placeholder_text="Заглавие...")
        self.event_title_entry.pack(fill="x", pady=(10, 5))
        
        # Time picker
        self.time_frame = ctk.CTkFrame(self.add_event_frame)
        self.time_frame.pack(fill="x", pady=5)
        
        self.time_label = ctk.CTkLabel(self.time_frame, text="Време:")
        self.time_label.pack(side="left", padx=5)
        
        # Hours combo
        hours = [str(h).zfill(2) for h in range(24)]
        self.hour_var = ctk.StringVar(value=current_date.strftime("%H"))
        self.hour_combo = ctk.CTkOptionMenu(self.time_frame, values=hours, variable=self.hour_var,
                                         width=60)
        self.hour_combo.pack(side="left", padx=5)
        
        self.colon_label = ctk.CTkLabel(self.time_frame, text=":")
        self.colon_label.pack(side="left")
        
        # Minutes combo
        minutes = [str(m).zfill(2) for m in range(0, 60, 5)]
        self.minute_var = ctk.StringVar(value=str(current_date.minute // 5 * 5).zfill(2))
        self.minute_combo = ctk.CTkOptionMenu(self.time_frame, values=minutes, variable=self.minute_var,
                                           width=60)
        self.minute_combo.pack(side="left", padx=5)
        
        # Description text
        self.description_label = ctk.CTkLabel(self.add_event_frame, text="Описание:")
        self.description_label.pack(anchor="w", pady=(10, 0))
        
        self.event_desc_text = ctk.CTkTextbox(self.add_event_frame, height=100)
        self.event_desc_text.pack(fill="x", pady=5)
        
        # Buttons
        self.buttons_frame = ctk.CTkFrame(self.add_event_frame)
        self.buttons_frame.pack(fill="x", pady=5)
        
        self.save_button = ctk.CTkButton(self.buttons_frame, text="Запази",
                                       command=self.save_event)
        self.save_button.pack(side="left", fill="x", expand=True, padx=5)
        
        self.delete_button = ctk.CTkButton(self.buttons_frame, text="Изтрий", 
                                         fg_color="#FF5555", hover_color="#FF3333",
                                         command=self.delete_event)
        self.delete_button.pack(side="right", fill="x", expand=True, padx=5)
        
        # Update events display
        self.refresh_events_display(current_date.strftime("%Y-%m-%d"))
    
    def load_events(self):
        try:
            if os.path.exists(self.events_file):
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    self.events = json.load(f)
            else:
                self.events = []
        except Exception as e:
            print(f"Грешка при зареждане на събития: {e}")
            self.events = []
    
    def save_events(self):
        try:
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Грешка при запазване на събития: {e}")
    
    def on_date_selected(self, event):
        selected_date = self.calendar.get_date()
        date_obj = dt.strptime(selected_date, "%m/%d/%y")
        
        # Update date label
        self.date_label.configure(text=date_obj.strftime("%d %B %Y"))
        
        # Refresh events for the selected date
        self.refresh_events_display(date_obj.strftime("%Y-%m-%d"))
        
        # Clear event editing fields
        self.clear_event_fields()
    
    def go_to_today(self):
        today = dt.now()
        self.calendar.selection_set(today)
        self.date_label.configure(text=today.strftime("%d %B %Y"))
        self.refresh_events_display(today.strftime("%Y-%m-%d"))
    
    def refresh_events_display(self, date_str):
        # Clear existing events
        for widget in self.events_list_frame.winfo_children():
            widget.destroy()
        
        # Find events for the selected date
        date_events = [event for event in self.events if event['date'] == date_str]
        
        if not date_events:
            no_events_label = ctk.CTkLabel(self.events_list_frame, 
                                         text="Няма събития за този ден",
                                         text_color="gray")
            no_events_label.pack(pady=20)
        else:
            # Sort events by time
            sorted_events = sorted(date_events, key=lambda x: x.get('time', '00:00'))
            
            # Add events to list
            for event in sorted_events:
                self.create_event_item(event)
    
    def create_event_item(self, event):
        event_frame = ctk.CTkFrame(self.events_list_frame)
        event_frame.pack(fill="x", expand=True, padx=5, pady=5)
        
        # Time label
        time_label = ctk.CTkLabel(event_frame, 
                                text=event.get('time', '--:--'),
                                width=60,
                                font=ctk.CTkFont(weight="bold"))
        time_label.pack(side="left", padx=5, pady=5)
        
        # Title and description
        content_frame = ctk.CTkFrame(event_frame)
        content_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        title_label = ctk.CTkLabel(content_frame, 
                                 text=event.get('title', 'Без заглавие'),
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 anchor="w")
        title_label.pack(fill="x", padx=5)
        
        if event.get('description'):
            desc_label = ctk.CTkLabel(content_frame, 
                                    text=event.get('description'),
                                    anchor="w",
                                    justify="left")
            desc_label.pack(fill="x", padx=5)
        
        # Edit button
        edit_button = ctk.CTkButton(event_frame, 
                                  text="⚙️",
                                  width=30,
                                  command=lambda: self.edit_event(event))
        edit_button.pack(side="right", padx=5, pady=5)
    
    def clear_event_fields(self):
        self.current_event_id = None
        self.event_title_entry.delete(0, "end")
        self.event_desc_text.delete("1.0", "end")
        
        # Reset time to current time
        current_time = dt.now()
        self.hour_var.set(current_time.strftime("%H"))
        self.minute_var.set(str(current_time.minute // 5 * 5).zfill(2))
    
    def edit_event(self, event):
        self.current_event_id = event['id']
        
        # Fill form with event data
        self.event_title_entry.delete(0, "end")
        self.event_title_entry.insert(0, event.get('title', ''))
        
        self.event_desc_text.delete("1.0", "end")
        self.event_desc_text.insert("1.0", event.get('description', ''))
        
        # Set time if available
        if 'time' in event and ':' in event['time']:
            hour, minute = event['time'].split(':')
            self.hour_var.set(hour)
            self.minute_var.set(minute)
    
    def save_event(self):
        title = self.event_title_entry.get().strip()
        description = self.event_desc_text.get("1.0", "end-1c")  # -1c to remove trailing newline
        
        # Don't save if title is empty
        if not title:
            return
        
        selected_date = self.calendar.get_date()
        date_obj = dt.strptime(selected_date, "%m/%d/%y")
        date_str = date_obj.strftime("%Y-%m-%d")
        
        # Format time
        time_str = f"{self.hour_var.get()}:{self.minute_var.get()}"
        
        if self.current_event_id is None:
            # Create new event
            new_event = {
                'id': str(len(self.events) + 1),
                'title': title,
                'description': description,
                'date': date_str,
                'time': time_str,
                'created': dt.now().isoformat()
            }
            self.events.append(new_event)
        else:
            # Update existing event
            for event in self.events:
                if event.get('id') == self.current_event_id:
                    event['title'] = title
                    event['description'] = description
                    event['date'] = date_str
                    event['time'] = time_str
                    event['modified'] = dt.now().isoformat()
                    break
        
        # Save to file
        self.save_events()
        
        # Clear form and refresh display
        self.clear_event_fields()
        self.refresh_events_display(date_str)
    
    def delete_event(self):
        if self.current_event_id is None:
            return
        
        # Get current date
        selected_date = self.calendar.get_date()
        date_obj = dt.strptime(selected_date, "%m/%d/%y")
        date_str = date_obj.strftime("%Y-%m-%d")
        
        # Remove event
        self.events = [event for event in self.events if event.get('id') != self.current_event_id]
        
        # Save changes
        self.save_events()
        
        # Clear form and refresh display
        self.clear_event_fields()
        self.refresh_events_display(date_str) 