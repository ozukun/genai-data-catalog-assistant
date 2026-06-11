import json
import csv
from pathlib import Path
from typing import Any

#CATALOG_DIR = Path("catalog")

def load_json(filename):
        path="data/Prj_2_Source/"+filename
        with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

def load_csv(filename):
        path="data/Prj_2_Source/"+filename
        with open(path, "r", encoding="utf-8") as f:
                return list(csv.DictReader(f))

def load_catalog_files():
      c1= { 
                "business_areas":load_json("catalog_business_areas.json") ,
                "departments":load_json("catalog_departments.json") ,
                "entities":load_csv("catalog_entities.csv") ,
                "relationships_types":load_csv("catalog_relationships_types.csv") ,
                "kpi":load_json("catalog_kpis_v2.json") ,
                "tables":load_json("catalog_tables.json") ,
                "table_columns":load_json("catalog_table_columns.json") ,
                "entity_mappings":load_json("catalog_entity_mappings.json") ,
          }
      return c1  

if __name__== "__main__":
        catalog_set1=load_catalog_files()
        print(catalog_set1['business_areas'][0]['description'])
        print(catalog_set1['departments'][0]['source_columns'])
        print(catalog_set1.keys())

    
