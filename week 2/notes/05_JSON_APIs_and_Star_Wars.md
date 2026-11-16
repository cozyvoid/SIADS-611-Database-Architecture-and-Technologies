> **SIADS 611 — Module 2 supplementary study notes**  
> These notes cover lecture topics **not addressed** in the uploaded *Relational Database Design — Many-to-Many* slide deck. Explanations and sample code are instructional illustrations, **not verbatim video transcripts**.  
> Instructor references: [Python and PostgreSQL](https://www.pg4e.com/lectures/06-Python.php) · [JSON and PostgreSQL](https://www.pg4e.com/lectures/06-JSON.php)

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
