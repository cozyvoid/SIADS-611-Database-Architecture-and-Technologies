# Lecture 3 — JavaScript in Three Slides (for Python Developers)

**Weekly topic:** Video: JavaScript in Three Slides (For Python Developers) (6 min)  
**Slide coverage:** Strong — slides 32–35.

## Key points

1. Python and JavaScript are both interpreted, high-level languages, but their syntax differs substantially.
2. Python dictionaries map closely to JavaScript objects.
3. Python lists map closely to JavaScript arrays.
4. JavaScript uses braces `{}` to define blocks instead of indentation.
5. Deno code frequently uses asynchronous JavaScript/TypeScript, so `async` and `await` are important additions to the three-slide comparison.

---

## 1. Dictionary vs. object

### Python

```python
x = {
    'key': 'value',
    'lines': 25
}

print(x)
```

### JavaScript

```js
const x = {
  key: "value",
  lines: 25
};

console.log(x);
```

Mental translation:

```text
Python dict  ≈  JavaScript object
```

---

## 2. List vs. array

### Python

```python
y = ['bob', 'alice']
print(y)
```

### JavaScript

```js
const y = ["bob", "alice"];
console.log(y);
```

Mental translation:

```text
Python list  ≈  JavaScript array
```

Deno KV keys are JavaScript arrays:

```js
["books", "Hamlet"]
```

That is why understanding arrays is especially important in this module.

---

## 3. Printing output

### Python

```python
print("hello")
```

### JavaScript

```js
console.log("hello");
```

---

## 4. Conditional statements

### Python

```python
a = 17

if a < 20:
    print("Below 20")
else:
    print("20 or higher")
```

### JavaScript

```js
const a = 17;

if (a < 20) {
  console.log("Below 20");
} else {
  console.log("20 or higher");
}
```

Important difference:

- Python uses indentation to define a block.
- JavaScript uses `{ ... }`.

---

## 5. Loops

The lecture uses a traditional JavaScript counting loop.

### Python

```python
for i in range(5):
    print(i)
```

### JavaScript

```js
for (let i = 0; i < 5; i++) {
  console.log(i);
}
```

Breakdown:

```text
let i = 0     initialize
i < 5         keep looping while true
i++           increase i by one after each iteration
```

---

## 6. Splitting strings

### Python

```python
"/a/b/c".split("/")
```

### JavaScript

```js
"/a/b/c".split("/");
```

Both produce approximately:

```text
["", "a", "b", "c"]
```

This is directly relevant to the KVAdmin server.

A URL path such as:

```text
/books/Hamlet
```

can be transformed into a Deno KV key with:

```js
key.split("/")
```

---

## 7. Strings and newline characters

Both languages support escape sequences such as `\n`.

### Python

```python
c = "hello" + "\n" + "world"
```

### JavaScript

```js
const c = "hello" + "\n" + "world";
```

---

## 8. `const` and `let`

The lecture examples use simple assignment to focus on syntax.

For modern JavaScript, prefer:

```js
const x = 17;
```

when the variable will not be reassigned.

Use:

```js
let x = 17;
x = 18;
```

when reassignment is needed.

Avoid creating variables without `const`, `let`, or `var`.

---

## 9. `async` and `await` — important Deno supplement

Deno KV operations are asynchronous.

Example:

```js
const kv = await Deno.openKv();

const result = await kv.get([
  "books",
  "Hamlet"
]);
```

`await` means:

> Pause this async operation until the promise completes, then continue with the result.

You will see this repeatedly in Deno KV code.

---

## 10. Python → JavaScript quick-reference table

| Python | JavaScript |
|---|---|
| `print(x)` | `console.log(x)` |
| `dict` | object |
| `list` / `tuple` | array |
| `None` | `null` |
| `True`, `False` | `true`, `false` |
| `len(x)` | `x.length` |
| `for i in range(5)` | `for (let i=0; i<5; i++)` |
| indentation | `{ }` blocks |
| `and`, `or`, `not` | `&&`, `||`, `!` |
| `x['name']` | `x["name"]` or `x.name` |
| `json.loads()` | `JSON.parse()` |
| `json.dumps()` | `JSON.stringify()` |

---

## Main takeaway

You do **not** need to become a full JavaScript developer to follow this module. Focus on recognizing objects, arrays, conditionals, loops, string methods, functions, and especially `async`/`await`. The Deno KV code is structurally similar to Python once you learn the syntax translation.
