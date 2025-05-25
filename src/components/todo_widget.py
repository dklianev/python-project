import customtkinter as ctk
import json
import os
import datetime


class TodoWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.todo_file = "data/todos.json"
        self.todos = []
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.todo_file), exist_ok=True)
        
        # Load existing todos
        self.load_todos()
        
        # Create header
        self.header_label = ctk.CTkLabel(self, text="Задачи", 
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(pady=10)
        
        # Create input frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Task entry
        self.task_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Нова задача...")
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(5, 10), pady=10)
        self.task_entry.bind("<Return>", lambda event: self.add_todo())
        
        # Priority selector
        self.priority_var = ctk.StringVar(value="Medium")
        self.priority_options = ["Low", "Medium", "High"]
        
        self.priority_dropdown = ctk.CTkOptionMenu(
            self.input_frame, 
            values=self.priority_options,
            variable=self.priority_var
        )
        self.priority_dropdown.pack(side="left", padx=5, pady=10)
        
        # Add button
        self.add_button = ctk.CTkButton(self.input_frame, text="Добави", command=self.add_todo)
        self.add_button.pack(side="right", padx=5, pady=10)
        
        # Create tabs
        self.tab_frame = ctk.CTkFrame(self)
        self.tab_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.all_tab = ctk.CTkButton(self.tab_frame, text="Всички", 
                                   command=lambda: self.show_tab("all"))
        self.all_tab.pack(side="left", fill="x", expand=True, padx=2)
        
        self.active_tab = ctk.CTkButton(self.tab_frame, text="Активни", 
                                      command=lambda: self.show_tab("active"))
        self.active_tab.pack(side="left", fill="x", expand=True, padx=2)
        
        self.completed_tab = ctk.CTkButton(self.tab_frame, text="Завършени", 
                                         command=lambda: self.show_tab("completed"))
        self.completed_tab.pack(side="left", fill="x", expand=True, padx=2)
        
        # Set default active tab
        self.current_tab = "all"
        self.highlight_active_tab()
        
        # Create tasks list
        self.tasks_frame = ctk.CTkScrollableFrame(self)
        self.tasks_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Footer with stats
        self.footer_frame = ctk.CTkFrame(self)
        self.footer_frame.pack(fill="x", padx=10, pady=10)
        
        self.stats_label = ctk.CTkLabel(self.footer_frame, text="0 активни, 0 завършени")
        self.stats_label.pack(side="left", padx=5)
        
        self.clear_completed_button = ctk.CTkButton(
            self.footer_frame, 
            text="Изчисти завършените", 
            command=self.clear_completed
        )
        self.clear_completed_button.pack(side="right", padx=5)
        
        # Initialize UI
        self.refresh_todo_list()
        self.update_stats()
    
    def load_todos(self):
        try:
            if os.path.exists(self.todo_file):
                with open(self.todo_file, 'r', encoding='utf-8') as f:
                    self.todos = json.load(f)
            else:
                self.todos = []
        except Exception as e:
            print(f"Грешка при зареждане на задачи: {e}")
            self.todos = []
    
    def save_todos(self):
        try:
            with open(self.todo_file, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Грешка при запазване на задачи: {e}")
    
    def add_todo(self):
        task_text = self.task_entry.get().strip()
        if not task_text:
            return
        
        timestamp = datetime.datetime.now().isoformat()
        
        new_todo = {
            'id': str(len(self.todos) + 1),
            'text': task_text,
            'completed': False,
            'created': timestamp,
            'priority': self.priority_var.get()
        }
        
        self.todos.append(new_todo)
        self.save_todos()
        
        # Clear input field
        self.task_entry.delete(0, "end")
        
        # Refresh UI
        self.refresh_todo_list()
        self.update_stats()
    
    def toggle_todo(self, todo_id):
        for todo in self.todos:
            if todo['id'] == todo_id:
                todo['completed'] = not todo['completed']
                break
        
        self.save_todos()
        self.refresh_todo_list()
        self.update_stats()
    
    def delete_todo(self, todo_id):
        self.todos = [todo for todo in self.todos if todo['id'] != todo_id]
        self.save_todos()
        self.refresh_todo_list()
        self.update_stats()
    
    def clear_completed(self):
        self.todos = [todo for todo in self.todos if not todo['completed']]
        self.save_todos()
        self.refresh_todo_list()
        self.update_stats()
    
    def show_tab(self, tab):
        self.current_tab = tab
        self.highlight_active_tab()
        self.refresh_todo_list()
    
    def highlight_active_tab(self):
        default_color = "#1f538d"  # Default button color
        active_color = "#14375e"   # Darker color for active tab
        
        self.all_tab.configure(fg_color=active_color if self.current_tab == "all" else default_color)
        self.active_tab.configure(fg_color=active_color if self.current_tab == "active" else default_color)
        self.completed_tab.configure(fg_color=active_color if self.current_tab == "completed" else default_color)
    
    def refresh_todo_list(self):
        # Clear existing todos
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()
        
        # Filter todos based on current tab
        filtered_todos = self.todos
        if self.current_tab == "active":
            filtered_todos = [todo for todo in self.todos if not todo['completed']]
        elif self.current_tab == "completed":
            filtered_todos = [todo for todo in self.todos if todo['completed']]
        
        # Sort todos by priority and creation date
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        sorted_todos = sorted(
            filtered_todos, 
            key=lambda x: (x['completed'], priority_order.get(x['priority'], 99), x.get('created', ''))
        )
        
        # Add todos to list
        for todo in sorted_todos:
            self.create_todo_item(todo)
    
    def create_todo_item(self, todo):
        # Create frame for todo item
        todo_frame = ctk.CTkFrame(self.tasks_frame)
        todo_frame.pack(fill="x", expand=True, padx=5, pady=2)
        
        # Priority indicator
        priority_color = "#FF6B6B" if todo['priority'] == "High" else \
                        "#FFCC5C" if todo['priority'] == "Medium" else "#88CC88"
        
        priority_indicator = ctk.CTkFrame(todo_frame, width=5, height=30, fg_color=priority_color)
        priority_indicator.pack(side="left", fill="y", padx=(0, 5))
        
        # Checkbox
        checkbox_var = ctk.IntVar(value=1 if todo['completed'] else 0)
        checkbox = ctk.CTkCheckBox(
            todo_frame, 
            text="",
            variable=checkbox_var,
            command=lambda: self.toggle_todo(todo['id']),
            width=20
        )
        checkbox.pack(side="left", padx=5)
        
        # Task text
        text_color = "grey" if todo['completed'] else "white"
        font_style = ctk.CTkFont(slant="italic" if todo['completed'] else "roman")
        
        task_label = ctk.CTkLabel(
            todo_frame, 
            text=todo['text'],
            font=font_style,
            text_color=text_color,
            anchor="w"
        )
        task_label.pack(side="left", fill="x", expand=True, padx=5)
        
        # Delete button
        delete_button = ctk.CTkButton(
            todo_frame, 
            text="🗑️",
            width=30,
            command=lambda: self.delete_todo(todo['id']),
            fg_color="transparent",
            hover_color="#FF5555"
        )
        delete_button.pack(side="right", padx=5)
    
    def update_stats(self):
        active_count = sum(1 for todo in self.todos if not todo['completed'])
        completed_count = sum(1 for todo in self.todos if todo['completed'])
        
        self.stats_label.configure(
            text=f"{active_count} активни, {completed_count} завършени"
        ) 