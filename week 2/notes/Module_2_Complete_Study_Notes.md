# Module 2 — Complete Supplementary Lecture Study Guide

> **SIADS 611 — Module 2 supplementary study notes**  
> These notes cover lecture topics **not addressed** in the uploaded *Relational Database Design — Many-to-Many* slide deck. Explanations and sample code are instructional illustrations, **not verbatim video transcripts**.  
> Instructor references: [Python and PostgreSQL](https://www.pg4e.com/lectures/06-Python.php) · [JSON and PostgreSQL](https://www.pg4e.com/lectures/06-JSON.php)

## Contents

- [01 Python and PostgreSQL](#01-python-and-postgresql)
- [02 Mail Archive and Search Ranking](#02-mail-archive-and-search-ranking)
- [03 JSON Fundamentals and Python](#03-json-fundamentals-and-python)
- [04 PostgreSQL JSON JSONB](#04-postgresql-json-jsonb)
- [05 JSON APIs and Star Wars](#05-json-apis-and-star-wars)

---

# Part A — Python and PostgreSQL

**Lectures 1–3:** PostgreSQL and Python (5 min); `simple.py` (16 min); `loadbook.py` (13 min).

## 1. Connecting Python to PostgreSQL

**Main idea:** Python can connect to PostgreSQL to retrieve, insert, update, and analyze database records automatically. `psql` lets you type SQL manually; a Python program issues SQL programmatically.

**Conceptual workflow:** Python program → database connection → cursor executes SQL → PostgreSQL → rows returned to Python.

| Term | Meaning |
|---|---|
| `psycopg2` | Python database adapter for PostgreSQL |
| Connection | Authenticated session between Python and PostgreSQL |
| Cursor | Object that executes SQL and retrieves results |
| Transaction | Unit of work that can be committed or rolled back |
| `commit()` | Persists pending database changes |

## 2. `simple.py`: Basic Python/PostgreSQL workflow

```python
import psycopg2

conn = psycopg2.connect(
    host="your_host",
    dbname="your_database",
    user="your_username",
    password="your_password"
)

cur = conn.cursor()
cur.execute("SELECT id, name FROM artist;")
rows = cur.fetchall()
for row in rows:
    print(row)

cur.close()
conn.close()
```

**Read the example in order:**
1. `connect()` authenticates with PostgreSQL.
2. `cursor()` makes a command interface.
3. `execute()` sends a SQL query.
4. `fetchall()` collects the returned rows.
5. `close()` releases resources.

**Safe inserts — always parameterize values:**

```python
cur.execute(
    "INSERT INTO artist (name) VALUES (%s)",
    ("Queen",)
)
conn.commit()
```

The `%s` marker represents a value supplied separately; this helps prevent SQL injection. `execute()` runs the statement, while `commit()` makes a change permanent. A plain `SELECT` ordinarily does not require committing a change.

**Helpful additional methods:** `fetchone()` returns one row; `fetchmany(n)` returns a batch. Use `rollback()` after a failed transaction when necessary.

## 3. `loadbook.py`: Turning a text document into database rows

**Main idea:** Extract text, split it into meaningful units such as paragraphs, insert them into PostgreSQL, and index the content for searching.

**Workflow:** Download text → read/split paragraphs → insert rows → commit batches → create index → query.

```sql
CREATE TABLE book (
    id SERIAL PRIMARY KEY,
    body TEXT
);

CREATE INDEX book_search_idx
ON book USING GIN (to_tsvector('english', body));

SELECT id, body
FROM book
WHERE to_tsvector('english', body)
      @@ to_tsquery('english', 'database');
```

- `to_tsvector('english', body)` converts text into searchable normalized tokens.
- `to_tsquery('english', 'database')` creates a full-text query.
- `@@` tests whether document tokens match the query.
- `GIN` is an index type useful for full-text lookup.

**Connection to Week 1:** This is the same full-text pattern used in the `docs03` assignment, but Python first loads the data.

**Study check:** What is the difference between inserting raw text and making that text searchable using a GIN index?

**Reference code:** [loadbook.py](https://www.pg4e.com/code/loadbook.py).


---

# Part B — Mail Archive and Search Ranking

**Lectures 4–8:** Mail Archive (4 min); Mail Archive 1/3 (17 min); Mail Archive 2/3 (11 min); Ranking Search Results with PostgreSQL (4 min); Mail Archive 3/3 (7 min).

## 4. Mail Archive: A messy real-world dataset

**Main idea:** Raw email archives contain metadata and body text that can be parsed, cleaned, loaded into PostgreSQL, and searched.

Common fields include sender, recipient, subject, timestamps, headers, and body. **Mbox** is a format for storing multiple email messages in one file.

## 5–6. Mail Archive demonstrations 1/3 and 2/3

The process resembles **ETL — Extract, Transform, Load**:

| Phase | Action |
|---|---|
| Extract | Retrieve messages from an archive |
| Transform | Parse headers, normalize dates, handle inconsistent formatting |
| Load | Insert records into PostgreSQL |

Illustrative table:

```sql
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    email TEXT,
    sent_at TIMESTAMPTZ,
    subject TEXT,
    headers TEXT,
    body TEXT
);
```

Important engineering ideas:
- **Data cleaning:** heterogeneous source formats need standardization.
- **Restartability:** save processing progress so the job can resume after interruption.
- **Incremental commits:** persist chunks of completed work rather than holding everything in one long transaction.
- **Duplicate handling:** a restarted loader needs a strategy to avoid repeating previously committed records.
- **Indexing:** query performance matters after messages have been stored.

## 7. Ranking Search Results with PostgreSQL

A full-text search can return many matches. Relevance ranking answers a different question: **which matching documents are most useful?**

| Function | Meaning |
|---|---|
| `ts_rank()` | Relevance based on matching terms, frequencies, and optional weights |
| `ts_rank_cd()` | Cover-density relevance that considers proximity of matches |

```sql
SELECT id, subject,
       ts_rank(
           to_tsvector('english', body),
           to_tsquery('english', 'personal & learning')
       ) AS relevance
FROM messages
WHERE to_tsvector('english', body)
      @@ to_tsquery('english', 'personal & learning')
ORDER BY relevance DESC;
```

Breakdown:
1. `WHERE ... @@ ...` filters to messages matching **both** search terms.
2. `ts_rank(...)` calculates a score.
3. `ORDER BY relevance DESC` displays the highest score first.

**Distinguish:** A GIN full-text index speeds finding matches; ranking functions order the results. An index does not automatically choose the best-ranked match.

## 8. Mail Archive demonstration 3/3

This closes the pipeline: **Raw mail → Parsing → Cleaning → PostgreSQL → Full-text indexing → Search → Ranking**.

**Study check:** Why might an archive loader need both incremental commits and duplicate protection?

**Reference code:** [gmane.py](https://www.pg4e.com/code/gmane.py).


---

# Part C — JSON Fundamentals and Python

**Lectures 9–11:** JavaScript Object Notation (11 min); Douglas Crockford interview (7 min); Python and JSON (7 min).

## 9. JavaScript Object Notation (JSON)

**JSON = JavaScript Object Notation**, a text-based, language-independent format for exchanging structured data.

```json
{
  "student": "Jane",
  "age": 25,
  "enrolled": true,
  "courses": ["Python", "SQL"],
  "address": {"city": "Ann Arbor", "state": "Michigan"}
}
```

| JSON type | Example | Python counterpart |
|---|---|---|
| Object | `{"name":"Jane"}` | `dict` |
| Array | `["SQL","Python"]` | `list` |
| String | `"Jane"` | `str` |
| Number | `25`, `3.5` | `int`, `float` |
| Boolean | `true`, `false` | `True`, `False` |
| Null | `null` | `None` |

**Syntax rules:** Keys and strings use **double quotes**; booleans and `null` are lowercase; trailing commas are not allowed in standard JSON.

## 10. Douglas Crockford interview: Why JSON matters

JSON became popular as a lightweight alternative to more verbose interchange formats such as XML. Its simple arrays and objects map naturally to programming data structures, allowing different systems to communicate.

**Key conclusion:** A widely supported shared data format reduces the work needed to exchange structured information.

## 11. Python and JSON

Python provides the built-in `json` module.

| Function | Direction |
|---|---|
| `json.dumps(python_object)` | Python object → JSON string |
| `json.loads(json_string)` | JSON string → Python object |
| `json.dump(obj, file)` | Python object → JSON file |
| `json.load(file)` | JSON file → Python object |

```python
import json

student = {
    "name": "Jane",
    "courses": ["SQL", "Python"],
    "active": True
}

json_string = json.dumps(student, indent=4)
print(json_string)

restored = json.loads(json_string)
print(restored["name"])  # Jane
```

- **Serialization** means converting a Python object into JSON for storage or transmission.
- **Deserialization** means parsing JSON back into Python data structures.
- JSON is **text**, not a Python dictionary; you must parse it before accessing keys as Python objects.

**Study check:** How do `json.dumps()` and `json.loads()` differ? Why is `True` valid Python but not valid raw JSON?


---

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


---

# Part E — JSON APIs and Star Wars Demonstrations

**Lectures 14–16:** Using a JSON API (3 min); Star Wars API 1/2 (17 min); Star Wars API 2/2 (16 min).

## 14. Using a JSON API

**API = Application Programming Interface.** A web API allows software to request data from another service. Many APIs return JSON.

**Typical flow:** Python sends HTTP GET → API returns JSON → Python parses and validates → PostgreSQL stores records.

| Status | Meaning |
|---|---|
| `200` | OK |
| `400` | Bad request |
| `401` | Unauthorized / authentication failed |
| `404` | Not found |
| `429` | Too many requests |
| `500` | Server error |

Additional terms:
- **Endpoint:** URL that accepts an API request.
- **Pagination:** dividing results into multiple pages.
- **Rate limiting:** controlling how many requests a client can make.
- **Timeout:** upper limit on how long the client waits for a response.

## 15. Star Wars API 1/2: Retrieval and storage

**Main idea:** Use an API to download JSON resources and save them as PostgreSQL JSONB records.

An illustrative Python example (not the instructor's complete script):

```python
import requests
import psycopg2
from psycopg2.extras import Json

url = "https://swapi.py4e.com/api/people/1/"
response = requests.get(url, timeout=15)
response.raise_for_status()
data = response.json()

conn = psycopg2.connect(
    host="your_host",
    dbname="your_database",
    user="your_username",
    password="your_password"
)

with conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id SERIAL PRIMARY KEY,
                data JSONB
            )
        """)
        cur.execute(
            "INSERT INTO characters (data) VALUES (%s)",
            (Json(data),)
        )
conn.close()
```

`response.raise_for_status()` throws an error for an unsuccessful HTTP response. `response.json()` parses the JSON into a Python object. `Json(data)` adapts a Python object for storage in a PostgreSQL JSON/JSONB column.

## 16. Star Wars API 2/2: Following links and querying JSONB

Many API responses contain URLs to other resources. A **crawler/spider** follows those links to discover more records. Practical crawlers track visited URLs, avoid redundant requests, handle failed responses, and resume after interruptions.

Query the stored JSONB documents:

```sql
SELECT data->>'name' AS character_name,
       data->>'gender' AS gender
FROM characters;
```

**Complete ingestion pattern:** Request → Check response → Parse JSON → Store safely → Discover new URLs → Track completed URLs → Repeat.

**Study check:** How is fetching a single API endpoint different from a crawler? What should happen when an API returns HTTP 429 or times out?

**Reference code:** [swapi.py](https://www.pg4e.com/code/swapi.py).


---

# Module 2 — Review Checklist and Quick Reference

## Preparation checklist

- [ ] Explain what `psycopg2` does.
- [ ] Use a connection and cursor to execute SQL.
- [ ] Distinguish `execute()`, `fetchone()`, `fetchall()`, and `commit()`.
- [ ] Explain ETL and why ingestion pipelines need restartability.
- [ ] Distinguish `ts_rank()` and `ts_rank_cd()`.
- [ ] Recognize valid JSON types and syntax.
- [ ] Use `json.dumps()` and `json.loads()`.
- [ ] Explain the differences between `JSON` and `JSONB`.
- [ ] Use `->`, `->>`, `@>`, `?`, and casts.
- [ ] Explain a JSONB GIN index versus a full-text GIN index.
- [ ] Describe the API → Python → PostgreSQL workflow.
- [ ] Explain HTTP codes, pagination, rate limits, and retries.
- [ ] Explain why a crawler tracks previously visited URLs.
- [ ] Write a JSONB query that extracts one named field.

## SQL/Python quick reference

| Task | Command |
|---|---|
| Connect | `psycopg2.connect(...)` |
| Cursor | `conn.cursor()` |
| Query | `cur.execute(...)` |
| One row | `cur.fetchone()` |
| All rows | `cur.fetchall()` |
| Persist transaction | `conn.commit()` |
| Python → JSON text | `json.dumps(data)` |
| JSON text → Python | `json.loads(text)` |
| JSONB field as JSON | `body->'name'` |
| JSONB field as text | `body->>'name'` |
| JSONB containment | `body @> '{"name":"Jane"}'` |
| Convert text to integer | `::int` |
| Full-text relevance | `ts_rank(vector, query)` |
| GIN on JSONB | `CREATE INDEX ... USING GIN (body);` |

## Note about the uploaded slides

The 60-slide *Relational Database Design — Many-to-Many* presentation covers relational schema design, keys, normalization, JOINs, cascade behavior, and many-to-many junction tables. It does **not** directly teach the listed Python, mail archive, JSONB, and API demonstrations. These supplementary files fill that gap through summarized explanations and illustrative code rather than representing the video's complete spoken content.
