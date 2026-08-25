from Prj_2.services.graph_service import GraphResult


class AnswerService:

    def __init__(self):
        pass

    def build_context(
        self,
        question: str,
        graph_result: GraphResult,
        unique_data: list[tuple]
    ) -> str:

        source_lines = []

        for source in graph_result.source_entities:
            source_lines.append(
                f"{source.entity_type}:{source.entity_id}"
            )

        result_lines = []

        for item in unique_data:
            result_lines.append(
                ":".join(item)
            )

        context = f"""
Question:
{question}

Source Entities:
{chr(10).join(source_lines)}

Target Entity:
{graph_result.target_entity}

Resolved Results:
{chr(10).join(result_lines)}
"""

        return context.strip()



if __name__ == "__main__":

    from Prj_2.services.entity_resolver_service import ResolvedEntity
    from Prj_2.services.graph_service import GraphResult, GraphRelation

    answer_service = AnswerService()

    test_graph_result = GraphResult(
        source_entities=[
            ResolvedEntity(
                entity_type="business_term",
                entity_id="margin",
                display_name="margin"
            )
        ],
        target_entity="department",
        relations=[
            GraphRelation(
                source_entity_type="kpi",
                source_entity_id="gross_margin",
                relationship="mapped_to_department",
                target_entity_type="department",
                target_entity_id="Sales"
            ),
            GraphRelation(
                source_entity_type="kpi",
                source_entity_id="gross_margin",
                relationship="mapped_to_department",
                target_entity_type="department",
                target_entity_id="Finance"
            )
        ]
    )

    test_unique_data = [
        ("department", "Sales"),
        ("department", "Finance"),
        ("department", "Purchasing")
    ]

    question = "Which departments are related to Margin?"

    context = answer_service.build_context(
        question,
        test_graph_result,
        test_unique_data
    )

    print("\nGenerated Context:")
    print(context)