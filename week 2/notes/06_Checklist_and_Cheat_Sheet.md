> **SIADS 611 — Module 2 supplementary study notes**  
> These notes cover lecture topics **not addressed** in the uploaded *Relational Database Design — Many-to-Many* slide deck. Explanations and sample code are instructional illustrations, **not verbatim video transcripts**.  
> Instructor references: [Python and PostgreSQL](https://www.pg4e.com/lectures/06-Python.php) · [JSON and PostgreSQL](https://www.pg4e.com/lectures/06-JSON.php)

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
