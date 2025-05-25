"""
Database manager for the Personal Assistant application.
Handles SQLite database operations for storing notes, todos, etc.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional


class DatabaseManager:
    def __init__(self, db_path: str = "data/assistant.db"):
        """Initialize the database manager."""
        self.db_path = db_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Notes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Todos table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    priority TEXT DEFAULT 'medium',
                    due_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Calendar events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    event_date DATE NOT NULL,
                    event_time TIME,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def add_note(self, title: str, content: str) -> int:
        """Add a new note and return its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (title, content) VALUES (?, ?)",
                (title, content)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_notes(self) -> List[Dict]:
        """Get all notes."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "created_at": row[3],
                    "updated_at": row[4]
                }
                for row in rows
            ]
    
    def update_note(self, note_id: int, title: str, content: str) -> bool:
        """Update an existing note."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notes SET title=?, content=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (title, content, note_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_todo(self, task: str, priority: str = "medium", due_date: str = None) -> int:
        """Add a new todo and return its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO todos (task, priority, due_date) VALUES (?, ?, ?)",
                (task, priority, due_date)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_todos(self) -> List[Dict]:
        """Get all todos."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "task": row[1],
                    "completed": bool(row[2]),
                    "priority": row[3],
                    "due_date": row[4],
                    "created_at": row[5]
                }
                for row in rows
            ]
    
    def toggle_todo(self, todo_id: int) -> bool:
        """Toggle todo completion status."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE todos SET completed = NOT completed WHERE id=?",
                (todo_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM todos WHERE id=?", (todo_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_event(self, title: str, description: str, date: str, time: str) -> int:
        """Add a new event and return its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO events (title, description, event_date, event_time) VALUES (?, ?, ?, ?)",
                (title, description, date, time)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_events(self) -> List[Dict]:
        """Get all events."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events ORDER BY event_date DESC")
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "event_date": row[3],
                    "event_time": row[4],
                    "created_at": row[5]
                }
                for row in rows
            ]
    
    def update_event(self, event_id: int, title: str, description: str, date: str, time: str) -> bool:
        """Update an existing event."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE events SET title=?, description=?, event_date=?, event_time=? WHERE id=?",
                (title, description, date, time, event_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events WHERE id=?", (event_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_pomodoro_session(self, duration: int) -> int:
        """Add a completed pomodoro session and return its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration) VALUES (?)",
                (duration,)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_pomodoro_stats(self) -> Dict:
        """Get pomodoro statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count, SUM(duration) as total FROM pomodoro_sessions")
            result = cursor.fetchone()
            
            return {
                "completed_pomodoros": result[0],
                "total_focus_time": result[1]
            }
    
    def migrate_from_json(self, json_data_dir: str = "data"):
        """Migrate data from JSON files to SQLite database."""
        self._migrate_notes(os.path.join(json_data_dir, "notes.json"))
        self._migrate_todos(os.path.join(json_data_dir, "todos.json"))
        self._migrate_events(os.path.join(json_data_dir, "events.json"))
        self._migrate_pomodoro_stats(os.path.join(json_data_dir, "pomodoro_stats.json"))
    
    def _migrate_notes(self, json_file: str):
        """Migrate notes from JSON."""
        if not os.path.exists(json_file):
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                notes = json.load(f)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    for note in notes:
                        cursor.execute(
                            "INSERT INTO notes (title, content) VALUES (?, ?)",
                            (note.get('title', ''), note.get('content', ''))
                        )
                    conn.commit()
        except Exception as e:
            print(f"Error migrating notes: {e}")
    
    def _migrate_todos(self, json_file: str):
        """Migrate todos from JSON."""
        if not os.path.exists(json_file):
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                todos = json.load(f)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    for todo in todos:
                        cursor.execute(
                            "INSERT INTO todos (task, completed, priority, due_date) VALUES (?, ?, ?, ?)",
                            (todo.get('task', ''), 1 if todo.get('completed', False) else 0, 
                             todo.get('priority', 'medium'), todo.get('due_date'))
                        )
                    conn.commit()
        except Exception as e:
            print(f"Error migrating todos: {e}")
    
    def _migrate_events(self, json_file: str):
        """Migrate events from JSON."""
        if not os.path.exists(json_file):
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    for event in events:
                        cursor.execute(
                            "INSERT INTO events (title, description, event_date, event_time) VALUES (?, ?, ?, ?)",
                            (event.get('title', ''), event.get('description', ''),
                             event.get('date', ''), event.get('time', ''))
                        )
                    conn.commit()
        except Exception as e:
            print(f"Error migrating events: {e}")
    
    def _migrate_pomodoro_stats(self, json_file: str):
        """Migrate pomodoro stats from JSON."""
        if not os.path.exists(json_file):
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    for session in stats.get('sessions', []):
                        cursor.execute(
                            "INSERT INTO pomodoro_sessions (duration) VALUES (?)",
                            (session.get('duration', 0),)
                        )
                    conn.commit()
        except Exception as e:
            print(f"Error migrating pomodoro stats: {e}") 