# GenAI Data Catalog Assistant

Local demo project for a semantic data catalog assistant.

## Purpose

This project loads business catalog metadata such as KPIs, business areas, departments, tables, columns, and entity mappings.  
It indexes catalog records into ChromaDB and answers catalog-related questions using OpenAI.

<img width="1572" height="1001" alt="data_model_sc" src="https://github.com/user-attachments/assets/608629b2-7902-4ce9-850c-3c5c1a703751" />


## Main files

- `app.py` - FastAPI application
- `index_catalog.py` - indexes catalog files into ChromaDB
- `catalog_loader.py` - loads catalog JSON/CSV files
- `data/Prj_2_Source/` - catalog source files

## Run locally

Create `.env`:

```env
OPENAI_API_KEY=your_api_key
