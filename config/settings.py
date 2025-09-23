"""
Application Configuration Settings
"""

import os
from pathlib import Path

class AppConfig:
    """Application configuration class"""

    def __init__(self):
        # Base directories
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.MODELS_DIR = self.DATA_DIR / "models"
        self.ASSETS_DIR = self.BASE_DIR / "assets"

        # Ensure required directories exist
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        self.ASSETS_DIR.mkdir(parents=True, exist_ok=True)

        # Database settings
        self.DATABASE_PATH = self.DATA_DIR / "gallery.db"

        # AI Model settings
        self.CLIP_MODEL_NAME = "ViT-B/32"  # Options: ViT-B/32, ViT-B/16, ViT-L/14
        self.DEVICE = "cuda" if self._check_cuda() else "cpu"
        self.TAG_CONFIDENCE_THRESHOLD = 0.1
        self.MAX_TAGS_PER_IMAGE = 10

        # Search and GUI settings
        self.FAISS_INDEX_TYPE = "IndexFlatIP"  # Inner product for CLIP
        self.SIMILARITY_SEARCH_TOP_K = 20
        self.SEARCH_RESULTS_LIMIT = 100
        self.WINDOW_WIDTH = 1200
        self.WINDOW_HEIGHT = 800
        self.THUMBNAIL_SIZE = (200, 200)
        self.IMAGES_PER_PAGE = 12
        self.GRID_COLUMNS = 4

        # Image processing settings
        self.SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'}
        self.MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB max
        self.BATCH_PROCESSING_SIZE = 10  # Images to process at once

        # Default labels for tag generation (expand as needed)
        self.DEFAULT_LABELS = [
            # People/animals
            "person", "dog", "cat", "child", "man", "woman",
            # Vehicles
            "car", "bus", "bicycle", "airplane", "train", "boat",
            # Nature/outdoors
            "tree", "mountain", "beach", "river", "snow", "sunset",
            # Objects/items
            "chair", "table", "phone", "computer", "book", "bottle",
            # Sports/activities
            "football", "soccer", "basketball", "tennis", "guitar"
        ]

    def _check_cuda(self):
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def get_database_url(self):
        return f"sqlite:///{self.DATABASE_PATH}"

    def is_supported_format(self, file_path):
        return Path(file_path).suffix.lower() in self.SUPPORTED_FORMATS

    def validate_image_size(self, file_path):
        return os.path.getsize(file_path) <= self.MAX_IMAGE_SIZE
