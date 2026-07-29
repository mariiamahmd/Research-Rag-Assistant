import os

from qdrant_client import QdrantClient, models
from dotenv import load_dotenv
from qdrant_client.models import Filter
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    PayloadSchemaType,
)

import streamlit as st

load_dotenv()


QDRANT_URL = st.secrets["QDRANT_URL"]
QDRANT_API_KEY = st.secrets["QDRANT_API_KEY"]

print("URL:", repr(QDRANT_URL))
print("API:", QDRANT_API_KEY[:8] if QDRANT_API_KEY else None)
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=120,
)


COLLECTION_NAME = "research_papers"

def clear_collection():
    if collection_exists():
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter()
)

def get_max_chunk_id():
    """Get the highest chunk ID currently in Qdrant"""
    try:
        if not collection_exists():
            return 0
        
        collection = client.get_collection(COLLECTION_NAME)
        if collection.points_count == 0:
            return 0
        
        all_points, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=collection.points_count,
        )
        
        if all_points:
            return max(p.id for p in all_points) + 1
        return 0
        
    except Exception:
        return 0


def create_collection(vector_size):
    try:
        client.get_collection(COLLECTION_NAME)
        print("Collection already exists.")
        return
    except Exception:
        pass

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="filename",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    print("Collection created.")


def upload_chunks(chunks, embeddings):
    batch_size = 25
    next_id = get_max_chunk_id()

    for start in range(0, len(chunks), batch_size):
        end = min(start + batch_size, len(chunks))
        points = []

        for i in range(start, end):
            embedding = embeddings[i]

            if hasattr(embedding, "tolist"):
                embedding = embedding.tolist()

            points.append(
                PointStruct(
                    id=next_id,
                    vector=embedding,
                    payload=chunks[i],
                )
            )
            
            next_id += 1

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True,
        )

        print(f"Uploaded {end}/{len(chunks)}")


def collection_exists():
    try:
        collections = client.get_collections().collections
        return COLLECTION_NAME in [c.name for c in collections]
    except Exception:
        return False


def search(query_vector, limit=5, filenames=None):

    if hasattr(query_vector, "tolist"):
        query_vector = query_vector.tolist()

    search_filter = None

    if filenames:
        search_filter = models.Filter(
            should=[
                models.FieldCondition(
                    key="filename",
                    match=models.MatchValue(value=name)
                )
                for name in filenames
            ]
        )

    return client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        query_filter=search_filter
    ).points


def delete_collection():
    client.delete_collection(COLLECTION_NAME)


def paper_exists(filename):
    if not collection_exists():
        return False

    records, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="filename",
                    match=models.MatchValue(value=filename)
                )
            ]
        ),
        limit=1,
    )

    return len(records) > 0