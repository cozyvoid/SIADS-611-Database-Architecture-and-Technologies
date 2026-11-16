> **SIADS 611 — Module 2 supplementary study notes**  
> These notes cover lecture topics **not addressed** in the uploaded *Relational Database Design — Many-to-Many* slide deck. Explanations and sample code are instructional illustrations, **not verbatim video transcripts**.  
> Instructor references: [Python and PostgreSQL](https://www.pg4e.com/lectures/06-Python.php) · [JSON and PostgreSQL](https://www.pg4e.com/lectures/06-JSON.php)

# Part D — PostgreSQL JSON and JSONB

**Lectures 12–13:** PostgreSQL and JSON (11 min); Music Tracks and JSONB (27 min).

## 12. Storing JSON in PostgreSQL

**Main idea:** A PostgreSQL table can hold a structured JSON document in one column rather than requiring a separate column for every document attribute.

| Feature | `JSON` | `JSONB` |
|---|---|---|
| Storage | Preserves input JSON text representation | Parsed binary representation |
| Formatting and key order | Input representation preserved | Not preserved |
| Indexing | More limited | GIN indexing available |
| Common fit | Keep source text representation | Query and filter document properties |

`JSONB` is often convenient when documents will be queried repeatedly.

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    details JSONB
);

INSERT INTO products (details)
VALUES ('{"name":"Laptop","price":900,"brand":"Dell"}');
```

### Important JSONB operators

| Operator | Meaning | Example |
|---|---|---|
| `->` | Return a JSON/JSONB value | `details->'price'` |
| `->>` | Return a value as SQL text | `details->>'name'` |
| `@>` | JSONB containment | `details @> '{"brand":"Dell"}'` |
| `?` | Check for a top-level key or string array element | `details ? 'brand'` |
| `::` | SQL type cast | `(details->>'price')::numeric` |

```sql
SELECT details->>'name' AS name,
       (details->>'price')::numeric AS price
FROM products
WHERE (details->>'price')::numeric > 500;
```

**Why cast?** `->>` returns SQL text, so numeric comparison requires converting that text to a number.

## 13. Music Tracks and JSONB

An example music document:

```json
{
  "name": "Black Dog",
  "artist": "Led Zeppelin",
  "album": "IV",
  "count": 25,
  "rating": 5
}
```

Store and query documents:

```sql
CREATE TABLE jtrack (
    id SERIAL PRIMARY KEY,
    body JSONB
);

SELECT body->>'name' AS song
FROM jtrack
WHERE body->>'artist' = 'Led Zeppelin';

SELECT *
FROM jtrack
WHERE body @> '{"artist":"Led Zeppelin"}';
```

Index the JSONB column:

```sql
CREATE INDEX jtrack_gin
ON jtrack USING GIN (body);
```

**Distinguish two GIN uses:**
- Full-text GIN indexes support searches over lexemes produced by `to_tsvector`.
- JSONB GIN indexes support certain queries over JSON structure and contained values, such as `@>`.

**Study check:** What does `->>` return? Why would a containment query and an ordinary text equality query use different indexing strategies?
