import json
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
import os


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found. Check .env file."
    )


BASE_DIR = Path(__file__).resolve().parent
CATALOG_DIR = BASE_DIR / "Prj_2_Source"

CHROMA_PATH = BASE_DIR.parent / "chroma_db"
COLLECTION_NAME = "catalog_entities"


openai_client = OpenAI(
    api_key=api_key
)

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


def load_json(
    filename: str
) -> list[dict]:

    path = CATALOG_DIR / filename

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def create_embedding(
    text: str
) -> list[float]:

    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


def join_values(
    values: list
) -> str:

    return ", ".join(
        str(value)
        for value in values
    )


# ------------------------------------------------
# KPI
# ------------------------------------------------

def build_kpi_documents() -> list[dict]:

    kpis = load_json(
        "catalog_kpis_v2.json"
    )

    documents = []

    for kpi in kpis:

        business_terms = join_values(
            kpi.get(
                "business_terms",
                []
            )
        )

        departments = join_values(
            kpi.get(
                "departments",
                []
            )
        )

        source_tables = join_values(
            kpi.get(
                "source_tables",
                []
            )
        )

        source_columns = join_values(
            kpi.get(
                "source_columns",
                []
            )
        )

        text = f"""
Entity type: KPI
Name: {kpi["display_name"]}
Description: {kpi.get("description", "")}
Business terms: {business_terms}
Departments: {departments}
Source tables: {source_tables}
Source columns: {source_columns}
""".strip()

        document = {
            "id": f'kpi:{kpi["kpi_id"]}',
            "text": text,
            "metadata": {
                "entity_type": "kpi",
                "entity_id": kpi["kpi_id"],
                "display_name": kpi["display_name"]
            }
        }

        documents.append(
            document
        )

    return documents


# ------------------------------------------------
# Department
# ------------------------------------------------

def build_department_documents() -> list[dict]:

    departments = load_json(
        "catalog_departments.json"
    )

    documents = []

    for department in departments:

        business_terms = join_values(
            department.get(
                "business_terms",
                []
            )
        )

        related_kpis = join_values(
            department.get(
                "related_kpis",
                []
            )
        )

        related_tables = join_values(
            department.get(
                "related_tables",
                []
            )
        )

        business_areas = join_values(
            department.get(
                "business_area_ids",
                []
            )
        )

        text = f"""
Entity type: Department
Name: {department["department_name"]}
Business areas: {business_areas}
Related KPIs: {related_kpis}
Related tables: {related_tables}
Business terms: {business_terms}
""".strip()

        document = {
            "id": (
                f'department:'
                f'{department["department_id"]}'
            ),
            "text": text,
            "metadata": {
                "entity_type": "department",
                "entity_id": department[
                    "department_id"
                ],
                "display_name": department[
                    "department_name"
                ]
            }
        }

        documents.append(
            document
        )

    return documents


# ------------------------------------------------
# Table
# ------------------------------------------------

def build_table_documents() -> list[dict]:

    tables = load_json(
        "catalog_tables.json"
    )

    documents = []

    for table in tables:

        business_terms = join_values(
            table.get(
                "business_terms",
                []
            )
        )

        departments = join_values(
            table.get(
                "departments",
                []
            )
        )

        related_kpis = join_values(
            table.get(
                "related_kpis",
                []
            )
        )

        business_areas = join_values(
            table.get(
                "business_area_ids",
                []
            )
        )

        text = f"""
Entity type: Table
Name: {table["table_name"]}
Business areas: {business_areas}
Related KPIs: {related_kpis}
Departments: {departments}
Business terms: {business_terms}
""".strip()

        document = {
            "id": f'table:{table["table_id"]}',
            "text": text,
            "metadata": {
                "entity_type": "table",
                "entity_id": table["table_id"],
                "display_name": table["table_name"]
            }
        }

        documents.append(
            document
        )

    return documents


# ------------------------------------------------
# Column
# ------------------------------------------------

def build_column_documents() -> list[dict]:

    columns = load_json(
        "catalog_table_columns.json"
    )

    documents = []

    for column in columns:

        business_terms = join_values(
            column.get(
                "business_terms",
                []
            )
        )

        departments = join_values(
            column.get(
                "departments",
                []
            )
        )

        related_kpis = join_values(
            column.get(
                "related_kpis",
                []
            )
        )

        business_areas = join_values(
            column.get(
                "business_area_ids",
                []
            )
        )

        display_name = (
            f'{column["table_name"]}.'
            f'{column["column_name"]}'
        )

        text = f"""
Entity type: Column
Name: {display_name}
Table: {column["table_name"]}
Column: {column["column_name"]}
Business areas: {business_areas}
Related KPIs: {related_kpis}
Departments: {departments}
Business terms: {business_terms}
""".strip()

        document = {
            "id": (
                f'column:'
                f'{column["column_id"]}'
            ),
            "text": text,
            "metadata": {
                "entity_type": "column",
                "entity_id": column[
                    "column_id"
                ],
                "display_name": display_name
            }
        }

        documents.append(
            document
        )

    return documents


# ------------------------------------------------
# Business Area
# ------------------------------------------------

def build_business_area_documents() -> list[dict]:

    business_areas = load_json(
        "catalog_business_areas.json"
    )

    documents = []

    for business_area in business_areas:

        business_terms = join_values(
            business_area.get(
                "business_terms",
                []
            )
        )

        related_departments = join_values(
            business_area.get(
                "related_departments",
                []
            )
        )

        related_kpis = join_values(
            business_area.get(
                "related_kpis",
                []
            )
        )

        related_tables = join_values(
            business_area.get(
                "related_tables",
                []
            )
        )

        text = f"""
Entity type: Business Area
Name: {business_area["business_area_name"]}
Description: {business_area.get("description", "")}
Related departments: {related_departments}
Related KPIs: {related_kpis}
Related tables: {related_tables}
Business terms: {business_terms}
""".strip()

        document = {
            "id": (
                f'business_area:'
                f'{business_area["business_area_id"]}'
            ),
            "text": text,
            "metadata": {
                "entity_type": "business_area",
                "entity_id": business_area[
                    "business_area_id"
                ],
                "display_name": business_area[
                    "business_area_name"
                ]
            }
        }

        documents.append(
            document
        )

    return documents


# ------------------------------------------------
# Business Term
# ------------------------------------------------

def build_business_term_documents() -> list[dict]:

    source_files = [
        "catalog_kpis_v2.json",
        "catalog_departments.json",
        "catalog_tables.json",
        "catalog_table_columns.json",
        "catalog_business_areas.json"
    ]

    business_terms = set()

    for filename in source_files:

        records = load_json(
            filename
        )

        for record in records:

            terms = record.get(
                "business_terms",
                []
            )

            for term in terms:

                business_terms.add(
                    term.strip().lower()
                )

    documents = []

    for term in sorted(
        business_terms
    ):

        text = f"""
Entity type: Business Term
Name: {term}
Business concept: {term}
""".strip()

        document = {
            "id": f"business_term:{term}",
            "text": text,
            "metadata": {
                "entity_type": "business_term",
                "entity_id": term,
                "display_name": term
            }
        }

        documents.append(
            document
        )

    return documents


# ------------------------------------------------
# Build all entity documents
# ------------------------------------------------

def build_documents() -> list[dict]:

    documents = []

    documents.extend(
        build_kpi_documents()
    )

    documents.extend(
        build_department_documents()
    )

    documents.extend(
        build_table_documents()
    )

    documents.extend(
        build_column_documents()
    )

    documents.extend(
        build_business_area_documents()
    )

    documents.extend(
        build_business_term_documents()
    )

    return documents


# ------------------------------------------------
# Main
# ------------------------------------------------

def main():

    try:
        chroma_client.delete_collection(
            COLLECTION_NAME
        )

    except Exception:
        pass

    collection = (
        chroma_client.get_or_create_collection(
            name=COLLECTION_NAME
        )
    )

    documents = build_documents()

    ids = []
    texts = []
    metadatas = []
    embeddings = []

    for document in documents:

        embedding = create_embedding(
            document["text"]
        )

        ids.append(
            document["id"]
        )

        texts.append(
            document["text"]
        )

        metadatas.append(
            document["metadata"]
        )

        embeddings.append(
            embedding
        )

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(
        f"Indexed {len(documents)} catalog entities "
        f"into Chroma collection "
        f"'{COLLECTION_NAME}'."
    )


if __name__ == "__main__":
    main()