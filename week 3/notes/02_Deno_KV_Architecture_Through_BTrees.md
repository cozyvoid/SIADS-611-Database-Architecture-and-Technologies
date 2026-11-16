# Lecture 2 — Exploring Deno KV Architecture Through B-Trees

**Weekly topic:** Video: Exploring Deno KV Architecture Through B-Trees (13 min)  
**Slide coverage:** Strong conceptually — mainly slides 23–31.

## Key points

1. **B-trees keep keys sorted while supporting efficient search, insertion, and deletion.**
2. **Sorted keys make prefix/range access natural**, which helps explain Deno KV's ordered key space.
3. **The lecture uses a distributed B-tree as a conceptual model** for imagining how key ranges might be coordinated across nodes.
4. **Distributed writes create coordination problems**, so temporary disagreement between replicas/nodes is an important systems concept.
5. **Current Deno KV documentation says reads are strongly consistent by default**, with eventual consistency available as an option for reads.

---

## 1. What is a B-tree?

A **B-tree** is a balanced search-tree data structure optimized for storage systems that read and write blocks of data.

Important properties:

- keys remain sorted
- search is efficient
- insertion is efficient
- deletion is efficient
- the tree remains balanced
- nodes can contain multiple keys

The lecture describes typical operations as logarithmic-time operations.

Conceptually:

```text
             [07 | 16]
             /   |   \
      [01 02 05] [09 12] [18 21]
```

A search does not inspect every value. It uses comparison boundaries to move toward the correct branch.

---

## 2. Why B-trees fit database systems

Databases need to perform:

- exact lookup
- ordered traversal
- range scans
- insertions
- deletions

A B-tree gives one ordered structure that supports all of these efficiently.

This is why B-tree-family indexes are common in relational database systems.

The lecture explicitly compares Deno KV's logical ordering to a PostgreSQL B-tree index.

---

## 3. Relating B-trees to Deno KV keys

Suppose these keys exist:

```text
["books", "Mindshift"]
["books", "Python"]
["books", "Raspberry PI"]
["books", "Wisdom of Crowds"]
```

Because keys have an ordering, Deno KV can efficiently scan a prefix:

```ts
kv.list({ prefix: ["books"] });
```

The core mental connection is:

```text
ordered key space
        +
prefix/range access
        =
B-tree-like database behavior
```

---

## 4. The lecture's distributed B-tree model

The slides illustrate a single logical tree spread across multiple Deno Deploy nodes.

Conceptually:

```text
             logical root
           /      |      \
      key range  key range  key range
         |          |          |
      node A      node B      node C
```

A client might contact one node, but that node needs enough information to determine where the requested key belongs.

### Important caution

The slide says Deno KV is **"likely some variation of a single large B-tree structure"** distributed across nodes.

Treat this as a **teaching analogy**, not a verified statement of the internal implementation.

Current Deno documentation instead tells us that:

- local Deno KV uses SQLite
- production Deno KV is backed by FoundationDB

The exact internal structures of those systems are more complex than the lecture diagram.

---

## 5. The write-propagation example

The lecture demonstrates adding a new key such as:

```text
/04
```

During the update:

1. One node may first know that `/04` exists.
2. Other nodes may still have older routing/state information.
3. Updated state propagates.
4. Eventually all nodes agree again.

This is useful for learning the general distributed-systems problem:

> How do multiple machines maintain a coherent view of shared data while updates are occurring?

---

## 6. Consistency: lecture model vs. current Deno behavior

### Lecture framing

The lecture concludes that B-trees are a natural starting point for a distributed **eventual-consistency** database.

That is useful as a distributed-systems teaching model.

### Current official Deno KV behavior

Current Deno documentation describes Deno KV differently:

- **Strong consistency is the default for reads.**
- Writes are strongly consistent.
- A read may explicitly request **eventual consistency** for lower latency.

So you should distinguish:

**Concept learned from the slides:**  
Distributed replicas may require time and coordination to converge.

**Current Deno KV API behavior:**  
Applications get strong reads by default unless they opt into eventual reads.

---

## 7. Why auto-incrementing integers are awkward in distributed systems

The lecture notes that simple sequential IDs are difficult to coordinate globally.

In a centralized SQL database, this is easy:

```text
1, 2, 3, 4, 5 ...
```

In a distributed system, many nodes may attempt to create the "next" value simultaneously.

That would require global coordination.

Distributed systems therefore often use identifiers that can be generated independently.

---

## 8. ULID

The slides mention **ULID — Universally Unique Lexicographically Sortable Identifier**.

A ULID combines two desirable properties:

- globally unique enough for distributed creation
- lexicographically sortable

That second property is useful in ordered key-value stores because IDs can preserve approximate creation order.

---

## Important definitions

**B-tree**  
A balanced multi-way search tree that keeps keys sorted and supports efficient lookup, insertion, deletion, and sequential access.

**Key range**  
A contiguous portion of the ordered key space.

**Replica**  
Another copy of data maintained on a different node or location.

**Strong consistency**  
A read reflects the most recently completed write according to the system's consistency guarantees.

**Eventual consistency**  
Different replicas may temporarily return different values, but converge if no new writes occur.

**ULID**  
A unique identifier designed to be lexicographically sortable.

---

## Main takeaway

Use the B-tree material to understand **ordered key spaces, efficient lookup, prefix/range scans, and the coordination challenges created when data is distributed**. Do not interpret the lecture's distributed B-tree drawing as a literal blueprint of Deno KV's implementation.
