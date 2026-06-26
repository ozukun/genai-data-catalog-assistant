from Prj_2.index_catalog import load_json,load_csv

def find_kpis_by_business_term(term: str, mappings: list[dict]) -> list[str]:
    result = []

    for mapping in mappings:
        if (
            mapping.get("source_entity_type") == "business_term"
            and mapping.get("source_entity_name", "").lower() == term.lower()
            and mapping.get("relationship") == "refers_to"
            and mapping.get("target_entity_type") == "kpi"
        ):
            result.append(mapping.get("target_entity_name"))

    return sorted(set(result))


def find_departments_by_kpis(kpi_names: list[str], kpis: list[dict]) -> list[str]:
    departments = set()

    for kpi in kpis:
        if kpi.get("kpi_name") in kpi_names:
            for department in kpi.get("departments", []):
                departments.add(department)

    return sorted(departments)


def find_departments_by_business_terms(
    business_terms: list[str],
    mappings: list[dict],
    kpis: list[dict]
) -> dict:
    all_related_kpis = []

    for term in business_terms:
        related_kpis = find_kpis_by_business_term(term, mappings)
        all_related_kpis.extend(related_kpis)

    all_related_kpis = sorted(set(all_related_kpis))

    departments = find_departments_by_kpis(
        all_related_kpis,
        kpis
    )

    return {
        "business_terms": business_terms,
        "related_kpis": all_related_kpis,
        "departments": departments
    }


if __name__=="__main__":
    mappings = load_json("catalog_entity_mappings.json")
    kpis = load_json("catalog_kpis_v2.json")

    test_terms = ["margin"]

    result = find_departments_by_business_terms(
        business_terms=test_terms,
        mappings=mappings,
        kpis=kpis
    )
    print(result)