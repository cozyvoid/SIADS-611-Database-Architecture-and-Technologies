# Deno KV Week — Lecture Coverage Index

## Source basis

These notes are based primarily on the uploaded lecture deck **07-DenoKV.pptx.pdf** (58 slides), with supplemental material added only where the weekly topic list goes beyond what the slides explicitly explain.

The weekly topics are:

1. Intro to Deno and Deno KV
2. Exploring Deno KV Architecture Through B-Trees
3. JavaScript in Three Slides (for Python Developers)
4. Exploring CRUD in Deno KV Using KVAdmin.py
5. Installing KVAdmin.py Client and Server on Deno Deploy
6. Code Walkthrough — KVAdmin.py Client and Server
7. Building a Deno KV Model with Secondary Indexes
8. Reading — Deno KV Documentation

---

## Coverage assessment

| Topic | Slide coverage | Notes |
|---|---|---|
| Intro to Deno and Deno KV | **Strong** | Slides 2–19 cover Node/Deno history, edge architecture, Deno Deploy, Deno KV, and KV basics. |
| Deno KV Architecture Through B-Trees | **Strong, but conceptual** | Slides 23–31 explain B-trees, distributed key lookup, and consistency using diagrams. The "distributed B-tree" description is best treated as a teaching model rather than a literal implementation specification. |
| JavaScript in Three Slides | **Strong** | Slides 32–35 give a Python-to-JavaScript syntax comparison. |
| CRUD Using KVAdmin.py | **Strong** | Slides 36–46 demonstrate `set`, `get`, `list`, and `delete`, including client/server requests. |
| Installing KVAdmin.py Client and Server | **Partial** | The deck introduces the components but does not give the complete installation workflow. Supplemental installation notes are included from the course repository. |
| KVAdmin.py Client/Server Code Walkthrough | **Moderate-to-strong** | Slides 39–45 show key client and server fragments. Supplemental notes explain the full request flow and major server routes. |
| Deno KV Model with Secondary Indexes | **Strong** | Slides 47–56 compare SQL modeling with Deno KV and demonstrate manual secondary-index keys. |
| Deno KV Documentation | **Referenced, not summarized** | Slides link to Deno documentation; a separate reading guide summarizes the current core API. |

---

## Important current-platform note (November 2026)

The course slides and the `deno-kv-admin` repository were written around **Deno Deploy Classic**. That platform shut down on **July 20, 2026**. The newer Deno Deploy platform uses `console.deno.com`, supports Deno KV as a database engine, and automatically connects an assigned KV database through `Deno.openKv()`.

The current Deno documentation also says **Deno Deploy itself is scheduled to sunset in April 2027**.

For coursework, distinguish between:

- **Course mechanics:** what the lecture, assignment, or autograder expects.
- **Current platform behavior:** what the live Deno documentation says today.

Do not substitute current deployment instructions for assignment-specific instructions unless the course explicitly tells you to.

---

## Suggested study order

1. **01 — Intro to Deno and Deno KV**
2. **03 — JavaScript in Three Slides** if JavaScript is unfamiliar
3. **02 — B-Trees and KV Architecture**
4. **04 — CRUD with KVAdmin.py**
5. **05 — Installing the Client and Server**
6. **06 — Client/Server Code Walkthrough**
7. **07 — Secondary Index Data Modeling**
8. **08 — Deno KV Documentation Reading Guide**

This order moves from architecture → syntax → storage mechanics → tooling → data modeling.
