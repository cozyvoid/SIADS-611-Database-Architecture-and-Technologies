# Reading Guide — Deno KV Documentation

**Weekly topic:** Reading: Deno KV Documentation  
**Slide coverage:** The deck references the documentation but does not provide a complete documentation summary. This file is supplemental.

## What to focus on

For this module, you should be able to explain and recognize:

1. `Deno.openKv()`
2. Deno KV array keys
3. `set()`
4. `get()` and `getMany()`
5. `list()` and prefix scans
6. `delete()`
7. strong vs. eventual reads
8. versionstamps
9. atomic transactions
10. manual secondary indexes
11. `watch()`
12. local SQLite vs. hosted FoundationDB behavior

---

# 1. Opening a KV database

```ts
const kv =
  await Deno.openKv();
```

Local Deno can create or open a persistent KV store.

For testing, current documentation also supports:

```ts
const kv =
  await Deno.openKv(
    ":memory:"
  );
```

This creates an in-memory database suitable for tests.

---

# 2. Keys

Deno KV keys are arrays.

Example:

```ts
[
  "preferences",
  "ada"
]
```

Key parts can use supported JavaScript scalar types.

The order of key components matters.

Think of the key as a structured tuple, not simply as one string.

---

# 3. Values

Values can be JavaScript objects.

Example:

```ts
const prefs = {
  username: "ada",
  theme: "dark",
  language: "en-US"
};
```

Then:

```ts
await kv.set(
  [
    "preferences",
    "ada"
  ],
  prefs
);
```

---

# 4. `set()`

`set()` creates or updates a key.

```ts
await kv.set(
  [
    "users",
    "alice"
  ],
  {
    name: "Alice"
  }
);
```

This means Deno KV does not need separate INSERT and UPDATE commands for basic replacement.

---

# 5. `get()`

```ts
const result =
  await kv.get([
    "users",
    "alice"
  ]);
```

The returned entry includes:

- `key`
- `value`
- `versionstamp`

If the key does not exist, the value/versionstamp can be null.

---

# 6. `getMany()`

When several exact keys are known:

```ts
const results =
  await kv.getMany([
    [
      "users",
      "alice"
    ],
    [
      "users",
      "bob"
    ]
  ]);
```

This avoids manually issuing separate exact-key reads one by one.

---

# 7. `list()`

Prefix scanning is one of the most important Deno KV operations.

```ts
const entries =
  kv.list({
    prefix: [
      "users"
    ]
  });
```

Consume it asynchronously:

```ts
for await (
  const entry
  of entries
) {
  console.log(
    entry.key,
    entry.value
  );
}
```

The matching keys are returned according to Deno KV's key ordering rules.

---

# 8. `delete()`

```ts
await kv.delete([
  "users",
  "alice"
]);
```

If the key does not exist, deletion is effectively a no-op.

---

# 9. Versionstamps

A returned entry contains a `versionstamp`.

Conceptually, it answers:

> Which version of this key did I read?

Versionstamps enable conditional/optimistic updates.

Example use case:

1. read a record and its versionstamp
2. modify it
3. commit only if the versionstamp has not changed

---

# 10. Atomic transactions

Current Deno KV supports atomic operations.

Example concept:

```ts
const current =
  await kv.get(key);

const result =
  await kv
    .atomic()
    .check(current)
    .set(
      key,
      newValue
    )
    .commit();
```

This can prevent a lost update when multiple clients modify the same record.

Atomic transactions are also useful when maintaining multiple secondary-index keys.

---

# 11. Consistency

Current official documentation says Deno KV reads may use:

### Strong consistency

Returns the most recently committed value according to the database's strong-consistency guarantees.

This is the default.

### Eventual consistency

May return a temporarily stale value but can reduce read latency in distributed environments.

This is optional for reads.

Writes remain strongly consistent.

This is an important nuance because the lecture's B-tree section uses eventual consistency as a conceptual distributed-database model.

---

# 12. Secondary indexes

Deno KV does not automatically build secondary indexes from object properties.

Instead, create another key.

Primary record:

```ts
[
  "preferences",
  username
]
```

Secondary lookup:

```ts
[
  "preferencesByEmail",
  email
]
```

The secondary value can point to the primary key.

Example:

```ts
await kv.set(
  [
    "preferencesByEmail",
    prefs.email
  ],
  [
    "preferences",
    prefs.username
  ]
);
```

Lookup becomes:

```text
email
→ secondary key
→ primary key
→ full record
```

---

# 13. Watching keys

Deno KV supports:

```ts
kv.watch(...)
```

This produces updates when watched keys change.

A conceptual use case is chat:

```text
watch latest-message ID
        |
        v
new ID appears
        |
        v
list messages after
the previous ID
```

This supports reactive/event-driven applications.

---

# 14. Local implementation

Current documentation says local Deno KV uses **SQLite**.

That means your application sees the same high-level KV API while local storage can be file-backed.

---

# 15. Hosted implementation

Current Deno documentation describes production Deno KV as backed by **FoundationDB**.

FoundationDB is a distributed transactional key-value database.

The course slides mention both SQLite and FoundationDB when discussing low-level architecture.

---

# 16. Current runtime status

Current Deno documentation labels Deno KV as an **unstable / in-development API**.

Local execution requires the KV unstable flag.

Typical command:

```bash
deno run \
  --unstable-kv \
  main.ts
```

Exact CLI behavior can change, so check the documentation for your installed Deno version.

---

# 17. Current Deno Deploy status — November 2026

This has changed since the lecture materials were created.

### Deploy Classic

Shut down:

```text
July 20, 2026
```

### New Deno Deploy

Current documentation describes:

- organization-based management
- apps
- assignable database instances
- Deno KV as a supported database engine
- per-environment/timeline data isolation

After a KV database is assigned to an app:

```ts
Deno.openKv()
```

connects to the appropriate database for that environment.

### Future status

Current Deno documentation says Deno Deploy is scheduled to sunset in:

```text
April 2027
```

That platform-status change does not invalidate the database concepts in this module, but it does mean deployment screenshots and procedures can age quickly.

---

# 18. Questions you should be able to answer

### Conceptual

- What is a key-value database?
- How is Deno KV different from a relational database?
- Why are Deno KV keys arrays?
- What is a prefix scan?
- What is a versionstamp?
- What is a secondary index?
- Why must Deno KV secondary indexes be maintained by application code?
- What is the difference between strong and eventual consistency?

### Code recognition

What does this do?

```ts
await kv.set(
  [
    "books",
    "isbn",
    isbn
  ],
  book
);
```

What does this retrieve?

```ts
kv.list({
  prefix: [
    "books",
    "author",
    "Charles Severance"
  ]
});
```

Why might this be useful?

```ts
await kv
  .atomic()
  .check(oldEntry)
  .set(
    key,
    updatedValue
  )
  .commit();
```

---

# 19. Course-level summary

The Deno KV API is intentionally small.

The most important database-design work occurs in:

```text
how you structure keys
+
which prefixes you create
+
how you maintain related keys
```

That is the bridge from CRUD syntax to **database architecture**.
