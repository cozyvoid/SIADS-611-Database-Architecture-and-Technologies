# Week 4 Lecture Notes: Text in Databases

**Course focus:** Database Architecture and Technologies  
**Lecture source:** *Text in Databases* — Charles Severance  
**Primary system:** PostgreSQL

---

## 1. Big Picture

This lecture explains how databases store, search, transform, and index **text data**. It connects several ideas that matter in real database work:

- generating large test datasets,
- SQL text functions and pattern matching,
- character encodings such as ASCII, Unicode, and UTF-8,
- Python `str` versus `bytes`,
- hash functions,
- database index strategies,
- regular expressions for text search and extraction.

The central theme is that **text is not just “characters on a screen.”** In a database, text has an encoding, a storage cost, a comparison behavior, and performance implications.

---

# 2. Generating Test Data

Small tables are useful for learning SQL syntax, but they are not sufficient for testing database performance. The lecture therefore generates many rows of artificial data.

## Important PostgreSQL functions

### `random()`

Returns a pseudo-random floating-point number.

```sql
SELECT random();
```

To generate an integer-like value:

```sql
SELECT trunc(random() * 100);
```

### `repeat(text, n)`

Repeats a string `n` times.

```sql
SELECT repeat('Neon ', 5);
```

Result:

```text
Neon Neon Neon Neon Neon
```

### `generate_series(start, stop)`

Generates multiple rows of sequential values.

```sql
SELECT generate_series(1, 5);
```

This is conceptually similar to Python's `range()`.

## Why this matters

To evaluate indexes and query plans, we need enough rows that PostgreSQL has meaningful choices between:

- scanning every row, or
- using an index.

---

# 3. SQL Text Functions

PostgreSQL provides many tools for filtering and manipulating strings.

## Common comparison operators

```sql
=
>
<
>=
<=
BETWEEN
IN
```

## Pattern matching with `LIKE`

`LIKE` is case-sensitive.

```sql
SELECT *
FROM textfun
WHERE content LIKE '%150000%';
```

Wildcards:

- `%` = zero or more characters
- `_` = exactly one character

### Prefix search

```sql
WHERE content LIKE 'racing%'
```

This can often use a B-tree index.

### Contains search

```sql
WHERE content LIKE '%racing%'
```

Because the pattern begins with `%`, PostgreSQL usually cannot use a normal B-tree index efficiently and may perform a sequential scan.

## `ILIKE`

`ILIKE` performs case-insensitive pattern matching.

```sql
WHERE content ILIKE 'racing%'
```

A normal B-tree index on the original column may not help this query.

---

# 4. Text Transformation Functions

## `upper()` and `lower()`

```sql
SELECT upper(content)
FROM textfun;
```

```sql
SELECT lower(content)
FROM textfun;
```

Useful for standardizing case.

## `left()` and `right()`

```sql
SELECT left(content, 4);
SELECT right(content, 4);
```

## `strpos()`

Returns the starting position of a substring.

```sql
SELECT strpos(content, 'ttps://');
```

PostgreSQL positions are generally **1-based**, not 0-based like Python indexes.

## `substr()`

```sql
SELECT substr(content, 2, 4);
```

## `split_part()`

```sql
SELECT split_part(content, '/', 4);
```

Useful for extracting sections of delimited text such as URL paths.

## `translate()`

Performs character-by-character replacement.

```sql
SELECT translate(content, 'th.p/', 'TH!P_');
```

---

# 5. Query Performance and B-Tree Indexes

Suppose we create:

```sql
CREATE INDEX textfun_b
ON textfun(content);
```

PostgreSQL may use that index for an anchored prefix search:

```sql
SELECT content
FROM textfun
WHERE content LIKE 'racing%';
```

This is efficient because a B-tree keeps values in sorted order.

However:

```sql
SELECT content
FROM textfun
WHERE content LIKE '%racing%';
```

usually requires PostgreSQL to inspect many or all rows because the beginning of the text is unknown.

## `EXPLAIN ANALYZE`

Use:

```sql
EXPLAIN ANALYZE
SELECT ...
```

to see:

- whether PostgreSQL chose an index scan or sequential scan,
- estimated versus actual behavior,
- execution time,
- rows filtered,
- heap fetches.

### Index scan

PostgreSQL navigates an index to narrow the search.

### Sequential scan

PostgreSQL scans the table row by row.

A sequential scan is not automatically bad. For small tables or queries returning a large percentage of rows, it may be the correct plan.

---

# 6. `IN` and Indexed Exact Matches

An exact-value lookup such as:

```sql
SELECT content
FROM textfun
WHERE content IN (
    'http://www.pg4e.com/neon/150000',
    'https://www.pg4e.com/neon/150000'
);
```

can use a B-tree index efficiently because the database knows the exact values it is looking for.

Contrast this with a subquery whose inner search requires a pattern scan:

```sql
SELECT content
FROM textfun
WHERE content IN (
    SELECT content
    FROM textfun
    WHERE content LIKE '%150000%'
);
```

The outer lookup may use an index, but the inner search may still require a sequential scan.

---

# 7. Character Sets and ASCII

## ASCII

ASCII stands for **American Standard Code for Information Interchange**.

Traditional ASCII assigns numeric values to characters from 0 through 127.

Examples:

```sql
SELECT ascii('H');
```

returns `72`.

```sql
SELECT chr(72);
```

returns `H`.

## Byte

A **byte** is 8 bits.

Historically, programmers often assumed:

```text
1 byte = 1 character
```

That works for basic ASCII but not for modern multilingual text.

---

# 8. The Problem with Early Extended Character Sets

ASCII did not contain enough characters for every language.

Several incompatible 8-bit character sets therefore emerged, including:

- ISO-8859-1,
- ISO-8859-2,
- ISO-8859-5,
- Windows-1252.

The same numeric byte could represent different characters depending on the encoding.

## Core problem

The bytes themselves often did not identify which character set had been used. You needed external knowledge of the file encoding, which created portability and interoperability problems.

---

# 9. Unicode

Unicode provides a unified system for representing characters across languages.

Example:

```sql
SELECT chr(72), chr(231), chr(20013);
```

may produce:

```text
H
ç
中
```

## Code point

A **Unicode code point** is a number assigned to a character.

For example:

```text
U+0041 = A
```

Unicode defines the character. An encoding such as UTF-8 defines how that code point is stored as bytes.

---

# 10. UTF-8

UTF-8 is a variable-length encoding for Unicode.

Key properties:

- ASCII characters use one byte.
- Other characters use multiple bytes.
- ASCII text is valid UTF-8.
- UTF-8 is highly interoperable.

## Characters versus bytes

```sql
SELECT
    char_length('学习管理'),
    octet_length('学习管理'),
    bit_length('学习管理');
```

A Unicode string can contain 4 characters while occupying more than 4 bytes.

### Key distinction

```text
character count != byte count
```

This matters when:

- setting storage limits,
- transferring data,
- debugging encoding errors,
- reasoning about storage size.

## PostgreSQL server encoding

```sql
SHOW SERVER_ENCODING;
```

A modern PostgreSQL database commonly reports:

```text
UTF8
```

---

# 11. Python 3: `str` versus `bytes`

Python 3 distinguishes text from raw byte data.

## `str`

Python text strings are Unicode.

```python
x = "hello"
type(x)
# str
```

## `bytes`

Raw byte sequences use `bytes`.

```python
x = b"abc"
type(x)
# bytes
```

## Encode

```python
text = "hello"
data = text.encode("utf-8")
```

Conceptually:

```text
str -> bytes
```

## Decode

```python
data = b"hello"
text = data.decode("utf-8")
```

Conceptually:

```text
bytes -> str
```

## Important rule

**Encode when converting text to bytes. Decode when converting bytes to text.**

---

# 12. Opening Text Files in Python

Python's `open()` accepts an `encoding` argument.

```python
with open("data.txt", "r", encoding="utf-8") as f:
    text = f.read()
```

Explicitly specifying the encoding is safer than relying on a platform-specific default.

---

# 13. Python and PostgreSQL Text

When Python communicates with PostgreSQL through a database driver, character encoding conversions are usually handled automatically.

Conceptually:

```text
PostgreSQL UTF-8 data
        |
      decode
        |
Python Unicode strings
        |
      encode
        |
PostgreSQL UTF-8 data
```

The lecture specifically notes that database connectors such as `psycopg2` can handle this conversion.

---

# 14. Hash Functions

A hash function maps an input of arbitrary size to an output of fixed size.

```text
arbitrary-sized input -> fixed-sized hash
```

Common uses:

- checksums,
- data integrity,
- cryptographic signatures,
- fast lookup structures,
- Python dictionaries,
- database indexing strategies.

---

# 15. Properties of a Good Hash Function

## Deterministic

The same input must always produce the same output.

## Uniform distribution

Outputs should be broadly distributed across the possible result space.

## Sensitive to input

A small input change should cause a substantial output change.

## One-way

For cryptographic hashing, it should be computationally impractical to recover the original input from the hash.

---

# 16. Bitwise Operations in Hashing

Hash calculations frequently use bitwise operators.

```python
x << 1
x ^ y
x & y
```

Where:

- `<<` = left shift
- `^` = XOR
- `&` = bitwise AND

The lecture uses a simplified hash example to demonstrate mechanics; real cryptographic hash design is much more sophisticated.

---

# 17. MD5

MD5 produces a 128-bit hash.

```sql
SELECT md5('hello');
```

MD5 was historically common but is no longer considered secure for cryptographic collision resistance.

### Important distinction

MD5 may still appear in non-security or legacy contexts, but it should not be treated as a secure password-hashing algorithm.

---

# 18. SHA-256

SHA-256 belongs to the SHA-2 family and produces a 256-bit digest.

The lecture contrasts MD5 and SHA-256 to show that hash algorithms differ in:

- output size,
- design,
- security properties.

---

# 19. Indexes and Long Text Values

The lecture uses a web crawler as a motivating example.

A crawler may repeatedly:

1. retrieve a URL,
2. store the page,
3. extract outgoing links,
4. check whether each URL has already been seen,
5. add unseen URLs to a queue.

That makes fast URL lookup important.

## Indexing a hash of long text

One strategy is:

```sql
CREATE UNIQUE INDEX cr2_md5
ON cr2 (md5(url));
```

Then:

```sql
SELECT *
FROM cr2
WHERE md5(url) = md5('lemons');
```

can use the expression index.

---

# 20. Storing a Hash in a Separate Column

```sql
CREATE TABLE cr3 (
    id SERIAL,
    url TEXT,
    url_md5 UUID UNIQUE,
    content TEXT
);
```

Populate:

```sql
UPDATE cr3
SET url_md5 = md5(url)::uuid;
```

Query:

```sql
SELECT *
FROM cr3
WHERE url_md5 = md5('lemons')::uuid;
```

## Tradeoff

A compact indexed key can speed exact lookup, but it also adds storage and must remain synchronized with the original text.

---

# 21. PostgreSQL Index Types

## B-tree

Useful for:

- exact lookup,
- prefix lookup,
- `<`,
- `>`,
- ranges,
- sorting.

Example:

```sql
CREATE INDEX idx_name
ON table_name(column_name);
```

## Hash index

Specialized for equality lookup.

```sql
CREATE INDEX idx_name
ON table_name USING HASH(column_name);
```

Useful mainly for:

```sql
WHERE column_name = value
```

It does not preserve sorted order.

## Practical principle

Start with a B-tree unless the workload gives you a specific reason to use a specialized index.

---

# 22. Regular Expressions

A **regular expression (regex)** is a compact text pattern used for matching or extracting text.

PostgreSQL uses POSIX-style regular expressions.

| Pattern | Meaning |
|---|---|
| `^` | beginning of string/line |
| `$` | end of string/line |
| `.` | any character |
| `*` | zero or more repetitions |
| `+` | one or more repetitions |
| `[aeiou]` | one character from the set |
| `[^XYZ]` | one character not in the set |
| `[a-z0-9]` | one character from a range |
| `( ... )` | capture/extraction group |

---

# 23. PostgreSQL Regex Operators

## Case-sensitive match

```sql
~
```

## Case-insensitive match

```sql
~*
```

## Does not match

```sql
!~
```

## Case-insensitive does not match

```sql
!~*
```

---

# 24. `LIKE` versus Regex

These can express similar ideas:

```sql
tweet LIKE '%UMSI%'
```

and:

```sql
tweet ~ 'UMSI'
```

Regex is more expressive.

### Starts with `c`

```sql
WHERE email ~ '^c'
```

### Ends with `edu`

```sql
WHERE email ~ 'edu$'
```

### Starts with one of several characters

```sql
WHERE email ~ '^[gnt]'
```

### Contains a digit

```sql
WHERE email ~ '[0-9]'
```

### Contains two consecutive digits

```sql
WHERE email ~ '[0-9][0-9]'
```

---

# 25. Extracting Text with Regex

## Extract digits

```sql
SELECT substring(email FROM '[0-9]+')
FROM em
WHERE email ~ '[0-9]';
```

## Extract an email domain

```sql
SELECT substring(email FROM '.+@(.*)$')
FROM em;
```

The capture group `(.*)` returns the text after `@`.

---

# 26. Grouping Extracted Values

```sql
SELECT
    substring(email FROM '.+@(.*)$') AS domain,
    count(*)
FROM em
GROUP BY domain;
```

This illustrates a useful workflow:

```text
raw text
   ↓
extract structured component
   ↓
GROUP BY / COUNT / ORDER BY
```

---

# 27. Multiple Regex Matches

`substring()` generally extracts one match.

To obtain repeated matches, PostgreSQL provides `regexp_matches()`.

Example:

```sql
SELECT regexp_matches(
    tweet,
    '#([A-Za-z0-9_]+)',
    'g'
)
FROM tw;
```

`g` means **global**, so PostgreSQL returns all matches.

---

# 28. Email Parsing Demonstration

The lecture ends with a practical email-text example.

```sql
CREATE TABLE mbox (
    line TEXT
);
```

Filter `From ` lines:

```sql
SELECT line
FROM mbox
WHERE line ~ '^From ';
```

Extract email addresses:

```sql
SELECT substring(line, ' (.+@[^ ]+) ')
FROM mbox
WHERE line ~ '^From ';
```

Aggregate:

```sql
SELECT
    substring(line, ' (.+@[^ ]+) ') AS email,
    count(*)
FROM mbox
WHERE line ~ '^From '
GROUP BY email
ORDER BY count(*) DESC;
```

## Main lesson

PostgreSQL can:

- find patterns,
- extract structured fields from text,
- convert semi-structured text into analyzable values,
- aggregate those derived values.

---

# 29. Main Takeaways

1. **Text processing is a database concern.**
2. **Indexes change performance dramatically**, but only when the query structure is compatible with the index.
3. B-trees work well for exact values, ranges, sorting, and many prefix searches, but not arbitrary leading-wildcard searches.
4. **Unicode and UTF-8 solve multilingual text representation**, but characters and bytes are not the same.
5. Python 3 separates **Unicode strings (`str`)** from **raw bytes (`bytes`)**.
6. **Hash functions** map arbitrary input to fixed-sized output and can support compact lookup keys.
7. **MD5 is not suitable for modern cryptographic security.**
8. PostgreSQL regex operators support advanced matching and extraction.
9. Extracted text can then be analyzed with normal relational operations such as `GROUP BY`, `COUNT`, and `ORDER BY`.

---

# 30. Quick Study Checklist

You should be able to explain or use:

- [ ] `random()`
- [ ] `repeat()`
- [ ] `generate_series()`
- [ ] `LIKE` versus `ILIKE`
- [ ] `upper()` / `lower()`
- [ ] `left()` / `right()`
- [ ] `strpos()`
- [ ] `substr()`
- [ ] `split_part()`
- [ ] `EXPLAIN ANALYZE`
- [ ] sequential scan versus index scan
- [ ] ASCII versus Unicode
- [ ] UTF-8
- [ ] character length versus byte length
- [ ] Python `str` versus `bytes`
- [ ] `.encode()` versus `.decode()`
- [ ] hash-function properties
- [ ] MD5 versus SHA-256
- [ ] B-tree versus hash indexes
- [ ] regex operators `~`, `~*`, `!~`, `!~*`
- [ ] anchors `^` and `$`
- [ ] character classes such as `[0-9]`
- [ ] `substring(... FROM regex)`
- [ ] `regexp_matches(..., 'g')`

---

# 31. One-Minute Review

**Why can `LIKE 'abc%'` be faster than `LIKE '%abc%'`?**  
A B-tree can often use the known beginning of the string to narrow the search. A leading wildcard removes that ordered starting point.

**Unicode versus UTF-8?**  
Unicode defines characters/code points. UTF-8 defines how those characters are encoded into bytes.

**Python `str` versus `bytes`?**  
`str` represents Unicode text. `bytes` represents raw byte sequences.

**Why hash a long URL?**  
A fixed-size hash can provide a compact key for exact-match lookup.

**Why regex in SQL?**  
Regex lets SQL identify and extract meaningful patterns from semi-structured text.
