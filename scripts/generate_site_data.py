import json
import os
import shutil
from datetime import datetime, timezone

from rdflib import Graph
from rdflib.namespace import RDF

from tei_csv_to_rdf import WIKIDATA, TYPES, WD, SCHEMA, DCT

SOURCE_FILES_FOR_SITE = [
    ("tei", "tei_encoding.xml"),
    ("scripts", "tei_csv_to_rdf.py"),
]

NAME_PROP = SCHEMA.name
DESCRIPTION_PROP = DCT.description

MAIN_IDS = set(TYPES.keys())
EXTRA_IDS = set(WIKIDATA.keys()) - MAIN_IDS
SUBJECT_ID = "hattori_hanzo"

CLASS_LABELS = {
    "crm:E21_Person": "Person",
    "skos:Concept": "Concept",
    "schema:Place": "Place",
    "crm:E74_Group": "Organization / School",
    "schema:Book": "Book",
    "crm:E22_Human-Made_Object": "Object",
    "schema:Museum": "Museum",
    "schema:VideoGame": "Video Game",
    "schema:Event": "Event",
    "schema:AdministrativeArea": "Region / Province",
    "schema:LandmarksOrHistoricalBuildings": "Landmark",
    "schema:Corporation": "Corporation",
    "foaf:Person": "Person",
    "foaf:Organization": "Organization",
}


def load_graph(turtle_file):
    g = Graph()
    g.parse(turtle_file, format="turtle")
    return g


def qid_to_id():
    return {qid: entity_id for entity_id, qid in WIKIDATA.items()}


def entity_uri_to_id(uri, by_qid):
    if not str(uri).startswith(str(WD)):
        return None
    qid = str(uri)[len(str(WD)):]
    return by_qid.get(qid)


def build_entity(g, entity_id):
    uri = WD[WIKIDATA[entity_id]]

    SECONDARY_PREFIXES = ("foaf:", "edm:")
    types = sorted(g.qname(t) for t in g.objects(uri, RDF.type))
    primary_type = next((t for t in types if not t.startswith(SECONDARY_PREFIXES)), types[0] if types else None)
    type_label = CLASS_LABELS.get(primary_type, primary_type or "Unknown")

    label = str(next(g.objects(uri, NAME_PROP), entity_id))
    descriptions = [str(o) for o in g.objects(uri, DESCRIPTION_PROP)]

    return {
        "id": entity_id,
        "qid": WIKIDATA[entity_id],
        "uri": str(uri),
        "label": label,
        "type": type_label,
        "type_qname": primary_type,
        "descriptions": descriptions,
        "is_extra": entity_id in EXTRA_IDS,
    }


def build_relations(g, by_qid):
    relations = []
    for s, p, o in g:
        if p in (RDF.type, NAME_PROP, DESCRIPTION_PROP):
            continue
        if not str(o).startswith(str(WD)):
            continue  # literal fact, not an entity-to-entity relation

        subj_id = entity_uri_to_id(s, by_qid)
        obj_id = entity_uri_to_id(o, by_qid)
        if subj_id is None or obj_id is None:
            continue

        relations.append({
            "subject": subj_id,
            "subject_label": WIKIDATA_LABELS.get(subj_id, subj_id),
            "predicate": g.qname(p),
            "object": obj_id,
            "object_label": WIKIDATA_LABELS.get(obj_id, obj_id),
        })

    relations.sort(key=lambda r: (r["subject_label"], r["predicate"], r["object_label"]))
    return relations


def copy_source_files(base):
    assets_dir = os.path.join(base, "docs", "assets")
    os.makedirs(assets_dir, exist_ok=True)
    for subdir, filename in SOURCE_FILES_FOR_SITE:
        shutil.copyfile(
            os.path.join(base, subdir, filename),
            os.path.join(assets_dir, filename),
        )


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    base = os.path.dirname(here)
    turtle_file = os.path.join(base, "turtle", "ninja_merged.ttl")
    data_dir = os.path.join(base, "docs", "data")
    os.makedirs(data_dir, exist_ok=True)

    copy_source_files(base)

    g = load_graph(turtle_file)
    by_qid = qid_to_id()

    entities = [build_entity(g, entity_id) for entity_id in WIKIDATA]

    global WIKIDATA_LABELS
    WIKIDATA_LABELS = {e["id"]: e["label"] for e in entities}

    relations = build_relations(g, by_qid)

    subject = next(e for e in entities if e["id"] == SUBJECT_ID)
    main_entities = sorted(
        (e for e in entities if e["id"] in MAIN_IDS and e["id"] != SUBJECT_ID),
        key=lambda e: e["label"],
    )
    extra_entities = sorted(
        (e for e in entities if e["id"] in EXTRA_IDS),
        key=lambda e: e["label"],
    )

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "counts": {
            "entities": len(entities),
            "relations": len(relations),
        },
        "subject": subject,
        "entities": main_entities,
        "extra_entities": extra_entities,
        "relations": relations,
    }

    out_file = os.path.join(data_dir, "graph.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(entities)} entities and {len(relations)} relations to docs/data/graph.json")


if __name__ == "__main__":
    main()
