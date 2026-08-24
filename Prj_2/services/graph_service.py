import json
from pathlib import Path

from pydantic import BaseModel

from Prj_2.services.entity_resolver_service import (
    ResolvedEntity
)


BASE_DIR = Path(__file__).resolve().parent.parent


class GraphRelation(BaseModel):
    source_entity_type: str
    source_entity_id: str
    relationship: str
    target_entity_type: str
    target_entity_id: str


class GraphResult(BaseModel):
    source_entities: list[ResolvedEntity]
    target_entity: str | None
    relations: list[GraphRelation]


class GraphService:

    def __init__(self):

        with open(
            BASE_DIR
            / "Prj_2_Source"
            / "catalog_entity_mappings.json",
            "r",
            encoding="utf-8"
        ) as f:
            self.mappings = json.load(f)



    def find_direct_relations(
        self,
        source_entity: ResolvedEntity
    ) -> list[GraphRelation]:

        relations = []

        for mapping in self.mappings:

            if (
                mapping.get("source_entity_type")
                == source_entity.entity_type
                and mapping.get("source_entity_name")
                == source_entity.entity_id
            ):
                relations.append(
                    GraphRelation(
                        source_entity_type=mapping[
                            "source_entity_type"
                        ],
                        source_entity_id=mapping[
                            "source_entity_name"
                        ],
                        relationship=mapping[
                            "relationship"
                        ],
                        target_entity_type=mapping[
                            "target_entity_type"
                        ],
                        target_entity_id=mapping[
                            "target_entity_name"
                        ]
                    )
                )

        return relations

    def filter_find_relations(
        self,
        relations: list[GraphRelation],filter_criteria: str
    ) -> list[GraphRelation]:

        filtered_relations = []
        for relation in relations:
            if relation.target_entity_type == filter_criteria:
                filtered_relations.append(relation)

        return filtered_relations

    def search(
        self,
        source_entity: ResolvedEntity,
        target_entity: str,
        max_depth: int = 2
    ) -> GraphResult:

        current_sources = [source_entity]
        current_depth = 0
        found_relations = []

        visited = set()

        while current_sources and current_depth < max_depth:

            next_sources = []

            for current_source in current_sources:

                entity_key = (
                    current_source.entity_type,
                    current_source.entity_id
                )

                if entity_key in visited:
                    continue

                visited.add(entity_key)

                relations = self.find_direct_relations(
                    current_source
                )

                for relation in relations:

                    if relation.target_entity_type == target_entity:
                        found_relations.append(relation)

                    else:
                        next_sources.append(
                            ResolvedEntity(
                                entity_type=relation.target_entity_type,
                                entity_id=relation.target_entity_id,
                                display_name=relation.target_entity_id
                            )
                        )

            current_sources = next_sources
            current_depth += 1

        return GraphResult(
            source_entities=[source_entity],
            target_entity=target_entity,
            relations=found_relations
        )
        

if __name__ == "__main__":

    graph_service = GraphService()

    print(
        f"GraphService loaded "
        f"{len(graph_service.mappings)} mappings."
    )

    print("\nFirst mapping:")

    if graph_service.mappings:
        print(graph_service.mappings[0])

    test_entity = ResolvedEntity(
        entity_type="business_term",
        entity_id="margin",
        display_name="margin"
    )

    relations = graph_service.find_direct_relations(
        test_entity
    )

    print("\nDirect relations:")

    for relation in relations:
        print(relation)


    #print("\nFiltered relations:")
    #print(graph_service.filter_find_relations(relations, "table"))



    graph_result = graph_service.search(
        test_entity,
        "department",
        max_depth=2
    )

    print("\nSearch result:")
    print(graph_result)

