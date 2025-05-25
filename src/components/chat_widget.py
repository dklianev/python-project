import customtkinter as ctk
import json
import os
import datetime
import threading


class ChatWidget(ctk.CTkFrame):
    def __init__(self, parent, llm_service):
        super().__init__(parent)
        
        self.llm_service = llm_service
        self.chat_history = []
        self.chat_file = "data/chat_history.json"
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.chat_file), exist_ok=True)
        
        # Load chat history
        self.load_chat_history()
        
        # Create header
        self.header_label = ctk.CTkLabel(self, text="Чат с Асистент", 
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(pady=10)
        
        # Chat display area
        self.chat_frame = ctk.CTkScrollableFrame(self)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input area
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=10, pady=10)
        
        self.message_entry = ctk.CTkTextbox(self.input_frame, height=70, wrap="word")
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.on_enter_key)
        
        self.send_button = ctk.CTkButton(self.input_frame, text="Изпрати", command=self.send_message)
        self.send_button.pack(side="right", padx=5)
        
        self.clear_button = ctk.CTkButton(self.input_frame, text="Изчисти", 
                                        command=self.clear_chat,
                                        fg_color="#FF5555", hover_color="#FF3333")
        self.clear_button.pack(side="right", padx=5)
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(self, height=30)
        self.status_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.status_indicator = ctk.CTkLabel(self.status_frame, text="Готов", text_color="green")
        self.status_indicator.pack(side="left", padx=5)
        
        self.model_label = ctk.CTkLabel(self.status_frame, 
                                      text=f"Модел: {self.llm_service.model}")
        self.model_label.pack(side="right", padx=5)
        
        # Display existing chat history
        self.display_chat_history()
        
        # Welcome message if no history
        if not self.chat_history:
            self.add_assistant_message("Здравейте! С какво мога да ви помогна днес?")
    
    def load_chat_history(self):
        try:
            if os.path.exists(self.chat_file):
                with open(self.chat_file, 'r', encoding='utf-8') as f:
                    self.chat_history = json.load(f)
            else:
                self.chat_history = []
        except Exception as e:
            print(f"Грешка при зареждане на чат история: {e}")
            self.chat_history = []
    
    def save_chat_history(self):
        try:
            with open(self.chat_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Грешка при запазване на чат история: {e}")
    
    def display_chat_history(self):
        # Clear existing messages
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        
        # Display messages
        for message in self.chat_history:
            self.display_message(message['role'], message['content'])
    
    def display_message(self, role, content):
        # Create message frame
        if role == "user":
            message_frame = ctk.CTkFrame(self.chat_frame, fg_color="#1E3A5F")
            align = "e"  # east = right
        else:
            message_frame = ctk.CTkFrame(self.chat_frame, fg_color="#2D4263")
            align = "w"  # west = left
        
        message_frame.pack(fill="x", pady=5, padx=10, anchor=align)
        
        # Role label
        role_text = "Вие" if role == "user" else "Асистент"
        role_label = ctk.CTkLabel(message_frame, 
                                text=role_text,
                                font=ctk.CTkFont(size=12, weight="bold"))
        role_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # Message content
        content_label = ctk.CTkLabel(message_frame, 
                                   text=content,
                                   font=ctk.CTkFont(size=14),
                                   anchor="w",
                                   justify="left",
                                   wraplength=550)
        content_label.pack(fill="both", padx=10, pady=10)
        
        # Timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M")
        time_label = ctk.CTkLabel(message_frame, 
                               text=timestamp,
                               font=ctk.CTkFont(size=10),
                               text_color="gray")
        time_label.pack(anchor="e", padx=10, pady=(0, 5))
    
    def add_user_message(self, content):
        message = {"role": "user", "content": content, "time": datetime.datetime.now().isoformat()}
        self.chat_history.append(message)
        self.display_message("user", content)
        self.save_chat_history()
    
    def add_assistant_message(self, content):
        message = {"role": "assistant", "content": content, "time": datetime.datetime.now().isoformat()}
        self.chat_history.append(message)
        self.display_message("assistant", content)
        self.save_chat_history()
    
    def on_enter_key(self, event):
        # Only send if not combined with Shift (which creates a new line)
        if not event.state & 1:  # No Shift key
            self.send_message()
            return "break"  # Prevent default behavior
    
    def send_message(self):
        message = self.message_entry.get("1.0", "end-1c").strip()
        if not message:
            return
        
        # Clear input
        self.message_entry.delete("1.0", "end")
        
        # Add user message to chat
        self.add_user_message(message)
        
        # Update status
        self.status_indicator.configure(text="Мисля...", text_color="orange")
        
        # Get response in separate thread
        threading.Thread(target=self.get_response, args=(message,), daemon=True).start()
    
    def get_response(self, message):
        try:
            # This would call the LLM service
            response = self.llm_service.get_response(message, self.chat_history)
            
            # Update UI in main thread
            self.after(0, lambda: self.add_assistant_message(response))
        except Exception as e:
            error_message = f"Грешка при комуникацията с LLM: {str(e)}"
            self.after(0, lambda: self.add_assistant_message(error_message))
        finally:
            # Reset status
            self.after(0, lambda: self.status_indicator.configure(text="Готов", text_color="green"))
    
    def clear_chat(self):
        # Clear chat history
        self.chat_history = []
        self.save_chat_history()
        
        # Clear display
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        
        # Add welcome message
        self.add_assistant_message("Здравейте! С какво мога да ви помогна днес?") 