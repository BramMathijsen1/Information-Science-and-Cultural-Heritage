import csv
import os
import xml.etree.ElementTree as ET

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD, FOAF, OWL

CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
SCHEMA = Namespace("https://schema.org/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DCT = Namespace("http://purl.org/dc/terms/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")
WD = Namespace("http://www.wikidata.org/entity/")
VIAF = Namespace("https://viaf.org/viaf/")
GEONAMES = Namespace("https://sws.geonames.org/")
LOC = Namespace("https://id.loc.gov/authorities/names/")
DBR = Namespace("http://dbpedia.org/resource/")
EAC = Namespace("http://archivi.ibc.regione.emilia-romagna.it/ontology/eac-cpf/")
NINJA = Namespace("http://example.org/ninja-ontology#")
EDM = Namespace("http://www.europeana.eu/schemas/edm/")

EDM_PROVIDED_CHO_IDS = {"kunai", "mizugumo", "bansenshukai"}

TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

E22_HUMAN_MADE_OBJECT = CRM["E22_Human-Made_Object"]  # hyphen breaks attribute access

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)  # Ninja/
TEI_FILE = os.path.join(BASE, "tei", "tei_encoding.xml")
CSV_DIR = os.path.join(BASE, "csv")
TURTLE_DIR = os.path.join(BASE, "turtle")

# Every entity's identifiers live in its own @ref/@sameAs (TEI) or a "has
# wikidata id" row (CSV) — not a separate hand-maintained mapping.
NAME_TAGS = ("persName", "placeName", "orgName", "eventName", "title")


def find_all_refs(el):
    """Whitespace-separated URIs in this entity's name-child @ref, or its
    own @sameAs for <category>, which has no name-child."""
    for tag in NAME_TAGS:
        child = el.find(TEI + tag)
        if child is not None and child.get("ref"):
            return child.get("ref").split()

    obj_name = el.find(TEI + "objectIdentifier/" + TEI + "objectName")
    if obj_name is not None and obj_name.get("ref"):
        return obj_name.get("ref").split()

    same_as = el.get("sameAs")
    if same_as:
        return same_as.split()

    return []


def find_wikidata_qid(el):
    for ref in find_all_refs(el):
        if ref.startswith(str(WD)):
            return ref.rsplit("/", 1)[-1]
    return None


def collect_wikidata_ids(tei_file, csv_dir):
    ids = {}

    tree = ET.parse(tei_file)
    for el in tree.getroot().iter():
        xml_id = el.get(XML_ID)
        qid = find_wikidata_qid(el)
        if xml_id and qid:
            ids[xml_id] = qid

    for filename in sorted(os.listdir(csv_dir)):
        if not filename.endswith(".csv"):
            continue
        with open(os.path.join(csv_dir, filename), encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # header row
            for row in reader:
                if not row or row[0].strip().startswith("#"):
                    continue
                subject, predicate, obj = (cell.strip() for cell in row)
                if predicate == "has wikidata id":
                    ids[subject] = obj

    return ids


def collect_same_as_uris(tei_file):
    """xml:id -> every @ref/@sameAs URI other than the Wikidata one."""
    ids = {}
    tree = ET.parse(tei_file)
    for el in tree.getroot().iter():
        xml_id = el.get(XML_ID)
        if xml_id is None:
            continue
        extra = [ref for ref in find_all_refs(el) if not ref.startswith(str(WD))]
        if extra:
            ids[xml_id] = extra
    return ids


WIKIDATA = collect_wikidata_ids(TEI_FILE, CSV_DIR)
SAME_AS = collect_same_as_uris(TEI_FILE)


def uri(entity_id):
    return URIRef(WD + WIKIDATA[entity_id])


TYPES = {
    "hattori_hanzo": CRM.E21_Person,
    "ninja": SKOS.Concept,
    "ninjutsu": SKOS.Concept,
    "iga_province": SCHEMA.Place,
    "iga_ryu": CRM.E74_Group,
    "bansenshukai": SCHEMA.Book,
    "mizugumo": E22_HUMAN_MADE_OBJECT,
    "kunai": E22_HUMAN_MADE_OBJECT,
    "ninja_museum": SCHEMA.Museum,
    "ghost_tsushima": SCHEMA.VideoGame,
    "kaminogo_siege": SCHEMA.Event,
}

# born_in -> schema:homeLocation, NOT schema:birthPlace: that's reserved for
# the CSV's sourced "was born in" fact (Mikawa Province). Both mapping to
# birthPlace would assert two different birthplaces for the same person.
RELATIONS = {
    "member_of": CRM.P107i_is_current_or_former_member_of,
    "embodies": NINJA.embodiesArchetype,
    "born_in": SCHEMA.homeLocation,
    "practices": SCHEMA.knowsAbout,
    "originates_in": DCT.spatial,
    "teaches": SCHEMA.knowsAbout,
    "documents": DCT.subject,
    "location": DCT.spatial,
    "about": DCT.subject,
    "displays": DCT.relation,
    "used_by": DCT.relation,
    "depicts": FOAF.depicts,
    "had_participant": CRM.P11_had_participant,
    "demonstrates": DCT.relation,
}

TYPE_CLASS = {
    "person": CRM.E21_Person,
    "concept": SKOS.Concept,
    "region": SCHEMA.Place,
    "province": SCHEMA.Place,
    "prefecture": SCHEMA.Place,
    "castle": SCHEMA.Place,
    "school": CRM.E74_Group,
    "organization": CRM.E74_Group,
    "book": SCHEMA.Book,
    "object": E22_HUMAN_MADE_OBJECT,
    "museum": SCHEMA.Museum,
    "video game": SCHEMA.VideoGame,
    "event": SCHEMA.Event,
}

PROP = {
    "has title": SCHEMA.name,
    "has note": DCT.description,
    "has material": CRM.P45_consists_of,
    "has length": CRM.P43_has_dimension,
    "has date": DCT.date,
    "has release date": DCT.issued,
    "has foundation date": SCHEMA.foundingDate,
    "has genre": SCHEMA.genre,
    "has publisher": SCHEMA.publisher,
    "has author": SCHEMA.author,
    "was born in": SCHEMA.birthPlace,
    "is retainer of": NINJA.isVassalOf,
    "is succeeded by": DCT.isReplacedBy,
    "relates to": SKOS.related,
    "is used in": DCT.relation,
    "location": DCT.spatial,
    "had participant": CRM.P11_had_participant,
    "has developer": FOAF.maker,
    "is about": DCT.subject,
}

DATE_PREDS = {"has date", "has release date", "has foundation date"}
STRING_PREDS = {"has title", "has note", "has material", "has length",
                "has genre", "has publisher", "has author"}


def declare_vassal_of(g):

    g.add((NINJA.isVassalOf, RDF.type, OWL.ObjectProperty))
    g.add((NINJA.isVassalOf, RDFS.subPropertyOf, EAC.cpfRelation))
    g.add((NINJA.isVassalOf, RDFS.domain, CRM.E21_Person))
    g.add((NINJA.isVassalOf, RDFS.range, CRM.E21_Person))
    g.add((NINJA.isVassalOf, RDFS.label, Literal("is vassal of", lang="en")))
    g.add((NINJA.isVassalOf, RDFS.comment, Literal(
        "A feudal-era person's ongoing service obligation to their lord. "
        "No CIDOC-CRM or schema.org property models this without reifying "
        "it as its own Activity/Employment event; EAC-CPF's cpfRelation is "
        "the closest existing model (built for person/family/corporate-body "
        "relations) but its own relation-type vocabulary has no term this "
        "specific, so this narrower property is declared as its sub-property.",
        lang="en")))


def declare_embodies_archetype(g):

    g.add((NINJA.embodiesArchetype, RDF.type, OWL.ObjectProperty))
    g.add((NINJA.embodiesArchetype, RDFS.domain, CRM.E21_Person))
    g.add((NINJA.embodiesArchetype, RDFS.range, SKOS.Concept))
    g.add((NINJA.embodiesArchetype, RDFS.label, Literal("embodies archetype", lang="en")))
    g.add((NINJA.embodiesArchetype, RDFS.comment, Literal(
        "A real person who became the cultural archetype/exemplar of a "
        "legendary identity. Declared as a new term: no existing property "
        "in CIDOC-CRM, schema.org, SKOS or EAC-CPF models a person-to-"
        "concept exemplification relation without a forced domain/range "
        "mismatch.",
        lang="en")))


def bind_prefixes(g):
    g.bind("crm", CRM)
    g.bind("schema", SCHEMA)
    g.bind("skos", SKOS)
    g.bind("dct", DCT)
    g.bind("foaf", FOAF)
    g.bind("wdt", WDT)
    g.bind("wd", WD)
    g.bind("owl", OWL)
    g.bind("viaf", VIAF)
    g.bind("geonames", GEONAMES)
    g.bind("loc", LOC)
    g.bind("dbr", DBR)
    g.bind("eac-cpf", EAC)
    g.bind("ninja", NINJA)
    g.bind("edm", EDM)


def get_name(el):
    # skos:Concept entities (ninja/ninjutsu) get their name from the CSV's
    # "has title" instead: catDesc prose has no clean name to extract.
    for tag in ("persName", "placeName", "orgName", "title", "label", "eventName"):
        child = el.find(TEI + tag)
        if child is not None and child.text:
            return child.text.strip()
    obj_name = el.find(TEI + "objectIdentifier/" + TEI + "objectName")
    if obj_name is not None and obj_name.text:
        return obj_name.text.strip()
    return None


def parse_tei(g, tei_file):
    declare_embodies_archetype(g)
    tree = ET.parse(tei_file)
    root = tree.getroot()

    id_to_uri = {}
    for el in root.iter():
        xml_id = el.get(XML_ID)
        if xml_id is None or xml_id not in TYPES:
            continue  # no class mapping

        entity_uri = uri(xml_id)
        id_to_uri[xml_id] = entity_uri

        g.add((entity_uri, RDF.type, TYPES[xml_id]))
        if TYPES[xml_id] == CRM.E21_Person:
            g.add((entity_uri, RDF.type, FOAF.Person))
        if xml_id in EDM_PROVIDED_CHO_IDS:
            g.add((entity_uri, RDF.type, EDM.ProvidedCHO))

        name = get_name(el)
        if name:
            g.add((entity_uri, SCHEMA.name, Literal(name)))

        for extra_uri in SAME_AS.get(xml_id, []):
            g.add((entity_uri, OWL.sameAs, URIRef(extra_uri)))

    for rel in root.iter(TEI + "relation"):
        name = rel.get("name")
        active = rel.get("active").lstrip("#")
        passive = rel.get("passive").lstrip("#")
        g.add((id_to_uri[active], RELATIONS[name], id_to_uri[passive]))

    return g


def parse_csv(g, csv_dir):
    declare_vassal_of(g)
    for filename in sorted(os.listdir(csv_dir)):
        if not filename.endswith(".csv"):
            continue
        with open(os.path.join(csv_dir, filename), encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # header row
            for row in reader:
                if not row or row[0].strip().startswith("#"):
                    continue
                subject, predicate, obj = (cell.strip() for cell in row)

                if predicate == "has wikidata id":
                    continue  # handled by collect_wikidata_ids()

                if predicate == "has type":
                    g.add((uri(subject), RDF.type, TYPE_CLASS[obj]))
                    if obj == "person":
                        g.add((uri(subject), RDF.type, FOAF.Person))

                elif predicate in DATE_PREDS:
                    date_type = XSD.date if obj.count("-") == 2 else XSD.gYear
                    g.add((uri(subject), PROP[predicate], Literal(obj, datatype=date_type)))

                elif predicate in STRING_PREDS:
                    g.add((uri(subject), PROP[predicate], Literal(obj)))

                else:
                    g.add((uri(subject), PROP[predicate], uri(obj)))

    return g


def main():
    os.makedirs(TURTLE_DIR, exist_ok=True)

    tei_graph = Graph()
    bind_prefixes(tei_graph)
    parse_tei(tei_graph, TEI_FILE)
    tei_graph.serialize(destination=os.path.join(TURTLE_DIR, "ninja_tei.ttl"), format="turtle")
    print(f"Wrote {len(tei_graph)} triples to turtle/ninja_tei.ttl")

    csv_graph = Graph()
    bind_prefixes(csv_graph)
    parse_csv(csv_graph, CSV_DIR)
    csv_graph.serialize(destination=os.path.join(TURTLE_DIR, "ninja_csv.ttl"), format="turtle")
    print(f"Wrote {len(csv_graph)} triples to turtle/ninja_csv.ttl")

    merged = Graph()
    bind_prefixes(merged)
    for triple in tei_graph:
        merged.add(triple)
    for triple in csv_graph:
        merged.add(triple)
    merged.serialize(destination=os.path.join(TURTLE_DIR, "ninja_merged.ttl"), format="turtle")
    print(f"Wrote {len(merged)} triples to turtle/ninja_merged.ttl "
          f"({len(tei_graph) + len(csv_graph) - len(merged)} duplicate triples collapsed)")


if __name__ == "__main__":
    main()
