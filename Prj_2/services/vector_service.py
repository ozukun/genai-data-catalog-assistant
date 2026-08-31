import json
from pathlib import Path

import chromadb
from openai import OpenAI
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_PATH = BASE_DIR.parent / "chroma_db"
COLLECTION_NAME = "catalog_entities"


class SemanticCandidate(BaseModel):
    entity_type: str
    entity_id: str
    display_name: str
    distance: float


class VectorService:

    def __init__(
        self,
        openai_client: OpenAI
    ):

        self.openai_client = openai_client

        self.chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )

        self.collection = (
            self.chroma_client.get_or_create_collection(
                name=COLLECTION_NAME
            )
        )

    def create_embedding(
        self,
        text: str
    ) -> list[float]:

        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )

        return response.data[0].embedding

    def search(
        self,
        term: str,
        limit: int = 3,
        max_distance: float = 1.30
    ) -> list[SemanticCandidate]:

        query_embedding = self.create_embedding(
            term
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )

        candidates = []

        if not results["ids"]:
            return candidates

        ids = results["ids"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for i in range(len(ids)):

            distance = distances[i]

            if distance > max_distance:
                continue

            metadata = metadatas[i]

            candidate = SemanticCandidate(
                entity_type=metadata["entity_type"],
                entity_id=metadata["entity_id"],
                display_name=metadata["display_name"],
                distance=distance
            )

            candidates.append(
                candidate
            )

        return candidates