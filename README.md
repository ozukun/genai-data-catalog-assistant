# GenAI Data Catalog Assistant

Local demo project for a semantic data catalog assistant.

## Purpose

This project loads business catalog metadata such as KPIs, business areas, departments, tables, columns, and entity mappings.

It combines exact entity resolution, semantic search with ChromaDB, catalog relationship traversal, and OpenAI-based answer generation to answer data catalog questions.



<img width="1538" height="1022" alt="AI_2" src="https://github.com/user-attachments/assets/20c99f71-1f45-40ec-b5b1-5c891016c427" />



<img width="1024" height="1536" alt="RAG" src="https://github.com/user-attachments/assets/c99074fd-9ab0-4379-bd3c-5258b2fae921" />


## Architecture

The application combines deterministic catalog resolution with semantic retrieval and graph-based relationship traversal.

1. **QueryService** analyzes the user question and identifies the intent, source entity mentions, and target entity type.
2. **EntityResolverService** attempts to resolve the source entity directly against the catalog.
3. **VectorService** uses ChromaDB as a semantic fallback when an exact catalog entity cannot be resolved.
4. **GraphService** traverses relationships defined in `catalog_entity_mappings.json`.
5. **AnswerService** uses the retrieved catalog context to generate a grounded natural-language answer.

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


## Example End-to-End Query Flow
<img width="1024" height="1536" alt="ETE" src="https://github.com/user-attachments/assets/eeac921f-2382-4855-9b56-f0f1edbb6de5" />


