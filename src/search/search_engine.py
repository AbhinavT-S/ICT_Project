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
        # Retrieve image IDs and their embeddings from the DB
        image_ids, embeddings = self.db_manager.get_all_embeddings()
        if len(embeddings) == 0:
            print("No embeddings found. Process images first.")
            return

        self.image_ids = image_ids
        d = embeddings.shape[1]

        # Create index for inner product (cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(d)
        self.index = faiss.IndexIDMap(self.index)

        # Normalize embeddings before indexing
        faiss.normalize_L2(embeddings)

        # Add embeddings and IDs to index
        self.index.add_with_ids(embeddings.astype(np.float32), np.array(image_ids, dtype=np.int64))
        print(f"FAISS index built with {len(embeddings)} images.")

    def search_similar_images(self, query_text, top_k=10):
        if not self.index or not self.ai_handler.model:
            return []

        try:
            # Preprocess and encode text query
            tokens = self.ai_handler.preprocess_text(query_text).to(self.ai_handler.device)
            with torch.no_grad():
                text_features = self.ai_handler.model.encode_text(tokens)
                text_features = text_features.cpu().numpy().astype(np.float32)

            # Normalize the query embedding vector
            faiss.normalize_L2(text_features)

            # Search to find top_k most similar image embeddings
            scores, indices = self.index.search(text_features, top_k)

            # Collect valid results (filter out -1 which means no result)
            results = [(int(i), float(score)) for i, score in zip(indices[0], scores[0]) if i != -1]

            return results
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return []
