import customtkinter as ctk
import json
import os
import datetime


class NotesWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.notes_file = "data/notes.json"
        self.notes = []
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.notes_file), exist_ok=True)
        
        # Load existing notes
        self.load_notes()
        
        # Create header
        self.header_label = ctk.CTkLabel(self, text="Моите Бележки", 
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(pady=10)
        
        # Split into left and right frames
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left frame for notes list
        self.notes_list_frame = ctk.CTkFrame(self.main_frame)
        self.notes_list_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Search bar
        self.search_frame = ctk.CTkFrame(self.notes_list_frame)
        self.search_frame.pack(fill="x", padx=5, pady=5)
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Търсене...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        self.search_button = ctk.CTkButton(self.search_frame, text="🔍", width=30, command=self.search_notes)
        self.search_button.pack(side="right", padx=5)
        
        # Create notes listbox
        self.notes_listbox_frame = ctk.CTkFrame(self.notes_list_frame)
        self.notes_listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.notes_listbox = ctk.CTkScrollableFrame(self.notes_listbox_frame)
        self.notes_listbox.pack(fill="both", expand=True)
        
        # Create add note button
        self.add_button = ctk.CTkButton(self.notes_list_frame, text="Нова Бележка", command=self.new_note)
        self.add_button.pack(pady=10, padx=5, fill="x")
        
        # Right frame for note content
        self.note_content_frame = ctk.CTkFrame(self.main_frame)
        self.note_content_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Note title
        self.title_entry = ctk.CTkEntry(self.note_content_frame, placeholder_text="Заглавие...", 
                                      font=ctk.CTkFont(size=18, weight="bold"))
        self.title_entry.pack(fill="x", padx=10, pady=10)
        
        # Note content
        self.content_text = ctk.CTkTextbox(self.note_content_frame, wrap="word")
        self.content_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Save and delete buttons
        self.buttons_frame = ctk.CTkFrame(self.note_content_frame)
        self.buttons_frame.pack(fill="x", padx=10, pady=10)
        
        self.save_button = ctk.CTkButton(self.buttons_frame, text="Запази", command=self.save_current_note)
        self.save_button.pack(side="left", padx=5, expand=True, fill="x")
        
        self.delete_button = ctk.CTkButton(self.buttons_frame, text="Изтрий", 
                                         command=self.delete_current_note, 
                                         fg_color="#FF5555", hover_color="#FF3333")
        self.delete_button.pack(side="right", padx=5, expand=True, fill="x")
        
        # Initialize UI
        self.current_note_id = None
        self.refresh_notes_list()
    
    def load_notes(self):
        try:
            if os.path.exists(self.notes_file):
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    self.notes = json.load(f)
            else:
                self.notes = []
        except Exception as e:
            print(f"Грешка при зареждане на бележки: {e}")
            self.notes = []
    
    def save_notes(self):
        try:
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Грешка при запазване на бележки: {e}")
    
    def refresh_notes_list(self, search_term=None):
        # Clear existing notes
        for widget in self.notes_listbox.winfo_children():
            widget.destroy()
        
        # Sort notes by last modified date (newest first)
        sorted_notes = sorted(self.notes, key=lambda x: x.get('modified', ''), reverse=True)
        
        # Filter notes if search term provided
        if search_term:
            search_term = search_term.lower()
            sorted_notes = [note for note in sorted_notes if 
                          search_term in note['title'].lower() or 
                          search_term in note['content'].lower()]
        
        # Add notes to listbox
        for i, note in enumerate(sorted_notes):
            note_frame = ctk.CTkFrame(self.notes_listbox)
            note_frame.pack(fill="x", expand=True, padx=5, pady=2)
            
            title = note['title'] if note['title'] else "Без заглавие"
            date = note.get('modified', '')[:10]
            
            note_button = ctk.CTkButton(note_frame, text=f"{title}", 
                                     anchor="w", 
                                     command=lambda n=note: self.display_note(n))
            note_button.pack(side="left", fill="x", expand=True, padx=5, pady=5)
            
            date_label = ctk.CTkLabel(note_frame, text=f"{date}")
            date_label.pack(side="right", padx=5, pady=5)
    
    def new_note(self):
        # Save current note before creating a new one
        if self.current_note_id is not None:
            self.save_current_note()
        
        # Clear fields
        self.title_entry.delete(0, "end")
        self.content_text.delete("1.0", "end")
        self.current_note_id = None
        
        # Set focus to title
        self.title_entry.focus_set()
    
    def display_note(self, note):
        # Save current note before displaying another
        if self.current_note_id is not None:
            self.save_current_note()
        
        # Display selected note
        self.current_note_id = note.get('id')
        
        # Clear existing content
        self.title_entry.delete(0, "end")
        self.content_text.delete("1.0", "end")
        
        # Set new content
        self.title_entry.insert(0, note.get('title', ''))
        self.content_text.insert("1.0", note.get('content', ''))
    
    def save_current_note(self):
        title = self.title_entry.get()
        content = self.content_text.get("1.0", "end-1c")  # -1c to remove trailing newline
        
        # Don't save empty notes
        if not title.strip() and not content.strip():
            return
        
        timestamp = datetime.datetime.now().isoformat()
        
        if self.current_note_id is None:
            # New note
            new_note = {
                'id': str(len(self.notes) + 1),  # Simple ID generation
                'title': title,
                'content': content,
                'created': timestamp,
                'modified': timestamp
            }
            self.notes.append(new_note)
            self.current_note_id = new_note['id']
        else:
            # Update existing note
            for note in self.notes:
                if note.get('id') == self.current_note_id:
                    note['title'] = title
                    note['content'] = content
                    note['modified'] = timestamp
                    break
        
        # Save to file
        self.save_notes()
        
        # Refresh notes list
        self.refresh_notes_list()
    
    def delete_current_note(self):
        if self.current_note_id is None:
            return
        
        # Find and remove the current note
        self.notes = [note for note in self.notes if note.get('id') != self.current_note_id]
        
        # Save changes
        self.save_notes()
        
        # Clear fields
        self.title_entry.delete(0, "end")
        self.content_text.delete("1.0", "end")
        self.current_note_id = None
        
        # Refresh list
        self.refresh_notes_list()
    
    def search_notes(self):
        search_term = self.search_entry.get().strip()
        self.refresh_notes_list(search_term if search_term else None) 