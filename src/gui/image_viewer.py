import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sqlite3


class ImageViewer(tk.Toplevel):
    def __init__(self, parent, image_path, db_path):
        super().__init__(parent)
        self.title(f"Image Details - {os.path.basename(image_path)}")
        self.geometry("800x600")
        self.image_path = image_path
        self.db_path = db_path
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Image display
        img_frame = ttk.Frame(main_frame)
        img_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        try:
            img = Image.open(self.image_path)
            img.thumbnail((500, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            img_label = ttk.Label(img_frame, image=photo)
            img_label.image = photo  # keep reference to avoid GC
            img_label.pack(pady=10)
        except Exception as e:
            ttk.Label(img_frame, text=f"Error loading image: {e}").pack(pady=20)

        # Right: Metadata and AI-generated tags
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        ttk.Label(info_frame, text="Image Information", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))

        info_text = f"Path: {self.image_path}\nFilename: {os.path.basename(self.image_path)}\n"
        try:
            stat = os.stat(self.image_path)
            size_mb = stat.st_size / (1024 * 1024)
            info_text += f"Size: {size_mb:.2f} MB\n"

            img = Image.open(self.image_path)
            info_text += f"Dimensions: {img.size[0]} x {img.size[1]}\nFormat: {img.format}\n"
        except Exception:
            pass

        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(info_frame, text="AI Generated Tags", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))

        tags = self.get_tags(self.image_path)
        tags_text = "\n".join([f"• {tag} ({conf:.3f})" for tag, conf in tags]) if tags else "No tags generated"

        tags_label = ttk.Label(info_frame, text=tags_text, justify=tk.LEFT)
        tags_label.pack(anchor=tk.W)

    def get_tags(self, image_path):
        """Retrieve AI-generated tags from database for the given image_path"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT tags.tag, tags.confidence FROM tags
            JOIN images ON tags.image_id = images.id
            WHERE images.path = ?
            ORDER BY tags.confidence DESC
            ''',
            (image_path,),
        )
        tags = cursor.fetchall()
        conn.close()
        return tags
