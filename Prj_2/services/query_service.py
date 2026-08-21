import json
from pydantic import BaseModel
from openai import OpenAI
from pathlib import Path
import csv

class QueryAnalysis(BaseModel):
    entity_mentions: list[str]
    intent: str
    target_entity: str | None
    question_type: str


BASE_DIR = Path(__file__).resolve().parent.parent

class QueryService:
    def __init__(self, openai_client: OpenAI):
        self.openai_client = openai_client

        

        with open(f"{BASE_DIR}/kpi_content.txt", "r", encoding="utf-8") as f:
            self.kpi_content = f.read()

    def get_intent(self):
        with open(
            f"{BASE_DIR}/Prj_2_Source/catalog_intents.json",
            "r",
            encoding="utf-8"
        ) as f:
            cat_int = json.load(f)

        intent_list = []

        for intent_obj in cat_int:
            intent_list.append([
                intent_obj["intent_name"],
                intent_obj["intent_description"],
                intent_obj["question_type"]
            ])

        return intent_list

    def get_entities(self):
        with open(
            f"{BASE_DIR}/Prj_2_Source/catalog_entities.csv",
            "r",
            encoding="utf-8"
        ) as f:
            cat_ent = csv.DictReader(f)

            ent_list = []

            for ent_obj in cat_ent:
                ent_list.append([
                    ent_obj["entity_type"],
                    ent_obj["description"]
                ])

        return ent_list





    def analyze(self, question: str) -> QueryAnalysis:
        intent_list = self.get_intent()
        entity_list = self.get_entities()

        prompt_extract = self.kpi_content.format(
            intent_list=intent_list,
            entity_list=entity_list,
            question=question
        )

        response_find = self.openai_client.chat.completions.create(
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

        return QueryAnalysis.model_validate_json(answer_find)

  # FOLLOWING CODE ADD FOR TESTING PURPOSES
  # 

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found.")

    client = OpenAI(api_key=api_key)

    query_service = QueryService(client)

    questions = [
        "Which KPIs are related to Margin?",
        "Which departments are related to Margin?",
        "Which source tables are used by Gross Margin?",
        "Which source columns are used to calculate Gross Margin?",
        "What does Gross Margin mean?",
        "Which KPIs are related to the Finance department?",
        "Show me KPIs related to Customer.",
        "Which department is Customer Churn related to?",
        "Which source tables are used by Revenue?",
        "Explain the metrics related to sales performance."
    ]

    for question in questions:
        print(f"\nQuestion: {question}")

        result = query_service.analyze(question)

        print("Entity Mentions:", result.entity_mentions)
        print("Intent:", result.intent)
        print("Target Entity:", result.target_entity)
        print("Question Type:", result.question_type)