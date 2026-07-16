import os
import xml.etree.ElementTree as ET

from tei_csv_to_rdf import BASE

# .drawio files are hand-maintained; this only converts their current
# state to SVG, never regenerates their content.
ORG_DIR = os.path.join(BASE, "organization")
OUT_DIR = os.path.join(BASE, "docs", "assets")
FONT = "Segoe UI, Helvetica Neue, Arial, sans-serif"

DIAGRAMS = [
    ("theoretical-model.drawio", "theoretical-model.svg",
     "Theoretical model: Hattori Hanzō and the entities connected to him", "#0d0d10"),
    ("ConceptualModel.drawio", "conceptual-model.svg",
     "Conceptual model: classes and properties in the Ninja RDF graph", "#fbfaf7"),
    ("PipelineDiagram.drawio", "pipeline-diagram.svg",
     "Pipeline: how the project files feed into each script and out to the website", "#0d0d10"),
]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                   .replace('"', "&quot;"))


def parse_style(style):
    """drawio style strings are ';'-separated tokens: key=value pairs, or
    bare flags stored as True (so `"ellipse" in style` works)."""
    result = {}
    for token in (style or "").split(";"):
        token = token.strip()
        if not token:
            continue
        if "=" in token:
            k, v = token.split("=", 1)
            result[k] = v
        else:
            result[token] = True
    return result


def shape_kind(style):
    if "text" in style and "fillColor" not in style:
        return "text"
    if "ellipse" in style:
        return "ellipse"
    if style.get("shape") == "parallelogram":
        return "parallelogram"
    return "rect"


def render_node(cell, geom):
    style = parse_style(cell.get("style"))
    x, y = float(geom.get("x", 0)), float(geom.get("y", 0))
    w, h = float(geom.get("width", 0)), float(geom.get("height", 0))
    fill = style.get("fillColor", "#ffffff")
    stroke = style.get("strokeColor", "#333333")
    font_color = style.get("fontColor", "#1a1a1a")
    font_size = float(style.get("fontSize", "14"))
    bold = style.get("fontStyle") == "1"
    kind = shape_kind(style)

    if kind == "text":
        shape = ""
    elif kind == "ellipse":
        shape = (f'<ellipse cx="{x+w/2:.0f}" cy="{y+h/2:.0f}" rx="{w/2:.0f}" ry="{h/2:.0f}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    elif kind == "parallelogram":
        slant = min(14, w * 0.12)
        pts = (f"{x+slant:.0f},{y:.0f} {x+w:.0f},{y:.0f} "
               f"{x+w-slant:.0f},{y+h:.0f} {x:.0f},{y+h:.0f}")
        shape = f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    else:
        shape = (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="8" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>')

    align = style.get("align", "center")
    anchor = {"left": "start", "right": "end", "center": "middle"}.get(align, "middle")
    text_x = x if anchor == "start" else (x + w if anchor == "end" else x + w / 2)

    label = (cell.get("value") or "").strip()
    lines = [l for l in label.split("<br>") if l != ""] or ([label] if label else [])
    n = len(lines)
    cy = y + h / 2
    start_y = cy - (n - 1) * (font_size * 0.62)
    weight = "700" if bold else "400"
    text_parts = []
    for i, line in enumerate(lines):
        ty = start_y + i * (font_size * 1.24)
        text_parts.append(
            f'<text x="{text_x:.0f}" y="{ty:.0f}" text-anchor="{anchor}" dominant-baseline="middle" '
            f'font-size="{font_size:.0f}" font-weight="{weight}" fill="{font_color}" '
            f'font-family="{FONT}">{esc(line)}</text>'
        )
    return shape + "".join(text_parts)


def box_boundary_point(cx, cy, hw, hh, dx, dy):
    """Point on a (hw*2, hh*2) box's edge, centered at (cx, cy), in the
    direction (dx, dy) from its center."""
    if dx == 0 and dy == 0:
        return cx, cy
    scale = float("inf")
    if dx != 0:
        scale = min(scale, hw / abs(dx))
    if dy != 0:
        scale = min(scale, hh / abs(dy))
    return cx + dx * scale, cy + dy * scale


def marker_id(kind, color):
    return f"arrow-{kind}-{color.lstrip('#')}"


def render_edge(cell, node_geom, markers, loop_index=0):
    source, target = cell.get("source"), cell.get("target")
    if source not in node_geom or target not in node_geom:
        return ""
    sx, sy, sw, sh = node_geom[source]

    style = parse_style(cell.get("style"))
    stroke = style.get("strokeColor", "#666666")
    font_color = style.get("fontColor", "#666666")
    font_size = float(style.get("fontSize", "16"))
    kind = "open" if style.get("endArrow") == "open" else "block"
    marker = marker_id(kind, stroke)
    markers[(kind, stroke)] = True

    if source == target:
        # Straight source-center-to-target-center geometry collapses to a
        # point for self-loops; bulge a loop out from the right edge instead.
        # A same-radius horizontal offset isn't enough separation for labels
        # this wide, so successive loops on the same box alternate between
        # the upper and lower half of the box's right edge instead.
        loop_r = max(sw, sh) * 0.35
        x_edge = sx + sw
        if loop_index % 2 == 0:
            y1, y2 = sy + sh * 0.12, sy + sh * 0.42
        else:
            y1, y2 = sy + sh * 0.58, sy + sh * 0.88
        cx = x_edge + loop_r
        line = (f'<path d="M {x_edge:.0f} {y1:.0f} C {cx:.0f} {y1:.0f}, '
                f'{cx:.0f} {y2:.0f}, {x_edge:.0f} {y2:.0f}" fill="none" '
                f'stroke="{stroke}" stroke-width="1.5" marker-end="url(#{marker})"/>')
        mx, my = x_edge + loop_r, (y1 + y2) / 2
    else:
        tx, ty, tw, th = node_geom[target]
        cx1, cy1 = sx + sw / 2, sy + sh / 2
        cx2, cy2 = tx + tw / 2, ty + th / 2
        dx, dy = cx2 - cx1, cy2 - cy1
        # Clip each end to its own box's boundary instead of its center —
        # nodes paint over edges (drawn after them), so a marker sitting at
        # a center point was rendering completely hidden underneath the
        # target box's own fill, not just hard to see.
        x1, y1 = box_boundary_point(cx1, cy1, sw / 2, sh / 2, dx, dy)
        x2, y2 = box_boundary_point(cx2, cy2, tw / 2, th / 2, -dx, -dy)
        line = (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                f'stroke="{stroke}" stroke-width="1.5" marker-end="url(#{marker})"/>')
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2

    label = (cell.get("value") or "").strip()
    if not label:
        return line

    lines = [l for l in label.split("<br>") if l != ""] or [label]
    label_bg = style.get("labelBackgroundColor", "none")
    rect = ""
    if label_bg != "none":
        w = max(font_size * 2, max(len(l) for l in lines) * font_size * 0.6 + font_size)
        h = font_size * 1.5 * len(lines)
        rect = f'<rect x="{mx - w/2:.0f}" y="{my - h/2:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{label_bg}" fill-opacity="0.92"/>'
    n = len(lines)
    start_y = my - (n - 1) * (font_size * 0.62)
    text = "".join(
        f'<text x="{mx:.0f}" y="{start_y + i * font_size * 1.24 + font_size * 0.32:.0f}" text-anchor="middle" '
        f'font-size="{font_size:.0f}" fill="{font_color}" font-family="{FONT}">{esc(l)}</text>'
        for i, l in enumerate(lines)
    )
    return line + rect + text


def build_arrow_defs(markers):
    """One marker per (kind, color) actually used, colored to match its own
    edge's stroke — a single fixed marker color was invisible against edge
    colors it didn't match, especially on the dark theoretical model."""
    parts = ["<defs>"]
    for kind, color in markers:
        mid = marker_id(kind, color)
        if kind == "open":
            parts.append(
                f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="11" '
                f'markerHeight="11" orient="auto-start-reverse">'
                f'<path d="M1,1 L9,5 L1,9" fill="none" stroke="{color}" stroke-width="1.6"/></marker>'
            )
        else:
            parts.append(
                f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="11" '
                f'markerHeight="11" orient="auto-start-reverse">'
                f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>'
            )
    parts.append("</defs>")
    return "".join(parts)


def convert(drawio_path, title, bg):
    tree = ET.parse(drawio_path)
    root_cells = tree.getroot().find(".//root")

    node_geom = {}
    vertex_cells = []
    edge_cells = []

    for cell in root_cells.findall("mxCell"):
        if cell.get("vertex") == "1":
            geom = cell.find("mxGeometry")
            if geom is None:
                continue
            x, y = float(geom.get("x", 0)), float(geom.get("y", 0))
            w, h = float(geom.get("width", 0)), float(geom.get("height", 0))
            node_geom[cell.get("id")] = (x, y, w, h)
            vertex_cells.append((cell, geom))
        elif cell.get("edge") == "1":
            edge_cells.append(cell)

    node_svg = [render_node(cell, geom) for cell, geom in vertex_cells]
    loop_counts = {}
    markers = {}
    edge_svg = []
    for cell in edge_cells:
        source = cell.get("source")
        loop_index = 0
        if source == cell.get("target"):
            loop_index = loop_counts.get(source, 0)
            loop_counts[source] = loop_index + 1
        edge_svg.append(render_edge(cell, node_geom, markers, loop_index))

    # Boxes dragged left/above the drawio canvas's own origin (negative x/y)
    # used to render outside a viewBox that always started at 0,0 and got
    # silently clipped — the viewBox origin now follows the actual content.
    min_x = min((x for x, y, w, h in node_geom.values()), default=0)
    min_y = min((y for x, y, w, h in node_geom.values()), default=0)
    max_x = max((x + w for x, y, w, h in node_geom.values()), default=800)
    max_y = max((y + h for x, y, w, h in node_geom.values()), default=800)
    vx, vy = int(min_x) - 20, int(min_y) - 20
    width, height = int(max_x - min_x) + 40, int(max_y - min_y) + 40

    inner = build_arrow_defs(markers) + "".join(edge_svg) + "".join(node_svg)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {width} {height}" '
            f'font-family="{FONT}" role="img" aria-label="{esc(title)}">'
            f'<rect x="{vx}" y="{vy}" width="{width}" height="{height}" fill="{bg}"/>{inner}</svg>')


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for src_name, out_name, title, bg in DIAGRAMS:
        src_path = os.path.join(ORG_DIR, src_name)
        svg = convert(src_path, title, bg)
        out_path = os.path.join(OUT_DIR, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Wrote docs/assets/{out_name} ({len(svg)} bytes) from organization/{src_name}")


if __name__ == "__main__":
    main()
