# GenAI Data Catalog Assistant

Local demo project for a semantic data catalog assistant.

## Purpose

This project loads business catalog metadata such as KPIs, business areas, departments, tables, columns, and entity mappings.  
It indexes catalog records into ChromaDB and answers catalog-related questions using OpenAI.

<img width="1538" height="1022" alt="AI_2" src="https://github.com/user-attachments/assets/20c99f71-1f45-40ec-b5b1-5c891016c427" />


## Main files

## Main files

- `Prj_2/app.py` - FastAPI application. Handles user questions, AI-based term/intent extraction, graph lookup, vector retrieval, and final answer generation.

- `Prj_2/index_catalog.py` - Indexes catalog JSON/CSV files into ChromaDB for semantic/vector search.

- `Prj_2/catalog_loader.py` - Loads catalog JSON/CSV source files from `data/Prj_2_Source/`.

- `Prj_2/catalog_graph.py` - Deterministic graph-style relationship lookup layer. Uses exact catalog mappings to find related KPIs, departments, tables, and columns.

- `Prj_2/kpi_content.txt` - Prompt used to extract business terms, KPI candidates, department candidates, intent, and question type from the user question.

- `Prj_2/final_prompt.txt` - Prompt used to generate the final answer using graph results and retrieved catalog context.

- `data/Prj_2_Source/` - Source catalog files including business areas, departments, KPIs, tables, columns, intents, relationship types, and entity mappings.

- `chroma_db/` - Local generated ChromaDB vector database folder. This should not be committed to GitHub.

## Run locally

Create `.env`:

```env
OPENAI_API_KEY=your_api_key
