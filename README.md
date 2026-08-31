# GenAI Data Catalog Assistant

Local demo project for a semantic data catalog assistant.

## Purpose

This project loads business catalog metadata such as KPIs, business areas, departments, tables, columns, and entity mappings.  
It indexes catalog records into ChromaDB and answers catalog-related questions using OpenAI.

<img width="1538" height="1022" alt="AI_2" src="https://github.com/user-attachments/assets/20c99f71-1f45-40ec-b5b1-5c891016c427" />

<img width="1024" height="1536" alt="RAG" src="https://github.com/user-attachments/assets/c99074fd-9ab0-4379-bd3c-5258b2fae921" />

## Main files

## Main files

- `Prj_2/app.py` - FastAPI application and end-to-end query flow
- `Prj_2/index_catalog.py` - creates embeddings and indexes catalog entities into ChromaDB
- `Prj_2/services/query_service.py` - analyzes user questions and extracts intent, entity mentions, and target entity
- `Prj_2/services/entity_resolver_service.py` - resolves exact catalog entities and tracks unresolved terms
- `Prj_2/services/vector_service.py` - performs semantic search over catalog entities in ChromaDB
- `Prj_2/services/graph_service.py` - traverses relationships stored in `catalog_entity_mappings.json`
- `Prj_2/services/answer_service.py` - builds grounded context and generates the final answer
- `Prj_2/Prj_2_Source/` - catalog source JSON/CSV files

## Run locally

Create `.env`:

```env
OPENAI_API_KEY=your_api_key
