# Week 4 Supplemental Lecture: SQL and Pandas

> **Supplemental material:** The uploaded *Text in Databases* deck is primarily about PostgreSQL text handling, encodings, hashing, indexes, and regular expressions. It does **not** substantially teach pandas. These notes fill that gap for a Week 4 topic labeled **SQL and Pandas**.

---

# 1. Why SQL and Pandas Are Taught Together

SQL and pandas solve overlapping data-manipulation problems, but they operate in different environments.

## SQL

SQL usually operates **inside a database management system**.

Strengths:

- filtering large datasets before data leaves the database,
- joins,
- grouping and aggregation,
- enforcing schema and constraints,
- indexes and query optimization,
- multi-user access,
- persistent storage.

## pandas

pandas usually operates **inside Python memory** using a `DataFrame`.

Strengths:

- exploratory data analysis,
- flexible reshaping,
- cleaning,
- feature engineering,
- integration with NumPy, scikit-learn, matplotlib, and other Python tools.

## Core workflow

```text
Database
   ↓
SQL query
   ↓
smaller result set
   ↓
pandas DataFrame
   ↓
analysis / visualization / machine learning
```

A useful rule:

> **Let the database do database work, and let pandas do analysis work.**

Do not pull millions of unnecessary rows into pandas if SQL can reduce the dataset first.

---

# 2. SQL Table versus pandas DataFrame

| Database concept | pandas concept |
|---|---|
| table | `DataFrame` |
| row | observation / DataFrame row |
| column | `Series` |
| `SELECT` | column selection |
| `WHERE` | Boolean filtering |
| `ORDER BY` | `sort_values()` |
| `GROUP BY` | `groupby()` |
| `JOIN` | `merge()` |
| `NULL` | usually `NaN`, `None`, or `pd.NA`, depending on dtype |
| database schema | DataFrame dtypes + conventions |
| database index | not the same as a pandas index |

### Important warning

A pandas **index** is mainly a labeling/alignment mechanism.

A database **index** is mainly a query-performance structure.

---

# 3. Reading SQL Data into pandas

```python
import pandas as pd

query = """
SELECT id, email
FROM em
WHERE email LIKE '%umich%';
"""

df = pd.read_sql_query(query, connection)
```

The SQL result becomes a pandas `DataFrame`.

You may also see:

```python
pd.read_sql(...)
```

which can read a SQL query or a table, depending on the connection and input.

---

# 4. Parameterized Queries

Avoid constructing SQL by inserting untrusted values directly into a query string.

Poor pattern:

```python
name = input("Name: ")
query = f"SELECT * FROM users WHERE name = '{name}'"
```

Prefer parameterized SQL supported by the database layer.

Conceptually:

```python
query = """
SELECT *
FROM users
WHERE name = :name
"""

df = pd.read_sql_query(
    query,
    connection,
    params={"name": name}
)
```

Exact placeholder syntax can vary by driver or SQL toolkit.

---

# 5. `SELECT` versus Column Selection

SQL:

```sql
SELECT id, email
FROM em;
```

pandas:

```python
df[["id", "email"]]
```

Single column:

```python
df["email"]
```

returns a `Series`.

Multiple columns:

```python
df[["id", "email"]]
```

returns a `DataFrame`.

---

# 6. `WHERE` versus Boolean Filtering

SQL:

```sql
SELECT *
FROM em
WHERE id > 3;
```

pandas:

```python
df[df["id"] > 3]
```

Multiple conditions in SQL:

```sql
SELECT *
FROM em
WHERE id > 3
  AND email LIKE '%edu';
```

pandas:

```python
df[
    (df["id"] > 3)
    & (df["email"].str.endswith("edu"))
]
```

Use:

- `&` for AND
- `|` for OR
- `~` for NOT

Put each comparison in parentheses.

---

# 7. String Operations

## Lowercase

SQL:

```sql
SELECT lower(email)
FROM em;
```

pandas:

```python
df["email"].str.lower()
```

## Uppercase

```python
df["email"].str.upper()
```

## Starts with

SQL:

```sql
WHERE email LIKE 'c%'
```

pandas:

```python
df[df["email"].str.startswith("c")]
```

## Ends with

SQL:

```sql
WHERE email LIKE '%edu'
```

pandas:

```python
df[df["email"].str.endswith("edu")]
```

## Contains

SQL:

```sql
WHERE email LIKE '%umich%'
```

pandas:

```python
df[df["email"].str.contains("umich", regex=False)]
```

`regex=False` means treat the search text literally.

---

# 8. Regular Expressions in pandas

## Find rows containing a digit

SQL:

```sql
SELECT *
FROM em
WHERE email ~ '[0-9]';
```

pandas:

```python
df[df["email"].str.contains(r"[0-9]", regex=True)]
```

## Extract digits

SQL:

```sql
SELECT substring(email FROM '[0-9]+')
FROM em;
```

pandas:

```python
df["number"] = df["email"].str.extract(r"([0-9]+)")
```

## Extract email domain

SQL:

```sql
SELECT substring(email FROM '.+@(.*)$')
FROM em;
```

pandas:

```python
df["domain"] = df["email"].str.extract(r"@(.+)$")
```

---

# 9. `DISTINCT` versus `drop_duplicates()`

SQL:

```sql
SELECT DISTINCT domain
FROM email_data;
```

pandas:

```python
df["domain"].drop_duplicates()
```

or:

```python
df.drop_duplicates(subset=["domain"])
```

For an array of unique values:

```python
df["domain"].unique()
```

---

# 10. `ORDER BY` versus `sort_values()`

SQL:

```sql
SELECT *
FROM em
ORDER BY email;
```

pandas:

```python
df.sort_values("email")
```

Descending:

```python
df.sort_values("email", ascending=False)
```

Multiple columns:

```python
df.sort_values(
    ["domain", "email"],
    ascending=[True, False]
)
```

---

# 11. `GROUP BY` versus `groupby()`

SQL:

```sql
SELECT domain, COUNT(*)
FROM email_data
GROUP BY domain;
```

pandas:

```python
df.groupby("domain").size()
```

To return a DataFrame:

```python
counts = (
    df.groupby("domain")
      .size()
      .reset_index(name="count")
)
```

## Multiple aggregates

SQL:

```sql
SELECT
    department,
    COUNT(*) AS n,
    AVG(salary) AS avg_salary
FROM employees
GROUP BY department;
```

pandas:

```python
summary = (
    df.groupby("department")
      .agg(
          n=("salary", "size"),
          avg_salary=("salary", "mean")
      )
      .reset_index()
)
```

---

# 12. `HAVING` versus Filtering an Aggregation

SQL:

```sql
SELECT domain, COUNT(*) AS n
FROM email_data
GROUP BY domain
HAVING COUNT(*) > 5;
```

pandas:

```python
counts = (
    df.groupby("domain")
      .size()
      .reset_index(name="n")
)

counts[counts["n"] > 5]
```

Remember:

- `WHERE` filters rows **before** grouping.
- `HAVING` filters groups **after** aggregation.

---

# 13. SQL Joins versus `merge()`

## Inner join

SQL:

```sql
SELECT *
FROM patients
JOIN visits
USING (patient_id);
```

pandas:

```python
patients.merge(
    visits,
    on="patient_id",
    how="inner"
)
```

## Left join

SQL:

```sql
SELECT *
FROM patients
LEFT JOIN visits
USING (patient_id);
```

pandas:

```python
patients.merge(
    visits,
    on="patient_id",
    how="left"
)
```

Common `how=` values:

```python
"inner"
"left"
"right"
"outer"
"cross"
```

Current pandas also supports anti-join styles such as:

```python
"left_anti"
"right_anti"
```

---

# 14. Important Join Difference: Missing Keys

SQL and pandas can behave differently when join keys are missing.

In SQL, a `NULL` key does not normally compare equal to another `NULL`.

In pandas merges, missing key values can match each other.

Before joining, inspect key columns:

```python
df["patient_id"].isna().sum()
```

Then decide whether missing keys should be:

- removed,
- imputed,
- left unmatched,
- treated as a special category.

---

# 15. `IN` versus `isin()`

SQL:

```sql
SELECT *
FROM em
WHERE domain IN ('umich.edu', 'apple.com');
```

pandas:

```python
df[
    df["domain"].isin(
        ["umich.edu", "apple.com"]
    )
]
```

Negation:

```python
df[
    ~df["domain"].isin(
        ["umich.edu", "apple.com"]
    )
]
```

---

# 16. `BETWEEN` versus `between()`

SQL:

```sql
SELECT *
FROM scores
WHERE score BETWEEN 70 AND 90;
```

pandas:

```python
df[df["score"].between(70, 90)]
```

---

# 17. Missing Values

SQL:

```sql
WHERE value IS NULL
```

pandas:

```python
df[df["value"].isna()]
```

Non-missing:

```python
df[df["value"].notna()]
```

Fill missing values:

```python
df["value"] = df["value"].fillna(0)
```

Drop rows with missing values:

```python
df.dropna()
```

---

# 18. SQL `CASE` versus pandas Conditional Logic

SQL:

```sql
SELECT
    score,
    CASE
        WHEN score >= 90 THEN 'A'
        WHEN score >= 80 THEN 'B'
        ELSE 'Other'
    END AS grade
FROM scores;
```

pandas:

```python
import numpy as np

df["grade"] = np.select(
    [
        df["score"] >= 90,
        df["score"] >= 80
    ],
    [
        "A",
        "B"
    ],
    default="Other"
)
```

Simple two-way condition:

```python
df["passed"] = np.where(
    df["score"] >= 70,
    "yes",
    "no"
)
```

---

# 19. `LIMIT` versus `head()`

SQL:

```sql
SELECT *
FROM em
LIMIT 5;
```

pandas:

```python
df.head(5)
```

Last rows:

```python
df.tail(5)
```

---

# 20. Calculated Columns

SQL:

```sql
SELECT
    price,
    quantity,
    price * quantity AS total
FROM sales;
```

pandas:

```python
df["total"] = (
    df["price"] * df["quantity"]
)
```

---

# 21. SQL Aggregate Functions and pandas

| SQL | pandas |
|---|---|
| `COUNT(*)` | `len(df)` or `groupby().size()` |
| `COUNT(col)` | `df["col"].count()` |
| `SUM(col)` | `df["col"].sum()` |
| `AVG(col)` | `df["col"].mean()` |
| `MIN(col)` | `df["col"].min()` |
| `MAX(col)` | `df["col"].max()` |
| `STDDEV(col)` | `df["col"].std()` |

`COUNT(column)` ignores SQL `NULL`s; similarly, pandas `.count()` counts non-missing values.

---

# 22. Push Filtering into SQL When Possible

Suppose the database has 10 million records but you need only 2026 rows.

Less efficient:

```python
df = pd.read_sql_query(
    "SELECT * FROM visits",
    connection
)

df = df[df["visit_date"] >= "2026-01-01"]
```

Better:

```python
df = pd.read_sql_query(
    """
    SELECT *
    FROM visits
    WHERE visit_date >= '2026-01-01'
    """,
    connection
)
```

Why?

The database can:

- use indexes,
- avoid transferring unnecessary rows,
- reduce Python memory use,
- reduce network traffic.

---

# 23. Select Only Needed Columns

Less efficient:

```sql
SELECT *
FROM massive_table;
```

Better:

```sql
SELECT
    patient_id,
    visit_date,
    diagnosis
FROM massive_table;
```

This reduces:

- I/O,
- network transfer,
- memory use,
- clutter in pandas.

---

# 24. Use SQL for Heavy Joins When Appropriate

If large tables already live in PostgreSQL, joining them in SQL is often better than loading all of them separately and joining in pandas.

```sql
SELECT
    p.patient_id,
    p.age,
    v.visit_date,
    v.diagnosis
FROM patients AS p
JOIN visits AS v
  ON p.patient_id = v.patient_id;
```

Then:

```python
df = pd.read_sql_query(
    query,
    connection
)
```

This lets PostgreSQL use:

- indexes,
- join planning,
- statistics,
- query optimization.

---

# 25. Use pandas for Flexible Analysis After Extraction

Once a manageable result is in memory, pandas is convenient for:

- cleaning,
- reshaping,
- exploratory summaries,
- plotting,
- feature engineering,
- model preparation.

Example:

```python
df["domain"] = (
    df["email"]
      .str.extract(r"@(.+)$")
)

summary = (
    df["domain"]
      .value_counts()
      .rename_axis("domain")
      .reset_index(name="count")
)
```

---

# 26. SQL and pandas Regex Side by Side

## Contains digits

SQL:

```sql
WHERE email ~ '[0-9]'
```

pandas:

```python
df["email"].str.contains(r"[0-9]")
```

## Starts with `c`

SQL:

```sql
WHERE email ~ '^c'
```

pandas:

```python
df["email"].str.startswith("c")
```

## Ends with `edu`

SQL:

```sql
WHERE email ~ 'edu$'
```

pandas:

```python
df["email"].str.endswith("edu")
```

## Extract domain

SQL:

```sql
substring(email FROM '.+@(.*)$')
```

pandas:

```python
df["email"].str.extract(r"@(.+)$")
```

---

# 27. SQL and pandas Equivalent Cheat Sheet

| Goal | SQL | pandas |
|---|---|---|
| choose columns | `SELECT a, b` | `df[["a","b"]]` |
| filter | `WHERE a > 5` | `df[df["a"] > 5]` |
| sort | `ORDER BY a` | `df.sort_values("a")` |
| first rows | `LIMIT 5` | `df.head(5)` |
| unique | `DISTINCT a` | `df["a"].drop_duplicates()` |
| membership | `a IN (...)` | `df["a"].isin(...)` |
| range | `BETWEEN` | `.between()` |
| group | `GROUP BY` | `.groupby()` |
| count groups | `COUNT(*)` | `.groupby().size()` |
| inner join | `INNER JOIN` | `.merge(..., how="inner")` |
| left join | `LEFT JOIN` | `.merge(..., how="left")` |
| null test | `IS NULL` | `.isna()` |
| not null | `IS NOT NULL` | `.notna()` |
| lowercase | `lower(a)` | `.str.lower()` |
| uppercase | `upper(a)` | `.str.upper()` |
| starts with | `LIKE 'abc%'` | `.str.startswith("abc")` |
| contains | `LIKE '%abc%'` | `.str.contains("abc", regex=False)` |
| regex match | `~` | `.str.contains(regex)` |
| regex extract | `substring(... FROM regex)` | `.str.extract(regex)` |

---

# 28. Reproducing the Lecture's Email-Domain Analysis in pandas

```python
df = pd.DataFrame({
    "email": [
        "csev@umich.edu",
        "coleen@umich.edu",
        "sally@uiuc.edu",
        "ted79@umuc.edu",
        "glenn1@apple.com",
        "nbody@apple.com"
    ]
})
```

Extract the domain:

```python
df["domain"] = (
    df["email"]
      .str.extract(r"@(.+)$")
)
```

Count domains:

```python
domain_counts = (
    df.groupby("domain")
      .size()
      .reset_index(name="count")
      .sort_values(
          "count",
          ascending=False
      )
)
```

Equivalent SQL:

```sql
SELECT
    substring(email FROM '.+@(.*)$') AS domain,
    COUNT(*) AS count
FROM em
GROUP BY domain
ORDER BY count DESC;
```

Studying the same operation in both languages is an effective way to learn the relationship between SQL and pandas.

---

# 29. Example Database-First Workflow

```python
import pandas as pd

query = """
SELECT
    patient_id,
    visit_date,
    diagnosis,
    age
FROM visits
WHERE visit_date >= '2026-01-01'
  AND age >= 18;
"""

df = pd.read_sql_query(
    query,
    connection
)
```

Then:

```python
summary = (
    df.groupby("diagnosis")
      .agg(
          patients=("patient_id", "nunique"),
          visits=("patient_id", "size"),
          avg_age=("age", "mean")
      )
      .reset_index()
      .sort_values(
          "visits",
          ascending=False
      )
)
```

The database performs filtering; pandas performs flexible analysis.

---

# 30. Performance Decision Guide

## Prefer SQL when:

- data already lives in the database,
- the dataset is very large,
- rows or columns can be reduced before transfer,
- joins involve large database tables,
- indexes can accelerate filtering,
- multiple users need consistent persistent data.

## Prefer pandas when:

- the result fits comfortably in memory,
- you are exploring interactively,
- you need custom cleaning,
- you are preparing ML features,
- you need quick reshaping,
- you need Python visualization or modeling tools.

## Often best: use both

```text
SQL:
filter + join + aggregate large raw data

pandas:
clean + reshape + explore + visualize + model
```

---

# 31. Common Mistakes

## Mistake 1: `SELECT *` on a huge table

Fix: request only needed columns.

## Mistake 2: Pulling all rows and filtering in pandas

Fix: push major filters into SQL.

## Mistake 3: Confusing a pandas index with a database index

They serve different purposes.

## Mistake 4: Building SQL with f-strings from user input

Use parameterized queries.

## Mistake 5: Ignoring missing join keys

SQL and pandas can behave differently with null keys.

## Mistake 6: Forgetting `.str`

Incorrect:

```python
df["email"].contains("umich")
```

Correct:

```python
df["email"].str.contains("umich")
```

## Mistake 7: Using Python `and` / `or` for pandas filters

Incorrect:

```python
(df["age"] > 18) and (df["score"] > 80)
```

Correct:

```python
(df["age"] > 18) & (df["score"] > 80)
```

---

# 32. What to Know for a Quiz or Assignment

Be able to translate basic operations in both directions.

### SQL -> pandas

```sql
SELECT domain, COUNT(*)
FROM users
WHERE active = true
GROUP BY domain
ORDER BY COUNT(*) DESC;
```

Think:

```python
(
    df[df["active"]]
      .groupby("domain")
      .size()
      .sort_values(ascending=False)
)
```

### pandas -> SQL

```python
df[df["age"] >= 18][["id", "age"]]
```

Think:

```sql
SELECT id, age
FROM table_name
WHERE age >= 18;
```

---

# 33. Main Takeaways

1. SQL and pandas overlap heavily in filtering, sorting, grouping, joining, and text manipulation.
2. SQL usually works on persistent data managed by a database server.
3. pandas usually works on in-memory DataFrames inside Python.
4. Databases can optimize queries with indexes and query planning; pandas does not replace this capability.
5. Push major filters, projections, joins, and aggregations into SQL when they substantially reduce data transfer.
6. Use pandas for flexible analysis after the dataset is a manageable size.
7. `pandas.merge()` is conceptually similar to SQL joins, but null-key behavior can differ.
8. PostgreSQL regex concepts transfer naturally to pandas `.str.contains()` and `.str.extract()`.
9. Translating a task between SQL and pandas is a useful database/data-science skill.

---

# 34. Quick Practice

## Question 1

Translate:

```sql
SELECT *
FROM users
WHERE age >= 21
ORDER BY age DESC;
```

Answer:

```python
df[df["age"] >= 21].sort_values(
    "age",
    ascending=False
)
```

## Question 2

Translate:

```python
df["state"].value_counts()
```

Conceptual SQL:

```sql
SELECT state, COUNT(*)
FROM table_name
GROUP BY state
ORDER BY COUNT(*) DESC;
```

## Question 3

Why is this often preferable?

```sql
SELECT id, age
FROM users
WHERE age >= 21;
```

instead of loading the entire table and filtering later in pandas?

Because the database can reduce rows and columns before transfer and may use an index to make the filtering efficient.

---

# 35. Suggested Study Method

Write the same operation both ways.

```text
Filter rows
SQL:    WHERE
pandas: Boolean mask
```

```text
Group
SQL:    GROUP BY
pandas: groupby()
```

```text
Join
SQL:    JOIN
pandas: merge()
```

This translation method is especially useful for assignments that move between PostgreSQL and Python.
