import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os
from ..database.db_manager import DatabaseManager
from ..ai.model_handler import AIModelHandler
from ..search.search_engine import SearchEngine

class GalleryApp:
    def __init__(self, config):
        self.config = config
        self.root = tk.Tk()
        self.root.title("AI-Powered Offline Gallery")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        # Initialize components
        self.db_manager = DatabaseManager(config.DATABASE_PATH)
        self.ai_handler = AIModelHandler(config)
        self.search_engine = SearchEngine(self.db_manager, self.ai_handler, config)
        
        self.current_images = []
        self.current_page = 0
        
        self.setup_ui()
        
        # Build search index
        threading.Thread(target=self.search_engine.build_index, daemon=True).start()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="Add Folder", 
                  command=self.add_folder).pack(side=tk.LEFT, padx=(0, 10))
        
        # Search functionality
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 5))
        self.search_entry.bind('<Return>', self.search_images)
        
        ttk.Button(search_frame, text="Search", command=self.search_images).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Show All", command=self.show_all_images).pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        
        # Image display area with scrolling
        self.canvas = tk.Canvas(main_frame, bg="white")
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X, side=tk.BOTTOM)
        
        self.load_existing_images()
    
    def add_folder(self):
        folder_path = filedialog.askdirectory(title="Select Image Folder")
        if folder_path:
            self.status_var.set("Processing folder...")
            self.progress_bar.pack(fill=tk.X, pady=(5, 5))
            threading.Thread(target=self.process_folder, args=(folder_path,), daemon=True).start()
    
    def run(self):
        self.root.mainloop()