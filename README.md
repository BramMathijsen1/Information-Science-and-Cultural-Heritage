# Out of the shadows

**The ninja legend in cultural heritage: a Linked Open Data project**

## Introduction of the project

During my time in Japan I became fascinated by the Ninja (also known as shinobi no mono, Iga no mono). This project tries to capture the concepts surrounding the Shinobi using the most famous ninja Hattori Hanzō as a bridge.

## Who were the Shinobi and who was Hattori Hanzō?

The Shinobi no mono have been speaking to the imagination for centuries. They appeared from hollywood blockbusters to contemporary kabuki theater. Trough time fact and fiction about the Shinobi became intertwined, especially during and after the Meji restoration (1868–1912) where the Ninja became an important part for the creation of an identity for the emerging Japanese nation.

Hattori Hanzō might have been the most famous ninja ever. He was a samurai trained in the art of the Ninja in Iga who saved the life of Tokugawa Ieyasu, and later helped him to become the ruler of an united Japan. He was trained by his family in Iga. Iga was a by mountain isolated provine where the art of the Shinobi was perfected. That is why, in contemporary literature, the Ninja were also refered as Iga no mono (Person from Iga). 

This project tries to keep the the Ninja active, but focusses on the historical part instead of the mythologized version. In this way the cultural heritage gets preserved in a historically representative way.

## The entities

| Item | Entity type | Ontology class | Wikidata |
|---|---|---|---|
| Hattori Hanzō | Person | `crm:E21_Person` | [Q316952](https://www.wikidata.org/wiki/Q316952) |
| Ninja | Occupation / concept | `skos:Concept` | [Q9402](https://www.wikidata.org/wiki/Q9402) |
| Ninjutsu | Martial art / discipline | `skos:Concept` | [Q539067](https://www.wikidata.org/wiki/Q539067) |
| Iga Province | Historical region | `schema:Place` | [Q1047128](https://www.wikidata.org/wiki/Q1047128) |
| Iga-ryū | Ninja school / tradition | `crm:E74_Group` | [Q3275530](https://www.wikidata.org/wiki/Q3275530) |
| Bansenshūkai | Book (ninjutsu manual) | `schema:Book` | [Q806956](https://www.wikidata.org/wiki/Q806956) |
| Mizugumo  | Object (tool) | `crm:E22_Human-Made_Object` | [Q6884757](https://www.wikidata.org/wiki/Q6884757) |
| Kunai | Object (tool/weapon) | `crm:E22_Human-Made_Object` | [Q860340](https://www.wikidata.org/wiki/Q860340) |
| Ninja Museum of Igaryu | Museum | `schema:Museum` | [Q4306401](https://www.wikidata.org/wiki/Q4306401) |
| Ghost of Tsushima | Video Game | `schema:VideoGame` | [Q42564798](https://www.wikidata.org/wiki/Q42564798) |
| Siege of Kaminogō Castle | Event | `schema:Event` | [Q7510141](https://www.wikidata.org/wiki/Q7510141) |

## Repository structure

```
Ninja/
├── README.md              this file
├── decisions.txt          full decision log: every non-obvious choice, question and fix made while building this project
├── tei/
│   └── tei_encoding.xml   TEI source: Wikipedia-sourced text, tagged entities, external identifiers (@ref), relations
├── csv/                   one CSV per entity, plus extra_entities.csv for bridge entities — subject/predicate/object
│                          facts that aren't stated in the TEI body text
├── organization/
│   ├── theoretical-model.drawio   hand-maintained mind map: Hanzō + every entity, labelled relations
│   └── ConceptualModel.drawio     hand-maintained conceptual model: classes and properties only, no individuals
├── scripts/                the pipeline — see below
├── xslt/
│   ├── tei_to_html.xsl     XSLT stylesheet: TEI -> standalone HTML
│   ├── transform.py        runs the stylesheet (lxml), writes tei_encoding.html
│   └── tei_encoding.html   generated output
├── turtle/                generated RDF output (.ttl) — overwritten on every pipeline run, never hand-edited
└── docs/                  the website (docs/ is GitHub Pages' auto-detected folder name)
    ├── index.html
    ├── css/style.css
    ├── js/site.js         reads docs/data/graph.json at page load and renders every section from it
    ├── data/graph.json    generated website data
    └── assets/*.svg       generated diagrams
```

## The pipeline

Everything in `turtle/`, `docs/data/graph.json`, `docs/assets/*.svg` and `xslt/tei_encoding.html` is generated, not hand-typed. Run the whole thing with:

```
python3 scripts/main.py
```

Five steps, in order:

1. `tei_csv_to_rdf.py` — TEI + CSV → RDF (`turtle/*.ttl`).
2. `generate_site_data.py` — RDF → website data (`docs/data/graph.json`), and copies the TEI file + `tei_csv_to_rdf.py` into `docs/assets/` for the site's source-code section.
3. `generate_diagrams.py` — the two hand-drawn `.drawio` files → SVG.
4. `generate_rdf_graph_diagram.py` — full RDF graph → SVG via ldf.fi (needs internet).
5. `transform.py` (in `xslt/`) — TEI → HTML via `tei_to_html.xsl`

Edit a CSV or the TEI file, rerun `main.py`, everything above regenerates.

## Products

- TEI document — the encoded source text
- CSV tables — entity facts not in the TEI body
- RDF database — the generated knowledge graph (`turtle/*.ttl`)
- Theoretical + conceptual model diagrams
- RDF graph diagram — auto-generated from the live data
- Website — reads all of the above
