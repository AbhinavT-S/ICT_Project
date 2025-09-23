import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import GalleryApp
from config.settings import AppConfig

def main():
    config = AppConfig()
    app = GalleryApp(config)
    app.run()

if __name__ == "__main__":
    main()