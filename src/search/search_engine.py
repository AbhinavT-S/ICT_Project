import numpy as np
import faiss
import torch

class SearchEngine:
    def __init__(self, db_manager, ai_handler, config):
        self.db_manager = db_manager
        self.ai_handler = ai_handler
        self.config = config
        self.index = None
        self.image_ids = []

    def build_index(self):
        # Retrieve all image embeddings and their IDs from the database
        image_ids, embeddings = self.db_manager.get_all_embeddings()
        if len(embeddings) == 0:
            print("No embeddings found. Process images first.")
            return

        self.image_ids = image_ids
        d = embeddings.shape[1]
        # Inner product for CLIP. For cosine similarity, embeddings must be normalized
        self.index = faiss.IndexFlatIP(d)
        self.index = faiss.IndexIDMap(self.index)
        # Make sure embeddings are float32
        vectors = embeddings.astype(np.float32)
        # Add vectors and corresponding image IDs to the index
        self.index.add_with_ids(vectors, np.array(image_ids, dtype=np.int64))
        print(f"FAISS index built with {len(embeddings)} images.")

    def search_similar_images(self, query_text, top_k=10):
        """
        Search for images semantically similar to user's text query.
        Returns a list of tuples: (image_id, similarity_score)
        """
        if not self.index or not self.ai_handler.model:
            return []

        try:
            text = self.ai_handler.preprocess_text(query_text).to(self.ai_handler.device)
            with torch.no_grad():
                text_features = self.ai_handler.model.encode_text(text)
                text_features = text_features.cpu().numpy().astype(np.float32)
            # Normalize for cosine if desired
            # faiss.normalize_L2(text_features)
            scores, indices = self.index.search(text_features, top_k)
            results = []
            for i, score in zip(indices[0], scores[0]):
                if i != -1:
                    results.append((int(i), float(score)))
            return results
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []