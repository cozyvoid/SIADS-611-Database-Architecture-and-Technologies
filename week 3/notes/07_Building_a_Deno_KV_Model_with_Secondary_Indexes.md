# Lecture 7 — Building a Deno KV Model with Secondary Indexes

**Weekly topic:** Video: Building a Deno KV Model with Secondary Indexes (11 min)  
**Slide coverage:** Strong — slides 47–56.

## Key points

1. Deno KV does not automatically provide SQL-style secondary indexes for arbitrary fields.
2. To support an efficient query, you design a **key prefix specifically for that query**.
3. A unique identifier such as ISBN can act as the canonical/primary record key.
4. Secondary index keys can contain the searchable field plus the unique ID.
5. Unlike SQL, the application is responsible for maintaining the primary record and all secondary index entries consistently.

---

# 1. Start with the queries

The lecture begins with book data containing:

- title
- ISBN
- language
- author

Possible application queries:

- book by ISBN
- books in a language
- books by an author
- exact title lookup

In SQL, these could be supported by indexes.

In Deno KV, you design different key prefixes.

---

# 2. SQL mental model

A normalized SQL design might separate:

```text
Book
Language
Author
```

and connect them with:

- primary keys
- foreign keys
- one-to-many relationships
- secondary indexes

SQL lets the database optimizer use indexes and joins to answer multiple query shapes.

---

# 3. Deno KV mental model

The lecture emphasizes that Deno KV does not give you:

- SQL tables
- SQL joins
- foreign-key constraints
- automatic secondary indexes

Instead, the application deliberately creates keys for the access patterns it needs.

This is a **query-first** or **access-pattern-first** modeling style.

---

# 4. Canonical record by ISBN

Assume ISBN is truly unique.

Primary/canonical record:

```ts
await kv.set(
  [
    "books",
    "isbn",
    "9781511654944"
  ],
  {
    title:
      "Introduction to Networking",
    author:
      "Charles Severance",
    language:
      "en",
    isbn:
      "9781511654944"
  }
);
```

Key:

```text
["books", "isbn", ISBN]
```

Value:

```text
full book document
```

---

# 5. Secondary index by title

```ts
await kv.set(
  [
    "books",
    "title",
    "Introduction to Networking",
    "9781511654944"
  ],
  {}
);
```

Why include ISBN at the end?

Because title may not be globally unique.

The ISBN disambiguates duplicate titles.

---

# 6. Secondary index by author

```ts
await kv.set(
  [
    "books",
    "author",
    "Charles Severance",
    "9781511654944"
  ],
  {}
);
```

Now all books by that author can be found with:

```ts
kv.list({
  prefix: [
    "books",
    "author",
    "Charles Severance"
  ]
});
```

---

# 7. Secondary index by language

```ts
await kv.set(
  [
    "books",
    "language",
    "en",
    "9781511654944"
  ],
  {}
);
```

Then:

```ts
kv.list({
  prefix: [
    "books",
    "language",
    "en"
  ]
});
```

finds English-language book references.

---

# 8. Why the secondary value can be `{}`

The secondary key itself contains the information needed to identify the canonical book.

Example:

```text
[
  "books",
  "author",
  "Charles Severance",
  "9781511654944"
]
```

The final component is the ISBN.

The application can then retrieve:

```text
[
  "books",
  "isbn",
  "9781511654944"
]
```

to get the full document.

So the index entry can be a lightweight marker:

```js
{}
```

Another valid design is to store the primary key as the secondary value.

---

# 9. Query-first design

Suppose you need these queries:

```text
Q1: find book by ISBN
Q2: find books by author
Q3: find books by language
Q4: find book by exact title
```

You might design:

```text
["books", "isbn", ISBN]

["books", "author", AUTHOR, ISBN]

["books", "language", LANG, ISBN]

["books", "title", TITLE, ISBN]
```

Each query has a natural prefix.

This is a major NoSQL modeling principle:

> Model the key space around the queries you need to execute efficiently.

---

# 10. Denormalization

This design duplicates information across multiple keys.

That is **denormalization**.

SQL often tries to reduce duplication through normalization.

Key-value/NoSQL systems often intentionally duplicate index information to make reads efficient.

Tradeoff:

```text
faster/simple reads
        vs.
more complex writes
```

---

# 11. Maintaining indexes correctly

Suppose the author changes from:

```text
Charles Severance
```

to:

```text
Chuck Severance
```

You must update:

1. the canonical ISBN record
2. delete the old author-index key
3. create the new author-index key

If you forget one, the index becomes stale.

---

# 12. Atomic transactions — important supplement

Current Deno KV supports atomic transactions.

That is highly relevant when maintaining secondary indexes.

Conceptually:

```ts
const tx =
  kv.atomic();

tx.set(
  [
    "books",
    "isbn",
    isbn
  ],
  book
);

tx.set(
  [
    "books",
    "author",
    book.author,
    isbn
  ],
  {}
);

tx.set(
  [
    "books",
    "language",
    book.language,
    isbn
  ],
  {}
);

await tx.commit();
```

The goal is for related writes to succeed together rather than leaving a partially updated index structure.

---

# 13. Deno KV vs. SQL indexes

| SQL | Deno KV |
|---|---|
| Table schema | Hierarchical key space |
| Primary key constraint | Application-defined canonical key |
| `CREATE INDEX` | Additional KV key pattern |
| Foreign key | Application-managed relationship |
| Join | Multiple lookups / denormalized keys |
| Query optimizer | Application chooses key/prefix |
| Automatic index maintenance | Application maintains index entries |

---

## Important definitions

**Primary/canonical key**  
The key used to store the authoritative version of a record.

**Secondary index**  
An additional lookup structure that lets the same logical record be found by another attribute.

**Prefix**  
The initial components of a hierarchical key used for scanning related entries.

**Denormalization**  
Intentionally duplicating data or references to improve read performance.

**Access pattern**  
A specific way the application needs to retrieve data.

**Atomic transaction**  
A group of operations that commit together or fail as a unit.

---

## Main takeaway

Deno KV data modeling is fundamentally about **designing keys around access patterns**. If the application must query efficiently by ISBN, author, language, and title, you usually create separate key families for each access pattern and maintain them together.
