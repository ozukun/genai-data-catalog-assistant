# GenAI Data Catalog Assistant

Local demo project for a semantic data catalog assistant.

## Purpose

This project loads business catalog metadata such as KPIs, business areas, departments, tables, columns, and entity mappings.  
It indexes catalog records into ChromaDB and answers catalog-related questions using OpenAI.

## Main files

- `app.py` - FastAPI application
- `index_catalog.py` - indexes catalog files into ChromaDB
- `catalog_loader.py` - loads catalog JSON/CSV files
- `data/Prj_2_Source/` - catalog source files

## Run locally

Create `.env`:

```env
OPENAI_API_KEY=your_api_key
