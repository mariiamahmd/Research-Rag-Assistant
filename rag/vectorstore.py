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

####### Connecting to qdrant DB ##############
QDRANT_URL = st.secrets["QDRANT_URL"]
QDRANT_API_KEY = st.secrets["QDRANT_API_KEY"]


print("URL:", repr(QDRANT_URL))
print("API:", QDRANT_API_KEY[:8] if QDRANT_API_KEY else None)
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=120,
)

#================================================================#

COLLECTION_NAME = "research_papers"

## to start fresh whenever i click on delete all ##
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
        pass # Collection doesn't exist, create it

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,  # 384 (dimension of embeddings)
            distance=Distance.COSINE, # Cosine similarity for comparison
        ),
    )
# Create an index on "filename" for fast filtering
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="filename",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    print("Collection created.")

# Takes chunks and embeddings, packages them into Qdrant points, and uploads them in batches.
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
# data is stored [id + vector embedding +text]
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
 # If user wants to search only specific papers
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
        query=query_vector, # compare question with the chunks
        limit=limit, # return top 5
        query_filter=search_filter
    ).points


def delete_collection():
    client.delete_collection(COLLECTION_NAME)


# Checks if a paper has already been uploaded (prevents duplicates).
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
        limit=1,  # Just check if at least one exists
    )

    return len(records) > 0



def get_uploaded_papers():
    """Return unique filenames stored in Qdrant."""

    if not collection_exists():
        return []

    papers = set()

    offset = None

    while True:
        records, offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        for record in records:
            filename = record.payload.get("filename")
            if filename:
                papers.add(filename)

        if offset is None:
            break

    return sorted(list(papers))