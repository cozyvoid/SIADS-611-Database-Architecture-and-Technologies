> **SIADS 611 — Module 2 supplementary study notes**  
> These notes cover lecture topics **not addressed** in the uploaded *Relational Database Design — Many-to-Many* slide deck. Explanations and sample code are instructional illustrations, **not verbatim video transcripts**.  
> Instructor references: [Python and PostgreSQL](https://www.pg4e.com/lectures/06-Python.php) · [JSON and PostgreSQL](https://www.pg4e.com/lectures/06-JSON.php)

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
