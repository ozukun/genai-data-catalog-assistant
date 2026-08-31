import os

from dotenv import load_dotenv
from openai import OpenAI

from Prj_2.services.vector_service import VectorService


load_dotenv()


def test_vector_search():

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found."
        )

    client = OpenAI(
        api_key=api_key
    )

    vector_service = VectorService(
        openai_client=client
    )

    test_terms = [
        "profitability",
        "sales performance",
        "buying expenses",
        "Customer",
        "Customer Churn"
    ]

    for term in test_terms:

        results = vector_service.search(
            term=term,
            limit=3
        )

        print("\n" + "=" * 60)
        print(f"QUERY: {term}")
        print("=" * 60)

        if not results:
            print("No semantic candidate found.")
            continue

        for result in results:
            print(
                result.entity_type,
                result.entity_id,
                result.display_name,
                result.distance
            )


if __name__ == "__main__":
    test_vector_search()