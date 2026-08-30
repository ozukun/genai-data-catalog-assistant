import os

from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel

from Prj_2.services.query_service import QueryService
from Prj_2.services.entity_resolver_service import EntityResolverService
from Prj_2.services.graph_service import GraphService
from Prj_2.services.answer_service import AnswerService


# --------------------------------------------------
# Environment
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found. Check .env file."
    )


# --------------------------------------------------
# FastAPI
# --------------------------------------------------

app = FastAPI(
    title="GenAI Data Catalog Assistant"
)


# --------------------------------------------------
# Shared OpenAI client
# --------------------------------------------------

openai_client = OpenAI(
    api_key=api_key
)


# --------------------------------------------------
# Services
# --------------------------------------------------

query_service = QueryService(
    openai_client=openai_client
)

entity_resolver = EntityResolverService()

graph_service = GraphService()

answer_service = AnswerService()


# --------------------------------------------------
# Request Model
# --------------------------------------------------

class QuestionRequest(BaseModel):
    question: str


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "GenAI Data Catalog Assistant is running"
    }


# --------------------------------------------------
# Ask
# --------------------------------------------------

@app.post("/ask")
def ask_question(
    request: QuestionRequest
):

    question = request.question


    # ----------------------------------------------
    # 1. Understand the question
    # ----------------------------------------------

    query_analysis = query_service.analyze(
        question
    )


    # ----------------------------------------------
    # 2. Resolve catalog entities
    # ----------------------------------------------

    resolved_query = entity_resolver.resolve(
        query_analysis
    )


    # ----------------------------------------------
    # 3. Vector fallback will come here later
    # ----------------------------------------------

    if not resolved_query.source_entities:

        return {
            "question": question,
            "query_analysis": query_analysis,
            "resolved_query": resolved_query,
            "answer": (
                "No exact catalog entity could be resolved. "
                "Semantic vector fallback is not implemented yet."
            )
        }


    # ----------------------------------------------
    # 4. Target entity required for graph search
    # ----------------------------------------------

    if not resolved_query.target_entity:

        return {
            "question": question,
            "query_analysis": query_analysis,
            "resolved_query": resolved_query,
            "answer": (
                "No target entity was identified for "
                "structured graph retrieval."
            )
        }


    # ----------------------------------------------
    # 5. Graph Search
    # ----------------------------------------------

    source_entity = resolved_query.source_entities[0]

    graph_result = graph_service.search(
        source_entity=source_entity,
        target_entity=resolved_query.target_entity,
        max_depth=2
    )


    # ----------------------------------------------
    # 6. Unique target entities
    # ----------------------------------------------

    unique_data = graph_service.get_unique_data(
        graph_result,
        key_fields=(
            "target_entity_type",
            "target_entity_id"
        )
    )


    # ----------------------------------------------
    # 7. Build grounded LLM context
    # ----------------------------------------------

    context = answer_service.build_context(
        question=question,
        graph_result=graph_result,
        unique_data=unique_data
    )


    # ----------------------------------------------
    # 8. Generate final answer
    # ----------------------------------------------

    answer = answer_service.generate_answer(
        context
    )


    # ----------------------------------------------
    # 9. API Response
    # ----------------------------------------------

    return {
        "question": question,
        "query_analysis": query_analysis,
        "resolved_query": resolved_query,
        "graph_result": graph_result,
        "unique_data": unique_data,
        "answer": answer
    }