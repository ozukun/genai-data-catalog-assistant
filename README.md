# GenAI Data Catalog Assistant

Local demo project for a semantic data catalog assistant.

## Purpose

This project loads business catalog metadata such as KPIs, business areas, departments, tables, columns, and entity mappings.  
It indexes catalog records into ChromaDB and answers catalog-related questions using OpenAI.

<img width="1538" height="1022" alt="AI_2" src="https://github.com/user-attachments/assets/20c99f71-1f45-40ec-b5b1-5c891016c427" />


## Main files

- `app.py` - FastAPI application
- `index_catalog.py` - indexes catalog files into ChromaDB
- `catalog_loader.py` - loads catalog JSON/CSV files
- `data/Prj_2_Source/` - catalog source files

## Run locally

Create `.env`:

```env
OPENAI_API_KEY=your_api_key
