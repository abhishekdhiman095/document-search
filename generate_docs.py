from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

OUTPUT = "DocSearch_Documentation.pdf"

# ── Colour palette ──────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#1A2B4A")
TEAL   = colors.HexColor("#0D7A8A")
SILVER = colors.HexColor("#F4F6F8")
MUTED  = colors.HexColor("#6B7280")
RED    = colors.HexColor("#DC2626")
GREEN  = colors.HexColor("#16A34A")
AMBER  = colors.HexColor("#D97706")

# ── Styles ──────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def style(name, parent="Normal", **kw):
    s = ParagraphStyle(name, parent=base[parent], **kw)
    return s

H1 = style("H1", "Heading1", fontSize=22, textColor=NAVY,
           spaceAfter=6, spaceBefore=18, fontName="Helvetica-Bold")
H2 = style("H2", "Heading2", fontSize=15, textColor=TEAL,
           spaceAfter=4, spaceBefore=14, fontName="Helvetica-Bold")
H3 = style("H3", "Heading3", fontSize=12, textColor=NAVY,
           spaceAfter=3, spaceBefore=8, fontName="Helvetica-Bold")
BODY = style("BODY", fontSize=10, leading=15, spaceAfter=6,
             alignment=TA_JUSTIFY, textColor=colors.HexColor("#1F2937"))
CODE = style("CODE", fontSize=8.5, fontName="Courier",
             backColor=SILVER, leftIndent=12, rightIndent=12,
             leading=13, spaceBefore=4, spaceAfter=4,
             textColor=colors.HexColor("#111827"))
BULLET = style("BULLET", parent="Normal", leftIndent=18,
               bulletIndent=6, spaceAfter=3, fontSize=10, leading=15,
               alignment=TA_JUSTIFY, textColor=colors.HexColor("#1F2937"))
CAPTION = style("CAPTION", fontSize=8, textColor=MUTED,
                alignment=TA_CENTER, spaceAfter=8)
COVER_TITLE = style("CT", fontSize=34, textColor=colors.white,
                    fontName="Helvetica-Bold", alignment=TA_CENTER, leading=40)
COVER_SUB = style("CS", fontSize=13, textColor=colors.HexColor("#CBD5E1"),
                  alignment=TA_CENTER, spaceAfter=6)

def hr(): return HRFlowable(width="100%", thickness=1, color=TEAL, spaceAfter=8, spaceBefore=4)
def sp(h=8): return Spacer(1, h)
def b(text): return f"<b>{text}</b>"
def code_block(text): return Paragraph(text.replace("\n", "<br/>").replace(" ", "&nbsp;"), CODE)
def bullet(text): return Paragraph(f"• &nbsp;{text}", BULLET)
def tag(color, label):
    return f'<font color="{color}"><b>[{label}]</b></font>'

# ── Badge table helper ───────────────────────────────────────────────────────
def badge_table(rows):
    data = []
    for label, status, color in rows:
        data.append([
            Paragraph(label, style("BL", fontSize=9, fontName="Helvetica-Bold")),
            Paragraph(status, style("BS", fontSize=9, textColor=color, fontName="Helvetica-Bold")),
        ])
    t = Table(data, colWidths=[2.8*inch, 3.8*inch])
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.white, SILVER]),
        ("GRID",           (0,0), (-1,-1), 0.4, colors.HexColor("#E5E7EB")),
        ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",    (0,0), (-1,-1), 8),
        ("RIGHTPADDING",   (0,0), (-1,-1), 8),
        ("TOPPADDING",     (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",  (0,0), (-1,-1), 5),
    ]))
    return t

# ── Cover page ───────────────────────────────────────────────────────────────
def cover():
    elems = []
    # coloured banner
    banner = Table(
        [[Paragraph("DocSearch", COVER_TITLE)],
         [Paragraph("Multi-Tenant Document Search Engine", COVER_SUB)],
         [Paragraph("Architecture &amp; Production Readiness Report", COVER_SUB)]],
        colWidths=[6.5*inch]
    )
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), NAVY),
        ("TOPPADDING",    (0,0), (-1,-1), 28),
        ("BOTTOMPADDING", (0,0), (-1,-1), 28),
        ("LEFTPADDING",   (0,0), (-1,-1), 20),
        ("RIGHTPADDING",  (0,0), (-1,-1), 20),
        ("ROUNDEDCORNERS",(0,0), (-1,-1), [8,8,8,8]),
    ]))
    elems += [sp(60), banner, sp(30)]

    meta = [
        ["Project",  "DocSearch — In-Memory Multi-Tenant Search API"],
        ["Stack",    "Spring Boot 4.1 · Java 17 · Lombok"],
        ["Author",   "Abhishek Dhiman"],
        ["Date",     "June 2026"],
        ["Version",  "0.1.0-SNAPSHOT"],
    ]
    mt = Table(meta, colWidths=[1.4*inch, 5.1*inch])
    mt.setStyle(TableStyle([
        ("FONTNAME",       (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE",       (0,0), (-1,-1), 10),
        ("TEXTCOLOR",      (0,0), (0,-1), TEAL),
        ("GRID",           (0,0), (-1,-1), 0.4, colors.HexColor("#E5E7EB")),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.white, SILVER]),
        ("TOPPADDING",     (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",  (0,0), (-1,-1), 6),
        ("LEFTPADDING",    (0,0), (-1,-1), 8),
    ]))
    elems += [mt, PageBreak()]
    return elems

# ── Section 1 — Architecture Design ─────────────────────────────────────────
def section_architecture():
    e = []
    e += [Paragraph("1. Architecture Design", H1), hr()]

    e += [Paragraph("1.1 System Overview", H2),
          Paragraph(
              "DocSearch is a RESTful document search engine built on Spring Boot 4.1. "
              "It provides full multi-tenant isolation, inverted-index search at the word "
              "and trigram (n=3) levels, and Levenshtein edit-distance fuzzy matching — "
              "all backed by in-memory data structures for prototype speed.", BODY)]

    # Component table
    e += [Paragraph("1.2 Component Map", H2)]
    comp = [
        [b("Layer"), b("Class"), b("Responsibility")],
        ["API",       "TenantController",   "Tenant CRUD — POST/GET/DELETE /api/v1/tenants"],
        ["API",       "DocumentController", "Document CRUD + search — /api/v1/documents, /api/v1/search"],
        ["API",       "GeneralController",  "Health check — GET /health-check"],
        ["Service",   "TenantService",      "Owns Tenant entities and per-tenant TenantIndex instances"],
        ["Service",   "DocumentService",    "Indexes, retrieves, deletes docs; runs 3-pass search"],
        ["Store",     "TenantIndex",        "Per-tenant: docs map, word inverted index, trigram index"],
        ["Model",     "Tenant",             "id · name · createdAt"],
        ["Model",     "Document",           "id · tenantId · title · content · createdAt"],
        ["DTO",       "CreateDocumentRequest", "title · content (POST body)"],
        ["DTO",       "CreateTenantRequest",   "name (POST body)"],
        ["DTO",       "SearchResult",          "document · score (search response)"],
    ]
    ct = Table([[Paragraph(c, style("TH", fontSize=9, fontName="Helvetica-Bold",
                                    textColor=colors.white if i == 0 else colors.HexColor("#1F2937")))
                 for c in row] for i, row in enumerate(comp)],
               colWidths=[0.9*inch, 1.8*inch, 3.8*inch])
    ct.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  NAVY),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, SILVER]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#E5E7EB")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("FONTSIZE",      (0,1), (-1,-1), 9),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    e += [ct, sp(10)]

    e += [Paragraph("1.3 Request Flow", H2),
          Paragraph("Every inbound request follows this path:", BODY),
          bullet("HTTP client sends request with <b>X-Tenant-Id</b> header (or <b>?tenant=</b> for search)."),
          bullet("<b>DocumentController</b> validates tenant existence via <b>TenantService.exists()</b> — returns 404 if unknown."),
          bullet("<b>DocumentService</b> calls <b>TenantService.getIndex(tenantId)</b> to retrieve that tenant's isolated <b>TenantIndex</b>."),
          bullet("All reads/writes operate exclusively on that <b>TenantIndex</b> — no shared state across tenants."),
          bullet("Search returns a scored, ranked <b>List&lt;SearchResult&gt;</b>."),
          sp(6)]

    e += [Paragraph("1.4 Inverted Index Design", H2),
          Paragraph(
              "Each <b>TenantIndex</b> maintains two separate ConcurrentHashMaps:", BODY),
          bullet("<b>wordIndex</b>: token &rarr; Set&lt;docId&gt;  — exact word lookup."),
          bullet("<b>trigramIndex</b>: 3-char gram &rarr; Set&lt;docId&gt;  — substring / fuzzy lookup."),
          sp(4),
          Paragraph("Indexing — on every POST /documents:", BODY),
          code_block(
              'tokenize("Spring Boot Guide")  →  ["spring", "boot", "guide"]\n'
              'trigrams("spring")            →  ["spr","pri","rin","ing"]\n'
              'wordIndex["spring"]           →  {docId}\n'
              'trigramIndex["spr"]           →  {docId}  (etc.)'
          ), sp(4),
          Paragraph("1.5 Search Scoring (3-pass)", H2),
          Paragraph("For each query token:", BODY)]

    score_rows = [
        [b("Pass"), b("Condition"), b("Points"), b("Purpose")],
        ["1", "edit_distance(query, word) == 0",   "+10",          "Exact word match"],
        ["2", "edit_distance(query, word) <= maxD", "+(10 - d*3)", "Fuzzy word match"],
        ["3", "trigram overlap",                    "+1 / gram",    "Partial / substring"],
    ]
    st = Table([[Paragraph(c, style("STH", fontSize=9,
                                    fontName="Helvetica-Bold" if i==0 else "Helvetica",
                                    textColor=colors.white if i==0 else colors.HexColor("#1F2937")))
                 for c in row] for i, row in enumerate(score_rows)],
               colWidths=[0.5*inch, 2.5*inch, 1.0*inch, 2.5*inch])
    st.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), TEAL),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, SILVER]),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor("#E5E7EB")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("FONTSIZE",      (0,1),(-1,-1), 9),
    ]))
    e += [st, sp(6),
          Paragraph(
              "The <b>maxEditDistance</b> threshold is read from "
              "<b>application.properties</b> (key: <b>search.max-edit-distance</b>, default 2) "
              "and injected via <b>@Value</b>. No restart is required if externalised via "
              "environment variable or config server.", BODY),
          PageBreak()]
    return e

# ── Section 2 — Production Readiness ─────────────────────────────────────────
def section_production():
    e = []
    e += [Paragraph("2. Production Readiness Analysis", H1), hr(),
          Paragraph(
              "The prototype demonstrates the core algorithm and API contract. "
              "The table below maps each production concern to its current state "
              "and a recommended upgrade path.", BODY), sp(6)]

    rows = [
        # label, status, color, notes
        ("Persistence",          "Not implemented", RED,
         "All data lives in JVM heap — lost on restart. "
         "Upgrade: add Spring Data JPA + PostgreSQL (documents table) and "
         "a dedicated search store such as Elasticsearch or OpenSearch."),
        ("Authentication / AuthZ","Not implemented", RED,
         "No auth on any endpoint. "
         "Upgrade: Spring Security + JWT (stateless) or OAuth 2.0 with a tenant-scoped scope claim. "
         "The X-Tenant-Id header must be derived from the verified token, not trusted from the client."),
        ("Input Validation",      "Partial", AMBER,
         "No @NotNull/@NotBlank constraints on DTOs. "
         "Upgrade: add jakarta.validation annotations + @Valid in controller params. "
         "Return 400 with structured error body."),
        ("Error Handling",        "Partial", AMBER,
         "404 / 204 returned correctly; no global exception handler. "
         "Upgrade: @ControllerAdvice + ProblemDetail (RFC 7807) for consistent error envelope."),
        ("API Rate Limiting",     "Not implemented", RED,
         "No throttling — a single tenant can saturate the JVM. "
         "Upgrade: Bucket4j or API gateway-level rate limiting per tenantId."),
        ("Observability",         "Not implemented", RED,
         "No metrics, tracing, or structured logging. "
         "Upgrade: Micrometer + Prometheus for metrics, OpenTelemetry for traces, "
         "Logback JSON encoder for structured logs."),
        ("Horizontal Scaling",    "Not implemented", RED,
         "In-memory state is not shared across pods. "
         "Upgrade: externalise indexes to Redis (inverted index as sorted sets) "
         "or Elasticsearch. Stateless Spring Boot instances behind a load balancer."),
        ("Tenant Lifecycle",      "Partial", AMBER,
         "Tenant delete cascades to indexes but not via a transactional boundary. "
         "Upgrade: wrap in a distributed transaction or saga when using an external store."),
        ("Search Quality",        "Partial", AMBER,
         "TF-IDF weighting not implemented; all word occurrences count equally. "
         "Upgrade: store term frequency at index time; multiply score by IDF."),
        ("Pagination",            "Not implemented", RED,
         "Search returns all matching docs. "
         "Upgrade: add ?page=&size= params; return Page<SearchResult> with total count."),
        ("Configuration Mgmt",    "Partial", AMBER,
         "search.max-edit-distance in application.properties. "
         "Upgrade: Spring Cloud Config or environment-variable overrides for per-environment tuning."),
        ("CI / CD",               "Not implemented", RED,
         "No pipeline defined. "
         "Upgrade: GitHub Actions — build + test on PR, Docker image push on merge to main, "
         "Helm chart deploy to Kubernetes."),
        ("Containerisation",      "Not implemented", RED,
         "No Dockerfile. "
         "Upgrade: multi-stage Dockerfile (eclipse-temurin:17-jdk-alpine builder + JRE runtime layer). "
         "Expose port 8080, set JVM heap via -XX:MaxRAMPercentage."),
        ("Health / Readiness",    "Partial", AMBER,
         "GET /health-check returns plain string. "
         "Upgrade: Spring Boot Actuator (/actuator/health with readiness + liveness probes for k8s)."),
        ("Secret Management",     "Not implemented", RED,
         "No secrets in use yet, but no vault integration either. "
         "Upgrade: HashiCorp Vault or AWS Secrets Manager; never commit credentials to source."),
    ]

    for label, status, color, notes in rows:
        badge = Table(
            [[Paragraph(label, style("RL", fontSize=10, fontName="Helvetica-Bold", textColor=NAVY)),
              Paragraph(status, style("RS", fontSize=9, fontName="Helvetica-Bold", textColor=color))]],
            colWidths=[3.2*inch, 3.3*inch]
        )
        badge.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), SILVER),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("LINEBELOW",     (0,0), (-1,-1), 1, TEAL),
        ]))
        e += [KeepTogether([badge, Paragraph(notes, style("N", fontSize=9, leading=13,
                                                           leftIndent=8, spaceAfter=8,
                                                           textColor=colors.HexColor("#374151")))])]

    e += [PageBreak()]
    return e

# ── Section 3 — Experience Showcase ──────────────────────────────────────────
def section_experience():
    e = []
    e += [Paragraph("3. Experience Showcase", H1), hr(),
          Paragraph(
              "This section highlights the engineering decisions made during the prototype "
              "and what they demonstrate about system design capability.", BODY)]

    items = [
        ("Structural Tenant Isolation",
         "Rather than filtering a shared store by a key prefix (error-prone), each tenant "
         "receives its own TenantIndex object — separate ConcurrentHashMaps for docs, word index, "
         "and trigram index. Cross-tenant data leakage becomes a compile-time impossibility: "
         "there is no shared collection to accidentally query without a tenant context."),
        ("Layered Fuzzy Search",
         "Three complementary signals are combined into a single relevance score: "
         "(1) exact word match via the word inverted index, "
         "(2) edit-distance word matching using Levenshtein (iterative, O(m*n) time, O(n) space), and "
         "(3) raw trigram overlap for substring and partial matches. "
         "This mirrors the approach used in production search engines such as Elasticsearch's "
         "match query pipeline."),
        ("Configurable Edit Distance",
         "The maximum Levenshtein distance is externalised to application.properties "
         "(search.max-edit-distance). This single line controls the fuzziness budget for the "
         "entire system — no recompilation needed. In a production system this would be "
         "per-tenant or per-index configurable."),
        ("Inverted Index with Trigram Pre-filter",
         "Trigrams act as a cheap candidate filter before the more expensive Levenshtein "
         "computation. Only words that share at least one trigram with the query token are "
         "evaluated for edit distance, bounding the worst-case cost to O(V * m * n) where "
         "V is the matching vocabulary fraction rather than the full vocabulary."),
        ("Score-ranked Responses",
         "Search results surface the raw relevance score alongside the document. "
         "This makes the ranking decision transparent for debugging and allows "
         "clients to apply their own threshold (e.g. hide results with score < 5)."),
        ("Clean Service Boundaries",
         "TenantService owns tenant lifecycle and hands TenantIndex instances to DocumentService. "
         "DocumentService has no knowledge of HTTP. Controllers have no business logic — "
         "they translate HTTP concerns (headers, status codes) and delegate. "
         "This separation means the search algorithm can be unit-tested without Spring context."),
        ("Concurrent-safe Data Structures",
         "ConcurrentHashMap is used throughout. computeIfAbsent / computeIfPresent "
         "are used for atomic index updates, avoiding lost-update races under concurrent indexing."),
    ]

    for title, body in items:
        e += [KeepTogether([
            Paragraph(title, H3),
            Paragraph(body, BODY),
            sp(4)
        ])]

    e += [PageBreak()]
    return e

# ── Section 4 — AI Tool Usage ─────────────────────────────────────────────────
def section_ai():
    e = []
    e += [Paragraph("4. AI Tool Usage", H1), hr(),
          Paragraph(
              "Claude Code (Anthropic) was used as a pair-programmer throughout this project. "
              "The following describes what was AI-assisted and where human judgement drove decisions.", BODY),
          sp(6)]

    assisted = [
        ("Scaffolding", "Initial controller stubs and DTO classes were generated from a natural-language description of the API contract, saving boilerplate time."),
        ("Boilerplate", "Levenshtein implementation, tokenizer, and trigram generator were generated and verified against known examples."),
        ("Dependency Diagnosis", "The root cause of the original /health-check 500 error (wrong Maven artifact names: spring-boot-starter-webmvc instead of spring-boot-starter-web) was identified by the AI in one step."),
        ("Documentation", "This PDF was authored with AI assistance — structure, content, and Python/ReportLab code."),
    ]

    human = [
        ("Architecture Decisions", "The choice to use per-tenant TenantIndex instances (structural isolation) over a shared map with prefix filtering was a deliberate design decision made by the engineer, not suggested by the AI."),
        ("Scoring Design", "The three-pass scoring model (exact=10, edit-distance scaled, trigram=1) and the decision to expose score in the API response were human-driven."),
        ("Production Readiness Prioritisation", "Identifying which gaps matter most for a real multi-tenant SaaS product (auth, persistence, rate limiting) reflects domain experience, not AI output."),
        ("Code Review", "Every generated snippet was read, understood, and accepted or modified before being committed. The AI produced no code that was not reviewed."),
    ]

    e += [Paragraph("AI-Assisted Tasks", H2)]
    for title, body in assisted:
        e += [Paragraph(f"<b>{title}</b> — {body}", BULLET), sp(3)]

    e += [sp(6), Paragraph("Human-Led Decisions", H2)]
    for title, body in human:
        e += [Paragraph(f"<b>{title}</b> — {body}", BULLET), sp(3)]

    e += [sp(10),
          Paragraph(
              "AI tooling accelerated execution on well-defined tasks (\"write a Levenshtein function\", "
              "\"generate a DTO\") while leaving architectural thinking, trade-off analysis, "
              "and production readiness judgement to the engineer. "
              "The result is a prototype that reflects genuine engineering reasoning, "
              "not uncritical AI output.", BODY)]
    return e

# ── Build ────────────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=letter,
        leftMargin=0.9*inch, rightMargin=0.9*inch,
        topMargin=0.85*inch, bottomMargin=0.85*inch,
        title="DocSearch Documentation",
        author="Abhishek Dhiman",
    )

    story = []
    story += cover()
    story += section_architecture()
    story += section_production()
    story += section_experience()
    story += section_ai()

    doc.build(story)
    print(f"Created: {OUTPUT}")

if __name__ == "__main__":
    build()
