import os
import urllib.error
import urllib.parse
import urllib.request

from tei_csv_to_rdf import BASE

# Only pipeline step that needs internet: sends the full merged graph
# (entities and literal facts alike) to ldf.fi's RDF Grapher and saves the
# result. Fails loudly rather than leaving a stale file if unreachable.
TURTLE_FILE = os.path.join(BASE, "turtle", "ninja_merged.ttl")
OUT_FILE = os.path.join(BASE, "docs", "assets", "rdf-graph.svg")

ENDPOINT = "https://www.ldf.fi/service/rdf-grapher"


def main():
    if not os.path.exists(TURTLE_FILE):
        raise SystemExit(
            f"{TURTLE_FILE} not found — run tei_csv_to_rdf.py first "
            f"(or just run main.py, which runs steps in order)."
        )

    with open(TURTLE_FILE, encoding="utf-8") as f:
        turtle = f.read()

    body = urllib.parse.urlencode({
        "rdf": turtle,
        "from": "ttl",
        "to": "svg",
    }).encode("utf-8")

    request = urllib.request.Request(ENDPOINT, data=body, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            svg = response.read()
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        raise SystemExit(
            f"Could not reach ldf.fi RDF Grapher ({exc}). This step needs "
            f"internet access; docs/assets/rdf-graph.svg was left unchanged."
        )

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "wb") as f:
        f.write(svg)
    print(f"Wrote docs/assets/rdf-graph.svg ({len(svg)} bytes) via ldf.fi RDF Grapher")


if __name__ == "__main__":
    main()
