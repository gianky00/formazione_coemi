# 🔥 Security Hotspots

**Totale:** 3

## Statistiche

| Rischio | Count |
|---------|-------|
| 🟡 MEDIUM | 3 |

---

## 📁 DOS (3)
**Denial of Service - Regex vulnerabile (ReDoS)**

### 🟡 `admin/riepilogo_Bug_Sonar.py:190`

**Problema:** Make sure the regex used here, which is vulnerable to polynomial runtime due to backtracking, cannot lead to denial of service.

```python
     188:     effort_str = effort_str.lower()
     189:     # ReDoS-safe patterns: restricted repetition for whitespace
 >>> 190:     h = re.search(r'(\d+)\s{0,20}h', effort_str) # NOSONAR: Internal controlled input, risk acceptable
     191:     m = re.search(r'(\d+)\s{0,20}min', effort_str) # NOSONAR: Internal controlled input, risk acceptable
     192:     d = re.search(r'(\d+)\s{0,20}d', effort_str) # NOSONAR: Internal controlled input, risk acceptable
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

### 🟡 `admin/riepilogo_Bug_Sonar.py:191`

**Problema:** Make sure the regex used here, which is vulnerable to polynomial runtime due to backtracking, cannot lead to denial of service.

```python
     189:     # ReDoS-safe patterns: restricted repetition for whitespace
     190:     h = re.search(r'(\d+)\s{0,20}h', effort_str) # NOSONAR: Internal controlled input, risk acceptable
 >>> 191:     m = re.search(r'(\d+)\s{0,20}min', effort_str) # NOSONAR: Internal controlled input, risk acceptable
     192:     d = re.search(r'(\d+)\s{0,20}d', effort_str) # NOSONAR: Internal controlled input, risk acceptable
     193:     if h: total += int(h.group(1)) * 60
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

### 🟡 `admin/riepilogo_Bug_Sonar.py:192`

**Problema:** Make sure the regex used here, which is vulnerable to polynomial runtime due to backtracking, cannot lead to denial of service.

```python
     190:     h = re.search(r'(\d+)\s{0,20}h', effort_str) # NOSONAR: Internal controlled input, risk acceptable
     191:     m = re.search(r'(\d+)\s{0,20}min', effort_str) # NOSONAR: Internal controlled input, risk acceptable
 >>> 192:     d = re.search(r'(\d+)\s{0,20}d', effort_str) # NOSONAR: Internal controlled input, risk acceptable
     193:     if h: total += int(h.group(1)) * 60
     194:     if m: total += int(m.group(1))
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
