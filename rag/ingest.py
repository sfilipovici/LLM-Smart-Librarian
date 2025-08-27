import json, os, uuid
from dotenv import load_dotenv
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

DB_DIR = os.environ.get("CHROMA_DB_DIR", ".chroma")
COLLECTION = os.environ.get("CHROMA_COLLECTION", "books")
DATA_PATH = os.environ.get("BOOKS_PATH", "data/book_summaries.json")

def stringify_metadata(meta):
    # Convert any list value in metadata to a comma-separated string
    return {k: (", ".join(v) if isinstance(v, list) else v) for k, v in meta.items()}

def main():
    load_dotenv()

    # Wire OpenAI embeddings explicitly (important for querying)
    embedder = OpenAIEmbeddingFunction(
        api_key=os.environ.get("OPENAI_API_KEY"),
        model_name=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    )

    client = chromadb.PersistentClient(path=DB_DIR)
    coll = client.get_or_create_collection(COLLECTION, embedding_function=embedder)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs, metas, ids = [], [], []
    for b in data:
        docs.append(b["summary_short"])
        metas.append({"title": b["title"], "themes": b["themes"]})
        ids.append(str(uuid.uuid4()))

    metas = [stringify_metadata(meta) for meta in metas]

    # Upsert-like behavior: a quick way is to recreate the collection if you want clean state
    # Here we simply add; in real use you'd manage duplicates or clear the collection first.
    coll.add(documents=docs, metadatas=metas, ids=ids)
    print(f"✅ Ingested {len(docs)} docs into '{COLLECTION}' at '{DB_DIR}'")

if __name__ == "__main__":
    main()
