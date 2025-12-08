# 🔴 RELIABILITY Issues

**Totale:** 2
**Tempo:** 6min

---

## 📄 `guide_frontend/src/components/Sidebar.jsx` (1)

### Riga 76 🟡
**Problema:** Either remove this useless object instantiation of "globalContext.QWebChannel" or use it.

```jsx
     74:     if (globalContext.qt?.webChannelTransport) {
     75:       // Assign to a variable to prevent object from being dropped immediately
 >>> 76:       new globalContext.QWebChannel(globalContext.qt.webChannelTransport, function(c) {
     77:         if (c.objects?.bridge) {
     78:             setBridge(c.objects.bridge);
```

**❓ Perché:**
Creating an object without assigning it to a variable or using it in any function means the object is essentially created for no reason and may be
dropped immediately without being used. Most of the time, this is due to a missing piece of code and could lead to an unexpected behavior.

If it’s intended because the constructor has side effects, that side effect should be moved into a separate method and called directly. This can
help to improve the performance and readability of the code.

```
new MyConstructor(); // Noncompliant: object may be dropped
```

Determine if the objects are necessar

**📚 Risorse:**
### Documentation

  -  MDN web docs - [`Object.prototype.constructor`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/constructor) 

  -  MDN web docs - [constructor](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/constructor) 

  -  MDN web docs - [`new` operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference

---

## 📄 `admin/riepilogo_Bug_Sonar.py` (1)

### Riga 654 🟢
**Problema:** Replace with dict fromkeys method call

```python
     652:     """Recupera tutti gli issues."""
     653:     all_issues = []
 >>> 654:     issues_count = {q: 0 for q in SOFTWARE_QUALITIES}
     655:     
     656:     for quality in SOFTWARE_QUALITIES:
```

**❓ Perché:**
Using a dictionary comprehension to build a dictionary where every key maps to the exact same constant value e.g., {k: 1 for k in
keys} is less efficient and less idiomatic than using the `dict.fromkeys()` class method. `dict.fromkeys()` is
specifically designed for this use case and offers better performance, especially for large iterables, as it avoids the overhead of creating and
processing individual key-value pairs in a comprehension.

**✅ Come risolvere:**
Rewrite the dictionary comprehension `{x: constant for x in iterable}` as `dict.fromkeys(iterable, constant)`. If the
constant value is `None`, you can omit the value argument in `dict.fromkeys()`, as it defaults to `None`.

### Noncompliant code example

```
keys = ['a', 'b', 'c']

dict_comp_one = {k: 1 for k in keys} # Noncompliant
```

### Compliant solution

```
keys = ['a', 'b', 'c']

dict_fromkeys_one = dict.fromkeys(keys, 1)
```

**📚 Risorse:**
### Documentation

  -  Python Documentation - [dict.fromkeys](https://docs.python.org/3/library/stdtypes.html#dict.fromkeys)

---
