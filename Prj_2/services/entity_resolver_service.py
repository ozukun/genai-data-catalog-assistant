import json
from pathlib import Path

from pydantic import BaseModel

from Prj_2.services.query_service import QueryAnalysis


BASE_DIR = Path(__file__).resolve().parent.parent


class ResolvedEntity(BaseModel):
    entity_type: str
    entity_id: str
    display_name: str


class ResolvedQuery(BaseModel):
    intent: str
    target_entity: str | None
    question_type: str
    source_entities: list[ResolvedEntity]
    unresolved_terms: list[str]


class EntityResolverService:

    def __init__(self):

        # KPI catalog
        with open(
            BASE_DIR / "Prj_2_Source" / "catalog_kpis_v2.json",
            "r",
            encoding="utf-8"
        ) as f:
            self.kpis = json.load(f)

        # Department catalog
        with open(
            BASE_DIR / "Prj_2_Source" / "catalog_departments.json",
            "r",
            encoding="utf-8"
        ) as f:
            self.departments = json.load(f)

        # Table catalog
        with open(
            BASE_DIR / "Prj_2_Source" / "catalog_tables.json",
            "r",
            encoding="utf-8"
        ) as f:
            self.tables = json.load(f)

        # Column catalog
        with open(
            BASE_DIR / "Prj_2_Source" / "catalog_table_columns.json",
            "r",
            encoding="utf-8"
        ) as f:
            self.columns = json.load(f)

        # Business area catalog
        with open(
            BASE_DIR / "Prj_2_Source" / "catalog_business_areas.json",
            "r",
            encoding="utf-8"
        ) as f:
            self.business_areas = json.load(f)

        # Build common entity registry
        self.entity_registry = self.build_entity_registry()


    def normalize(self, value: str) -> str:
        return (
            value
            .strip()
            .lower()
            .replace("_", " ")
        )


    def add_to_registry(
        self,
        registry: dict,
        alias: str,
        entity: ResolvedEntity
    ):

        normalized_alias = self.normalize(alias)

        if normalized_alias not in registry:
            registry[normalized_alias] = []

        # Avoid duplicate entity records
        already_exists = any(
            item.entity_type == entity.entity_type
            and item.entity_id == entity.entity_id
            for item in registry[normalized_alias]
        )

        if not already_exists:
            registry[normalized_alias].append(entity)


    def build_entity_registry(
        self
    ) -> dict[str, list[ResolvedEntity]]:

        registry = {}

        # ------------------------------------------------
        # 1. KPI entities
        # ------------------------------------------------

        for kpi in self.kpis:

            entity = ResolvedEntity(
                entity_type="kpi",
                entity_id=kpi["kpi_id"],
                display_name=kpi["display_name"]
            )

            self.add_to_registry(
                registry,
                kpi["kpi_id"],
                entity
            )

            self.add_to_registry(
                registry,
                kpi["kpi_name"],
                entity
            )

            self.add_to_registry(
                registry,
                kpi["display_name"],
                entity
            )

            # Optional natural-language alias
            self.add_to_registry(
                registry,
                f'{kpi["display_name"]} KPI',
                entity
            )


        # ------------------------------------------------
        # 2. Department entities
        # ------------------------------------------------

        for department in self.departments:

            entity = ResolvedEntity(
                entity_type="department",
                entity_id=department["department_id"],
                display_name=department["department_name"]
            )

            self.add_to_registry(
                registry,
                department["department_id"],
                entity
            )

            self.add_to_registry(
                registry,
                department["department_name"],
                entity
            )

            self.add_to_registry(
                registry,
                f'{department["department_name"]} department',
                entity
            )


        # ------------------------------------------------
        # 3. Table entities
        # ------------------------------------------------

        for table in self.tables:

            entity = ResolvedEntity(
                entity_type="table",
                entity_id=table["table_id"],
                display_name=table["table_name"]
            )

            self.add_to_registry(
                registry,
                table["table_id"],
                entity
            )

            self.add_to_registry(
                registry,
                table["table_name"],
                entity
            )


        # ------------------------------------------------
        # 4. Column entities
        # ------------------------------------------------

        for column in self.columns:

            display_name = (
                f'{column["table_name"]}.'
                f'{column["column_name"]}'
            )

            entity = ResolvedEntity(
                entity_type="column",
                entity_id=column["column_id"],
                display_name=display_name
            )

            self.add_to_registry(
                registry,
                column["column_id"],
                entity
            )

            self.add_to_registry(
                registry,
                display_name,
                entity
            )

        # NOTE:
        # We intentionally do NOT register only column_name
        # such as "margin" or "revenue".
        #
        # Otherwise these can conflict with business terms.


        # ------------------------------------------------
        # 5. Business area entities
        # ------------------------------------------------

        for business_area in self.business_areas:

            entity = ResolvedEntity(
                entity_type="business_area",
                entity_id=business_area["business_area_id"],
                display_name=business_area[
                    "business_area_name"
                ]
            )

            self.add_to_registry(
                registry,
                business_area["business_area_id"],
                entity
            )

            self.add_to_registry(
                registry,
                business_area["business_area_name"],
                entity
            )


        # ------------------------------------------------
        # 6. Business term entities
        # ------------------------------------------------

        business_terms = set()

        source_lists = [
            self.kpis,
            self.departments,
            self.tables,
            self.columns,
            self.business_areas
        ]

        for source_list in source_lists:

            for record in source_list:

                for term in record.get(
                    "business_terms",
                    []
                ):
                    business_terms.add(
                        term.strip().lower()
                    )

        for term in business_terms:

            entity = ResolvedEntity(
                entity_type="business_term",
                entity_id=term,
                display_name=term
            )

            self.add_to_registry(
                registry,
                term,
                entity
            )

        return registry


    def resolve_entity(
        self,
        name: str
    ) -> ResolvedEntity | None:

        normalized_name = self.normalize(name)

        matches = self.entity_registry.get(
            normalized_name,
            []
        )

        if not matches:
            return None

        if len(matches) == 1:
            return matches[0]

        # ------------------------------------------------
        # Ambiguous match priority
        # ------------------------------------------------

        priority = [
            "kpi",
            "department",
            "table",
            "business_area",
            "column",
            "business_term"
        ]

        for entity_type in priority:

            for entity in matches:

                if entity.entity_type == entity_type:
                    return entity

        return matches[0]


    def resolve(
        self,
        query: QueryAnalysis
    ) -> ResolvedQuery:

        source_entities = []
        unresolved_terms = []

        # ------------------------------------------------
        # QueryService now provides only entity_mentions
        # ------------------------------------------------

        for mention in query.entity_mentions:

            entity = self.resolve_entity(mention)

            if entity:
                source_entities.append(entity)

            else:
                unresolved_terms.append(mention)

        return ResolvedQuery(
            intent=query.intent,
            target_entity=query.target_entity,
            question_type=query.question_type,
            source_entities=source_entities,
            unresolved_terms=unresolved_terms
        )


if __name__ == "__main__":

    import os

    from dotenv import load_dotenv
    from openai import OpenAI

    from Prj_2.services.query_service import QueryService

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found."
        )

    client = OpenAI(
        api_key=api_key
    )

    query_service = QueryService(client)

    entity_resolver = EntityResolverService()

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

    TEST_OUTPUT_FILE = (
        BASE_DIR
        / "test_outputs"
        / "entity_resolver_test.txt"
    )

    TEST_OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        TEST_OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as test_file:

        for question in questions:

            raw_query = query_service.analyze(
                question
            )

            resolved_query = (
                entity_resolver.resolve(
                    raw_query
                )
            )

            output = f"""
            ======================================================================
            QUESTION: {question}

            RAW QUERY ANALYSIS
            Entity Mentions: {raw_query.entity_mentions}
            Intent: {raw_query.intent}
            Target Entity: {raw_query.target_entity}
            Question Type: {raw_query.question_type}

            RESOLVED QUERY
            Intent: {resolved_query.intent}
            Target Entity: {resolved_query.target_entity}
            Question Type: {resolved_query.question_type}

            Source Entities:
            {resolved_query.source_entities}

            Unresolved Terms:
            {resolved_query.unresolved_terms}

            """

            test_file.write(output)

    print(
        f"All questions processed. "
        f"Results written to "
        f"{TEST_OUTPUT_FILE}"
    )