import sqlite3
import numpy as np

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Images metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                size INTEGER,
                width INTEGER,
                height INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Tags linked to images
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER,
                tag TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                FOREIGN KEY (image_id) REFERENCES images (id)
            )
        ''')
        
        # Embeddings stored as BLOB
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER UNIQUE,
                embedding BLOB,
                FOREIGN KEY (image_id) REFERENCES images (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_image(self, path, filename, size, width, height):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO images (path, filename, size, width, height)
            VALUES (?, ?, ?, ?, ?)
        ''', (path, filename, size, width, height))
        conn.commit()
        image_id = cursor.lastrowid
        conn.close()
        return image_id
    
    def add_tags(self, image_id, tags):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for tag, confidence in tags:
            cursor.execute('''
                INSERT INTO tags (image_id, tag, confidence)
                VALUES (?, ?, ?)
            ''', (image_id, tag, confidence))
        conn.commit()
        conn.close()
    
    def add_embedding(self, image_id, embedding: np.ndarray):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        embedding_bytes = embedding.tobytes()
        cursor.execute('''
            INSERT OR REPLACE INTO embeddings (image_id, embedding)
            VALUES (?, ?)
        ''', (image_id, embedding_bytes))
        conn.commit()
        conn.close()
    
    def get_images(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM images')
        images = cursor.fetchall()
        conn.close()
        return images
    
    def get_tags_for_image(self, image_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT tag, confidence FROM tags WHERE image_id = ?', (image_id,))
        tags = cursor.fetchall()
        conn.close()
        return tags
    
    def get_embedding_for_image(self, image_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT embedding FROM embeddings WHERE image_id = ?', (image_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return np.frombuffer(result[0], dtype=np.float32)
        return None
