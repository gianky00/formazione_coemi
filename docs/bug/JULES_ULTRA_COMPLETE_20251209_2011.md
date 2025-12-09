# 🔧 ULTRA-COMPLETE Fix Guide

**Totale:** 8 issues
**Tempo:** 1h 2min

---

## 📄 `admin/riepilogo_Bug_Sonar.py`

### Riga 190 🟡 🟡
**Problema:** Fix the syntax of this issue suppression comment.
**Regola:** `python:S7632` - Issue suppression comment should have the correct format

```python
     188:     effort_str = effort_str.lower()
     189:     # ReDoS-safe patterns: restricted repetition for whitespace
 >>> 190:     h = re.search(r'(\d+)\s{0,20}h', effort_str) # NOSONAR: Internal controlled input, risk acceptable
     191:     m = re.search(r'(\d+)\s{0,20}min', effort_str) # NOSONAR: Internal controlled input, risk acceptable
     192:     d = re.search(r'(\d+)\s{0,20}d', effort_str) # NOSONAR: Internal controlled input, risk acceptable
```

**❓ Perché è un problema:**
Issue suppression comments like `# NOSONAR` and `# noqa` are essential tools for controlling code analysis. When these
comments have incorrect syntax, they may not work as expected, leading to confusion about which issues are actually suppressed.

Python code analysis supports two main suppression formats: - `# NOSONAR` - SonarQube’s suppression comment - `# noqa` -
Python’s standard "no quality assurance" comment

Each format has specific syntax rules. When these rules are violated, the suppression might fail silently or behave unexpectedly, making it unclear
whether issues are intentionally ignored or accidentally unsuppressed.

### What is the potential impact?

Incorrectly formatted suppression comments can lead to unintended code analysis behavior. Issues that developers think are sup

**✅ Come risolvere:**
Fix the syntax of issue suppression comments to follow the correct format.

For `# NOSONAR`:

  -  Use `# NOSONAR` alone to suppress all issues on the line 

  -  Use `# NOSONAR()` with empty parentheses to suppress all issues 

  -  Use `# NOSONAR(ruleKey1, ruleKey2)` to suppress specific rules 

  -  Don’t use redundant commas in the parentheses, e.g. `# NOSONAR(,)` 

  -  The rule keys should only consist of alphanumeric characters, like `S7632` or `NoSonar` 

  -  Close all parentheses properly 

For `# noqa`:

  -  Use `# noqa` alone to suppress all issues on the line 

  -  Use `# noqa: rule1,rule2` to suppress specific rules (with or without spaces after colon) 

  -  Don’t use redundant commas in the comma-separated lists, e.g. `# noqa: ,rule1` 

  -  Don’t forget the colon (`:`) between `noqa` and the rule ID, and don’t use other punctuation 

### Noncompliant code example

```
def example():
    x = 1  # NOSONAR(  # Noncompliant
    y = 2  # NOSONAR(a,)  # Noncompliant
    z 

**📚 Risorse:**
### Documentation

  -  SonarQube documentation - [Managing your code issues](https://docs.sonarqube.org/latest/user-guide/issues/#header-4) 

  -  Flake8 documentation - [In-line Ignoring Errors](https://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors)

---

### Riga 191 🟡 🟡
**Problema:** Fix the syntax of this issue suppression comment.
**Regola:** `python:S7632` - Issue suppression comment should have the correct format

```python
     189:     # ReDoS-safe patterns: restricted repetition for whitespace
     190:     h = re.search(r'(\d+)\s{0,20}h', effort_str) # NOSONAR: Internal controlled input, risk acceptable
 >>> 191:     m = re.search(r'(\d+)\s{0,20}min', effort_str) # NOSONAR: Internal controlled input, risk acceptable
     192:     d = re.search(r'(\d+)\s{0,20}d', effort_str) # NOSONAR: Internal controlled input, risk acceptable
     193:     if h: total += int(h.group(1)) * 60
```

**❓ Perché è un problema:**
Issue suppression comments like `# NOSONAR` and `# noqa` are essential tools for controlling code analysis. When these
comments have incorrect syntax, they may not work as expected, leading to confusion about which issues are actually suppressed.

Python code analysis supports two main suppression formats: - `# NOSONAR` - SonarQube’s suppression comment - `# noqa` -
Python’s standard "no quality assurance" comment

Each format has specific syntax rules. When these rules are violated, the suppression might fail silently or behave unexpectedly, making it unclear
whether issues are intentionally ignored or accidentally unsuppressed.

### What is the potential impact?

Incorrectly formatted suppression comments can lead to unintended code analysis behavior. Issues that developers think are sup

**✅ Come risolvere:**
Fix the syntax of issue suppression comments to follow the correct format.

For `# NOSONAR`:

  -  Use `# NOSONAR` alone to suppress all issues on the line 

  -  Use `# NOSONAR()` with empty parentheses to suppress all issues 

  -  Use `# NOSONAR(ruleKey1, ruleKey2)` to suppress specific rules 

  -  Don’t use redundant commas in the parentheses, e.g. `# NOSONAR(,)` 

  -  The rule keys should only consist of alphanumeric characters, like `S7632` or `NoSonar` 

  -  Close all parentheses properly 

For `# noqa`:

  -  Use `# noqa` alone to suppress all issues on the line 

  -  Use `# noqa: rule1,rule2` to suppress specific rules (with or without spaces after colon) 

  -  Don’t use redundant commas in the comma-separated lists, e.g. `# noqa: ,rule1` 

  -  Don’t forget the colon (`:`) between `noqa` and the rule ID, and don’t use other punctuation 

### Noncompliant code example

```
def example():
    x = 1  # NOSONAR(  # Noncompliant
    y = 2  # NOSONAR(a,)  # Noncompliant
    z 

**📚 Risorse:**
### Documentation

  -  SonarQube documentation - [Managing your code issues](https://docs.sonarqube.org/latest/user-guide/issues/#header-4) 

  -  Flake8 documentation - [In-line Ignoring Errors](https://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors)

---

### Riga 192 🟡 🟡
**Problema:** Fix the syntax of this issue suppression comment.
**Regola:** `python:S7632` - Issue suppression comment should have the correct format

```python
     190:     h = re.search(r'(\d+)\s{0,20}h', effort_str) # NOSONAR: Internal controlled input, risk acceptable
     191:     m = re.search(r'(\d+)\s{0,20}min', effort_str) # NOSONAR: Internal controlled input, risk acceptable
 >>> 192:     d = re.search(r'(\d+)\s{0,20}d', effort_str) # NOSONAR: Internal controlled input, risk acceptable
     193:     if h: total += int(h.group(1)) * 60
     194:     if m: total += int(m.group(1))
```

**❓ Perché è un problema:**
Issue suppression comments like `# NOSONAR` and `# noqa` are essential tools for controlling code analysis. When these
comments have incorrect syntax, they may not work as expected, leading to confusion about which issues are actually suppressed.

Python code analysis supports two main suppression formats: - `# NOSONAR` - SonarQube’s suppression comment - `# noqa` -
Python’s standard "no quality assurance" comment

Each format has specific syntax rules. When these rules are violated, the suppression might fail silently or behave unexpectedly, making it unclear
whether issues are intentionally ignored or accidentally unsuppressed.

### What is the potential impact?

Incorrectly formatted suppression comments can lead to unintended code analysis behavior. Issues that developers think are sup

**✅ Come risolvere:**
Fix the syntax of issue suppression comments to follow the correct format.

For `# NOSONAR`:

  -  Use `# NOSONAR` alone to suppress all issues on the line 

  -  Use `# NOSONAR()` with empty parentheses to suppress all issues 

  -  Use `# NOSONAR(ruleKey1, ruleKey2)` to suppress specific rules 

  -  Don’t use redundant commas in the parentheses, e.g. `# NOSONAR(,)` 

  -  The rule keys should only consist of alphanumeric characters, like `S7632` or `NoSonar` 

  -  Close all parentheses properly 

For `# noqa`:

  -  Use `# noqa` alone to suppress all issues on the line 

  -  Use `# noqa: rule1,rule2` to suppress specific rules (with or without spaces after colon) 

  -  Don’t use redundant commas in the comma-separated lists, e.g. `# noqa: ,rule1` 

  -  Don’t forget the colon (`:`) between `noqa` and the rule ID, and don’t use other punctuation 

### Noncompliant code example

```
def example():
    x = 1  # NOSONAR(  # Noncompliant
    y = 2  # NOSONAR(a,)  # Noncompliant
    z 

**📚 Risorse:**
### Documentation

  -  SonarQube documentation - [Managing your code issues](https://docs.sonarqube.org/latest/user-guide/issues/#header-4) 

  -  Flake8 documentation - [In-line Ignoring Errors](https://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors)

---

### Riga 452 🟡 🟡
**Problema:** Remove the unused function parameter "summary".
**Regola:** `python:S1172` - Unused function parameters should be removed

```python
     450:     return None
     451: 
 >>> 452: def _process_test_case(testcase, summary):
     453:     """Processa un singolo test case."""
     454:     classname = testcase.get('classname', '')
```

**❓ Perché è un problema:**
A typical code smell known as unused function parameters refers to parameters declared in a function but not used anywhere within the function’s
body. While this might seem harmless at first glance, it can lead to confusion and potential errors in your code. Disregarding the values passed to
such parameters, the function’s behavior will be the same, but the programmer’s intention won’t be clearly expressed anymore. Therefore, removing
function parameters that are not being utilized is considered best practice.

### Exceptions

This rule ignores overriding methods.

```
class C(B):
  def do_something(self, a, b): # no issue reported on b
    return self.compute(a)
```

This rule also ignores variables named with a single underscore `_`. Such naming is a common practice for indicating that t

**✅ Come risolvere:**
Having unused function parameters in your code can lead to confusion and misunderstanding of a developer’s intention. They reduce code readability
and introduce the potential for errors. To avoid these problems, developers should remove unused parameters from function declarations.

### Noncompliant code example

```
def do_something(a, b): # second parameter is unused
  return compute(a)
```

### Compliant solution

```
def do_something(a):
  return compute(a)
```

---

### Riga 675 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     673:     return data
     674: 
 >>> 675: def fetch_all_issues():
     676:     """Recupera tutti gli issues."""
     677:     all_issues = []
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 1213 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 44 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1211: 
     1212: 
 >>> 1213: def generate_summary(issues, analysis, issues_count, hotspots, hotspot_analysis, 
     1214:                      junit_summary, test_analysis, timestamp, generated_files):
     1215:     """Genera SUMMARY."""
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

### Riga 1670 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 21 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1668:             order += 1
     1669: 
 >>> 1670: def main():
     1671:     stats['start_time'] = datetime.now()
     1672:     
```

**❓ Perché è un problema:**
Cognitive Complexity is a measure of how hard it is to understand the control flow of a unit of code. Code with high cognitive complexity is hard
to read, understand, test, and modify.

As a rule of thumb, high cognitive complexity is a sign that the code should be refactored into smaller, easier-to-manage pieces.

### Which syntax in code does impact cognitive complexity score?

Here are the core concepts:

  -  **Cognitive complexity is incremented each time the code breaks the normal linear reading flow.**
 This concerns, for example,
  loop structures, conditionals, catches, switches, jumps to labels, and conditions mixing multiple operators. 

  -  **Each nesting level increases complexity.**
 During code reading, the deeper you go through nested layers, the harder it
  becomes to kee

**✅ Come risolvere:**
Reducing cognitive complexity can be challenging.
 Here are a few suggestions:

  -  **Extract complex conditions in a new function.**
 Mixed operators in condition will increase complexity. Extracting the
  condition in a new function with an appropriate name will reduce cognitive load. 

  -  **Break down large functions.**
 Large functions can be hard to understand and maintain. If a function is doing too many
  things, consider breaking it down into smaller, more manageable functions. Each function should have a single responsibility. 

  -  **Avoid deep nesting by returning early.**
 To avoid the nesting of conditions, process exceptional cases first and return
  early. 

**Extraction of a complex condition in a new function.**

### Noncompliant code example

The code is using a complex condition and has a cognitive cost of 5.

```
def process_eligible_users(users):
    for user in users:             # +1 (for)
        if ((user.is_active and    # +1 (if) +1 (nested) +1 (multiple 

**📚 Risorse:**
### Documentation

  -  Sonar - [Cognitive Complexity](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) 

### Articles & blog posts

  -  Sonar Blog - 5 Clean Code Tips for Reducing
  Cognitive Complexity

---

## 📄 `guide_frontend/src/components/Sidebar.jsx`

### Riga 77 🟡 🟢
**Problema:** Prefer `globalThis` over `window`.
**Regola:** `javascript:S7764` - Use "globalThis" instead of "window", "self", or "global"

```jsx
     75:       // Assign to window to prevent object from being dropped immediately and ensure it persists
     76:       // Using window._channel to bypass linter checks for unused variables while ensuring persistence
 >>> 77:       window._channel = new globalContext.QWebChannel(globalContext.qt.webChannelTransport, function(c) {
     78:         if (c.objects?.bridge) {
     79:             setBridge(c.objects.bridge);
```

**❓ Perché è un problema:**
`globalThis` is the standardized way to access the global object across all JavaScript environments. Before `globalThis`,
developers had to use different global references depending on the environment:

  -  `window` in browsers 

  -  `global` in Node.js 

  -  `self` in Web Workers 

This created compatibility issues when code needed to run in multiple environments. Using environment-specific globals makes code less portable and
harder to maintain.

`globalThis` was introduced in ES2020 as a unified solution that works consistently across all JavaScript environments. It provides the
same global object reference regardless of whether your code runs in a browser, Node.js, or Web Worker.

Using `globalThis` makes your code more future-proof and eliminates the need for environment detection 

---
