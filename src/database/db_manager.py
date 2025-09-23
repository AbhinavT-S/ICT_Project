import sqlite3
import numpy as np
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            size INTEGER,
            width INTEGER, height INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed BOOLEAN DEFAULT FALSE
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER,
            tag TEXT NOT NULL,
            confidence REAL DEFAULT 0.0,
            FOREIGN KEY (image_id) REFERENCES images (id)
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER UNIQUE,
            embedding BLOB,
            FOREIGN KEY (image_id) REFERENCES images (id)
        )''')
        
        conn.commit()
        conn.close()