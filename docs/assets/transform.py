import os
import shutil

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)

TEI_FILE = os.path.join(BASE, "tei", "tei_encoding.xml")
XSL_FILE = os.path.join(HERE, "tei_to_html.xsl")
OUT_FILE = os.path.join(HERE, "tei_encoding.html")
SITE_COPY = os.path.join(BASE, "docs", "tei_encoding.html")


def main():
    xml = etree.parse(TEI_FILE)
    xslt = etree.XSLT(etree.parse(XSL_FILE))
    result = xslt(xml)
    with open(OUT_FILE, "wb") as f:
        f.write(etree.tostring(result, pretty_print=True, encoding="utf-8", method="html"))
    print(f"Wrote xslt/tei_encoding.html ({os.path.getsize(OUT_FILE)} bytes)")

    # xslt/ isn't published by GitHub Pages (only docs/ is) — copy so the
    # site can link to it directly.
    shutil.copyfile(OUT_FILE, SITE_COPY)
    print(f"Copied to docs/tei_encoding.html for the website link")


if __name__ == "__main__":
    main()
