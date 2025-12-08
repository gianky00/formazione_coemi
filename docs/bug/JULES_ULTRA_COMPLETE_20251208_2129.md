# 🔧 ULTRA-COMPLETE Fix Guide

**Totale:** 24 issues
**Tempo:** 3h 20min

---

## 📄 `admin/riepilogo_Bug_Sonar.py`

### Riga 227 🟡 🟡
**Problema:** Fix the syntax of this issue suppression comment.
**Regola:** `python:S7632` - Issue suppression comment should have the correct format

```python
     225:     # ReDoS-safe pattern: avoid nested quantifiers or catastrophic backtracking
     226:     # Using explicit exclusion [^&gt;]* instead of . and restricted quantifiers where possible
 >>> 227:     text = re.sub(r'&lt;a[^&gt;]*href="([^"]*)"[^&gt;]*&gt;(.*?)&lt;/a&gt;', r'[\2](\1)', text) # NOSONAR: Internal controlled input, risk acceptable
     228:     text = re.sub(r'&lt;[^&gt;]+&gt;', '', text)
     229:     
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

### Riga 228 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal r'<[^>]+>' 3 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     226:     # Using explicit exclusion [^&gt;]* instead of . and restricted quantifiers where possible
     227:     text = re.sub(r'&lt;a[^&gt;]*href="([^"]*)"[^&gt;]*&gt;(.*?)&lt;/a&gt;', r'[\2](\1)', text) # NOSONAR: Internal controlled input, risk acceptable
 >>> 228:     text = re.sub(r'&lt;[^&gt;]+&gt;', '', text)
     229:     
     230:     entities = {'&amp;nbsp;': ' ', '&amp;lt;': '&lt;', '&amp;gt;': '&gt;', '&amp;amp;': '&amp;', '&amp;quot;': '"', '&amp;#39;': "'"}
```

**❓ Perché è un problema:**
Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

### Exceptions

No issue will be raised on:

  -  duplicated string in decorators 

  -  strings with less than 5 characters 

  -  strings with only letters, numbers and underscores

**✅ Come risolvere:**
Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

### Noncompliant code example

With the default threshold of 3:

```
def run():
    prepare("action1")  # Noncompliant - "action1" is duplicated 3 times
    execute("action1")
    release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
    pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT'])  # Compliant - strings inside decorators are ignored
def projects():
    pass
```

### Compliant solution

```
ACTION_1 = "action1"

def run():
    prepare(ACTION_1)
    execute(ACTION_1)
    release(ACTION_1)
```

---

### Riga 430 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 32 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     428: # ============================================================
     429: 
 >>> 430: def parse_junit_xml():
     431:     """Parsa il file junit.xml e estrae i dettagli dei test falliti."""
     432:     global test_failures_details
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

### Riga 490 🟡 🟢
**Problema:** Remove the unused local variable "skipped".
**Regola:** `python:S1481` - Unused local variables should be removed

```python
     488:                 failure = testcase.find('failure')
     489:                 error = testcase.find('error')
 >>> 490:                 skipped = testcase.find('skipped')
     491:                 
     492:                 if failure is not None or error is not None:
```

**❓ Perché è un problema:**
An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

### What is the potential impact?

Having unused local variables in your code can lead to several issues:

  -  **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
  can distract from the main logic of the code. 

  -  **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
  to confusion and misinterpretation of the code’s inte

**✅ Come risolvere:**
The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

### Noncompliant code example

```
def hello(name):
    message = "Hello " + name # Noncompliant - message is unused
    print(name)
for i in range(10): # Noncompliant - i is unused
    foo()
```

### Compliant solution

```
def hello(name):
    message = "Hello " + name
    print(message)
for _ in range(10):
    foo()
```

---

### Riga 654 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     652: 
     653: 
 >>> 654: def fetch_all_issues():
     655:     """Recupera tutti gli issues."""
     656:     all_issues = []
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

### Riga 703 🟡 🟡
**Problema:** Add replacement fields or use a normal string instead of an f-string.
**Regola:** `python:S3457` - String formatting should be used correctly

```python
     701:     """Recupera Security Hotspots."""
     702:     all_hotspots = []
 >>> 703:     print(f"\n   Estrazione Security Hotspots...")
     704:     page = 1
     705:     
```

**❓ Perché è un problema:**
A format string is a string that contains placeholders, usually represented by special characters such as "%s" or "{}", depending on the technology
in use. These placeholders are replaced by values when the string is printed or logged. Thus, it is required that a string is valid and arguments
match replacement fields in this string.

This applies to [the % operator](https://docs.python.org/3/tutorial/inputoutput.html#old-string-formatting), the [str.format](https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method) method, and loggers from the [logging](https://docs.python.org/3/library/logging.html) module. Internally, the latter use the `%-formatting`. The only
difference is that they will log an error instead of raising an exception when the provided arguments are inv

**✅ Come risolvere:**
A `printf-`-style format string is a string that contains placeholders, which are replaced by values when the string is printed or
logged. Mismatch in the format specifiers and the arguments provided can lead to incorrect strings being created.

To avoid issues, a developer should ensure that the provided arguments match format specifiers.

### Noncompliant code example

```
"Error %(message)s" % {"message": "something failed", "extra": "some dead code"}  # Noncompliant. Remove the unused argument "extra" or add a replacement field.

"Error: User {} has not been able to access []".format("Alice", "MyFile")  # Noncompliant. Remove 1 unexpected argument or add a replacement field.

user = "Alice"
resource = "MyFile"
message = f"Error: User [user] has not been able to access [resource]"  # Noncompliant. Add replacement fields or use a normal string instead of an f-string.

import logging
logging.error("Error: User %s has not been able to access %s", "Alice")  # Noncompliant. Add 1 missing

**📚 Risorse:**
-  [Python documentation - Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax) 

  -  Python documentation - printf-style String
  Formatting 

  -  [Python documentation - Loggers](https://docs.python.org/3/howto/logging.html#loggers) 

  -  Python
  documentation - Using particular formatting styles throughout your application 

  -  Python documentation - Formatted string
  literals

---

### Riga 893 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 29 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     891: # ============================================================
     892: 
 >>> 893: def generate_test_failures_file(junit_summary, test_analysis, timestamp):
     894:     """Genera file JULES_TEST_FAILURES con tutti i dettagli."""
     895:     # pylint: disable=unused-argument
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

### Riga 910 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "| Metrica | Valore |" 4 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     908:     md.append("## 📊 Statistiche Test")
     909:     md.append("")
 >>> 910:     md.append("| Metrica | Valore |")
     911:     md.append("|---------|--------|")
     912:     md.append(f"| Test totali | {junit_summary.get('total', 0)} |")
```

**❓ Perché è un problema:**
Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

### Exceptions

No issue will be raised on:

  -  duplicated string in decorators 

  -  strings with less than 5 characters 

  -  strings with only letters, numbers and underscores

**✅ Come risolvere:**
Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

### Noncompliant code example

With the default threshold of 3:

```
def run():
    prepare("action1")  # Noncompliant - "action1" is duplicated 3 times
    execute("action1")
    release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
    pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT'])  # Compliant - strings inside decorators are ignored
def projects():
    pass
```

### Compliant solution

```
ACTION_1 = "action1"

def run():
    prepare(ACTION_1)
    execute(ACTION_1)
    release(ACTION_1)
```

---

### Riga 911 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "|---------|--------|" 4 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     909:     md.append("")
     910:     md.append("| Metrica | Valore |")
 >>> 911:     md.append("|---------|--------|")
     912:     md.append(f"| Test totali | {junit_summary.get('total', 0)} |")
     913:     md.append(f"| ✅ Passati | {junit_summary.get('passed', 0)} |")
```

**❓ Perché è un problema:**
Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

### Exceptions

No issue will be raised on:

  -  duplicated string in decorators 

  -  strings with less than 5 characters 

  -  strings with only letters, numbers and underscores

**✅ Come risolvere:**
Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

### Noncompliant code example

With the default threshold of 3:

```
def run():
    prepare("action1")  # Noncompliant - "action1" is duplicated 3 times
    execute("action1")
    release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
    pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT'])  # Compliant - strings inside decorators are ignored
def projects():
    pass
```

### Compliant solution

```
ACTION_1 = "action1"

def run():
    prepare(ACTION_1)
    execute(ACTION_1)
    release(ACTION_1)
```

---

### Riga 1010 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "**✅ Come risolvere:**" 4 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     1008:             
     1009:             # Come risolvere
 >>> 1010:             md.append("**✅ Come risolvere:**")
     1011:             md.append("")
     1012:             md.append(error_info.get('how_to_fix', 'Analizza lo stack trace per identificare il problema'))
```

**❓ Perché è un problema:**
Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

### Exceptions

No issue will be raised on:

  -  duplicated string in decorators 

  -  strings with less than 5 characters 

  -  strings with only letters, numbers and underscores

**✅ Come risolvere:**
Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

### Noncompliant code example

With the default threshold of 3:

```
def run():
    prepare("action1")  # Noncompliant - "action1" is duplicated 3 times
    execute("action1")
    release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
    pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT'])  # Compliant - strings inside decorators are ignored
def projects():
    pass
```

### Compliant solution

```
ACTION_1 = "action1"

def run():
    prepare(ACTION_1)
    execute(ACTION_1)
    release(ACTION_1)
```

---

### Riga 1017 🟡 🔴
**Problema:** Define a constant instead of duplicating this literal "**📚 Risorse:**" 3 times.
**Regola:** `python:S1192` - String literals should not be duplicated

```python
     1015:             # Risorse
     1016:             if error_info.get('resources'):
 >>> 1017:                 md.append("**📚 Risorse:**")
     1018:                 md.append("")
     1019:                 for resource in error_info.get('resources', []):
```

**❓ Perché è un problema:**
Duplicated string literals make the process of refactoring complex and error-prone, as any change would need to be propagated on all
occurrences.

### Exceptions

No issue will be raised on:

  -  duplicated string in decorators 

  -  strings with less than 5 characters 

  -  strings with only letters, numbers and underscores

**✅ Come risolvere:**
Use constants to replace the duplicated string literals. Constants can be referenced from many places, but only need to be updated in a single
place.

### Noncompliant code example

With the default threshold of 3:

```
def run():
    prepare("action1")  # Noncompliant - "action1" is duplicated 3 times
    execute("action1")
    release("action1")

@app.route("/api/users/", methods=['GET', 'POST', 'PUT'])
def users():
    pass

@app.route("/api/projects/", methods=['GET', 'POST', 'PUT'])  # Compliant - strings inside decorators are ignored
def projects():
    pass
```

### Compliant solution

```
ACTION_1 = "action1"

def run():
    prepare(ACTION_1)
    execute(ACTION_1)
    release(ACTION_1)
```

---

### Riga 1034 🟡 🟡
**Problema:** Remove the unused function parameter "junit_summary".
**Regola:** `python:S1172` - Unused function parameters should be removed

```python
     1032: 
     1033: 
 >>> 1034: def generate_dynamic_prompts(issues, analysis, issues_count, hotspots, hotspot_analysis, junit_summary, test_analysis):
     1035:     """Genera prompt dinamici."""
     1036:     prompts = {}
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

### Riga 1034 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 25 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1032: 
     1033: 
 >>> 1034: def generate_dynamic_prompts(issues, analysis, issues_count, hotspots, hotspot_analysis, junit_summary, test_analysis):
     1035:     """Genera prompt dinamici."""
     1036:     prompts = {}
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

### Riga 1093 🟡 🟡
**Problema:** Add replacement fields or use a normal string instead of an f-string.
**Regola:** `python:S3457` - String formatting should be used correctly

```python
     1091:             prompts['test_failures'] += f"- {info['emoji']} **{error_type}** ({count}x)\n"
     1092:         
 >>> 1093:         prompts['test_failures'] += f"""
 >>> 1094: ## Strategia di fix
 >>> 1095: 
 >>> 1096: ### Per AssertionError:
 >>> 1097: 1. Verifica se il test o il codice è sbagliato
 >>> 1098: 2. Se il comportamento è cambiato, aggiorna il test
 >>> 1099: 3. Se il test è corretto, correggi il codice
 >>> 1100: 
 >>> 1101: ### Per errori di tipo (TypeError, AttributeError, KeyError):
 >>> 1102: 1. Controlla i tipi dei dati
 >>> 1103: 2. Aggiungi controlli null/None
 >>> 1104: 3. Verifica che i mock siano configurati correttamente
 >>> 1105: 
 >>> 1106: ### Per errori di connessione/file:
 >>> 1107: 1. Mocka le dipendenze esterne
 >>> 1108: 2. Usa fixtures per dati di test
 >>> 1109: 3. Non dipendere da risorse esterne
 >>> 1110: 
 >>> 1111: ## File da modificare
 >>> 1112: """
     1113:         if test_analysis:
     1114:             for filepath in list(test_analysis['by_file'].keys())[:10]:
```

**❓ Perché è un problema:**
A format string is a string that contains placeholders, usually represented by special characters such as "%s" or "{}", depending on the technology
in use. These placeholders are replaced by values when the string is printed or logged. Thus, it is required that a string is valid and arguments
match replacement fields in this string.

This applies to [the % operator](https://docs.python.org/3/tutorial/inputoutput.html#old-string-formatting), the [str.format](https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method) method, and loggers from the [logging](https://docs.python.org/3/library/logging.html) module. Internally, the latter use the `%-formatting`. The only
difference is that they will log an error instead of raising an exception when the provided arguments are inv

**✅ Come risolvere:**
A `printf-`-style format string is a string that contains placeholders, which are replaced by values when the string is printed or
logged. Mismatch in the format specifiers and the arguments provided can lead to incorrect strings being created.

To avoid issues, a developer should ensure that the provided arguments match format specifiers.

### Noncompliant code example

```
"Error %(message)s" % {"message": "something failed", "extra": "some dead code"}  # Noncompliant. Remove the unused argument "extra" or add a replacement field.

"Error: User {} has not been able to access []".format("Alice", "MyFile")  # Noncompliant. Remove 1 unexpected argument or add a replacement field.

user = "Alice"
resource = "MyFile"
message = f"Error: User [user] has not been able to access [resource]"  # Noncompliant. Add replacement fields or use a normal string instead of an f-string.

import logging
logging.error("Error: User %s has not been able to access %s", "Alice")  # Noncompliant. Add 1 missing

**📚 Risorse:**
-  [Python documentation - Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax) 

  -  Python documentation - printf-style String
  Formatting 

  -  [Python documentation - Loggers](https://docs.python.org/3/howto/logging.html#loggers) 

  -  Python
  documentation - Using particular formatting styles throughout your application 

  -  Python documentation - Formatted string
  literals

---

### Riga 1173 🟡 🟢
**Problema:** Remove the unused local variable "qi".
**Regola:** `python:S1481` - Unused local variables should be removed

```python
     1171:             continue
     1172:         
 >>> 1173:         qi = [i for i in issues if i.get('software_quality') == quality]
     1174:         effort = format_duration(analysis['effort_by_quality'].get(quality, 0))
     1175:         emoji = get_quality_emoji(quality)
```

**❓ Perché è un problema:**
An unused local variable is a variable that has been declared but is not used anywhere in the block of code where it is defined. It is dead code,
contributing to unnecessary complexity and leading to confusion when reading the code. Therefore, it should be removed from your code to maintain
clarity and efficiency.

### What is the potential impact?

Having unused local variables in your code can lead to several issues:

  -  **Decreased Readability**: Unused variables can make your code more difficult to read. They add extra lines and complexity, which
  can distract from the main logic of the code. 

  -  **Misunderstanding**: When other developers read your code, they may wonder why a variable is declared but not used. This can lead
  to confusion and misinterpretation of the code’s inte

**✅ Come risolvere:**
The fix for this issue is straightforward. Once you ensure the unused variable is not part of an incomplete implementation leading to bugs, you
just need to remove it.

### Noncompliant code example

```
def hello(name):
    message = "Hello " + name # Noncompliant - message is unused
    print(name)
for i in range(10): # Noncompliant - i is unused
    foo()
```

### Compliant solution

```
def hello(name):
    message = "Hello " + name
    print(message)
for _ in range(10):
    foo()
```

---

### Riga 1201 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 44 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1199: 
     1200: 
 >>> 1201: def generate_summary(issues, analysis, issues_count, hotspots, hotspot_analysis, 
     1202:                      junit_summary, test_analysis, timestamp, generated_files):
     1203:     """Genera SUMMARY."""
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

### Riga 1211 🟡 🟡
**Problema:** Add replacement fields or use a normal string instead of an f-string.
**Regola:** `python:S3457` - String formatting should be used correctly

```python
     1209:     md.append(f"**Progetto:** {PROJECT_KEY}")
     1210:     md.append(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
 >>> 1211:     md.append(f"**Versione:** SonarCloud Exporter v5.0")
     1212:     md.append(f"**Filtro issues:** {ISSUE_STATUSES}")
     1213:     md.append("")
```

**❓ Perché è un problema:**
A format string is a string that contains placeholders, usually represented by special characters such as "%s" or "{}", depending on the technology
in use. These placeholders are replaced by values when the string is printed or logged. Thus, it is required that a string is valid and arguments
match replacement fields in this string.

This applies to [the % operator](https://docs.python.org/3/tutorial/inputoutput.html#old-string-formatting), the [str.format](https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method) method, and loggers from the [logging](https://docs.python.org/3/library/logging.html) module. Internally, the latter use the `%-formatting`. The only
difference is that they will log an error instead of raising an exception when the provided arguments are inv

**✅ Come risolvere:**
A `printf-`-style format string is a string that contains placeholders, which are replaced by values when the string is printed or
logged. Mismatch in the format specifiers and the arguments provided can lead to incorrect strings being created.

To avoid issues, a developer should ensure that the provided arguments match format specifiers.

### Noncompliant code example

```
"Error %(message)s" % {"message": "something failed", "extra": "some dead code"}  # Noncompliant. Remove the unused argument "extra" or add a replacement field.

"Error: User {} has not been able to access []".format("Alice", "MyFile")  # Noncompliant. Remove 1 unexpected argument or add a replacement field.

user = "Alice"
resource = "MyFile"
message = f"Error: User [user] has not been able to access [resource]"  # Noncompliant. Add replacement fields or use a normal string instead of an f-string.

import logging
logging.error("Error: User %s has not been able to access %s", "Alice")  # Noncompliant. Add 1 missing

**📚 Risorse:**
-  [Python documentation - Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax) 

  -  Python documentation - printf-style String
  Formatting 

  -  [Python documentation - Loggers](https://docs.python.org/3/howto/logging.html#loggers) 

  -  Python
  documentation - Using particular formatting styles throughout your application 

  -  Python documentation - Formatted string
  literals

---

### Riga 1397 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1395: 
     1396: 
 >>> 1397: def generate_hotspots_file(hotspots, hotspot_analysis, timestamp):
     1398:     """Genera file hotspots."""
     1399:     if not hotspots:
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

### Riga 1458 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1456: 
     1457: 
 >>> 1458: def generate_quality_specific_file(issues, quality, output_file):
     1459:     """Genera file per quality specifica."""
     1460:     qi = [i for i in issues if i.get('software_quality') == quality]
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

### Riga 1543 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1541: 
     1542: 
 >>> 1543: def generate_ultra_complete(issues, output_file):
     1544:     """Genera file ultra-completo."""
     1545:     by_file = group_by_file(issues)
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

### Riga 1602 🟡 🔴
**Problema:** Refactor this function to reduce its Cognitive Complexity from 36 to the 15 allowed.
**Regola:** `python:S3776` - Cognitive Complexity of functions should not be too high

```python
     1600: # ============================================================
     1601: 
 >>> 1602: def main():
     1603:     stats['start_time'] = datetime.now()
     1604:     
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

### Riga 1653 🟡 🟡
**Problema:** Add replacement fields or use a normal string instead of an f-string.
**Regola:** `python:S3457` - String formatting should be used correctly

```python
     1651:         test_analysis = analyze_test_failures()
     1652:     else:
 >>> 1653:         print(f"   ○ junit.xml non trovato")
     1654:         print(f"      Per abilitare: pytest --junitxml=junit.xml")
     1655:     
```

**❓ Perché è un problema:**
A format string is a string that contains placeholders, usually represented by special characters such as "%s" or "{}", depending on the technology
in use. These placeholders are replaced by values when the string is printed or logged. Thus, it is required that a string is valid and arguments
match replacement fields in this string.

This applies to [the % operator](https://docs.python.org/3/tutorial/inputoutput.html#old-string-formatting), the [str.format](https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method) method, and loggers from the [logging](https://docs.python.org/3/library/logging.html) module. Internally, the latter use the `%-formatting`. The only
difference is that they will log an error instead of raising an exception when the provided arguments are inv

**✅ Come risolvere:**
A `printf-`-style format string is a string that contains placeholders, which are replaced by values when the string is printed or
logged. Mismatch in the format specifiers and the arguments provided can lead to incorrect strings being created.

To avoid issues, a developer should ensure that the provided arguments match format specifiers.

### Noncompliant code example

```
"Error %(message)s" % {"message": "something failed", "extra": "some dead code"}  # Noncompliant. Remove the unused argument "extra" or add a replacement field.

"Error: User {} has not been able to access []".format("Alice", "MyFile")  # Noncompliant. Remove 1 unexpected argument or add a replacement field.

user = "Alice"
resource = "MyFile"
message = f"Error: User [user] has not been able to access [resource]"  # Noncompliant. Add replacement fields or use a normal string instead of an f-string.

import logging
logging.error("Error: User %s has not been able to access %s", "Alice")  # Noncompliant. Add 1 missing

**📚 Risorse:**
-  [Python documentation - Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax) 

  -  Python documentation - printf-style String
  Formatting 

  -  [Python documentation - Loggers](https://docs.python.org/3/howto/logging.html#loggers) 

  -  Python
  documentation - Using particular formatting styles throughout your application 

  -  Python documentation - Formatted string
  literals

---

### Riga 1654 🟡 🟡
**Problema:** Add replacement fields or use a normal string instead of an f-string.
**Regola:** `python:S3457` - String formatting should be used correctly

```python
     1652:     else:
     1653:         print(f"   ○ junit.xml non trovato")
 >>> 1654:         print(f"      Per abilitare: pytest --junitxml=junit.xml")
     1655:     
     1656:     if test_metrics:
```

**❓ Perché è un problema:**
A format string is a string that contains placeholders, usually represented by special characters such as "%s" or "{}", depending on the technology
in use. These placeholders are replaced by values when the string is printed or logged. Thus, it is required that a string is valid and arguments
match replacement fields in this string.

This applies to [the % operator](https://docs.python.org/3/tutorial/inputoutput.html#old-string-formatting), the [str.format](https://docs.python.org/3/tutorial/inputoutput.html#the-string-format-method) method, and loggers from the [logging](https://docs.python.org/3/library/logging.html) module. Internally, the latter use the `%-formatting`. The only
difference is that they will log an error instead of raising an exception when the provided arguments are inv

**✅ Come risolvere:**
A `printf-`-style format string is a string that contains placeholders, which are replaced by values when the string is printed or
logged. Mismatch in the format specifiers and the arguments provided can lead to incorrect strings being created.

To avoid issues, a developer should ensure that the provided arguments match format specifiers.

### Noncompliant code example

```
"Error %(message)s" % {"message": "something failed", "extra": "some dead code"}  # Noncompliant. Remove the unused argument "extra" or add a replacement field.

"Error: User {} has not been able to access []".format("Alice", "MyFile")  # Noncompliant. Remove 1 unexpected argument or add a replacement field.

user = "Alice"
resource = "MyFile"
message = f"Error: User [user] has not been able to access [resource]"  # Noncompliant. Add replacement fields or use a normal string instead of an f-string.

import logging
logging.error("Error: User %s has not been able to access %s", "Alice")  # Noncompliant. Add 1 missing

**📚 Risorse:**
-  [Python documentation - Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax) 

  -  Python documentation - printf-style String
  Formatting 

  -  [Python documentation - Loggers](https://docs.python.org/3/howto/logging.html#loggers) 

  -  Python
  documentation - Using particular formatting styles throughout your application 

  -  Python documentation - Formatted string
  literals

---

## 📄 `guide_frontend/src/components/Sidebar.jsx`

### Riga 77 🟡 🟡
**Problema:** Remove this useless assignment to variable "channel".
**Regola:** `javascript:S1854` - Unused assignments should be removed

```jsx
     75:       // Assign to a variable to prevent object from being dropped immediately
     76:       // eslint-disable-next-line no-unused-vars
 >>> 77:       const channel = new globalContext.QWebChannel(globalContext.qt.webChannelTransport, function(c) {
     78:         if (c.objects?.bridge) {
     79:             setBridge(c.objects.bridge);
```

**❓ Perché è un problema:**
Dead stores refer to assignments made to local variables that are subsequently never used or immediately overwritten. Such assignments are
unnecessary and don’t contribute to the functionality or clarity of the code. They may even negatively impact performance. Removing them enhances code
cleanliness and readability. Even if the unnecessary operations do not do any harm in terms of the program’s correctness, they are - at best - a waste
of computing resources.

### Exceptions

The rule ignores

  -  Initializations to `-1`, `0`, `1`, `undefined`, `[]`, `{}`,
  `true`, `false` and `""`. 

  -  Variables that start with an underscore (e.g. `_unused`) are ignored. 

  -  Assignment of `null` is ignored because it is sometimes used to help garbage collection 

  -  Increment and decrement expr

**✅ Come risolvere:**
Remove the unnecessary assignment, then test the code to make sure that the right-hand side of a given assignment had no side effects (e.g. a
method that writes certain data to a file and returns the number of written bytes).

### Noncompliant code example

```
function foo(y) {
  let x = 100; // Noncompliant: dead store
  x = 150;     // Noncompliant: dead store
  x = 200;
  return x + y;
}
```

### Compliant solution

```
function foo(y) {
  let x = 200; // Compliant: no unnecessary assignment
  return x + y;
}
```

**📚 Risorse:**
### Standards

  -  CWE - [CWE-563 - Assignment to Variable without Use ('Unused Variable')](https://cwe.mitre.org/data/definitions/563) 

### Related rules

  -  S1763 - All code should be reachable 

  -  S2589 - Boolean expressions should not be gratuitous 

  -  S3516 - Function returns should not be invariant 

  -  S3626 - Jump statements should not be redundant

---
