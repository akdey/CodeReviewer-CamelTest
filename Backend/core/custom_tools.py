import logging
from typing import List, Dict
from features.indexed_retriever import IndexedRetriever

logger = logging.getLogger("hacker-society")
retriever = IndexedRetriever()

def semantic_code_search(query: str, n_results: int = 5) -> str:
    """
    Search for code snippets within the codebase using semantic similarity.
    Useful for finding where specific logic is implemented in large repositories.
    
    Args:
        query (str): The search query (e.g., "how is authentication handled?").
        n_results (int): Number of snippets to return.
        
    Returns:
        str: A formatted string containing the relevant code snippets and their locations.
    """
    try:
        results = retriever.query(query, n_results=n_results)
        if not results:
            return "No relevant code snippets found."
            
        output = []
        for res in results:
            path = res['metadata']['path']
            content = res['content']
            output.append(f"--- [FILE: {path}] ---\n{content}\n")
            
        return "\n".join(output)
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return f"Error performing semantic search: {str(e)}"
