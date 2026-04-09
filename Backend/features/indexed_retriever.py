import os
import logging
import chromadb
from typing import List, Dict
from core.settings import settings
from camel.embeddings import OpenAIEmbedding, AzureEmbedding
from camel.types import ModelPlatformType

logger = logging.getLogger("hacker-society")

class IndexedRetriever:
    """
    Semantic search engine for large codebases using ChromaDB.
    """
    def __init__(self, collection_name: str = "sentinel_elite_code"):
        self.db_path = os.path.join(os.getcwd(), "chroma_db")
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        # Detect provider for embeddings
        provider = os.getenv("ACTIVE_PROVIDER", "openai").lower()
        if provider == "azure":
            self.embed_model = AzureEmbedding(
                url=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_API_VERSION")
            )
        else:
            self.embed_model = OpenAIEmbedding(model_platform=ModelPlatformType.OPENAI)
        
    def index_codebase(self, root_path: str):
        """
        Walks the codebase, chunks files, and populates the vector store.
        """
        logger.info(f"Indexing codebase at {root_path} into ChromaDB...")
        
        # extensions to index
        valid_ext = {'.py', '.js', '.ts', '.env', '.json', '.md', '.txt'}
        
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'node_modules', '__pycache__', 'venv', '.venv'}]
            
            for file in files:
                if any(file.endswith(ext) for ext in valid_ext):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if not content.strip():
                                continue
                                
                            # Simple chunking logic (500 chars)
                            # In production, use more sophisticated chunking
                            chunks = [content[i:i + 1000] for i in range(0, len(content), 800)]
                            
                            for idx, chunk in enumerate(chunks):
                                chunk_id = f"{path}_{idx}"
                                self.collection.add(
                                    documents=[chunk],
                                    ids=[chunk_id],
                                    metadatas=[{"path": path, "chunk_index": idx}]
                                )
                    except Exception as e:
                        logger.error(f"Failed to index {path}: {e}")

        logger.info("Indexing complete.")

    def query(self, text: str, n_results: int = 5) -> List[Dict]:
        """
        Performs semantic search across the codebase.
        """
        results = self.collection.query(
            query_texts=[text],
            n_results=n_results
        )
        
        formatted = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                formatted.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i]
                })
        return formatted
