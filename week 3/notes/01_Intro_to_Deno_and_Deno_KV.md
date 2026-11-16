# Lecture 1 — Intro to Deno and Deno KV

**Weekly topic:** Video: Intro to Deno and Deno KV (22 min)  
**Slide coverage:** Strong — primarily slides 2–19.

## Key points

1. **Deno grew out of lessons learned from Node.js.** Ryan Dahl created Node.js in 2009 and later started Deno in 2018 as a cleaner, more opinionated runtime for JavaScript and TypeScript.
2. **Deno is more than a web server runtime.** The lecture emphasizes a broader ecosystem: runtime features, deployment, key-value storage, and event/notification capabilities.
3. **Deno KV is a schemaless key-value database.** Data is stored under hierarchical logical keys rather than SQL tables and integer primary keys.
4. **Deno KV keys are arrays.** A key such as `["books", "Hamlet"]` acts like a hierarchical path and can be retrieved directly or scanned by prefix.
5. **The architectural motivation is distributed computing.** Moving compute and data closer to users can reduce latency compared with a single centralized application server.

---

## 1. Why Deno exists

### Node.js background

The lecture starts with Node.js:

- Node.js was created in 2009.
- It made server-side JavaScript practical.
- Over time, its ecosystem accumulated design decisions and dependencies that became difficult to change.

### Pain points discussed in the lecture

The slides emphasize:

- JavaScript vs. TypeScript friction
- Heavy reliance on independently maintained packages
- npm/dependency-management complexity
- Difficulty modernizing core behavior without breaking compatibility

### Deno's design direction

Deno is presented as a more **opinionated**, "batteries-included" environment.

A useful analogy from the lecture is:

- **Flask-like approach:** minimal core, assemble many pieces yourself.
- **Django-like approach:** more built in and more conventions.

Deno is closer to the second idea.

---

## 2. Distributed web architecture

The lecture connects Deno to the evolution of web hosting.

Traditional architecture:

```text
User
  |
  v
CDN / Cloudflare
  |
  v
Single application server
  |
  v
SQL database
```

A CDN can already handle:

- static assets
- DNS
- TLS/HTTPS termination
- DDoS mitigation
- caching close to users

The next architectural step is to move **application logic** closer to users as well.

That is the motivation behind edge/serverless systems such as Cloudflare Workers and Deno Deploy.

---

## 3. What Deno provides

The slides emphasize three major pieces:

### Deno runtime

A JavaScript/TypeScript runtime with many capabilities available directly through the platform.

### Deno Deploy

A hosted environment for running Deno applications.

### Deno KV

A built-in key-value database accessed from Deno code.

Example:

```ts
const kv = await Deno.openKv();
```

The same programming model can be used locally and in a hosted environment.

---

## 4. Deno KV mental model

Deno KV stores **key-value pairs**.

A value might be a JavaScript object:

```ts
{
  title: "Hamlet",
  author: "William Shakespeare",
  isbn: "42",
  lang: "ang"
}
```

A logical key might be:

```ts
["books", "Hamlet"]
```

Think of this as:

```text
/books/Hamlet
```

### Important properties

Deno KV is presented in the slides as:

- schemaless
- no explicit SQL-style tables
- hierarchical logical keys
- keys represented as JavaScript arrays
- exact lookup by key
- prefix scanning with `list()`
- ordered by logical key

---

## 5. Core operations

### Store a value

```ts
await kv.set(["preferences", "ada"], {
  username: "ada",
  theme: "dark",
  language: "en-US"
});
```

### Get a value

```ts
const entry = await kv.get(["preferences", "ada"]);
console.log(entry.value);
```

### List values sharing a prefix

```ts
const entries = kv.list({
  prefix: ["preferences"]
});

for await (const entry of entries) {
  console.log(entry.key, entry.value);
}
```

### Delete a value

```ts
await kv.delete(["preferences", "ada"]);
```

---

## 6. Why key design matters

In SQL, you often begin by defining:

- tables
- columns
- primary keys
- foreign keys
- indexes

In Deno KV, the **key structure itself is part of the data model**.

For example:

```text
["books", "isbn", "9781511654944"]
["books", "author", "Charles Severance", "9781511654944"]
["books", "language", "en", "9781511654944"]
```

These prefixes determine which queries can be executed efficiently.

This becomes especially important in the lecture on secondary indexes.

---

## 7. Local vs. hosted storage

The lecture identifies two implementation contexts:

- **Local Deno KV:** backed by SQLite.
- **Hosted/production Deno KV:** current Deno documentation describes production Deno KV as backed by FoundationDB.

This matters because your application sees a simple KV API even though the underlying storage system may differ.

---

## 8. Current accuracy note — November 2026

The course slides describe Deno Deploy as an emerging hosted platform and refer to Deno Deploy Classic-era workflows.

Current official documentation states:

- Deno Deploy Classic shut down on **July 20, 2026**.
- The newer Deno Deploy platform supports Deno KV as an assignable database engine.
- In the newer platform, an application uses `Deno.openKv()` after a KV database has been assigned to the app.
- Deno KV is still documented as an **unstable/in-development API** and local use requires `--unstable-kv`.
- Deno Deploy is currently scheduled to sunset in **April 2027**.

For course assignments, follow the course's required environment and autograder instructions even when they use older terminology.

---

## Important definitions

**Deno**  
A JavaScript/TypeScript runtime designed as a modern alternative to Node.js.

**Deno Deploy**  
A hosted platform for running Deno applications.

**Deno KV**  
A key-value database integrated into the Deno runtime.

**Key-value database**  
A database in which each stored value is retrieved using a key.

**Schemaless**  
The database does not require a fixed SQL-style table schema before values are stored.

**Hierarchical key**  
A key made from multiple ordered components, such as `["books", "author", "Ada"]`.

**Prefix scan**  
Retrieving all keys that begin with a specified sequence of key components.

---

## Main takeaway

The lecture's central idea is that **Deno combines application execution and a simple distributed-friendly key-value data model into one programming environment**. Instead of modeling everything as SQL tables and joins, Deno KV asks you to think carefully about logical keys, prefixes, and the queries your application needs.
