# Lecture 4 — Exploring CRUD in Deno KV Using KVAdmin.py

**Weekly topic:** Video: Exploring CRUD in Deno KV Using KVAdmin.py (12 min)  
**Slide coverage:** Strong — slides 36–46.

## Key points

1. `kvadmin.py` is a simple Python command-line client for interacting with a Deno KV web service.
2. The tool demonstrates all four CRUD concepts: create, read, update, and delete.
3. Human-readable slash paths such as `/books/Hamlet` are translated into Deno KV array keys.
4. The Python client sends HTTP requests to a Deno/Hono server, and the server performs the actual KV operations.
5. Deno KV returns metadata such as a `versionstamp` alongside values.

---

## 1. What CRUD means

CRUD is the standard shorthand for four basic data operations:

| CRUD | Meaning | KVAdmin operation |
|---|---|---|
| Create | Add a new value | `set` |
| Read | Retrieve existing value(s) | `get`, `list` |
| Update | Replace an existing value | `set` |
| Delete | Remove value(s) | `delete`, `delete_prefix` |

Notice that Deno KV's `set()` handles both **create** and **update**.

---

## 2. Why KVAdmin.py exists

The slides explain that Deno KV did not have a traditional database administration client comparable to:

- `psql`
- MySQL CLI
- pgAdmin
- DBeaver
- phpMyAdmin

The course therefore uses a simple educational client:

```bash
python kvadmin.py
```

Conceptually:

```text
kvadmin.py
    |
    | HTTP request
    v
Deno/Hono web server
    |
    | Deno KV API
    v
Deno KV
```

This separation is central to the module.

---

## 3. SET — create or update

Example command:

```text
set /books/Hamlet
```

Then enter JSON:

```json
{
  "author": "Bill",
  "title": "Hamlet",
  "isbn": "42",
  "lang": "ang"
}
```

Conceptually the server executes:

```ts
await kv.set(
  ["books", "Hamlet"],
  {
    author: "Bill",
    title: "Hamlet",
    isbn: "42",
    lang: "ang"
  }
);
```

A successful set may return:

```json
{
  "ok": true,
  "versionstamp": "..."
}
```

---

## 4. GET — read one record

Command:

```text
get /books/Hamlet
```

Server-side equivalent:

```ts
const result = await kv.get([
  "books",
  "Hamlet"
]);
```

Response structure:

```json
{
  "key": ["books", "Hamlet"],
  "value": {
    "author": "Bill",
    "title": "Hamlet",
    "isbn": "42",
    "lang": "ang"
  },
  "versionstamp": "..."
}
```

---

## 5. LIST — read records by prefix

Command:

```text
list /books
```

Conceptual server code:

```ts
const iter = kv.list({
  prefix: ["books"]
});

for await (const entry of iter) {
  console.log(entry);
}
```

This is one of the most important Deno KV patterns.

`list /books` means:

> Return all records whose logical key begins with `"books"`.

---

## 6. DELETE — remove a specific key

Command:

```text
delete /books/Hamlet
```

Server-side equivalent:

```ts
await kv.delete([
  "books",
  "Hamlet"
]);
```

---

## 7. DELETE_PREFIX — remove a collection of matching keys

The course client also provides:

```text
delete_prefix /books
```

The server:

1. lists all keys beginning with the prefix
2. iterates over those keys
3. deletes each one

Conceptually:

```ts
for await (
  const entry of kv.list({
    prefix: ["books"]
  })
) {
  await kv.delete(entry.key);
}
```

---

## 8. How slash paths become array keys

The course presents keys in a path-like format:

```text
/books/Hamlet
```

The Deno server converts that string into an array.

Conceptually:

```js
"books/Hamlet".split("/")
```

becomes:

```js
["books", "Hamlet"]
```

Deno KV itself stores the **array key**, not a filesystem path.

---

## 9. Versionstamps

A KV record may contain:

```json
"versionstamp": "0100000003612c600000"
```

A **versionstamp** changes when the record changes.

It can be used for:

- detecting whether a value has been modified
- optimistic concurrency control
- atomic conditional updates

You do not need to interpret the characters as an ordinary integer.

---

## 10. CRUD request flow

Example: `get /books/Hamlet`

```text
1. User enters:
   get /books/Hamlet

2. Python client builds URL:
   /kv/get/books/Hamlet?token=...

3. HTTP GET request is sent.

4. Deno/Hono route receives request.

5. Server converts:
   books/Hamlet
   ->
   ["books", "Hamlet"]

6. Server calls:
   kv.get(["books", "Hamlet"])

7. Result is converted to JSON.

8. Python client prints the JSON.
```

---

## Main takeaway

The point of KVAdmin is not just to memorize commands. It exposes the entire architecture:

```text
command-line client
→ HTTP API
→ server route
→ Deno KV operation
→ JSON response
```

That client/server/database separation is a major database-architecture concept.
