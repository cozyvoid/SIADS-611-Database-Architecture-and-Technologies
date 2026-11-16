> **SIADS 611 — Module 2 supplementary study notes**  
> These notes cover lecture topics **not addressed** in the uploaded *Relational Database Design — Many-to-Many* slide deck. Explanations and sample code are instructional illustrations, **not verbatim video transcripts**.  
> Instructor references: [Python and PostgreSQL](https://www.pg4e.com/lectures/06-Python.php) · [JSON and PostgreSQL](https://www.pg4e.com/lectures/06-JSON.php)

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
