import json
import csv
from pathlib import Path
from typing import Any

import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check .env file.")

openai_client = OpenAI(api_key=api_key)

CATALOG_DIR = Path("data/Prj_2_Source")
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "data_catalog"


def load_json(filename: str) -> Any:
    path = CATALOG_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_csv(filename: str) -> list[dict]:
    path = CATALOG_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def create_embedding(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


def record_to_text(source_file: str, record: dict) -> str:
    return f"""
Source file: {source_file}

Record:
{json.dumps(record, indent=2, ensure_ascii=False)}
""".strip()


def build_documents() -> list[dict]:
    files = [
        ("catalog_business_areas.json", "json"),
        ("catalog_departments.json", "json"),
        ("catalog_entities.csv", "csv"),
        ("catalog_relationships_types.csv", "csv"),
        ("catalog_kpis_v2.json", "json"),
        ("catalog_tables.json", "json"),
        ("catalog_table_columns.json", "json"),
        ("catalog_entity_mappings.json", "json"),
    ]

    documents = []

    for filename, file_type in files:
        if file_type == "json":
            records = load_json(filename)
        else:
            records = load_csv(filename)

        for i, record in enumerate(records):
            text = record_to_text(filename, record)

            documents.append(
                {
                    "id": f"{filename}:{i}",
                    "text": text,
                    "metadata": {
                        "source_file": filename,
                        "record_index": i
                    }
                }
            )

    return documents


def main():
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    documents = build_documents()

    ids = []
    texts = []
    metadatas = []
    embeddings = []

    for doc in documents:
        ids.append(doc["id"])
        texts.append(doc["text"])
        metadatas.append(doc["metadata"])
        embeddings.append(create_embedding(doc["text"]))

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(f"Indexed {len(documents)} catalog records into Chroma collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()