import os

from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel

from Prj_2.services.query_service import QueryService
from Prj_2.services.entity_resolver_service import (
    EntityResolverService,
    ResolvedEntity
)
from Prj_2.services.graph_service import GraphService
from Prj_2.services.answer_service import AnswerService
from Prj_2.services.vector_service import VectorService


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

vector_service = VectorService(
    openai_client=openai_client
)

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
    # 2. Resolve exact catalog entities
    # ----------------------------------------------

    resolved_query = entity_resolver.resolve(
        query_analysis
    )


    # ----------------------------------------------
    # 3. Semantic vector fallback
    # ----------------------------------------------

    semantic_candidates = []

    if not resolved_query.source_entities:

        for unresolved_term in resolved_query.unresolved_terms:

            candidates = vector_service.search(
                term=unresolved_term,
                limit=3
            )

            semantic_candidates.extend(
                candidates
            )


        # ------------------------------------------
        # No exact or semantic entity found
        # ------------------------------------------

        if not semantic_candidates:

            return {
                "question": question,
                "query_analysis": query_analysis,
                "resolved_query": resolved_query,
                "semantic_candidates": [],
                "answer": (
                    "No relevant catalog entity "
                    "could be found."
                )
            }


        # ------------------------------------------
        # Select best semantic candidate
        # ------------------------------------------

        best_candidate = min(
            semantic_candidates,
            key=lambda candidate: candidate.distance
        )


        # ------------------------------------------
        # Convert semantic candidate
        # into resolved source entity
        # ------------------------------------------

        source_entity = ResolvedEntity(
            entity_type=best_candidate.entity_type,
            entity_id=best_candidate.entity_id,
            display_name=best_candidate.display_name
        )

        resolved_query.source_entities.append(
            source_entity
        )


    # ----------------------------------------------
    # 4. Target entity required for graph search
    # ----------------------------------------------

    if not resolved_query.target_entity:

        return {
            "question": question,
            "query_analysis": query_analysis,
            "resolved_query": resolved_query,
            "semantic_candidates": semantic_candidates,
            "answer": (
                "No target entity was identified for "
                "structured graph retrieval."
            )
        }


    # ----------------------------------------------
    # 5. Select source entity
    # ----------------------------------------------

    source_entity = resolved_query.source_entities[0]


    # ----------------------------------------------
    # 6. Graph Search
    # ----------------------------------------------

    graph_result = graph_service.search(
        source_entity=source_entity,
        target_entity=resolved_query.target_entity,
        max_depth=2
    )


    # ----------------------------------------------
    # 7. Unique target entities
    # ----------------------------------------------

    unique_data = graph_service.get_unique_data(
        graph_result,
        key_fields=(
            "target_entity_type",
            "target_entity_id"
        )
    )


    # ----------------------------------------------
    # 8. Build grounded LLM context
    # ----------------------------------------------

    context = answer_service.build_context(
        question=question,
        graph_result=graph_result,
        unique_data=unique_data
    )


    # ----------------------------------------------
    # 9. Generate final answer
    # ----------------------------------------------

    answer = answer_service.generate_answer(
        context
    )


    # ----------------------------------------------
    # 10. API Response
    # ----------------------------------------------

    return {
        "question": question,
        "query_analysis": query_analysis,
        "resolved_query": resolved_query,
        "semantic_candidates": semantic_candidates,
        "graph_result": graph_result,
        "unique_data": unique_data,
        "answer": answer
    }