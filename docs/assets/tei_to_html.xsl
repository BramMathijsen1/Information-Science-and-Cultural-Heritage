<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="tei">

  <xsl:output method="html" encoding="UTF-8" indent="yes" doctype-system="about:legacy-compat"/>

  <!-- ===================================================================
       Named template: splits a whitespace-separated list of URIs (as
       used in @ref / @sameAs throughout this TEI file) into a series of
       links, each labelled by the authority it points to. XSLT 1.0 has
       no tokenize(), so this recurses on substring-before/-after.
       =================================================================== -->
  <xsl:template name="ref-links">
    <xsl:param name="refs"/>
    <xsl:variable name="trimmed" select="normalize-space($refs)"/>
    <xsl:if test="$trimmed != ''">
      <xsl:variable name="first">
        <xsl:choose>
          <xsl:when test="contains($trimmed, ' ')"><xsl:value-of select="substring-before($trimmed, ' ')"/></xsl:when>
          <xsl:otherwise><xsl:value-of select="$trimmed"/></xsl:otherwise>
        </xsl:choose>
      </xsl:variable>
      <xsl:variable name="label">
        <xsl:choose>
          <xsl:when test="contains($first, 'wikidata.org')">Wikidata</xsl:when>
          <xsl:when test="contains($first, 'viaf.org')">VIAF</xsl:when>
          <xsl:when test="contains($first, 'geonames.org')">GeoNames</xsl:when>
          <xsl:when test="contains($first, 'id.loc.gov')">Library of Congress</xsl:when>
          <xsl:when test="contains($first, 'dbpedia.org')">DBpedia</xsl:when>
          <xsl:otherwise>link</xsl:otherwise>
        </xsl:choose>
      </xsl:variable>
      <a href="{$first}" class="ref-link" target="_blank" rel="noopener">
        <xsl:value-of select="$label"/>
      </a>
      <xsl:text> </xsl:text>
      <xsl:if test="contains($trimmed, ' ')">
        <xsl:call-template name="ref-links">
          <xsl:with-param name="refs" select="substring-after($trimmed, ' ')"/>
        </xsl:call-template>
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <!-- ===================================================================
       Root
       =================================================================== -->
  <xsl:template match="/tei:TEI">
    <html lang="en">
      <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title><xsl:value-of select="tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/></title>
        <style>
          body { font-family: Georgia, "Times New Roman", serif; max-width: 860px; margin: 0 auto; padding: 40px 24px 80px; line-height: 1.6; color: #232323; background: #fdfcf9; }
          h1 { font-size: 1.9rem; margin-bottom: 4px; }
          h2 { border-bottom: 2px solid #8b1e2b; padding-bottom: 4px; margin-top: 48px; }
          h3 { margin-bottom: 4px; }
          .subtitle { color: #666; font-style: italic; margin-top: 0; }
          nav.toc { background: #f2efe8; border: 1px solid #ddd; padding: 16px 24px; margin: 24px 0; }
          nav.toc ul { columns: 2; margin: 0; padding-left: 20px; }
          article { margin-bottom: 28px; padding-bottom: 20px; border-bottom: 1px solid #e5e2da; }
          article:last-child { border-bottom: none; }
          .meta { color: #666; font-size: 0.9rem; }
          .ref-link { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; background: #f2efe8; border: 1px solid #ddd; padding: 1px 6px; margin-right: 4px; text-decoration: none; color: #8b1e2b; }
          .ref-link:hover { background: #8b1e2b; color: #fff; }
          .entity-ref { color: #8b1e2b; text-decoration: none; border-bottom: 1px dotted #8b1e2b; }
          .term { font-style: italic; }
          .foreign { font-style: normal; }
          table.relations { border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 0.92rem; }
          table.relations th, table.relations td { text-align: left; padding: 6px 10px; border-bottom: 1px solid #e5e2da; }
          table.relations th { background: #f2efe8; }
          code { background: #f2efe8; padding: 1px 5px; font-size: 0.88em; }
          footer { margin-top: 60px; color: #888; font-size: 0.85rem; border-top: 1px solid #e5e2da; padding-top: 16px; }
        </style>
      </head>
      <body>
        <header>
          <h1><xsl:value-of select="tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"/></h1>
          <p class="subtitle">
            <xsl:value-of select="tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author"/>
            <xsl:text> &#8226; </xsl:text>
            <xsl:value-of select="tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:pubPlace"/>
            <xsl:text>, </xsl:text>
            <xsl:value-of select="tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date"/>
          </p>
        </header>

        <nav class="toc">
          <strong>Contents</strong>
          <ul>
            <li><a href="#bibliography">Bibliography</a></li>
            <li><a href="#concepts">Concepts</a></li>
            <li><a href="#persons">Persons</a></li>
            <li><a href="#organizations">Organizations</a></li>
            <li><a href="#places">Places</a></li>
            <li><a href="#objects">Objects</a></li>
            <li><a href="#events">Events</a></li>
            <li><a href="#relations">Relations</a></li>
            <li><a href="#text">Text</a></li>
          </ul>
        </nav>

        <section id="bibliography">
          <h2>Bibliography</h2>
          <p><xsl:apply-templates select="tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:bibl[not(@xml:id)]" mode="inline"/></p>
          <xsl:for-each select="tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:listBibl/tei:bibl">
            <article id="{@xml:id}">
              <h3>
                <xsl:value-of select="tei:title"/>
                <xsl:text> (</xsl:text><xsl:value-of select="tei:date"/><xsl:text>)</xsl:text>
              </h3>
              <p class="meta">
                <xsl:if test="tei:author">
                  <xsl:text>by </xsl:text>
                  <xsl:choose>
                    <xsl:when test="tei:author/@ref">
                      <a href="{tei:author/@ref}" class="entity-ref" target="_blank" rel="noopener"><xsl:value-of select="tei:author"/></a>
                    </xsl:when>
                    <xsl:otherwise><xsl:value-of select="tei:author"/></xsl:otherwise>
                  </xsl:choose>
                  <xsl:text> &#8226; </xsl:text>
                </xsl:if>
                <xsl:value-of select="tei:textLang/@mainLang"/>
              </p>
              <p><xsl:value-of select="tei:note"/></p>
              <p>
                <xsl:call-template name="ref-links">
                  <xsl:with-param name="refs" select="tei:title/@ref"/>
                </xsl:call-template>
              </p>
            </article>
          </xsl:for-each>
        </section>

        <section id="concepts">
          <h2>Concepts</h2>
          <xsl:for-each select="tei:teiHeader/tei:encodingDesc/tei:classDecl/tei:taxonomy/tei:category">
            <article id="{@xml:id}">
              <h3><xsl:value-of select="tei:catDesc/text()[1]"/></h3>
              <p><xsl:apply-templates select="tei:catDesc" mode="inline"/></p>
              <p>
                <xsl:call-template name="ref-links">
                  <xsl:with-param name="refs" select="@sameAs"/>
                </xsl:call-template>
              </p>
            </article>
          </xsl:for-each>
        </section>

        <section id="persons">
          <h2>Persons</h2>
          <xsl:for-each select="tei:teiHeader/tei:profileDesc/tei:particDesc/tei:listPerson/tei:person">
            <article id="{@xml:id}">
              <h3><xsl:value-of select="tei:persName/text()[1]"/></h3>
              <p class="meta">
                <xsl:value-of select="tei:birth/@when"/> &#8211; <xsl:value-of select="tei:death/@when"/>
              </p>
              <p><xsl:apply-templates select="tei:persName" mode="inline"/></p>
              <p>
                <xsl:call-template name="ref-links">
                  <xsl:with-param name="refs" select="tei:persName/@ref"/>
                </xsl:call-template>
              </p>
            </article>
          </xsl:for-each>
        </section>

        <section id="organizations">
          <h2>Organizations</h2>
          <xsl:for-each select="tei:teiHeader/tei:profileDesc/tei:particDesc/tei:listOrg/tei:org">
            <article id="{@xml:id}">
              <h3><xsl:value-of select="tei:orgName"/></h3>
              <p><xsl:value-of select="tei:note"/></p>
              <p>
                <xsl:call-template name="ref-links">
                  <xsl:with-param name="refs" select="tei:orgName/@ref"/>
                </xsl:call-template>
              </p>
            </article>
          </xsl:for-each>
        </section>

        <section id="places">
          <h2>Places</h2>
          <xsl:for-each select="tei:standOff/tei:listPlace/tei:place">
            <article id="{@xml:id}">
              <h3><xsl:value-of select="tei:placeName"/> <span class="meta">(<xsl:value-of select="@type"/>)</span></h3>
              <p><xsl:value-of select="tei:note"/></p>
              <p>
                <xsl:call-template name="ref-links">
                  <xsl:with-param name="refs" select="tei:placeName/@ref"/>
                </xsl:call-template>
              </p>
            </article>
          </xsl:for-each>
        </section>

        <section id="objects">
          <h2>Objects</h2>
          <xsl:for-each select="tei:standOff/tei:listObject/tei:object">
            <article id="{@xml:id}">
              <h3><xsl:value-of select="tei:objectIdentifier/tei:objectName"/></h3>
              <p><xsl:value-of select="tei:note"/></p>
              <p>
                <xsl:call-template name="ref-links">
                  <xsl:with-param name="refs" select="tei:objectIdentifier/tei:objectName/@ref"/>
                </xsl:call-template>
              </p>
            </article>
          </xsl:for-each>
        </section>

        <section id="events">
          <h2>Events</h2>
          <xsl:for-each select="tei:standOff/tei:listEvent/tei:event">
            <article id="{@xml:id}">
              <h3><xsl:value-of select="tei:eventName"/> <span class="meta">(<xsl:value-of select="@when"/>)</span></h3>
              <p><xsl:value-of select="tei:note"/></p>
              <p>
                <xsl:call-template name="ref-links">
                  <xsl:with-param name="refs" select="tei:eventName/@ref"/>
                </xsl:call-template>
              </p>
            </article>
          </xsl:for-each>
        </section>

        <section id="relations">
          <h2>Relations</h2>
          <table class="relations">
            <thead><tr><th>Active</th><th>Relation</th><th>Passive</th></tr></thead>
            <tbody>
              <xsl:for-each select="tei:standOff/tei:listRelation/tei:relation">
                <tr>
                  <td><a href="{@active}" class="entity-ref"><xsl:value-of select="substring-after(@active, '#')"/></a></td>
                  <td><code><xsl:value-of select="@name"/></code></td>
                  <td><a href="{@passive}" class="entity-ref"><xsl:value-of select="substring-after(@passive, '#')"/></a></td>
                </tr>
              </xsl:for-each>
            </tbody>
          </table>
        </section>

        <section id="text">
          <h2>Text</h2>
          <xsl:apply-templates select="tei:text/tei:body/tei:div"/>
        </section>

        <footer>
          <p>Generated by <code>xslt/tei_to_html.xsl</code> from <code>tei/tei_encoding.xml</code>.</p>
        </footer>
      </body>
    </html>
  </xsl:template>

  <!-- ===================================================================
       Body divs / paragraphs
       =================================================================== -->
  <xsl:template match="tei:div">
    <article id="text-{@type}">
      <h3><xsl:value-of select="tei:head"/></h3>
      <xsl:apply-templates select="tei:p" mode="inline"/>
    </article>
  </xsl:template>

  <!-- ===================================================================
       Inline mixed content (mode="inline") — used both inside <p> in the
       body text and inside <catDesc>/<persName>. Anything with @ref
       pointing at a local #id becomes a same-page link to that entity's
       <article>; anything else just keeps its text with light styling.
       =================================================================== -->
  <xsl:template match="tei:p | tei:catDesc" mode="inline">
    <p><xsl:apply-templates mode="inline"/></p>
  </xsl:template>

  <xsl:template match="tei:persName | tei:placeName | tei:orgName | tei:eventName | tei:title | tei:rs" mode="inline">
    <xsl:choose>
      <xsl:when test="starts-with(@ref, '#')">
        <a href="{@ref}" class="entity-ref"><xsl:apply-templates mode="inline"/></a>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates mode="inline"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="tei:term" mode="inline">
    <span class="term"><xsl:apply-templates mode="inline"/></span>
  </xsl:template>

  <xsl:template match="tei:foreign" mode="inline">
    <span class="foreign" lang="{@xml:lang}"><xsl:apply-templates mode="inline"/></span>
  </xsl:template>

  <xsl:template match="tei:addName" mode="inline">
    <span class="addname"><xsl:apply-templates mode="inline"/></span>
  </xsl:template>

  <xsl:template match="text()" mode="inline">
    <xsl:value-of select="."/>
  </xsl:template>

</xsl:stylesheet>
