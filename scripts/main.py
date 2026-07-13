import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent

# TEI+CSV parsing and the RDF merge live in one file (tei_csv_to_rdf.py) —
# see decisions.txt for why. Each step below also runs standalone. Paths are
# relative to the project root, not this folder, since the last step lives
# in xslt/ rather than scripts/.
PIPELINE = [
    ("scripts/tei_csv_to_rdf.py", "TEI + CSV -> RDF (merged)"),
    ("scripts/generate_site_data.py", "RDF -> website data (docs/data/graph.json)"),
    ("scripts/generate_diagrams.py", "drawio -> SVG (docs/assets/*.svg)"),
    ("scripts/generate_rdf_graph_diagram.py", "RDF -> full graph diagram via ldf.fi (docs/assets/rdf-graph.svg)"),
    ("xslt/transform.py", "TEI -> HTML via XSLT (xslt/tei_encoding.html)"),
]


def run_step(rel_path, description):
    script_path = BASE / rel_path
    if not script_path.exists():
        print(f"[skip]  {description} ({rel_path} not written yet)")
        return "skipped"

    print(f"[run]   {description} ({rel_path})")
    result = subprocess.run([sys.executable, str(script_path)], cwd=script_path.parent)
    if result.returncode != 0:
        print(f"[fail]  {description} exited with code {result.returncode}")
        return "failed"

    print(f"[done]  {description}")
    return "done"


def main():
    results = [run_step(path, desc) for path, desc in PIPELINE]

    print()
    print("Pipeline summary:")
    for (path, desc), status in zip(PIPELINE, results):
        print(f"  {status:8s} {desc} ({path})")

    if "failed" in results:
        sys.exit(1)


if __name__ == "__main__":
    main()
