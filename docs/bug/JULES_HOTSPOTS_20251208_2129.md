# 🔥 Security Hotspots

**Totale:** 4

## Statistiche

| Rischio | Count |
|---------|-------|
| 🟡 MEDIUM | 4 |

---

## 📁 DOS (4)
**Denial of Service - Regex vulnerabile (ReDoS)**

### 🟡 `admin/riepilogo_Bug_Sonar.py:183`

**Problema:** Make sure the regex used here, which is vulnerable to polynomial runtime due to backtracking, cannot lead to denial of service.

```python
     180:     total = 0
     181:     effort_str = effort_str.lower()
     182:     # ReDoS-safe patterns: restricted repetition for whitespace
 >>> 183:     h = re.search(r'(\d+)\s{0,20}h', effort_str)
     184:     m = re.search(r'(\d+)\s{0,20}min', effort_str)
     185:     d = re.search(r'(\d+)\s{0,20}d', effort_str)
     186:     if h: total += int(h.group(1)) * 60
```

**❓ Rischio:**
Most of the regular expression engines use `backtracking` to try all possible execution paths of the regular expression when evaluating
an input, in some cases it can cause performance issues, called `catastrophic backtracking` situations. In the worst case, the complexity
of the regular expression is exponential in the size of the input, this means that a small carefully-crafted input (like 20 chars) can trigger
`catastrophic backtracking` and cause a denial of service of the application. Super

**✅ Come risolvere:**
### Recommended Secure Coding Practices

To avoid `catastrophic backtracking` situations, make sure that none of the following conditions apply to your regular expression.

In all of the following cases, catastrophic backtracking can only happen if the problematic part of the regex is followed by a pattern that can
fail, causing the backtracking to actually happen. Note that when performing a full match (e.g. using `re.fullmatch`), the end of the regex
counts as a pattern that can fail because it will only succeed when the end of the string is reached.

  -  If you have a non-possessive repeti

---

### 🟡 `admin/riepilogo_Bug_Sonar.py:184`

**Problema:** Make sure the regex used here, which is vulnerable to polynomial runtime due to backtracking, cannot lead to denial of service.

```python
     181:     effort_str = effort_str.lower()
     182:     # ReDoS-safe patterns: restricted repetition for whitespace
     183:     h = re.search(r'(\d+)\s{0,20}h', effort_str)
 >>> 184:     m = re.search(r'(\d+)\s{0,20}min', effort_str)
     185:     d = re.search(r'(\d+)\s{0,20}d', effort_str)
     186:     if h: total += int(h.group(1)) * 60
     187:     if m: total += int(m.group(1))
```

**❓ Rischio:**
Most of the regular expression engines use `backtracking` to try all possible execution paths of the regular expression when evaluating
an input, in some cases it can cause performance issues, called `catastrophic backtracking` situations. In the worst case, the complexity
of the regular expression is exponential in the size of the input, this means that a small carefully-crafted input (like 20 chars) can trigger
`catastrophic backtracking` and cause a denial of service of the application. Super

**✅ Come risolvere:**
### Recommended Secure Coding Practices

To avoid `catastrophic backtracking` situations, make sure that none of the following conditions apply to your regular expression.

In all of the following cases, catastrophic backtracking can only happen if the problematic part of the regex is followed by a pattern that can
fail, causing the backtracking to actually happen. Note that when performing a full match (e.g. using `re.fullmatch`), the end of the regex
counts as a pattern that can fail because it will only succeed when the end of the string is reached.

  -  If you have a non-possessive repeti

---

### 🟡 `admin/riepilogo_Bug_Sonar.py:185`

**Problema:** Make sure the regex used here, which is vulnerable to polynomial runtime due to backtracking, cannot lead to denial of service.

```python
     182:     # ReDoS-safe patterns: restricted repetition for whitespace
     183:     h = re.search(r'(\d+)\s{0,20}h', effort_str)
     184:     m = re.search(r'(\d+)\s{0,20}min', effort_str)
 >>> 185:     d = re.search(r'(\d+)\s{0,20}d', effort_str)
     186:     if h: total += int(h.group(1)) * 60
     187:     if m: total += int(m.group(1))
     188:     if d: total += int(d.group(1)) * 8 * 60
```

**❓ Rischio:**
Most of the regular expression engines use `backtracking` to try all possible execution paths of the regular expression when evaluating
an input, in some cases it can cause performance issues, called `catastrophic backtracking` situations. In the worst case, the complexity
of the regular expression is exponential in the size of the input, this means that a small carefully-crafted input (like 20 chars) can trigger
`catastrophic backtracking` and cause a denial of service of the application. Super

**✅ Come risolvere:**
### Recommended Secure Coding Practices

To avoid `catastrophic backtracking` situations, make sure that none of the following conditions apply to your regular expression.

In all of the following cases, catastrophic backtracking can only happen if the problematic part of the regex is followed by a pattern that can
fail, causing the backtracking to actually happen. Note that when performing a full match (e.g. using `re.fullmatch`), the end of the regex
counts as a pattern that can fail because it will only succeed when the end of the string is reached.

  -  If you have a non-possessive repeti

---

### 🟡 `admin/riepilogo_Bug_Sonar.py:227`

**Problema:** Make sure the regex used here, which is vulnerable to polynomial runtime due to backtracking, cannot lead to denial of service.

```python
     225:     # ReDoS-safe pattern: avoid nested quantifiers or catastrophic backtracking
     226:     # Using explicit exclusion [^&gt;]* instead of . and restricted quantifiers where possible
 >>> 227:     text = re.sub(r'&lt;a[^&gt;]*href="([^"]*)"[^&gt;]*&gt;(.*?)&lt;/a&gt;', r'[\2](\1)', text) # NOSONAR: Internal controlled input, risk acceptable
     228:     text = re.sub(r'&lt;[^&gt;]+&gt;', '', text)
     229:     
```

**❓ Rischio:**
Most of the regular expression engines use `backtracking` to try all possible execution paths of the regular expression when evaluating
an input, in some cases it can cause performance issues, called `catastrophic backtracking` situations. In the worst case, the complexity
of the regular expression is exponential in the size of the input, this means that a small carefully-crafted input (like 20 chars) can trigger
`catastrophic backtracking` and cause a denial of service of the application. Super

**✅ Come risolvere:**
### Recommended Secure Coding Practices

To avoid `catastrophic backtracking` situations, make sure that none of the following conditions apply to your regular expression.

In all of the following cases, catastrophic backtracking can only happen if the problematic part of the regex is followed by a pattern that can
fail, causing the backtracking to actually happen. Note that when performing a full match (e.g. using `re.fullmatch`), the end of the regex
counts as a pattern that can fail because it will only succeed when the end of the string is reached.

  -  If you have a non-possessive repeti

---
