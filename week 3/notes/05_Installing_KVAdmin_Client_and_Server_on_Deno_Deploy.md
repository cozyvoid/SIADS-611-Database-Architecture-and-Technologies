# Lecture 5 — Installing KVAdmin.py Client and Server on Deno Deploy

**Weekly topic:** Video: Installing KVAdmin.py Client and Server on Deno Deploy (9 min)  
**Slide coverage:** Partial. The slide deck introduces the server/client architecture and links to the code, but the complete installation sequence is better documented in the course repository.

## Key points

1. KVAdmin has **two pieces**: a Python command-line client and a Deno web-service server.
2. The historical course workflow deployed `main.ts` to **Deno Deploy Classic** and configured a matching token in both the server and `hidden.py`.
3. `kvadmin.py` sends HTTP requests; it does not directly open the hosted Deno KV database.
4. The `/dump` route is used as a connectivity/debugging test.
5. The deployment instructions in the original course repository are now historically important because **Deno Deploy Classic shut down on July 20, 2026**.

---

# Part A — Historical course installation workflow

The following sequence reflects the course repository's Classic-era instructions. It is useful for understanding what the lecture is demonstrating.

## 1. Create the Deno server

The course repository uses:

```text
csev/deno-kv-admin
```

with a server entry file:

```text
main.ts
```

The historical instructions told students to:

1. Open Deno Deploy Classic.
2. Create a **New Playground**.
3. Copy the repository's `main.ts`.
4. Paste it into the playground.

---

## 2. Inspect the database-reset CRON job

The example server contains an hourly reset:

```ts
Deno.cron(
  "Hourly DB Reset",
  "0 * * * *",
  async () => {
    // delete KV records
  }
);
```

For a personal server, the repository instructs students to either:

- remove the CRON job, or
- change it to a much less frequent schedule.

Otherwise your database can be erased periodically.

---

## 3. Configure the token

The server has a function similar to:

```ts
function checkToken(c) {
  const token = c.req.query("token");

  if (token == "42") {
    return true;
  }

  throw new HTTPException(
    401,
    {
      message: "Missing or invalid token"
    }
  );
}
```

The autograder may require a specific token.

The same token must be used by the Python client.

---

## 4. Deploy and copy the service URL

The historical course workflow produced a URL resembling:

```text
https://your-project.deno.dev
```

Opening the bare root could legitimately produce:

```text
404 Not Found
```

because the application exposes specific API routes rather than a normal homepage.

---

## 5. Test the `/dump` route

Example:

```text
https://your-project.deno.dev/dump
```

The `/dump` route returns request information and is useful for verifying that the server is alive.

---

## 6. Test an authenticated KV route

Example:

```text
/kv/list/books?token=YOUR_TOKEN
```

If no matching values exist, a valid response can look like:

```json
{
  "records": [],
  "cursor": ""
}
```

If the token is incorrect, the server returns an HTTP 401-style error:

```text
Missing or invalid token
```

---

# Part B — Install the Python client

## 7. Download the client files

The course repository points to:

```text
kvadmin.py
hidden-dist.py
```

The secrets/configuration file is kept separate from the client code.

---

## 8. Create `hidden.py`

Copy:

```text
hidden-dist.py
```

to:

```text
hidden.py
```

Then configure the Deno host and token.

A course-style example is:

```python
def denokv():
    return {
        'token': 'YOUR_TOKEN',
        'url': 'https://your-project.deno.dev'
    }
```

Do not commit real credentials or course tokens to a public repository.

---

## 9. Run the client

From the folder containing the files:

```bash
python kvadmin.py
```

or:

```bash
python3 kvadmin.py
```

The client verifies the server before presenting its prompt.

Typical commands:

```text
help
samples
set /books/Hamlet
get /books/Hamlet
list /books
delete /books/Hamlet
delete_prefix /books
quit
```

---

# Part C — How the pieces connect

```text
Your computer
------------------------------------------------
kvadmin.py
    |
    | reads host + token from hidden.py
    |
    | HTTPS requests
    v

Deno server
------------------------------------------------
main.ts + Hono routes
    |
    | Deno.openKv()
    v

Deno KV
------------------------------------------------
hierarchical key-value records
```

---

# Important November 2026 platform update

The original repository tells students to use:

```text
dash.deno.com
```

and a Classic "Playground."

That platform no longer exists for active deployment:

- **Deno Deploy Classic shut down July 20, 2026.**
- The newer Deno Deploy uses `console.deno.com`.
- The newer platform organizes deployments around **organizations**, **apps**, and assignable **database instances**.
- A Deno KV database can be provisioned and assigned to an app.
- Inside the app, `Deno.openKv()` connects to the database associated with the current environment.
- Current Deno documentation says Deno Deploy is scheduled to sunset in **April 2027**.

Therefore, the original installation steps should be treated as **course/historical workflow**, not guaranteed current UI instructions.

If your assignment still expects a `.deno.dev` endpoint, a specific `kvadmin.py`, or a particular autograder token, follow the current course assignment instructions exactly.

---

## Security note

The course passes a token in the query string for simplicity:

```text
?token=42
```

That is suitable for a teaching demo, but not a recommended production-authentication pattern because URLs can be logged in multiple places.

Production systems normally use stronger authentication, HTTPS, secret management, and authorization controls.

---

## Main takeaway

Installation is really the setup of a **three-layer system**:

```text
Python client
→ HTTP API server
→ Deno KV database
```

The client and server must agree on the server URL, route structure, and authentication token before CRUD commands can work.
