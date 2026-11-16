> **SIADS 611 — Module 2 supplementary study notes**  
> These notes cover lecture topics **not addressed** in the uploaded *Relational Database Design — Many-to-Many* slide deck. Explanations and sample code are instructional illustrations, **not verbatim video transcripts**.  
> Instructor references: [Python and PostgreSQL](https://www.pg4e.com/lectures/06-Python.php) · [JSON and PostgreSQL](https://www.pg4e.com/lectures/06-JSON.php)

# Part C — JSON Fundamentals and Python

**Lectures 9–11:** JavaScript Object Notation (11 min); Douglas Crockford interview (7 min); Python and JSON (7 min).

## 9. JavaScript Object Notation (JSON)

**JSON = JavaScript Object Notation**, a text-based, language-independent format for exchanging structured data.

```json
{
  "student": "Jane",
  "age": 25,
  "enrolled": true,
  "courses": ["Python", "SQL"],
  "address": {"city": "Ann Arbor", "state": "Michigan"}
}
```

| JSON type | Example | Python counterpart |
|---|---|---|
| Object | `{"name":"Jane"}` | `dict` |
| Array | `["SQL","Python"]` | `list` |
| String | `"Jane"` | `str` |
| Number | `25`, `3.5` | `int`, `float` |
| Boolean | `true`, `false` | `True`, `False` |
| Null | `null` | `None` |

**Syntax rules:** Keys and strings use **double quotes**; booleans and `null` are lowercase; trailing commas are not allowed in standard JSON.

## 10. Douglas Crockford interview: Why JSON matters

JSON became popular as a lightweight alternative to more verbose interchange formats such as XML. Its simple arrays and objects map naturally to programming data structures, allowing different systems to communicate.

**Key conclusion:** A widely supported shared data format reduces the work needed to exchange structured information.

## 11. Python and JSON

Python provides the built-in `json` module.

| Function | Direction |
|---|---|
| `json.dumps(python_object)` | Python object → JSON string |
| `json.loads(json_string)` | JSON string → Python object |
| `json.dump(obj, file)` | Python object → JSON file |
| `json.load(file)` | JSON file → Python object |

```python
import json

student = {
    "name": "Jane",
    "courses": ["SQL", "Python"],
    "active": True
}

json_string = json.dumps(student, indent=4)
print(json_string)

restored = json.loads(json_string)
print(restored["name"])  # Jane
```

- **Serialization** means converting a Python object into JSON for storage or transmission.
- **Deserialization** means parsing JSON back into Python data structures.
- JSON is **text**, not a Python dictionary; you must parse it before accessing keys as Python objects.

**Study check:** How do `json.dumps()` and `json.loads()` differ? Why is `True` valid Python but not valid raw JSON?
