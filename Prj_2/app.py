import os
from dotenv import load_dotenv
import json
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import chromadb
from Prj_2.index_catalog import main

load_dotenv()



api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check .env file.")

app = FastAPI(title="GenAI Data Catalog Assistant")

openai_client = OpenAI(api_key=api_key)
chroma_client = chromadb.PersistentClient(path="./chroma_db")



with open("Prj_2/kpi_content.txt", "r", encoding="utf-8") as f:
    kpi_content = f.read()
#print(kpi_content)

with open("Prj_2/final_prompt.txt", "r", encoding="utf-8") as f:
    final_prompt = f.read()

class QuestionRequest(BaseModel):
    question: str


def get_intent():
        with open("data/Prj_2_Source/catalog_intents.json", "r", encoding="utf-8") as f:
            cat_int = json.load(f)
            intent_list=[]
            for intent_obj in cat_int:
                    intent_list.append( [intent_obj['intent_name'],intent_obj['intent_description'],intent_obj['question_type']] )
            return intent_list

def create_embedding(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding

def get_collection():
    return chroma_client.get_or_create_collection(
        name="data_catalog"
    )

@app.get("/")
def root():
    return {
        "message": "GenAI Data Catalog Assistant is running"
    }

@app.get("/debug/count")
def debug_count():
    return {
        "collection_count": collection.count()
    }

@app.get("/load data")
def load_data():
       main()

@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question
    question_embedding = create_embedding(question)

    intent_list = get_intent()
    
    prompt_extract = kpi_content.format(
    intent_list=intent_list,
    question=question
    )
    print(prompt_extract)
    response_find = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt_extract
                
            }
        ],
        temperature=0
    )

    answer_find = response_find.choices[0].message.content
    answer_find_json=json.loads(answer_find)
    #return answer_find_json['business_terms']
    
    with open("data/Prj_2_Source/catalog_entity_mappings.json", "r", encoding="utf-8") as f:
        cat_em = json.load(f)
    
    list_key_kpi=[]
    for answer_key in answer_find_json['business_terms']  :
        for k in cat_em:
            if answer_key in (k['source_entity_name']) and k['relationship']=='refers_to' and k['target_entity_type']=='kpi':
                list_key_kpi.append(k['target_entity_name']) 

    related_kpis= list(set(list_key_kpi))

    updated_question= f"{question} , related kpis:{related_kpis}"
    question_embedding_upd = create_embedding(updated_question)           

    print(answer_find_json['question_type'])
    if answer_find_json['question_type']=="structured":
        n_results_var=10
    elif answer_find_json['question_type']=="semantic":
        n_results_var=20
    else:
        return f"Error in n_result parameter  {answer_find_json}"

    collection=get_collection()
    results = collection.query(
        query_embeddings=[question_embedding_upd],
        n_results=n_results_var
    )

    retrieved_context = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, metadata, distance in zip(documents, metadatas, distances):
        retrieved_context.append(
            {
                "source_file": metadata.get("source_file"),
                "record_index": metadata.get("record_index"),
                "distance": distance,
                "content": doc
            }
        )


    prompt_extract_2 = final_prompt.format(
    question=question,
    retrieved_context=retrieved_context
    )    



    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a careful data catalog assistant. Do not invent facts."
            },
            {
                "role": "user",
                "content": prompt_extract_2
            }
        ],
        temperature=0
    )

    answer = response.choices[0].message.content

    return {
    "question": question,
    "extracted_terms": answer_find_json,
    "related_kpis": related_kpis,
    "updated_question": updated_question,
    "retrieved_context": retrieved_context,
    "answer": answer
    } 