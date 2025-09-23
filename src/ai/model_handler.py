import torch
import clip
import numpy as np
from PIL import Image

class AIModelHandler:
    def __init__(self, config):
        self.config = config
        self.device = config.DEVICE
        self.model = None
        self.preprocess = None
        self.load_model()
    
    def load_model(self):
        try:
            self.model, self.preprocess = clip.load(self.config.CLIP_MODEL_NAME, device=self.device)
            print(f"CLIP model loaded on {self.device}")
        except Exception as e:
            print(f"Error loading CLIP: {e}")
    
    def extract_features(self, image_path):
        if not self.model:
            return None
        try:
            image = self.preprocess(Image.open(image_path)).unsqueeze(0).to(self.device)
            with torch.no_grad():
                image_features = self.model.encode_image(image)
                return image_features.cpu().numpy().astype(np.float32).flatten()
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def generate_tags(self, image_path):
        if not self.model:
            return []
        
        try:
            image = self.preprocess(Image.open(image_path)).unsqueeze(0).to(self.device)
            text = clip.tokenize(self.config.DEFAULT_LABELS).to(self.device)
            
            with torch.no_grad():
                logits_per_image, _ = self.model(image, text)
                probs = logits_per_image.softmax(dim=-1).cpu().numpy().flatten()
            
            # Filter by confidence threshold
            threshold = self.config.TAG_CONFIDENCE_THRESHOLD
            top_indices = np.where(probs > threshold)[0]
            
            tags = [(self.config.DEFAULT_LABELS[idx], float(probs[idx])) 
                   for idx in top_indices]
            tags.sort(key=lambda x: x[1], reverse=True)
            
            return tags[:self.config.MAX_TAGS_PER_IMAGE]
        except Exception as e:
            print(f"Error generating tags: {e}")
            return []