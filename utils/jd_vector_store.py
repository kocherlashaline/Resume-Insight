import chromadb
from typing import List, Dict, Callable


def create_store():
    """Create an in-memory ChromaDB store. Returns (client, collection)."""
    try:
        client = chromadb.EphemeralClient()
    except AttributeError:
        client = chromadb.Client()
    collection = client.get_or_create_collection(
        name="jd_store",
        metadata={"hnsw:space": "cosine"},
    )
    return client, collection


def add_jds(collection, jds: List[Dict], embed_fn: Callable) -> None:
    """Embed and store JDs. Each jd dict: {id, title, text, company?}"""
    ids = [jd["id"] for jd in jds]
    texts = [jd["text"][:5000] for jd in jds]
    embeddings = [embed_fn(t) for t in texts]
    metadatas = [
        {"title": jd["title"], "company": jd.get("company", "")}
        for jd in jds
    ]
    collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)


def query_store(collection, question: str, embed_fn: Callable, n_results: int = 5) -> List[Dict]:
    """Semantic search. Returns [{title, company, text, distance}] sorted by relevance."""
    n = min(n_results, collection.count())
    if n == 0:
        return []
    results = collection.query(
        query_embeddings=[embed_fn(question)],
        n_results=n,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "title": results["metadatas"][0][i].get("title", f"JD {i + 1}"),
            "company": results["metadatas"][0][i].get("company", ""),
            "text": results["documents"][0][i],
            "distance": results["distances"][0][i],
        }
        for i in range(len(results["ids"][0]))
    ]
