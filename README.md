# DocSearch

A multi-tenant document search engine prototype built with Spring Boot 4.1 and Java 17.

Supports full-text search using a **word-level inverted index** + **trigram index (n=3)** + **Levenshtein edit-distance fuzzy matching** — all in-memory, no external dependencies.

---

## Stack

- Java 17
- Spring Boot 4.1
- Lombok
- Maven

---

## Quick Start

```bash
./mvnw spring-boot:run
```

Server starts on `http://localhost:8080`.

---

## API Reference

### Health

```
GET /health-check
```

---

### Tenants

Tenants must be registered before documents can be indexed.

```
POST   /api/v1/tenants          # Register a tenant
GET    /api/v1/tenants          # List all tenants
GET    /api/v1/tenants/{id}     # Get tenant by ID
DELETE /api/v1/tenants/{id}     # Delete tenant + all its documents
```

**Register a tenant**
```bash
curl -s -X POST http://localhost:8080/api/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{"name": "acme-corp"}'
```

```json
{
  "id": "a1b2c3d4-...",
  "name": "acme-corp",
  "createdAt": "2026-06-24T00:00:00Z"
}
```

---

### Documents

All document endpoints require the `X-Tenant-Id` header set to a registered tenant UUID.

```
POST   /api/v1/documents        # Index a new document
GET    /api/v1/documents/{id}   # Retrieve a document
DELETE /api/v1/documents/{id}   # Remove a document
```

**Index a document**
```bash
curl -s -X POST http://localhost:8080/api/v1/documents \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: <tenantId>" \
  -d '{"title": "Spring Boot Guide", "content": "Learn Spring Boot with Java 17."}'
```

```json
{
  "id": "d1e2f3...",
  "tenantId": "a1b2c3d4-...",
  "title": "Spring Boot Guide",
  "content": "Learn Spring Boot with Java 17.",
  "createdAt": "2026-06-24T00:00:00Z"
}
```

---

### Search

```
GET /api/v1/search?q={query}&tenant={tenantId}
```

Results are ranked by relevance score (descending). Fuzzy matching surfaces results even with typos.

```bash
curl "http://localhost:8080/api/v1/search?q=sprng+bot&tenant=<tenantId>"
```

```json
[
  {
    "document": {
      "id": "d1e2f3...",
      "title": "Spring Boot Guide",
      ...
    },
    "score": 11
  }
]
```

---

## Multi-Tenancy

Each tenant gets a completely isolated document store and inverted index. A document indexed under `tenant-a` is invisible to `tenant-b` — structurally, not just by filtering.

```
TenantService
├── tenant-a  →  TenantIndex (docs, wordIndex, trigramIndex)
└── tenant-b  →  TenantIndex (docs, wordIndex, trigramIndex)
```

---

## Search Algorithm

Every query runs a **3-pass scoring** model per token:

| Pass | Match type | Score |
|------|-----------|-------|
| 1 | Exact word match | +10 pts |
| 2 | Edit distance ≤ `max-edit-distance` | `+(10 - distance × 3)` |
| 3 | Trigram overlap | +1 pt per shared trigram |

**Trigrams** — sliding 3-character windows over each word:
```
"spring"  →  spr, pri, rin, ing
```
A search for `"sprng"` shares the trigram `spr` with `"spring"`, so the document surfaces even without an exact match.

**Edit distance** (Levenshtein) is computed after trigram pre-filtering to confirm fuzzy word matches precisely.

---

## Configuration

```properties
# application.properties
search.max-edit-distance=2   # 0 = exact only, 1 = one typo, 2 = two typos
```

---

## Project Structure

```
src/main/java/com/docsearch/app/
├── controller/
│   ├── DocumentController.java
│   ├── TenantController.java
│   └── GeneralController.java
├── service/
│   ├── DocumentService.java
│   ├── TenantService.java
│   └── TenantIndex.java
├── model/
│   ├── Document.java
│   └── Tenant.java
├── dto/
│   ├── CreateDocumentRequest.java
│   ├── CreateTenantRequest.java
│   └── SearchResult.java
└── AppApplication.java
```

---

## Postman Collection

Import `DocSearch.postman_collection.json` into Postman.

The collection auto-saves `tenantId` and `documentId` from responses — run **Register Tenant → Index Document → Search** without copying any IDs manually.

## Docker Command

docker build -t docsearch:latest .
docker run -p 8080:8080 docsearch:latest
docker run -p 8080:8080 -e SEARCH_MAX_EDIT_DISTANCE=1 docsearch:latest
