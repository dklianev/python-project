import sqlite3
import os
import json
import datetime


class DBManager:
    def __init__(self, db_path="data/assistant.db"):
        """
        Initialize the database manager
        
        Args:
            db_path: Path to the SQLite database file
        """
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.connection = None
        
        # Initialize database
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Configure to return results as dictionaries
            self.connection.row_factory = sqlite3.Row
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Notes table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                created_at TIMESTAMP NOT NULL,
                modified_at TIMESTAMP NOT NULL
            )
            ''')
            
            # Tasks table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0,
                priority TEXT NOT NULL DEFAULT 'Medium',
                created_at TIMESTAMP NOT NULL
            )
            ''')
            
            # Events table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                event_date TEXT NOT NULL,
                event_time TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                modified_at TIMESTAMP
            )
            ''')
            
            # Chat history table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
            ''')
            
            # Pomodoro sessions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                duration INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
            ''')
            
            self.connection.commit()
            return True
        
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            return False
    
    # Notes methods
    def get_notes(self, search_term=None):
        """Get all notes, optionally filtered by search term"""
        try:
            cursor = self.connection.cursor()
            
            if search_term:
                search_pattern = f"%{search_term}%"
                cursor.execute(
                    "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY modified_at DESC",
                    (search_pattern, search_pattern)
                )
            else:
                cursor.execute("SELECT * FROM notes ORDER BY modified_at DESC")
            
            notes = []
            for row in cursor.fetchall():
                notes.append(dict(row))
            
            return notes
        
        except sqlite3.Error as e:
            print(f"Error fetching notes: {e}")
            return []
    
    def get_note(self, note_id):
        """Get a specific note by ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            note = cursor.fetchone()
            
            if note:
                return dict(note)
            return None
        
        except sqlite3.Error as e:
            print(f"Error fetching note {note_id}: {e}")
            return None
    
    def add_note(self, title, content):
        """Add a new note"""
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO notes (title, content, created_at, modified_at) VALUES (?, ?, ?, ?)",
                (title, content, timestamp, timestamp)
            )
            
            self.connection.commit()
            return cursor.lastrowid
        
        except sqlite3.Error as e:
            print(f"Error adding note: {e}")
            return None
    
    def update_note(self, note_id, title, content):
        """Update an existing note"""
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE notes SET title = ?, content = ?, modified_at = ? WHERE id = ?",
                (title, content, timestamp, note_id)
            )
            
            self.connection.commit()
            return cursor.rowcount > 0
        
        except sqlite3.Error as e:
            print(f"Error updating note {note_id}: {e}")
            return False
    
    def delete_note(self, note_id):
        """Delete a note"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            
            self.connection.commit()
            return cursor.rowcount > 0
        
        except sqlite3.Error as e:
            print(f"Error deleting note {note_id}: {e}")
            return False
    
    # Tasks methods
    def get_tasks(self, filter_type=None):
        """
        Get tasks, optionally filtered
        
        Args:
            filter_type: 'all', 'active', or 'completed'
        """
        try:
            cursor = self.connection.cursor()
            
            if filter_type == "active":
                cursor.execute(
                    "SELECT * FROM tasks WHERE completed = 0 ORDER BY completed, priority, created_at"
                )
            elif filter_type == "completed":
                cursor.execute(
                    "SELECT * FROM tasks WHERE completed = 1 ORDER BY completed, priority, created_at"
                )
            else:
                cursor.execute(
                    "SELECT * FROM tasks ORDER BY completed, priority, created_at"
                )
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append(dict(row))
            
            return tasks
        
        except sqlite3.Error as e:
            print(f"Error fetching tasks: {e}")
            return []
    
    def add_task(self, text, priority="Medium"):
        """Add a new task"""
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO tasks (text, completed, priority, created_at) VALUES (?, ?, ?, ?)",
                (text, 0, priority, timestamp)
            )
            
            self.connection.commit()
            return cursor.lastrowid
        
        except sqlite3.Error as e:
            print(f"Error adding task: {e}")
            return None
    
    def toggle_task(self, task_id):
        """Toggle a task's completion status"""
        try:
            cursor = self.connection.cursor()
            
            # Get current status
            cursor.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
            result = cursor.fetchone()
            
            if result:
                current_status = bool(result['completed'])
                
                # Toggle status
                cursor.execute(
                    "UPDATE tasks SET completed = ? WHERE id = ?",
                    (1 if not current_status else 0, task_id)
                )
                
                self.connection.commit()
                return True
            
            return False
        
        except sqlite3.Error as e:
            print(f"Error toggling task {task_id}: {e}")
            return False
    
    def delete_task(self, task_id):
        """Delete a task"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            
            self.connection.commit()
            return cursor.rowcount > 0
        
        except sqlite3.Error as e:
            print(f"Error deleting task {task_id}: {e}")
            return False
    
    def clear_completed_tasks(self):
        """Delete all completed tasks"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM tasks WHERE completed = 1")
            
            self.connection.commit()
            return cursor.rowcount
        
        except sqlite3.Error as e:
            print(f"Error clearing completed tasks: {e}")
            return 0
    
    # Events methods
    def get_events_by_date(self, date_str):
        """Get events for a specific date"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM events WHERE event_date = ? ORDER BY event_time",
                (date_str,)
            )
            
            events = []
            for row in cursor.fetchall():
                events.append(dict(row))
            
            return events
        
        except sqlite3.Error as e:
            print(f"Error fetching events for {date_str}: {e}")
            return []
    
    def add_event(self, title, description, date_str, time_str):
        """Add a new event"""
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(
                """INSERT INTO events 
                   (title, description, event_date, event_time, created_at) 
                   VALUES (?, ?, ?, ?, ?)""",
                (title, description, date_str, time_str, timestamp)
            )
            
            self.connection.commit()
            return cursor.lastrowid
        
        except sqlite3.Error as e:
            print(f"Error adding event: {e}")
            return None
    
    def update_event(self, event_id, title, description, date_str, time_str):
        """Update an existing event"""
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(
                """UPDATE events 
                   SET title = ?, description = ?, event_date = ?, 
                       event_time = ?, modified_at = ? 
                   WHERE id = ?""",
                (title, description, date_str, time_str, timestamp, event_id)
            )
            
            self.connection.commit()
            return cursor.rowcount > 0
        
        except sqlite3.Error as e:
            print(f"Error updating event {event_id}: {e}")
            return False
    
    def delete_event(self, event_id):
        """Delete an event"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
            
            self.connection.commit()
            return cursor.rowcount > 0
        
        except sqlite3.Error as e:
            print(f"Error deleting event {event_id}: {e}")
            return False
    
    # Chat history methods
    def get_chat_history(self, limit=100):
        """Get chat history with optional limit"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM chat_history ORDER BY created_at LIMIT ?",
                (limit,)
            )
            
            messages = []
            for row in cursor.fetchall():
                messages.append(dict(row))
            
            return messages
        
        except sqlite3.Error as e:
            print(f"Error fetching chat history: {e}")
            return []
    
    def add_chat_message(self, role, content):
        """Add a chat message"""
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO chat_history (role, content, created_at) VALUES (?, ?, ?)",
                (role, content, timestamp)
            )
            
            self.connection.commit()
            return cursor.lastrowid
        
        except sqlite3.Error as e:
            print(f"Error adding chat message: {e}")
            return None
    
    def clear_chat_history(self):
        """Clear all chat history"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM chat_history")
            
            self.connection.commit()
            return cursor.rowcount
        
        except sqlite3.Error as e:
            print(f"Error clearing chat history: {e}")
            return 0
    
    # Pomodoro methods
    def add_pomodoro_session(self, duration):
        """Add a completed pomodoro session"""
        try:
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            timestamp = now.isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(
                """INSERT INTO pomodoro_sessions 
                   (date, time, duration, created_at) 
                   VALUES (?, ?, ?, ?)""",
                (date_str, time_str, duration, timestamp)
            )
            
            self.connection.commit()
            return cursor.lastrowid
        
        except sqlite3.Error as e:
            print(f"Error adding pomodoro session: {e}")
            return None
    
    def get_pomodoro_stats(self):
        """Get pomodoro statistics"""
        try:
            cursor = self.connection.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) as count FROM pomodoro_sessions")
            count_result = cursor.fetchone()
            count = count_result['count'] if count_result else 0
            
            # Get total duration
            cursor.execute("SELECT SUM(duration) as total FROM pomodoro_sessions")
            duration_result = cursor.fetchone()
            total_duration = duration_result['total'] if duration_result and duration_result['total'] else 0
            
            # Get recent sessions
            cursor.execute(
                "SELECT * FROM pomodoro_sessions ORDER BY created_at DESC LIMIT 10"
            )
            
            recent_sessions = []
            for row in cursor.fetchall():
                recent_sessions.append(dict(row))
            
            return {
                "completed_pomodoros": count,
                "total_focus_time": total_duration,
                "recent_sessions": recent_sessions
            }
        
        except sqlite3.Error as e:
            print(f"Error getting pomodoro stats: {e}")
            return {"completed_pomodoros": 0, "total_focus_time": 0, "recent_sessions": []}
    
    # Migration methods
    def migrate_from_json(self, json_data_dir="data"):
        """
        Migrate data from JSON files to SQLite database
        
        Args:
            json_data_dir: Directory containing JSON files
        """
        self._migrate_notes(os.path.join(json_data_dir, "notes.json"))
        self._migrate_todos(os.path.join(json_data_dir, "todos.json"))
        self._migrate_events(os.path.join(json_data_dir, "events.json"))
        self._migrate_chat_history(os.path.join(json_data_dir, "chat_history.json"))
        self._migrate_pomodoro_stats(os.path.join(json_data_dir, "pomodoro_stats.json"))
    
    def _migrate_notes(self, json_file):
        """Migrate notes from JSON"""
        if not os.path.exists(json_file):
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                notes = json.load(f)
                
                for note in notes:
                    created = note.get('created', datetime.datetime.now().isoformat())
                    modified = note.get('modified', created)
                    
                    cursor = self.connection.cursor()
                    cursor.execute(
                        "INSERT INTO notes (title, content, created_at, modified_at) VALUES (?, ?, ?, ?)",
                        (note.get('title', ''), note.get('content', ''), created, modified)
                    )
                
                self.connection.commit()
        except Exception as e:
            print(f"Error migrating notes: {e}")
    
    def _migrate_todos(self, json_file):
        """Migrate todos from JSON"""
        if not os.path.exists(json_file):
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                todos = json.load(f)
                
                for todo in todos:
                    created = todo.get('created', datetime.datetime.now().isoformat())
                    
                    cursor = self.connection.cursor()
                    cursor.execute(
                        "INSERT INTO tasks (text, completed, priority, created_at) VALUES (?, ?, ?, ?)",
                        (todo.get('text', ''), 1 if todo.get('completed', False) else 0, 
                         todo.get('priority', 'Medium'), created)
                    )
                
                self.connection.commit()
        except Exception as e:
            print(f"Error migrating todos: {e}")
    
    def _migrate_events(self, json_file):
        """Migrate events from JSON"""
        if not os.path.exists(json_file):
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
                
                for event in events:
                    created = event.get('created', datetime.datetime.now().isoformat())
                    
                    cursor = self.connection.cursor()
                    cursor.execute(
                        """INSERT INTO events 
                           (title, description, event_date, event_time, created_at) 
                           VALUES (?, ?, ?, ?, ?)""",
                        (event.get('title', ''), event.get('description', ''),
                         event.get('date', ''), event.get('time', ''), created)
                    )
                
                self.connection.commit()
        except Exception as e:
            print(f"Error migrating events: {e}")
    
    def _migrate_chat_history(self, json_file):
        """Migrate chat history from JSON"""
        if not os.path.exists(json_file):
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                
                for msg in messages:
                    created = msg.get('time', datetime.datetime.now().isoformat())
                    
                    cursor = self.connection.cursor()
                    cursor.execute(
                        "INSERT INTO chat_history (role, content, created_at) VALUES (?, ?, ?)",
                        (msg.get('role', 'user'), msg.get('content', ''), created)
                    )
                
                self.connection.commit()
        except Exception as e:
            print(f"Error migrating chat history: {e}")
    
    def _migrate_pomodoro_stats(self, json_file):
        """Migrate pomodoro stats from JSON"""
        if not os.path.exists(json_file):
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                
                # Add sessions
                sessions = stats.get('sessions', [])
                for session in sessions:
                    date = session.get('date', datetime.datetime.now().strftime("%Y-%m-%d"))
                    time = session.get('time', datetime.datetime.now().strftime("%H:%M:%S"))
                    duration = session.get('duration', 0)
                    
                    cursor = self.connection.cursor()
                    cursor.execute(
                        """INSERT INTO pomodoro_sessions 
                           (date, time, duration, created_at) 
                           VALUES (?, ?, ?, ?)""",
                        (date, time, duration, datetime.datetime.now().isoformat())
                    )
                
                self.connection.commit()
        except Exception as e:
            print(f"Error migrating pomodoro stats: {e}") 