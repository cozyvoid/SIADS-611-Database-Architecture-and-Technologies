# Lecture 6 — Code Walkthrough: KVAdmin.py Client and Server

**Weekly topic:** Video: Code Walkthrough — KVAdmin.py Client and Server (23 min)  
**Slide coverage:** Moderate-to-strong — especially slides 39–45. Supplemental detail below explains the full request flow represented by the course code.

## Key points

1. The Python client translates interactive commands into HTTP requests.
2. The Deno server uses the Hono framework to map HTTP routes to Deno KV operations.
3. A path such as `books/Hamlet` is converted into the array key `["books", "Hamlet"]`.
4. JSON is the interchange format between the Python client and TypeScript server.
5. The server also contains authentication, debugging, error handling, prefix deletion, and optional database-reset logic.

---

# 1. Server initialization

The server begins by importing Hono and opening Deno KV.

Conceptually:

```ts
import { Hono } from "...";

const app = new Hono();
const kv = await Deno.openKv();
```

`app` handles HTTP routes.

`kv` is the database handle.

---

# 2. SET route

The server defines a route conceptually like:

```ts
app.post(
  "/kv/set/:key{.*}",
  async (c) => {
    checkToken(c);

    const key =
      c.req.param("key");

    const body =
      await c.req.json();

    const result =
      await kv.set(
        key.split("/"),
        body
      );

    return c.json(result);
  }
);
```

Request:

```text
POST /kv/set/books/Hamlet
```

Path component:

```text
books/Hamlet
```

becomes:

```js
["books", "Hamlet"]
```

The POST JSON body becomes the value.

---

# 3. GET route

Conceptually:

```ts
app.get(
  "/kv/get/:key{.*}",
  async (c) => {
    checkToken(c);

    const key =
      c.req.param("key");

    const result =
      await kv.get(
        key.split("/")
      );

    return c.json(result);
  }
);
```

This maps:

```text
GET /kv/get/books/Hamlet
```

to:

```ts
kv.get([
  "books",
  "Hamlet"
]);
```

---

# 4. LIST route

The list route is more interesting because `kv.list()` returns an asynchronous iterator.

Conceptually:

```ts
const iter =
  kv.list(
    {
      prefix:
        key.split("/")
    },
    {
      limit: 100
    }
  );

const records = [];

for await (
  const entry of iter
) {
  records.push(entry);
}
```

Then the server returns JSON containing:

- the records
- a cursor for pagination/continuation

This demonstrates how a database API can stream or iterate over many matching records rather than returning a single row.

---

# 5. DELETE route

Conceptually:

```ts
app.delete(
  "/kv/delete/:key{.*}",
  async (c) => {
    checkToken(c);

    const key =
      c.req.param("key");

    await kv.delete(
      key.split("/")
    );

    return c.json({});
  }
);
```

---

# 6. DELETE_PREFIX route

Deno KV deletes one exact key at a time.

To delete an entire prefix, the course server:

1. calls `kv.list()` for the prefix
2. loops over the matching entries
3. deletes each entry

Conceptually:

```ts
const iter =
  kv.list({
    prefix:
      key.split("/")
  });

for await (
  const entry of iter
) {
  await kv.delete(
    entry.key
  );
}
```

This is a good example of composing lower-level database operations into a higher-level admin command.

---

# 7. Python client's role

The Python client accepts commands like:

```text
get /books/Hamlet
```

It parses the input into pieces.

Conceptually:

```python
pieces = command.split()
```

The client then constructs an HTTP URL.

Example idea:

```python
url = (
    secrets['url']
    + '/kv/get'
    + pieces[1]
    + '?token='
    + secrets['token']
)
```

Then it sends the request using Python's HTTP tools.

---

# 8. Reading the HTTP response

The course client reads the response body:

```python
text = (
    response
    .read()
    .decode('utf-8')
)
```

Then attempts to parse JSON:

```python
data = json.loads(text)
```

For readability:

```python
pretty = json.dumps(
    data,
    indent=4
)
```

This is why the command-line output resembles nicely formatted JSON.

---

# 9. End-to-end GET example

```text
USER
  |
  | get /books/Hamlet
  v
kvadmin.py
  |
  | GET
  | /kv/get/books/Hamlet?token=...
  v
Hono route
  |
  | key = "books/Hamlet"
  | split("/")
  v
["books", "Hamlet"]
  |
  | kv.get(...)
  v
Deno KV
  |
  | KvEntry
  v
JSON response
  |
  v
Python json.loads()
  |
  v
pretty printed result
```

---

# 10. Authentication

The server includes a simple function:

```ts
function checkToken(c) {
  const token =
    c.req.query("token");

  if (token == "42") {
    return true;
  }

  throw new HTTPException(
    401,
    {
      message:
        "Missing or invalid token"
    }
  );
}
```

Every protected route calls:

```ts
checkToken(c);
```

This demonstrates centralized authorization logic.

For coursework, the token is intentionally simple.

For production, query-string tokens are not a robust security design.

---

# 11. Error handling

The server registers a Hono error handler.

Conceptually:

```ts
app.onError(
  (err, c) => {
    if (
      err instanceof
      HTTPException
    ) {
      return c.text(
        err.message,
        err.status
      );
    }

    return c.text(
      "Internal Server Error",
      500
    );
  }
);
```

This allows the server to return meaningful HTTP status codes such as:

```text
401 Unauthorized
```

instead of crashing.

---

# 12. `/dump` debugging route

The `/dump` route returns information about an incoming HTTP request:

- method
- URL
- path
- headers
- query parameters
- body

This is a teaching/debugging endpoint for understanding HTTP requests.

It is not part of the core Deno KV API.

---

# 13. CRON reset logic

The course server contains an optional scheduled reset that iterates through the database and deletes entries.

Its purpose is convenient cleanup for shared instructional infrastructure.

If running your own persistent database, this reset must be removed or changed or it can erase your data.

---

# 14. Starting the server

The final line is conceptually:

```ts
Deno.serve(
  app.fetch
);
```

This hands incoming requests to the Hono application.

---

## Architecture concepts to remember

### Client

The program initiating a request.

In this module:

```text
kvadmin.py
```

### Server

The program receiving HTTP requests and running application logic.

In this module:

```text
main.ts + Hono
```

### Database

The persistent data store.

In this module:

```text
Deno KV
```

### API endpoint

A URL + HTTP method representing an operation.

Examples:

```text
POST   /kv/set/...
GET    /kv/get/...
GET    /kv/list/...
DELETE /kv/delete/...
```

---

## Main takeaway

This lecture is a miniature database-backed web application. The important architectural pattern is:

```text
Python CLI
→ HTTP
→ TypeScript web server
→ Deno KV
```

Once you understand that flow, the individual `set`, `get`, `list`, and `delete` handlers become straightforward.
