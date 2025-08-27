import os
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

DB_DIR = os.environ.get("CHROMA_DB_DIR", ".chroma")
COLLECTION = os.environ.get("CHROMA_COLLECTION", "books")

# set up a persistent client with the SAME embedding function used at ingest
_embedder = OpenAIEmbeddingFunction(
    api_key=os.environ.get("CHROMA_OPENAI_API_KEY"),
    model_name=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
)
_client = chromadb.PersistentClient(path=DB_DIR)
_coll = _client.get_or_create_collection(COLLECTION, embedding_function=_embedder)

def retrieve(query: str, k: int = 5):
    """
    Semantic search over short summaries; returns list of {title, themes, document}.
    """
    res = _coll.query(query_texts=[query], n_results=k)
    out = []
    if not res or not res.get("ids"):
        return out
    for i in range(len(res["ids"][0])):
        out.append({
            "document": res["documents"][0][i],
            "metadata": res["metadatas"][0][i]  # contains title + themes
        })
    return out
